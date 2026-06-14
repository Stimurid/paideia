"""LLM-агенты Paideia: section-filler, url-importer и др.

Каждый вызов логируется в llm_runs для аудита.
"""

from __future__ import annotations

import json
import re
import sqlite3
import time
from datetime import date
from pathlib import Path
from typing import Any

import frontmatter

from .config import get_settings
from .db import open_db, fetch_all
from .llm import get_llm
from .schemas import CANVAS_KEYS, CANVAS_SECTIONS

ROOT = Path(__file__).resolve().parent.parent
PROMPTS = ROOT / "prompts"
CASES_DIR = ROOT / "content" / "cases"
PROJECTS_DIR = ROOT / "content" / "projects"


def _entity_dir(kind: str) -> Path:
    if kind == "case":
        return CASES_DIR
    if kind == "project":
        return PROJECTS_DIR
    raise ValueError(f"unsupported entity kind: {kind}")


def _load_entity_md(kind: str, entity_id: str) -> tuple[Path, frontmatter.Post]:
    path = _entity_dir(kind) / f"{entity_id}.md"
    if not path.exists():
        raise FileNotFoundError(f"{kind} '{entity_id}' not found")
    return path, frontmatter.load(path)


def _load_prompt(name: str) -> str:
    return (PROMPTS / f"{name}.md").read_text(encoding="utf-8")


def _section_title(section_id: str) -> str:
    return dict(CANVAS_SECTIONS).get(section_id, section_id)


_PRICING_CACHE: dict | None = None


def _load_pricing() -> dict[str, dict[str, float]]:
    """Кеш цен по моделям из taxonomy/llm_pricing.yaml."""
    global _PRICING_CACHE
    if _PRICING_CACHE is not None:
        return _PRICING_CACHE
    import yaml as _yaml
    from pathlib import Path as _Path
    path = _Path(__file__).resolve().parent.parent / "taxonomy" / "llm_pricing.yaml"
    if not path.exists():
        _PRICING_CACHE = {}
    else:
        try:
            data = _yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            _PRICING_CACHE = data.get("pricing") or {}
        except Exception:
            _PRICING_CACHE = {}
    return _PRICING_CACHE


def _cost_for(model: str | None, tokens_prompt: int | None,
              tokens_completion: int | None) -> float | None:
    if not model:
        return None
    prices = _load_pricing().get(model)
    if not prices:
        return None
    p = prices.get("prompt_per_1m") or 0
    c = prices.get("completion_per_1m") or 0
    cost = ((tokens_prompt or 0) / 1_000_000) * p + ((tokens_completion or 0) / 1_000_000) * c
    return round(cost, 6) if cost else None


def _audit(conn: sqlite3.Connection, *, purpose: str, model_role: str,
           target_kind: str | None, target_id: str | None, section_id: str | None,
           input_obj: dict[str, Any], output_obj: dict[str, Any] | None,
           citations: list[str], status: str, error: str | None,
           duration_ms: int) -> int:
    # Пытаемся подцепить usage из последнего chat-вызова
    from .llm import LlmClient
    usage = LlmClient.last_usage() or {}
    tokens_prompt = usage.get("prompt_tokens")
    tokens_completion = usage.get("completion_tokens")
    tokens_total = usage.get("total_tokens")
    provider_name = usage.get("provider")
    model_name = usage.get("model")
    cached = 1 if usage.get("cached") else 0
    cost_usd = _cost_for(model_name, tokens_prompt, tokens_completion)

    from .session import current_session, current_ip
    sid = current_session.get()
    ip = current_ip.get()

    cur = conn.execute(
        """
        INSERT INTO llm_runs
        (purpose, model_role, target_kind, target_id, section_id,
         input_json, output_json, citations_json, status, error, duration_ms,
         tokens_prompt, tokens_completion, tokens_total,
         provider_name, model_name, cached, cost_usd, session_id, client_ip)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            purpose, model_role, target_kind, target_id, section_id,
            json.dumps(input_obj, ensure_ascii=False),
            json.dumps(output_obj, ensure_ascii=False) if output_obj else None,
            json.dumps(citations, ensure_ascii=False),
            status, error, duration_ms,
            tokens_prompt, tokens_completion, tokens_total,
            provider_name, model_name, cached, cost_usd, sid, ip,
        ),
    )
    conn.commit()
    return cur.lastrowid


# ---------------------------------------------------------------------------
# Section filler
# ---------------------------------------------------------------------------


def _load_case_md(case_id: str) -> tuple[Path, frontmatter.Post]:
    path = CASES_DIR / f"{case_id}.md"
    if not path.exists():
        raise FileNotFoundError(f"case '{case_id}' not found")
    return path, frontmatter.load(path)


def _case_summary_for_prompt(post: frontmatter.Post) -> dict[str, Any]:
    """Минимальная сводка кейса для контекста LLM."""
    m = post.metadata
    org = m.get("organization") or {}
    ai = m.get("ai") or {}
    return {
        "id": m.get("id"),
        "name": m.get("name"),
        "organization": {
            "name": org.get("name"),
            "country": org.get("country"),
            "type": org.get("type"),
        },
        "ai": {
            "pattern": ai.get("pattern"),
            "agentivity": ai.get("agentivity"),
            "technologies": ai.get("technologies"),
        },
        "facets": m.get("facets") or {},
        "transformation_mode": m.get("transformation_mode"),
        "lifecycle": m.get("lifecycle") or {},
    }


def fill_section(case_id: str, section_id: str, *, model_role: str = "search") -> dict[str, Any]:
    """Заполнить одну секцию канваса конкретного кейса через LLM с веб-поиском.

    Возвращает {section_id, text, confidence, sources, open_gaps} + audit_id.
    Карточку НЕ сохраняет на диск — это делает отдельный save_section.
    """
    if section_id not in CANVAS_KEYS:
        raise ValueError(f"unknown section '{section_id}'")

    path, post = _load_case_md(case_id)
    case_summary = _case_summary_for_prompt(post)
    section_title = _section_title(section_id)
    system_prompt = _load_prompt("section_filler")

    # RAG: ищем релевантные фрагменты из архива пользователя
    archive_context = ""
    try:
        from .retrieve import retrieve_archive
        org_name = case_summary.get("organization", {}).get("name") or ""
        rag_query = f"{case_summary.get('name','')} {section_title} {org_name}"
        chunks = retrieve_archive(rag_query, top_k=4)
        if chunks:
            archive_context = (
                "\n\nКонтекст из архива пользователя (опирайся на это в приоритете, "
                "если совпадает с веб-источниками):\n\n"
            )
            for ch in chunks:
                archive_context += (
                    f"--- [{ch['file_path']} @ offset {ch['offset']}, distance {ch['distance']}] ---\n"
                    f"{ch['text'][:1200]}\n\n"
                )
    except Exception:
        pass  # если индекс пуст или эмбеддинги недоступны — продолжаем без RAG

    user_prompt = (
        f"Кейс:\n```json\n{json.dumps(case_summary, ensure_ascii=False, indent=2)}\n```\n\n"
        f"Заполни секцию `{section_id}` («{section_title}»).\n"
        f"Верни строгий JSON по схеме из system-промпта."
        f"{archive_context}"
    )

    llm = get_llm()
    started = time.time()
    conn = open_db()
    try:
        try:
            if model_role == "search":
                res = llm.chat_search([
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ])
                text_raw = res["text"]
                citations = res["citations"]
            else:
                method = llm.chat_deep if model_role == "deep" else llm.chat_fast
                text_raw = method([
                    {"role": "system", "content": system_prompt + "\n\nВыведи только JSON, без markdown-обёртки."},
                    {"role": "user", "content": user_prompt},
                ])
                citations = []
            duration_ms = int((time.time() - started) * 1000)

            parsed = _extract_json(text_raw)
            if not parsed:
                raise ValueError(f"could not extract JSON from LLM response: {text_raw[:300]}")
            if not parsed.get("section_id"):
                parsed["section_id"] = section_id
            # объединить citations
            url_set = set(citations)
            for s in parsed.get("sources") or []:
                if isinstance(s, dict) and s.get("url"):
                    url_set.add(s["url"])
            citations = sorted(url_set)

            _audit(conn,
                   purpose="section_filler", model_role=model_role,
                   target_kind="case", target_id=case_id, section_id=section_id,
                   input_obj={"case_summary": case_summary, "section": section_id},
                   output_obj=parsed, citations=citations,
                   status="ok", error=None, duration_ms=duration_ms)
            parsed["citations"] = citations
            parsed["model_role"] = model_role
            parsed["duration_ms"] = duration_ms
            return parsed
        except Exception as exc:
            duration_ms = int((time.time() - started) * 1000)
            _audit(conn,
                   purpose="section_filler", model_role=model_role,
                   target_kind="case", target_id=case_id, section_id=section_id,
                   input_obj={"case_summary": case_summary, "section": section_id},
                   output_obj=None, citations=[],
                   status="error", error=str(exc), duration_ms=duration_ms)
            raise
    finally:
        conn.close()


def fill_project_section(project_id: str, section_id: str, *,
                         model_role: str = "deep") -> dict[str, Any]:
    """Заполнить секцию канваса своего проекта.

    Не делает веб-поиск: использует контекст из корпуса + RAG твоего архива +
    рассуждение LLM (gpt-5 по умолчанию).
    """
    if section_id not in CANVAS_KEYS:
        raise ValueError(f"unknown section '{section_id}'")

    path, post = _load_entity_md("project", project_id)
    section_title = _section_title(section_id)
    system_prompt = _load_prompt("project_section_filler")

    # Сводка проекта
    fm = post.metadata
    project_summary = {
        "id": fm.get("id"),
        "name": fm.get("name"),
        "author": fm.get("author"),
        "status": fm.get("status"),
        "organization": fm.get("organization"),
        "facets": fm.get("facets"),
        "ai": fm.get("ai"),
        "transformation_mode": fm.get("transformation_mode"),
        "axes": fm.get("axes"),
        "analogues": fm.get("analogues") or [],
    }
    existing_canvas = fm.get("canvas") or {}

    # Контекст: аналоги из корпуса
    analogues_context = ""
    analogue_ids = (fm.get("analogues") or [])[:5]
    if analogue_ids:
        conn = open_db()
        try:
            rows = fetch_all(
                conn,
                f"SELECT id, name, org_name, country, pattern, agentivity FROM cases WHERE id IN ({','.join('?'*len(analogue_ids))})",
                tuple(analogue_ids),
            )
            if rows:
                analogues_context = "\n\nАналоги-кейсы из корпуса (заявлены тобой):\n"
                for r in rows:
                    analogues_context += f"- [[{r['id']}]] {r['name']} · {r['org_name']} · {r['country']} · pattern {r['pattern']} · a{r['agentivity']}\n"
        finally:
            conn.close()

    # RAG из архива
    archive_context = ""
    try:
        from .retrieve import retrieve_archive
        rag_query = f"{fm.get('name','')} {section_title} {fm.get('author','')}"
        chunks = retrieve_archive(rag_query, top_k=4)
        if chunks:
            archive_context = "\n\nКонтекст из твоего архива (используй, если совпадает с замыслом):\n\n"
            for ch in chunks:
                archive_context += (
                    f"--- [{ch['file_path']} @ offset {ch['offset']}, distance {ch['distance']}] ---\n"
                    f"{ch['text'][:1200]}\n\n"
                )
    except Exception:
        pass

    # Уже заполненные секции — для согласованности
    canvas_brief = ""
    for sid, sdata in existing_canvas.items():
        if sid == section_id:
            continue
        if isinstance(sdata, dict) and sdata.get("text"):
            canvas_brief += f"\n[{sid}] {sdata['text'][:400]}\n"

    user_prompt = (
        f"Проект:\n```json\n{json.dumps(project_summary, ensure_ascii=False, indent=2)}\n```\n\n"
        f"Уже заполненные секции канваса:{canvas_brief or ' (пока ничего)'}\n\n"
        f"Заполни секцию `{section_id}` («{section_title}»). Верни строгий JSON по схеме."
        f"{analogues_context}"
        f"{archive_context}"
    )

    llm = get_llm()
    started = time.time()
    conn = open_db()
    try:
        try:
            method = llm.chat_deep if model_role == "deep" else llm.chat_fast
            text_raw = method([
                {"role": "system", "content": system_prompt + "\n\nВыведи только JSON, без markdown-обёртки."},
                {"role": "user", "content": user_prompt},
            ])
            duration_ms = int((time.time() - started) * 1000)
            parsed = _extract_json(text_raw)
            if not parsed:
                raise ValueError(f"could not extract JSON: {text_raw[:300]}")
            if not parsed.get("section_id"):
                parsed["section_id"] = section_id
            _audit(conn,
                   purpose="project_section_filler", model_role=model_role,
                   target_kind="project", target_id=project_id, section_id=section_id,
                   input_obj={"section": section_id, "analogues_count": len(analogue_ids)},
                   output_obj=parsed, citations=[], status="ok", error=None,
                   duration_ms=duration_ms)
            parsed["model_role"] = model_role
            parsed["duration_ms"] = duration_ms
            return parsed
        except Exception as exc:
            duration_ms = int((time.time() - started) * 1000)
            _audit(conn,
                   purpose="project_section_filler", model_role=model_role,
                   target_kind="project", target_id=project_id, section_id=section_id,
                   input_obj={"section": section_id},
                   output_obj=None, citations=[], status="error", error=str(exc),
                   duration_ms=duration_ms)
            raise
    finally:
        conn.close()


def save_section(entity_id: str, section_id: str, text: str, *,
                 status: str = "draft", source: str = "manual",
                 entity_kind: str = "case") -> None:
    """Сохранить секцию канваса обратно в md-файл (case или project)."""
    if section_id not in CANVAS_KEYS:
        raise ValueError(f"unknown section '{section_id}'")
    path, post = _load_entity_md(entity_kind, entity_id)
    canvas = post.metadata.get("canvas") or {}
    canvas[section_id] = {
        "text": text,
        "status": status,
        "source": source,
        "updated_at": date.today().isoformat(),
    }
    post.metadata["canvas"] = canvas
    raw = frontmatter.dumps(
        post, handler=frontmatter.YAMLHandler(),
        default_flow_style=False, allow_unicode=True, sort_keys=False,
    )
    path.write_text(raw + ("\n" if not raw.endswith("\n") else ""), encoding="utf-8")
    _auto_git_commit(
        path,
        f"canvas: {entity_kind}/{entity_id}/{section_id} ({source})",
    )


def _auto_git_commit(file_path: Path, message: str) -> None:
    """Автокоммит изменений в content/ — если репо git-инициализирован.

    Тихо игнорирует ошибки: если git не инициализирован, или nothing to commit,
    или git не в PATH — просто не делаем ничего.
    """
    try:
        import subprocess
        rel = file_path.relative_to(ROOT)
        # проверка что есть .git
        if not (ROOT / ".git").exists():
            return
        subprocess.run(
            ["git", "add", str(rel)],
            cwd=ROOT, capture_output=True, timeout=10, check=False,
        )
        subprocess.run(
            ["git", "commit", "-m", message, "--no-verify"],
            cwd=ROOT, capture_output=True, timeout=10, check=False,
        )
    except Exception:
        pass


# ---------------------------------------------------------------------------
# URL importer
# ---------------------------------------------------------------------------


def import_from_url(url: str) -> dict[str, Any]:
    """Извлечь черновик кейса из URL или вставленного текста."""
    system_prompt = _load_prompt("url_importer")
    user_prompt = (
        f"Источник: {url}\n\n"
        "Прогуляйся по этому источнику и связанным страницам, найди кейс/кейсы "
        "внедрения ИИ в образовании. Верни draft md как описано."
    )
    llm = get_llm()
    started = time.time()
    conn = open_db()
    try:
        try:
            res = llm.chat_search([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ])
            duration_ms = int((time.time() - started) * 1000)
            parsed = _extract_json(res["text"])
            if not parsed:
                raise ValueError(f"could not extract JSON: {res['text'][:300]}")
            citations = sorted(set(res["citations"]))
            _audit(conn,
                   purpose="url_importer", model_role="search",
                   target_kind="case", target_id=parsed.get("id"), section_id=None,
                   input_obj={"url": url},
                   output_obj=parsed, citations=citations,
                   status="ok", error=None, duration_ms=duration_ms)
            parsed["citations"] = citations
            parsed["duration_ms"] = duration_ms
            return parsed
        except Exception as exc:
            duration_ms = int((time.time() - started) * 1000)
            _audit(conn,
                   purpose="url_importer", model_role="search",
                   target_kind="case", target_id=None, section_id=None,
                   input_obj={"url": url}, output_obj=None, citations=[],
                   status="error", error=str(exc), duration_ms=duration_ms)
            raise
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Wave runner — дифф-прогон за период
# ---------------------------------------------------------------------------


def _known_cases_for_wave_prompt() -> list[dict[str, Any]]:
    """Лёгкая выборка известных кейсов для контекста wave-runner'а."""
    conn = open_db()
    try:
        rows = conn.execute(
            """
            SELECT id, name, country, pattern, agentivity, lifecycle_stage
            FROM cases ORDER BY id
            """
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# Расширенная сетка терминов (en+ru) для standard/deep режимов
_WAVE_SCAN_QUERIES = [
    "AI orchestration in higher education pilot 2026",
    "AI digital textbook ministry of education 2026",
    "multi-agent classroom LLM tutor university deployment",
    "ChatGPT Edu rollout university 2026 metrics",
    "agentic AI in education academic paper 2026",
    "Socratic AI tutor pilot results university 2026",
    "internal university AI platform private LLM Azure 2026",
    "Российский университет внедрение генеративного ИИ 2026",
    "цифровой учебник ИИ Россия Минпросвещения 2026",
    "AI cheating rollback university 2026",
    "Anthology Blackboard AI deployment higher education 2026",
    "Instructure Canvas AI agent rollout 2026",
]


def run_wave(window_from: str, window_to: str, focus: str | None = None,
             depth: str = "standard") -> dict[str, Any]:
    """Прогнать дифф-волну за период [window_from, window_to].

    depth:
      - quick: один sonar-pro вызов с общим промптом (~10 с, ~10 источников)
      - standard: 4 параллельных скан-запроса разных тематических веток +
        синтез через gpt-5 (~40-60 с, ~30 источников)
      - deep: 8 скан-запросов (en+ru) + синтез + перепроверка через gpt-5
        (~2-4 мин, ~50 источников)
    """
    if depth not in ("quick", "standard", "deep"):
        depth = "standard"
    if depth == "quick":
        return _run_wave_quick(window_from, window_to, focus)
    return _run_wave_multi(window_from, window_to, focus, depth)


def _run_wave_quick(window_from: str, window_to: str, focus: str | None) -> dict[str, Any]:
    system_prompt = _load_prompt("wave_runner")
    known = _known_cases_for_wave_prompt()
    known_compact = [{"id": k["id"], "name": k["name"], "country": k["country"],
                      "pattern": k["pattern"], "a": k["agentivity"],
                      "stage": k["lifecycle_stage"]} for k in known]
    user_prompt = (
        f"Окно: {window_from} → {window_to}.\n"
        + (f"Фокус: {focus}.\n" if focus else "")
        + "Известные кейсы корпуса (не дублируй):\n"
        + json.dumps(known_compact, ensure_ascii=False)
        + "\n\nВыполни дифф-прогон. Верни строгий JSON."
    )
    llm = get_llm()
    started = time.time()
    conn = open_db()
    try:
        res = llm.chat_search([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ])
        duration_ms = int((time.time() - started) * 1000)
        parsed = _extract_json(res["text"]) or {}
        citations = sorted(set(res["citations"]))
        wave_id = parsed.get("wave_id") or f"diff-{window_to}-quick"
        parsed["wave_id"] = wave_id
        trace = [{"step": "quick_scan", "query": "(single)", "raw_chars": len(res["text"]),
                  "citations": len(citations)}]
        return _finalize_wave(conn, parsed, citations, wave_id, window_from, window_to,
                              focus, depth="quick", duration_ms=duration_ms,
                              trace=trace, system_prompt=system_prompt, user_prompt=user_prompt)
    finally:
        conn.close()


def _run_wave_multi(window_from: str, window_to: str, focus: str | None,
                    depth: str) -> dict[str, Any]:
    """Standard/deep: запускаем серию скан-запросов, потом синтезируем gpt-5."""
    system_prompt = _load_prompt("wave_runner")
    known = _known_cases_for_wave_prompt()
    known_compact = [{"id": k["id"], "name": k["name"], "country": k["country"],
                      "pattern": k["pattern"], "a": k["agentivity"],
                      "stage": k["lifecycle_stage"]} for k in known]
    known_ids = {k["id"].lower() for k in known}
    known_names = {(k["name"] or "").lower() for k in known}

    queries = _WAVE_SCAN_QUERIES[:4] if depth == "standard" else _WAVE_SCAN_QUERIES
    llm = get_llm()
    started = time.time()
    conn = open_db()
    try:
        # ---- Этап 1: скан-запросы через sonar-pro ----
        scan_results: list[dict[str, Any]] = []
        all_citations: set[str] = set()
        trace: list[dict[str, Any]] = []
        scan_system = (
            "Ты исследователь поля «AI в образовании». Сделай узкий "
            "веб-поиск по запросу, верни сырые находки в формате:\n"
            "FINDING <id>: <org> · <country> · <дата>\n  url: <url>\n  short: <1-2 предложения>\n\n"
            f"Окно поиска: {window_from} → {window_to}. "
            "Не дублируй известные кейсы. Не выдумывай ссылок."
        )
        for q in queries:
            try:
                qres = llm.chat_search([
                    {"role": "system", "content": scan_system},
                    {"role": "user", "content": f"Запрос: {q}\n\nИзвестные кейсы (не дублируй):\n{json.dumps([k['id'] for k in known_compact], ensure_ascii=False)}"},
                ])
                scan_results.append({"query": q, "text": qres["text"], "citations": qres["citations"]})
                all_citations.update(qres["citations"])
                trace.append({"step": "scan", "query": q, "chars": len(qres["text"]),
                              "citations": len(qres["citations"])})
            except Exception as exc:
                trace.append({"step": "scan_error", "query": q, "error": str(exc)})

        # ---- Этап 2: синтез через gpt-5 (deep reasoning) ----
        scan_dump = "\n\n".join(
            f"### Скан-запрос: {sr['query']}\n{sr['text']}" for sr in scan_results
        )
        synthesis_messages = [
            {"role": "system", "content": system_prompt
             + "\n\nВ контексте ниже — сырые находки от sonar-pro по серии "
               "тематических запросов. Твоя задача: разобрать их, дедупить, "
               "сравнить с известным корпусом, разложить по схеме JSON. "
               "Каждое утверждение должно опираться на конкретный URL из контекста; "
               "выдуманных URL быть не должно."},
            {"role": "user", "content":
                f"Окно: {window_from} → {window_to}\n"
                + (f"Фокус: {focus}\n" if focus else "")
                + f"\nИзвестные кейсы корпуса:\n{json.dumps(known_compact, ensure_ascii=False)}"
                + f"\n\nСырые находки:\n{scan_dump}"
                + "\n\nВерни строгий JSON по схеме wave_runner."},
        ]
        synth_started = time.time()
        try:
            synth_text = llm.chat_deep(synthesis_messages)
        except Exception:
            # fallback на fast если gpt-5 недоступен
            synth_text = llm.chat_fast(synthesis_messages)
        trace.append({"step": "synthesis", "model": "gpt-5",
                      "duration_ms": int((time.time() - synth_started) * 1000),
                      "chars": len(synth_text)})

        # ---- Этап 3 (deep only): перепроверка ----
        if depth == "deep":
            verify_started = time.time()
            verify_msgs = [
                {"role": "system", "content":
                 "Ты адверсариальный рецензент. Получаешь черновик дифф-волны и "
                 "сырые находки. Проверь: (а) есть ли URL для каждого утверждения, "
                 "(б) не дублируются ли кейсы с уже известными, (в) не выдуман ли факт. "
                 "Верни ИСПРАВЛЕННЫЙ JSON в том же формате."},
                {"role": "user", "content":
                 f"Известные id: {sorted(known_ids)}\n\n"
                 f"Черновик:\n{synth_text}\n\n"
                 f"Сырые находки:\n{scan_dump[:8000]}"},
            ]
            try:
                synth_text = llm.chat_deep(verify_msgs)
                trace.append({"step": "verify", "model": "gpt-5",
                              "duration_ms": int((time.time() - verify_started) * 1000)})
            except Exception as exc:
                trace.append({"step": "verify_error", "error": str(exc)})

        parsed = _extract_json(synth_text) or {}
        # подтянем все URL из scan_results если в parsed.sources их меньше
        citations = sorted(all_citations)
        wave_id = parsed.get("wave_id") or f"diff-{window_to}-{depth}"
        parsed["wave_id"] = wave_id
        duration_ms = int((time.time() - started) * 1000)

        return _finalize_wave(conn, parsed, citations, wave_id, window_from, window_to,
                              focus, depth=depth, duration_ms=duration_ms,
                              trace=trace, system_prompt=system_prompt,
                              user_prompt=(scan_system + "\n\n[+ синтезирующий промпт]"))
    finally:
        conn.close()


def _finalize_wave(conn: sqlite3.Connection, parsed: dict[str, Any], citations: list[str],
                   wave_id: str, window_from: str, window_to: str, focus: str | None,
                   *, depth: str, duration_ms: int, trace: list[dict[str, Any]],
                   system_prompt: str, user_prompt: str) -> dict[str, Any]:
    waves_dir = ROOT / "content" / "waves"
    waves_dir.mkdir(parents=True, exist_ok=True)
    wave_path = waves_dir / f"{wave_id}.md"
    md_body = _wave_to_markdown(parsed, citations, depth=depth, trace=trace,
                                system_prompt=system_prompt, user_prompt=user_prompt)
    wave_path.write_text(md_body, encoding="utf-8")
    _audit(conn,
           purpose=f"wave_runner_{depth}", model_role="search+deep",
           target_kind="wave", target_id=wave_id, section_id=None,
           input_obj={"window_from": window_from, "window_to": window_to,
                      "focus": focus, "depth": depth},
           output_obj=parsed, citations=citations,
           status="ok", error=None, duration_ms=duration_ms)
    parsed["citations"] = citations
    parsed["duration_ms"] = duration_ms
    parsed["wave_path"] = str(wave_path.relative_to(ROOT))
    parsed["depth"] = depth
    parsed["trace"] = trace
    return parsed


def _wave_to_markdown(wave: dict[str, Any], citations: list[str],
                      *, depth: str = "quick", trace: list[dict[str, Any]] | None = None,
                      system_prompt: str = "", user_prompt: str = "") -> str:
    """Сериализовать дифф-волну в md для архива."""
    lines = [
        f"# Wave {wave.get('wave_id')}",
        "",
        f"Окно: **{wave.get('window', {}).get('from')} → {wave.get('window', {}).get('to')}** · "
        f"режим: **{depth}** · источников: {len(citations)}",
        "",
    ]
    nc = wave.get("new_cases") or []
    if nc:
        lines.append(f"## Новые кейсы ({len(nc)})\n")
        for c in nc:
            lines.append(f"- **{c.get('name')}** ({c.get('country')}, {c.get('org_type')}) — "
                         f"pattern {c.get('pattern')}, a{c.get('agentivity')}, {c.get('lifecycle_stage')}")
            if c.get("summary"):
                lines.append(f"  {c['summary']}")
            for s in c.get("sources") or []:
                lines.append(f"  - {s}")
        lines.append("")
    cs = wave.get("case_shifts") or []
    if cs:
        lines.append(f"## Сдвиги существующих ({len(cs)})\n")
        for s in cs:
            lines.append(f"- **{s.get('case_id')}** — {s.get('shift_type')}: "
                         f"{s.get('from')} → {s.get('to')}")
            if s.get("evidence"):
                lines.append(f"  {s['evidence']}")
            for src in s.get("sources") or []:
                lines.append(f"  - {src}")
        lines.append("")
    ncs = wave.get("new_counter_signals") or []
    if ncs:
        lines.append(f"## Новые контр-сигналы ({len(ncs)})\n")
        for cs in ncs:
            lines.append(f"- **{cs.get('name')}** против {cs.get('target_hypothesis')}: {cs.get('summary')}")
            for src in cs.get("sources") or []:
                lines.append(f"  - {src}")
        lines.append("")
    hu = wave.get("hypothesis_updates") or []
    if hu:
        lines.append(f"## Обновления гипотез ({len(hu)})\n")
        for h in hu:
            lines.append(f"- **{h.get('hypothesis_id')}** → {h.get('new_status')}")
            lines.append(f"  {h.get('reasoning', '')}")
            for src in h.get("sources") or []:
                lines.append(f"  - {src}")
        lines.append("")
    og = wave.get("open_gaps") or []
    if og:
        lines.append("## Не закрыто\n")
        for g in og:
            lines.append(f"- {g}")
        lines.append("")
    if citations:
        lines.append(f"## Источники ({len(citations)})\n")
        for c in citations:
            lines.append(f"- {c}")
    if trace:
        lines.append("")
        lines.append("## Трасса прогона\n")
        for step in trace:
            lines.append(f"- **{step.get('step')}** — " +
                         ", ".join(f"{k}={v}" for k, v in step.items() if k != "step"))
    if system_prompt or user_prompt:
        lines.append("")
        lines.append("## Использованный промпт\n")
        if system_prompt:
            lines.append("### System")
            lines.append("```")
            lines.append(system_prompt.strip())
            lines.append("```")
        if user_prompt:
            lines.append("### User")
            lines.append("```")
            lines.append(user_prompt.strip())
            lines.append("```")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Hypothesis rechecker
# ---------------------------------------------------------------------------


def recheck_hypothesis(hypothesis_id: str, window_from: str, window_to: str) -> dict[str, Any]:
    """Перепроверить гипотезу через веб-поиск за окно."""
    conn = open_db()
    try:
        row = conn.execute(
            "SELECT id, name, status_current, body_md FROM hypotheses WHERE id=?",
            (hypothesis_id,),
        ).fetchone()
        if not row:
            raise ValueError(f"hypothesis '{hypothesis_id}' not found")
        hyp = dict(row)
    finally:
        conn.close()

    system_prompt = _load_prompt("hypothesis_rechecker")
    user_prompt = (
        f"Гипотеза: **{hyp['id']} — {hyp['name']}**\n"
        f"Текущий статус: {hyp['status_current']}\n"
        f"Формулировка:\n{hyp['body_md']}\n\n"
        f"Окно: {window_from} → {window_to}\n\n"
        "Найди свидетельства и предложи статус. Верни строгий JSON."
    )
    return _run_search_agent(
        purpose="hypothesis_rechecker", target_kind="hypothesis", target_id=hypothesis_id,
        system_prompt=system_prompt, user_prompt=user_prompt,
        input_obj={"hypothesis_id": hypothesis_id, "window": [window_from, window_to]},
    )


# ---------------------------------------------------------------------------
# Match explainer
# ---------------------------------------------------------------------------


def explain_match(case_id: str, situation: dict[str, Any]) -> dict[str, Any]:
    """Сгенерировать объяснение «почему этот кейс похож на ситуацию»."""
    conn = open_db()
    try:
        row = conn.execute(
            """
            SELECT id, name, org_name, country, pattern, agentivity,
                   orchestration, pedagogy, control, transformation_mode,
                   lifecycle_stage, body_md, frontmatter_json
            FROM cases WHERE id=?
            """,
            (case_id,),
        ).fetchone()
        if not row:
            raise ValueError(f"case '{case_id}' not found")
        case = dict(row)
    finally:
        conn.close()

    system_prompt = _load_prompt("match_explainer")
    user_prompt = (
        f"Кейс-аналог:\n```json\n{json.dumps({k: case[k] for k in ['id','name','org_name','country','pattern','agentivity','orchestration','pedagogy','control','transformation_mode','lifecycle_stage']}, ensure_ascii=False, indent=2)}\n```\n\n"
        f"Описание ситуации пользователя:\n```json\n{json.dumps(situation, ensure_ascii=False, indent=2)}\n```\n\n"
        "Объясни. Верни строгий JSON."
    )
    return _run_search_agent(
        purpose="match_explainer", target_kind="case", target_id=case_id,
        system_prompt=system_prompt, user_prompt=user_prompt,
        input_obj={"case_id": case_id, "situation": situation},
        model_role="fast",  # дешевле и быстрее для коротких объяснений
    )


# ---------------------------------------------------------------------------
# Generic search-agent runner (используется hypothesis_rechecker, match_explainer)
# ---------------------------------------------------------------------------


def bulk_extract_candidates(text: str, *, max_segments: int = 30) -> dict[str, Any]:
    """Длинный текст → сегменты → LLM-извлечение кейсов из каждого сегмента.

    Возвращает {candidates: [...], segments: [...], stats: {...}}.
    Не сохраняет ничего — только список кандидатов для ревью пользователем.
    """
    from .extractors import segment_into_candidates

    if not text.strip():
        raise ValueError("empty text")

    segments = segment_into_candidates(text)
    if not segments:
        return {"candidates": [], "segments": [], "stats": {"text_len": len(text), "segments_total": 0}}

    if len(segments) > max_segments:
        # для длинного PWC-отчёта ограничиваем число сегментов — иначе долго и дорого
        segments = segments[:max_segments]

    system_prompt = _load_prompt("bulk_extractor")
    candidates: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    conn = open_db()
    total_duration = 0
    try:
        for idx, seg in enumerate(segments):
            user_prompt = (
                f"Сегмент {idx+1}/{len(segments)} (заголовок: {seg.get('header','')}):\n\n"
                f"{seg['text'][:6000]}\n\nВерни JSON по схеме."
            )
            llm = get_llm()
            started = time.time()
            try:
                text_raw = llm.chat_fast([
                    {"role": "system", "content": system_prompt + "\n\nВыведи только JSON, без markdown-обёртки."},
                    {"role": "user", "content": user_prompt},
                ])
                duration_ms = int((time.time() - started) * 1000)
                total_duration += duration_ms
                parsed = _extract_json(text_raw) or {}
                if not parsed.get("is_relevant"):
                    continue
                for cand in parsed.get("candidates") or []:
                    cid = cand.get("id") or ""
                    if not cid or cid in seen_ids:
                        continue
                    seen_ids.add(cid)
                    cand["segment_idx"] = idx
                    cand["segment_offset"] = seg.get("offset", 0)
                    candidates.append(cand)
            except Exception as exc:  # noqa: BLE001
                _audit(conn,
                       purpose="bulk_extractor", model_role="fast",
                       target_kind="bulk_segment", target_id=f"seg-{idx}",
                       section_id=None,
                       input_obj={"segment_idx": idx, "len": len(seg["text"])},
                       output_obj=None, citations=[],
                       status="error", error=str(exc), duration_ms=int((time.time()-started)*1000))
                continue

        _audit(conn,
               purpose="bulk_extractor", model_role="fast",
               target_kind="bulk_document", target_id=None, section_id=None,
               input_obj={"text_len": len(text), "segments_total": len(segments)},
               output_obj={"candidates_count": len(candidates)},
               citations=[],
               status="ok", error=None, duration_ms=total_duration)
    finally:
        conn.close()

    return {
        "candidates": candidates,
        "segments_total": len(segments),
        "stats": {"text_len": len(text), "duration_ms": total_duration},
    }


def save_bulk_candidates(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    """Сохранить выбранных bulk-кандидатов в content/cases/*.md.

    Скип, если файл с таким id уже существует. Пишет минимально валидный
    фронтматтер — пользователь дальше уточнит через section-filler.
    """
    saved: list[str] = []
    skipped: list[str] = []
    today = date.today().isoformat()
    today_short = today[:7]

    for cand in candidates:
        cid = (cand.get("id") or "").strip()
        if not cid:
            continue
        path = CASES_DIR / f"{cid}.md"
        if path.exists():
            skipped.append(cid)
            continue

        org = cand.get("organization") or {}
        ai = cand.get("ai") or {}
        fm: dict[str, Any] = {
            "id": cid,
            "name": cand.get("name") or cid,
            "organization": {
                "name": org.get("name") or "unknown",
                "type": (org.get("type") or "U").split("/")[0],
                "country": org.get("country") or "INT",
            },
            "ai": {
                "pattern": ai.get("pattern"),
                "agentivity": ai.get("agentivity"),
                "technologies": ai.get("technologies") or [],
            },
            "lifecycle": {
                "stage": cand.get("lifecycle_stage") or "pilot",
                "first_seen": "bulk-import-" + today_short,
            },
            "sources": [{"url": "bulk-import", "type": "imported",
                         "accessed": today_short}],
            "verified": False,
            "canvas": {
                "signature_context": {
                    "text": cand.get("summary") or "",
                    "status": "draft",
                    "source": "imported",
                    "updated_at": today,
                },
            },
        }
        # Excerpt — во вторую секцию как proof-of-extraction
        excerpt = cand.get("source_excerpt")
        if excerpt:
            fm["canvas"]["sources_verification"] = {
                "text": f"Извлечено из bulk-импорта (confidence: {cand.get('confidence','?')}).\n\nИсходный фрагмент:\n\n{excerpt}",
                "status": "draft",
                "source": "imported",
                "updated_at": today,
            }

        body = f"\n## Описание\n\n{cand.get('summary') or ''}\n"
        post = frontmatter.Post(content=body, **fm)
        raw = frontmatter.dumps(
            post, handler=frontmatter.YAMLHandler(),
            default_flow_style=False, allow_unicode=True, sort_keys=False,
        )
        path.write_text(raw + "\n", encoding="utf-8")
        saved.append(cid)

    return {"saved": len(saved), "skipped": len(skipped),
            "saved_ids": saved, "skipped_ids": skipped}


ROLE_PROFILES = {
    "teacher": {
        "label": "преподаватель",
        "frame": "Юзер проектирует свой курс/электив/модуль. Думает о студентах, "
                 "о практической применимости, о времени аудитории. Подсказывай "
                 "конкретные кейсы-аналоги и AgentRun-профили (KOSMOS, "
                 "Stakeholder Pressure). Предлагай Wizard/Канвас если ещё нет проекта.",
        "default_actions": ["/project/new/wizard", "/match"],
    },
    "methodologist": {
        "label": "методолог / исследователь",
        "frame": "Юзер работает с теоретической рамкой корпуса: гипотезы, "
                 "противоречия, типы, контр-сигналы. Опирайся на язык H1-H5, A-F, "
                 "tensions. Предлагай Map / Theory / Hypothesis Forge / диффы волн. "
                 "Не упрощай терминологию.",
        "default_actions": ["/map", "/theory", "/waves"],
    },
    "admin": {
        "label": "декан / администратор",
        "frame": "Юзер ищет аналоги под программу, оценивает риски, обстреливает "
                 "замысел стейкхолдерами. Подсказывай Match / Stakeholder Pressure / "
                 "Anti-Agent-Washing / экспорт документов. Думай в категориях бюджета, "
                 "стейкхолдеров, регуляторных рисков.",
        "default_actions": ["/match", "/projects"],
    },
    "student": {
        "label": "студент / участник курса",
        "frame": "Юзер — участник конкретного курса (если есть active course). "
                 "Объясняй простым языком, без жаргона корпуса. Подсказывай "
                 "активные курсы, материалы лекций, конкретные кейсы. "
                 "Не предлагай создание проектов и сценарии TRIZ.",
        "default_actions": ["/courses", "/library"],
    },
}


def ask_concierge(text: str, mode: str = "explore", *,
                  model_role: str = "fast",
                  user_role: str | None = None,
                  active_course_id: str | None = None) -> dict[str, Any]:
    """Главный LLM-вход на home. Принимает свободный запрос, возвращает
    suggested actions с URL + краткий ответ.

    mode: 'project' (юзер описывает свой замысел) или 'explore' (просто
    смотрит).
    """
    if not text.strip():
        raise ValueError("empty text")
    system_prompt = _load_prompt("concierge")

    # Минимальный контекст: список проектов + сводка корпуса + library
    from .db import open_db, fetch_all
    conn = open_db()
    try:
        projects = fetch_all(conn, "SELECT id, name FROM projects ORDER BY updated_at DESC LIMIT 10")
        n_cases = conn.execute("SELECT COUNT(*) FROM cases").fetchone()[0]
        n_types = conn.execute("SELECT COUNT(*) FROM types").fetchone()[0]
        n_books = conn.execute("SELECT COUNT(*) FROM library_books WHERE status NOT IN ('uploading','failed')").fetchone()[0]
    finally:
        conn.close()

    role_block = ""
    rp = ROLE_PROFILES.get(user_role or "")
    if rp:
        role_block = (
            f"\nРОЛЬ ПОЛЬЗОВАТЕЛЯ: **{rp['label']}**.\n"
            f"{rp['frame']}\n"
            f"Default-разделы для роли: {', '.join(rp['default_actions'])}.\n"
        )
    course_block = ""
    if active_course_id:
        course_block = (
            f"\nАКТИВНЫЙ КУРС: {active_course_id} — пользователь сейчас работает "
            f"в контексте этого курса. Ответы фильтруй по релевантности к нему. "
            f"Если уместно — предлагай action `/course/{active_course_id}`.\n"
        )

    ctx = (
        f"Корпус: {n_cases} кейсов, {n_types} типов.\n"
        f"Библиотека: {n_books} книг.\n"
        f"Мои проекты: {', '.join(p['name'] for p in projects) if projects else '(пока нет)'}.\n"
        f"Mode: {mode}.\n"
        f"{role_block}{course_block}"
    )

    # Hierarchical RAG из библиотеки + F1 selector противоречий
    lib_block = ""
    try:
        from .library import search_library
        from .selector import annotate_chunks_with_schools
        lib_chunks = annotate_chunks_with_schools(search_library(text, top_k=4))
        if lib_chunks:
            # Группировка по школе (если есть метки)
            by_school: dict[str | None, list[dict]] = {}
            for ch in lib_chunks:
                by_school.setdefault(ch.get("school"), []).append(ch)
            schools_with_chunks = {s: lst for s, lst in by_school.items() if s}
            lines: list[str] = []
            if len(schools_with_chunks) >= 2:
                lines.append("\nВНИМАНИЕ — В БИБЛИОТЕКЕ НАЙДЕНЫ ФРАГМЕНТЫ ИЗ ПРОТИВОРЕЧАЩИХ ШКОЛ:")
                for school, chs in schools_with_chunks.items():
                    lines.append(f"\n— Школа «{school}»:")
                    for ch in chs:
                        sec = ch.get("section_title") or f"sec {ch.get('section_num')}"
                        lines.append(f"  - 📚 [[{ch['book_id']}]] «{ch['book_title']}» / {sec}")
                        lines.append(f"    {ch['text'][:350].strip()}…")
                # концепты без школы — отдельно
                if by_school.get(None):
                    lines.append("\n— Без явной школьной принадлежности:")
                    for ch in by_school[None]:
                        sec = ch.get("section_title") or f"sec {ch.get('section_num')}"
                        lines.append(f"  - 📚 [[{ch['book_id']}]] «{ch['book_title']}» / {sec}")
                        lines.append(f"    {ch['text'][:300].strip()}…")
                lines.append("\nВ summary явно сообщи что нашлось две (или больше) позиции, и предложи выбор.")
            else:
                lines.append("\nРЕЛЕВАНТНЫЕ ФРАГМЕНТЫ БИБЛИОТЕКИ:")
                for ch in lib_chunks:
                    sec = ch.get("section_title") or f"sec {ch.get('section_num')}"
                    school_label = f" [{ch['school']}]" if ch.get("school") else ""
                    lines.append(
                        f"- 📚 [[{ch['book_id']}]] «{ch['book_title']}» / {ch['book_authors'] or '?'} / {sec}{school_label}"
                    )
                    lines.append(f"    {ch['text'][:400].strip()}…")
            lib_block = "\n".join(lines)
    except Exception:
        pass

    user_prompt = f"{ctx}{lib_block}\n\nЗапрос пользователя:\n\n{text.strip()[:6000]}\n\nВерни строгий JSON."

    if model_role not in ("fast", "deep", "search"):
        model_role = "fast"
    return _run_search_agent(
        purpose="concierge", target_kind="home", target_id="ask",
        system_prompt=system_prompt, user_prompt=user_prompt,
        input_obj={"mode": mode, "text_len": len(text),
                   "projects_count": len(projects), "model_role": model_role,
                   "user_role": user_role, "active_course_id": active_course_id},
        model_role=model_role,
    )


def parse_match_situation(description: str) -> dict[str, Any]:
    """Свободный текст описания проекта → структурированные оси для /match."""
    if not description.strip():
        raise ValueError("empty description")
    system_prompt = _load_prompt("match_parser")
    user_prompt = f"Описание проекта:\n\n{description.strip()[:12000]}\n\nВерни строгий JSON по схеме."
    return _run_search_agent(
        purpose="match_parser", target_kind="match_input", target_id="adhoc",
        system_prompt=system_prompt, user_prompt=user_prompt,
        input_obj={"description_len": len(description)},
        model_role="fast",  # gpt-4.1-mini, поиск не нужен
    )


def _run_search_agent(*, purpose: str, target_kind: str, target_id: str,
                      system_prompt: str, user_prompt: str,
                      input_obj: dict[str, Any], model_role: str = "search") -> dict[str, Any]:
    llm = get_llm()
    started = time.time()
    conn = open_db()
    try:
        try:
            if model_role == "search":
                res = llm.chat_search([
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ])
                text_raw, citations = res["text"], res["citations"]
            else:
                method = llm.chat_deep if model_role == "deep" else llm.chat_fast
                text_raw = method([
                    {"role": "system", "content": system_prompt + "\n\nВыведи только JSON."},
                    {"role": "user", "content": user_prompt},
                ])
                citations = []
            duration_ms = int((time.time() - started) * 1000)
            parsed = _extract_json(text_raw)
            if not parsed:
                raise ValueError(f"could not extract JSON: {text_raw[:300]}")
            citations = sorted(set(citations))
            _audit(conn, purpose=purpose, model_role=model_role,
                   target_kind=target_kind, target_id=target_id, section_id=None,
                   input_obj=input_obj, output_obj=parsed, citations=citations,
                   status="ok", error=None, duration_ms=duration_ms)
            parsed["citations"] = citations
            parsed["duration_ms"] = duration_ms
            parsed["model_role"] = model_role
            return parsed
        except Exception as exc:
            duration_ms = int((time.time() - started) * 1000)
            _audit(conn, purpose=purpose, model_role=model_role,
                   target_kind=target_kind, target_id=target_id, section_id=None,
                   input_obj=input_obj, output_obj=None, citations=[],
                   status="error", error=str(exc), duration_ms=duration_ms)
            raise
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# JSON extractor (модели иногда оборачивают в ```json ... ```)
# ---------------------------------------------------------------------------


def _extract_json(text: str) -> dict[str, Any] | None:
    if not text:
        return None
    # 1. прямой парсинг
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # 2. ```json ... ```
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass
    # 3. первый {...} в строке
    m = re.search(r"(\{[\s\S]*\})", text)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass
    return None
