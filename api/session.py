"""Сессии, rate-limit, supporter-status, token counter.

Сессия — анонимная (cookie `paideia_sess`), создаётся middleware при первом
заходе. Используется для: подсчёта токенов в навбаре (F-token), rate-limit
(F11), привязки роли (F9), активного курса (F3), supporter-tag (F12).
"""

from __future__ import annotations

import contextvars
import secrets
from typing import Any

from .db import open_db, fetch_all, fetch_one

# Контекст текущего запроса — заполняется middleware, читается _audit.
current_session: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "current_session", default=None
)
current_ip: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "current_ip", default=None
)

# Лимиты по умолчанию (F11). Жёстко после ~20 тестеров на 1 ключе.
DAILY_LIMITS = {
    "fast":   10,
    "deep":    2,
    "search":  1,
}
GLOBAL_DAILY_BUDGET_USD = 1.0  # глобальный потолок на всю платформу за сутки

COOKIE_NAME = "paideia_sess"
ROLE_COOKIE = "paideia_role"
COURSE_COOKIE = "paideia_course"


def new_session_id() -> str:
    return "s_" + secrets.token_urlsafe(16)


def ensure_session(session_id: str | None) -> str:
    """Создать сессию если её ещё нет; вернуть подтверждённый id."""
    sid = session_id or new_session_id()
    conn = open_db()
    try:
        row = conn.execute(
            "SELECT id FROM user_sessions WHERE id = ?", (sid,)
        ).fetchone()
        if not row:
            conn.execute(
                "INSERT INTO user_sessions (id) VALUES (?)", (sid,)
            )
        else:
            conn.execute(
                "UPDATE user_sessions SET last_seen_at = datetime('now') WHERE id = ?",
                (sid,),
            )
        conn.commit()
        return sid
    finally:
        conn.close()


def set_session_role(session_id: str, role: str) -> None:
    conn = open_db()
    try:
        conn.execute(
            "UPDATE user_sessions SET role = ? WHERE id = ?", (role, session_id)
        )
        conn.commit()
    finally:
        conn.close()


def set_session_course(session_id: str, course_id: str | None) -> None:
    conn = open_db()
    try:
        conn.execute(
            "UPDATE user_sessions SET course_id = ? WHERE id = ?",
            (course_id, session_id),
        )
        conn.commit()
    finally:
        conn.close()


def mark_supporter(session_id: str) -> None:
    conn = open_db()
    try:
        conn.execute(
            "UPDATE user_sessions SET is_supporter = 1 WHERE id = ?",
            (session_id,),
        )
        conn.commit()
    finally:
        conn.close()


def is_supporter(session_id: str | None) -> bool:
    if not session_id:
        return False
    conn = open_db()
    try:
        row = fetch_one(
            conn, "SELECT is_supporter FROM user_sessions WHERE id = ?", (session_id,)
        )
        return bool(row and row.get("is_supporter"))
    finally:
        conn.close()


def get_session_info(session_id: str | None) -> dict[str, Any]:
    if not session_id:
        return {}
    conn = open_db()
    try:
        row = fetch_one(
            conn,
            "SELECT id, role, course_id, is_supporter, created_at FROM user_sessions WHERE id = ?",
            (session_id,),
        )
        return row or {}
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# F-token: подсчёт токенов и стоимости для сессии. Цена × 2 (см. ниже).
# ---------------------------------------------------------------------------


COST_MULTIPLIER = 2.0  # фактор для UI-отображения (рендеринг ≈ x2 от себестоимости)


def session_stats(session_id: str | None) -> dict[str, Any]:
    """Аггрегация по llm_runs для сессии. Возвращает токены и cost × 2."""
    if not session_id:
        return {"tokens_total": 0, "calls": 0, "cost_usd": 0.0,
                "cost_usd_display": 0.0, "multiplier": COST_MULTIPLIER,
                "by_model": []}
    conn = open_db()
    try:
        total = fetch_one(
            conn,
            """SELECT
                 COALESCE(SUM(tokens_total),0) AS tokens_total,
                 COALESCE(SUM(cost_usd),0)     AS cost_usd,
                 COUNT(*)                       AS calls
               FROM llm_runs WHERE session_id = ?""",
            (session_id,),
        ) or {}
        by_model = fetch_all(
            conn,
            """SELECT model_name, COUNT(*) AS calls,
                      COALESCE(SUM(tokens_total),0) AS tokens,
                      COALESCE(SUM(cost_usd),0)     AS cost
               FROM llm_runs WHERE session_id = ?
               GROUP BY model_name ORDER BY cost DESC""",
            (session_id,),
        )
        cost_raw = float(total.get("cost_usd") or 0.0)
        return {
            "tokens_total": int(total.get("tokens_total") or 0),
            "calls": int(total.get("calls") or 0),
            "cost_usd": round(cost_raw, 5),
            "cost_usd_display": round(cost_raw * COST_MULTIPLIER, 5),
            "multiplier": COST_MULTIPLIER,
            "by_model": [
                {"model": r["model_name"], "calls": r["calls"],
                 "tokens": r["tokens"], "cost": round(r["cost"] * COST_MULTIPLIER, 5)}
                for r in by_model
            ],
        }
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# F11: rate limits
# ---------------------------------------------------------------------------


def check_rate_limit(session_id: str | None, client_ip: str | None,
                     model_role: str) -> dict[str, Any]:
    """Проверить дневной лимит. Возвращает dict с remaining/limit/allowed/reason.

    Supporter обходит все лимиты. Свой ключ (BYOK) — тоже обходит платформенные лимиты
    (но проверяется personal_budget). Глобальный budget cap проверяется тоже.
    """
    if is_supporter(session_id):
        return {"allowed": True, "limit": None, "remaining": None,
                "is_supporter": True, "reason": "supporter"}

    # BYOK: свой ключ → платформенные лимиты не применяем, только personal_budget
    try:
        from . import byok as byok_mod
        pb = byok_mod.check_personal_budget(session_id)
        if pb.get("has_key"):
            if pb.get("blocked"):
                return {"allowed": False, "limit": pb.get("limit_usd"),
                        "remaining": 0, "is_supporter": False,
                        "has_personal_key": True,
                        "reason": "personal_budget_exhausted",
                        "spent_usd": pb.get("spent_usd")}
            return {"allowed": True, "limit": None, "remaining": None,
                    "is_supporter": False, "has_personal_key": True,
                    "spent_usd": pb.get("spent_usd"),
                    "personal_limit_usd": pb.get("limit_usd"),
                    "reason": "byok"}
    except Exception:
        pass

    limit = DAILY_LIMITS.get(model_role, DAILY_LIMITS["fast"])
    conn = open_db()
    try:
        # Глобальный дневной потолок
        spent_today = conn.execute(
            "SELECT COALESCE(SUM(cost_usd),0) FROM llm_runs "
            "WHERE date(created_at) = date('now')"
        ).fetchone()[0] or 0.0
        if spent_today >= GLOBAL_DAILY_BUDGET_USD:
            return {"allowed": False, "limit": limit, "remaining": 0,
                    "is_supporter": False,
                    "reason": "global_budget_exhausted",
                    "spent_today_usd": round(spent_today, 4)}

        # Per-IP лимит на день+model_role
        ip_key = client_ip or "?"
        used = conn.execute(
            "SELECT COUNT(*) FROM llm_runs "
            "WHERE client_ip = ? AND model_role = ? "
            "AND date(created_at) = date('now')",
            (ip_key, model_role),
        ).fetchone()[0] or 0
        remaining = max(0, limit - used)
        return {
            "allowed": remaining > 0,
            "limit": limit,
            "remaining": remaining,
            "used_today": used,
            "is_supporter": False,
            "reason": "over_limit" if remaining <= 0 else "ok",
        }
    finally:
        conn.close()


def check_bypass_code(code: str) -> bool:
    """Проверить код тестера. Возвращает True если код валиден."""
    from .config import get_settings
    s = get_settings()
    if not s.bypass_codes:
        return False
    valid = {c.strip().lower() for c in s.bypass_codes.split(",") if c.strip()}
    return code.strip().lower() in valid


def daily_budget_status() -> dict[str, Any]:
    conn = open_db()
    try:
        spent = conn.execute(
            "SELECT COALESCE(SUM(cost_usd),0) FROM llm_runs "
            "WHERE date(created_at) = date('now')"
        ).fetchone()[0] or 0.0
        calls = conn.execute(
            "SELECT COUNT(*) FROM llm_runs WHERE date(created_at) = date('now')"
        ).fetchone()[0] or 0
        return {
            "spent_usd": round(spent, 4),
            "cap_usd": GLOBAL_DAILY_BUDGET_USD,
            "remaining_usd": round(max(0, GLOBAL_DAILY_BUDGET_USD - spent), 4),
            "calls_today": calls,
            "percent": round(100.0 * spent / GLOBAL_DAILY_BUDGET_USD, 1) if GLOBAL_DAILY_BUDGET_USD else 0,
        }
    finally:
        conn.close()
