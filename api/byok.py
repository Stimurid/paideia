"""BYOK: пользователь подключает свой LLM-ключ. Может шарить с лимитом.

Логика выбора ключа на каждый LLM-вызов:
    1. Если у сессии есть свой ключ (`user_keys[session_id]`) — используем его
    2. Если нет, но шарящий ключ есть и дневной лимит не исчерпан — используем шарящий
    3. Иначе — платформенный (LLM_PRIMARY_API_KEY) + наши rate-limits
"""

from __future__ import annotations

import time
from typing import Any

from .db import open_db, fetch_all, fetch_one


def save_key(*, session_id: str, api_key: str, base_url: str = "",
             nickname: str = "", daily_limit_usd: float = 0,
             shared: bool = False, share_daily_usd: float = 0,
             fast_model: str = "", deep_model: str = "",
             search_model: str = "") -> None:
    base_url = base_url.strip() or "https://api.302.ai/v1"
    conn = open_db()
    try:
        conn.execute(
            """INSERT OR REPLACE INTO user_keys
               (session_id, api_key, base_url, fast_model, deep_model,
                search_model, nickname, daily_limit_usd, shared, share_daily_usd,
                updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))""",
            (session_id, api_key.strip(), base_url,
             fast_model.strip() or None, deep_model.strip() or None,
             search_model.strip() or None,
             nickname.strip() or None,
             max(0, float(daily_limit_usd or 0)),
             1 if shared else 0,
             max(0, float(share_daily_usd or 0))),
        )
        conn.commit()
    finally:
        conn.close()


def get_key(session_id: str) -> dict | None:
    if not session_id:
        return None
    conn = open_db()
    try:
        return fetch_one(conn, "SELECT * FROM user_keys WHERE session_id = ?",
                         (session_id,))
    finally:
        conn.close()


def delete_key(session_id: str) -> None:
    conn = open_db()
    try:
        conn.execute("DELETE FROM user_keys WHERE session_id = ?", (session_id,))
        conn.commit()
    finally:
        conn.close()


def list_shared() -> list[dict]:
    """Какие пользователи шарят свой ключ."""
    conn = open_db()
    try:
        return fetch_all(
            conn,
            """SELECT session_id, nickname, share_daily_usd, base_url
               FROM user_keys WHERE shared = 1 ORDER BY share_daily_usd DESC""",
        )
    finally:
        conn.close()


def session_spent_today(session_id: str) -> float:
    """Сколько сессия потратила сегодня по всем llm_runs."""
    if not session_id:
        return 0.0
    conn = open_db()
    try:
        row = conn.execute(
            """SELECT COALESCE(SUM(cost_usd),0) FROM llm_runs
               WHERE session_id = ? AND date(created_at) = date('now')""",
            (session_id,),
        ).fetchone()
        return float(row[0] or 0)
    finally:
        conn.close()


def check_personal_budget(session_id: str) -> dict:
    """Проверка дневного лимита по своему ключу."""
    key = get_key(session_id)
    if not key:
        return {"has_key": False}
    limit = float(key.get("daily_limit_usd") or 0)
    spent = session_spent_today(session_id)
    return {
        "has_key": True,
        "limit_usd": limit,
        "spent_usd": round(spent, 4),
        "remaining_usd": round(max(0, limit - spent), 4) if limit else None,
        "blocked": bool(limit and spent >= limit),
    }


def llm_credentials_for(session_id: str | None) -> tuple[str, str, dict[str, str]]:
    """Возвращает (api_key, base_url, model_overrides) — какие реквизиты использовать.
    Если у юзера свой ключ — он. Иначе — платформенный.
    """
    from .config import get_settings
    s = get_settings()
    if session_id:
        key = get_key(session_id)
        if key and key.get("api_key"):
            personal_status = check_personal_budget(session_id)
            if not personal_status.get("blocked"):
                overrides = {
                    k: key[k] for k in ("fast_model", "deep_model",
                                         "search_model", "embed_model")
                    if key.get(k)
                }
                return key["api_key"], key.get("base_url") or s.llm_primary_base_url, overrides
    return s.llm_primary_api_key, s.llm_primary_base_url, {}
