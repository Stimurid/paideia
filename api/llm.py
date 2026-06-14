"""LLM-обвес с двумя openai-совместимыми провайдерами.

- Primary: 302.ai (роутер).
- Fallback: MAI Qwen.

При любой ошибке primary (auth, timeout, network, model_error) переключается на
fallback. Если оба упали — поднимает LlmProviderError.

Тут одна точка вызова `chat()` и одна `embed()`. Прикладной код (extractor,
matcher, verifier, wave_runner) не знает про провайдеров и retry-логику.

Адаптировано из C:/projects/memory-workbench/backend/app/services/llm.py.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from openai import (
    APIConnectionError,
    APIError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    NotFoundError,
    OpenAI,
)

from .config import Settings, get_settings

logger = logging.getLogger(__name__)

Role = Literal["system", "user", "assistant"]


@dataclass
class ProviderConfig:
    name: str
    base_url: str
    api_key: str
    model: str
    embed_model: str

    @property
    def configured(self) -> bool:
        return bool(self.base_url and self.api_key)


@dataclass
class LlmProviderError(Exception):
    status: str
    detail: str
    provider: str | None = None

    def __str__(self) -> str:
        return f"[{self.provider or '?'}/{self.status}] {self.detail}"


def _map_error(exc: Exception) -> tuple[str, str]:
    if isinstance(exc, APITimeoutError):
        return "timeout", "Provider request timed out"
    if isinstance(exc, AuthenticationError):
        return "auth_error", "Authentication failed: check API key"
    if isinstance(exc, NotFoundError):
        return "model_error", "Model not found for this provider/base_url"
    if isinstance(exc, BadRequestError):
        return "model_error", f"Bad request: {exc}"
    if isinstance(exc, APIConnectionError):
        return "network_error", "Provider unreachable"
    if isinstance(exc, APIError):
        return "provider_error", f"API error: {exc}"
    return "provider_error", f"Unexpected: {exc}"


class LlmClient:
    """Тонкая обёртка над двумя openai-совместимыми провайдерами с failover."""

    def __init__(self, settings: Settings | None = None, timeout_seconds: float = 180.0) -> None:
        s = settings or get_settings()
        self.timeout_seconds = timeout_seconds
        # BYOK: подменяем primary если у текущей сессии есть свой ключ
        api_key = s.llm_primary_api_key
        base_url = s.llm_primary_base_url
        try:
            from . import session as session_mod, byok as byok_mod
            sid = session_mod.current_session.get()
            if sid:
                personal_key, personal_url, _overrides = byok_mod.llm_credentials_for(sid)
                if personal_key and personal_key != s.llm_primary_api_key:
                    api_key = personal_key
                    base_url = personal_url or s.llm_primary_base_url
        except Exception:
            pass
        self.primary = ProviderConfig(
            name="302.ai",
            base_url=base_url,
            api_key=api_key,
            model=s.llm_primary_model,
            embed_model=s.llm_primary_embed_model,
        )
        self.fallback = ProviderConfig(
            name="MAI Qwen",
            base_url=s.llm_fallback_base_url,
            api_key=s.llm_fallback_api_key,
            model=s.llm_fallback_model,
            embed_model=s.llm_fallback_embed_model,
        )

    # --- internals -----------------------------------------------------------

    def _client(self, p: ProviderConfig) -> OpenAI:
        return OpenAI(api_key=p.api_key, base_url=p.base_url, timeout=self.timeout_seconds)

    def _ordered_providers(self) -> list[ProviderConfig]:
        out: list[ProviderConfig] = []
        if self.primary.configured:
            out.append(self.primary)
        if self.fallback.configured and self.fallback.base_url != self.primary.base_url:
            out.append(self.fallback)
        if not out:
            raise LlmProviderError("not_configured", "No LLM provider configured (set LLM_*_API_KEY)")
        return out

    # --- public API ----------------------------------------------------------

    # --- usage (tokens) shared bucket --------------------------------------

    # Последний chat-вызов сохраняет usage здесь, чтобы _audit мог его подцепить
    # без переделки всех callsite. Thread-local, чтобы не было гонок при
    # параллельных uvicorn workers.
    _last_usage: threading.local = threading.local()

    @classmethod
    def last_usage(cls) -> dict | None:
        return getattr(cls._last_usage, "value", None)

    @classmethod
    def _set_last_usage(cls, value: dict | None) -> None:
        cls._last_usage.value = value

    # --- cache --------------------------------------------------------------

    @staticmethod
    def _cache_dir() -> Path:
        return Path(__file__).resolve().parent.parent / "db" / "llm_cache"

    @staticmethod
    def _cache_key(provider: str, model: str, messages: list[dict],
                   temperature: float, response_format: Any) -> str:
        h = hashlib.sha256()
        payload = json.dumps({
            "provider": provider, "model": model, "messages": messages,
            "temperature": round(temperature, 3),
            "response_format": response_format,
        }, ensure_ascii=False, sort_keys=True)
        h.update(payload.encode("utf-8"))
        return h.hexdigest()[:32]

    @classmethod
    def _cache_get(cls, key: str) -> dict | None:
        if os.getenv("LLM_CACHE_ENABLED", "1") == "0":
            return None
        path = cls._cache_dir() / f"{key}.json"
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return None

    @classmethod
    def _cache_put(cls, key: str, value: dict) -> None:
        if os.getenv("LLM_CACHE_ENABLED", "1") == "0":
            return
        d = cls._cache_dir()
        d.mkdir(parents=True, exist_ok=True)
        try:
            (d / f"{key}.json").write_text(
                json.dumps(value, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception as exc:
            logger.warning("llm cache write failed: %s", exc)

    def chat(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float = 0.2,
        response_format: dict[str, Any] | None = None,
        model_override: str | None = None,
    ) -> str:
        """Простой чат-завершение, возвращает строку.

        response_format={"type": "json_object"} — для structured output, где это
        поддерживается провайдером.

        Кеш по hash(provider+model+messages+temperature+response_format).
        Отключается через LLM_CACHE_ENABLED=0.
        """
        last_error: LlmProviderError | None = None
        for provider in self._ordered_providers():
            model = model_override or provider.model
            cache_key = self._cache_key(provider.name, model, messages,
                                        temperature, response_format)
            cached = self._cache_get(cache_key)
            if cached:
                logger.debug("chat via %s cached", provider.name)
                self._set_last_usage({
                    **(cached.get("usage") or {}),
                    "cached": True, "provider": provider.name, "model": model,
                })
                return cached.get("content", "")

            client = self._client(provider)
            kwargs: dict[str, Any] = {
                "model": model, "messages": messages, "temperature": temperature,
            }
            if response_format:
                kwargs["response_format"] = response_format
            try:
                response = client.chat.completions.create(**kwargs)
                content = (response.choices[0].message.content or "").strip()
                usage_raw = getattr(response, "usage", None)
                usage = {
                    "prompt_tokens": getattr(usage_raw, "prompt_tokens", None),
                    "completion_tokens": getattr(usage_raw, "completion_tokens", None),
                    "total_tokens": getattr(usage_raw, "total_tokens", None),
                    "cached": False, "provider": provider.name, "model": model,
                } if usage_raw else {"provider": provider.name, "model": model,
                                     "cached": False}
                self._set_last_usage(usage)
                self._cache_put(cache_key, {"content": content, "usage": usage})
                logger.debug("chat via %s ok (%d chars, %s tokens)",
                             provider.name, len(content),
                             usage.get("total_tokens", "?"))
                return content
            except Exception as exc:
                status, detail = _map_error(exc)
                last_error = LlmProviderError(status=status, detail=detail, provider=provider.name)
                logger.warning("chat via %s failed: %s", provider.name, last_error)
                continue
        raise last_error or LlmProviderError("provider_error", "all providers failed")

    def chat_json(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float = 0.0,
    ) -> dict[str, Any]:
        """Чат с гарантированным JSON-ответом. Парсит результат."""
        raw = self.chat(messages, temperature=temperature, response_format={"type": "json_object"})
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            raise LlmProviderError("model_error", f"non-JSON response: {raw[:200]}") from exc

    def embed(self, texts: list[str], *, model_override: str | None = None) -> list[list[float]]:
        last_error: LlmProviderError | None = None
        for provider in self._ordered_providers():
            client = self._client(provider)
            try:
                response = client.embeddings.create(
                    model=model_override or provider.embed_model,
                    input=texts,
                )
                return [d.embedding for d in response.data]
            except Exception as exc:
                status, detail = _map_error(exc)
                last_error = LlmProviderError(status=status, detail=detail, provider=provider.name)
                logger.warning("embed via %s failed: %s", provider.name, last_error)
                continue
        raise last_error or LlmProviderError("provider_error", "all providers failed")

    def chat_fast(self, messages: list[dict[str, str]], **kw: Any) -> str:
        s = get_settings()
        return self.chat(messages, model_override=s.llm_fast_model, **kw)

    def chat_deep(self, messages: list[dict[str, str]], **kw: Any) -> str:
        s = get_settings()
        return self.chat(messages, model_override=s.llm_deep_model, **kw)

    def chat_search(self, messages: list[dict[str, str]], **kw: Any) -> dict[str, Any]:
        """Веб-поиск через sonar-pro. Возвращает {text, citations}."""
        s = get_settings()
        provider = self._ordered_providers()[0]
        client = self._client(provider)
        try:
            response = client.chat.completions.create(
                model=s.llm_search_model,
                messages=messages,
                temperature=kw.get("temperature", 0.2),
            )
        except Exception as exc:
            status, detail = _map_error(exc)
            raise LlmProviderError(status=status, detail=detail, provider=provider.name) from exc
        text = (response.choices[0].message.content or "").strip()
        citations: list[str] = []
        # Perplexity-style возвращает citations в extra полях
        raw = getattr(response, "model_extra", {}) or {}
        for key in ("citations", "search_results", "sources"):
            if key in raw and isinstance(raw[key], list):
                for c in raw[key]:
                    if isinstance(c, str):
                        citations.append(c)
                    elif isinstance(c, dict) and c.get("url"):
                        citations.append(c["url"])
        # некоторые модели прячут citations внутри choices[0]
        choice_extra = getattr(response.choices[0], "model_extra", {}) or {}
        if "citations" in choice_extra and not citations:
            citations = [c if isinstance(c, str) else c.get("url", "") for c in choice_extra["citations"]]
        return {"text": text, "citations": [c for c in citations if c]}

    def ping(self) -> dict[str, Any]:
        """Минимальная диагностика: какой провайдер отвечает первым."""
        try:
            providers = self._ordered_providers()
        except LlmProviderError as exc:
            return {"ok": False, "error": str(exc)}

        result: dict[str, Any] = {"ok": False, "providers": []}
        reply: str | None = None
        for provider in providers:
            entry: dict[str, Any] = {"name": provider.name, "model": provider.model}
            try:
                client = self._client(provider)
                response = client.chat.completions.create(
                    model=provider.model,
                    messages=[{"role": "user", "content": "Reply with: ok"}],
                    temperature=0.0,
                )
                reply = (response.choices[0].message.content or "").strip()
                entry["ok"] = True
                entry["reply"] = reply[:80]
                result["providers"].append(entry)
                result["ok"] = True
                result["active"] = provider.name
                break
            except Exception as exc:
                status, detail = _map_error(exc)
                entry["ok"] = False
                entry["status"] = status
                entry["detail"] = detail
                result["providers"].append(entry)
        return result


_clients: dict[str, LlmClient] = {}


def get_llm() -> LlmClient:
    """Session-aware кеш: для каждой сессии свой LlmClient (BYOK).
    Без сессии — общий платформенный."""
    try:
        from . import session as session_mod
        sid = session_mod.current_session.get() or "_platform"
    except Exception:
        sid = "_platform"
    if sid not in _clients:
        _clients[sid] = LlmClient()
    return _clients[sid]


def invalidate_llm_cache(session_id: str | None = None) -> None:
    """Сброс кеша — нужен когда юзер поменял свой ключ."""
    if session_id and session_id in _clients:
        del _clients[session_id]
    elif session_id is None:
        _clients.clear()
