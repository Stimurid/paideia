"""Voice: TTS через ElevenLabs + STT через 302.ai whisper.

TTS используется в /discuss для озвучки ответов Kaiyona голосом.
STT используется на странице события курса: загружаешь .mp3/.wav →
автоматический транскрипт → body_md → litops.

Конфиг через env:
    ELEVENLABS_API_KEY        — ключ из https://elevenlabs.io/app/speech-synthesis
    ELEVENLABS_VOICE_ID       — voice ID (по умолчанию — голос для Kaiyona)
    ELEVENLABS_MODEL          — eleven_multilingual_v2 (по умолчанию — поддерживает русский)
    LLM_PRIMARY_API_KEY/BASE_URL — уже есть, через них идёт whisper
"""

from __future__ import annotations

import httpx
from typing import Any

from .config import get_settings

# ---------------------------------------------------------------------------
# TTS — ElevenLabs
# ---------------------------------------------------------------------------

ELEVENLABS_API = "https://api.elevenlabs.io/v1"


def tts_configured() -> bool:
    s = get_settings()
    return bool(s.elevenlabs_api_key)


def synthesize(text: str, *, voice_id: str | None = None,
               model: str | None = None) -> bytes:
    """Текст → mp3 bytes через ElevenLabs."""
    s = get_settings()
    if not s.elevenlabs_api_key:
        raise RuntimeError("ELEVENLABS_API_KEY не задан")
    vid = voice_id or s.elevenlabs_voice_id or "nPczCjzI2devNBz1zQrb"  # Brian — низкий философский
    mdl = model or s.elevenlabs_model or "eleven_multilingual_v2"
    body = {
        "text": text[:4500],  # ElevenLabs cap ≈ 5000
        "model_id": mdl,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.7,
            "style": 0.3,
            "use_speaker_boost": True,
        },
    }
    headers = {
        "xi-api-key": s.elevenlabs_api_key,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    }
    with httpx.Client(timeout=60.0) as client:
        r = client.post(f"{ELEVENLABS_API}/text-to-speech/{vid}",
                        json=body, headers=headers)
        r.raise_for_status()
        return r.content


def list_voices() -> list[dict[str, Any]]:
    """Список доступных голосов для UI выбора."""
    s = get_settings()
    if not s.elevenlabs_api_key:
        return []
    with httpx.Client(timeout=15.0) as client:
        r = client.get(f"{ELEVENLABS_API}/voices",
                       headers={"xi-api-key": s.elevenlabs_api_key})
        r.raise_for_status()
        data = r.json()
    return [
        {"voice_id": v["voice_id"], "name": v["name"],
         "preview_url": v.get("preview_url"),
         "labels": v.get("labels", {})}
        for v in data.get("voices", [])
    ]


def quota_status() -> dict[str, Any]:
    """Сколько символов осталось в подписке ElevenLabs."""
    s = get_settings()
    if not s.elevenlabs_api_key:
        return {"configured": False}
    with httpx.Client(timeout=10.0) as client:
        r = client.get(f"{ELEVENLABS_API}/user/subscription",
                       headers={"xi-api-key": s.elevenlabs_api_key})
        r.raise_for_status()
        d = r.json()
    return {
        "configured": True,
        "character_count": d.get("character_count"),
        "character_limit": d.get("character_limit"),
        "tier": d.get("tier"),
        "next_reset_at": d.get("next_character_count_reset_unix"),
    }


# ---------------------------------------------------------------------------
# STT — Whisper через 302.ai (OpenAI-compatible)
# ---------------------------------------------------------------------------


def transcribe(audio_bytes: bytes, *, filename: str = "audio.mp3",
               language: str = "ru") -> dict[str, Any]:
    """Аудио → текст транскрипт через whisper на 302.ai.

    Возвращает {"text", "duration_s", "language"}.
    """
    s = get_settings()
    if not s.llm_primary_api_key:
        raise RuntimeError("LLM_PRIMARY_API_KEY не задан")
    import time
    started = time.time()
    files = {"file": (filename, audio_bytes, "audio/mpeg")}
    data = {"model": "whisper-1", "language": language,
            "response_format": "json"}
    headers = {"Authorization": f"Bearer {s.llm_primary_api_key}"}
    with httpx.Client(timeout=300.0) as client:
        r = client.post(
            f"{s.llm_primary_base_url}/audio/transcriptions",
            files=files, data=data, headers=headers,
        )
        r.raise_for_status()
        result = r.json()
    return {
        "text": result.get("text", ""),
        "duration_s": round(time.time() - started, 1),
        "language": language,
        "bytes": len(audio_bytes),
    }
