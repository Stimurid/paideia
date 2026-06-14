"""Код-логин для тестеров. Тимур выдаёт код → тестер вводит на /login →
session связывается с nickname и помечается as `is_owner`.

Это поверх Caddy basic_auth (внешняя стена). is_owner отвечает за то,
кто может редактировать чужие проекты / увидеть /service / удалять артефакты.

Без email/SMTP — самый простой путь для тестерского круга.
"""

from __future__ import annotations

import secrets
import time
from typing import Any

from .db import open_db, fetch_all, fetch_one


def _ensure_tables() -> None:
    conn = open_db()
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS auth_codes (
                code        TEXT PRIMARY KEY,
                nickname    TEXT NOT NULL,
                role        TEXT NOT NULL DEFAULT 'tester',
                created_by  TEXT,
                created_at  TEXT NOT NULL DEFAULT (datetime('now')),
                redeemed_at TEXT,
                redeemed_by TEXT,
                expires_at  TEXT,
                note        TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_auth_codes_redeem ON auth_codes(redeemed_at);

            ALTER TABLE user_sessions ADD COLUMN nickname TEXT;
        """)
        conn.commit()
    except Exception:
        pass  # ALTER падает если колонка уже есть — игнорим
    finally:
        conn.close()


def generate_code(*, nickname: str, role: str = "tester",
                  created_by: str | None = None,
                  ttl_days: int = 90, note: str = "") -> str:
    """Создать код-приглашение."""
    _ensure_tables()
    code = "P-" + secrets.token_urlsafe(6).replace("-", "").replace("_", "").upper()[:8]
    conn = open_db()
    try:
        expires = None
        if ttl_days > 0:
            expires = f"datetime('now', '+{ttl_days} days')"
        if expires:
            conn.execute(
                f"INSERT INTO auth_codes (code, nickname, role, created_by, expires_at, note) "
                f"VALUES (?, ?, ?, ?, {expires}, ?)",
                (code, nickname.strip(), role, created_by, note[:500] or None),
            )
        else:
            conn.execute(
                "INSERT INTO auth_codes (code, nickname, role, created_by, note) "
                "VALUES (?, ?, ?, ?, ?)",
                (code, nickname.strip(), role, created_by, note[:500] or None),
            )
        conn.commit()
        return code
    finally:
        conn.close()


def redeem(code: str, session_id: str) -> dict:
    """Привязать сессию к коду. После этого session помечается nickname+role."""
    _ensure_tables()
    code = code.strip().upper()
    conn = open_db()
    try:
        row = fetch_one(
            conn,
            "SELECT * FROM auth_codes WHERE code = ?",
            (code,),
        )
        if not row:
            return {"ok": False, "msg": "Код не найден"}
        if row.get("redeemed_at"):
            # Уже использован — но дадим тому же session_id повторно войти
            if row.get("redeemed_by") != session_id:
                return {"ok": False, "msg": "Код уже использован другим"}
        if row.get("expires_at"):
            exp = conn.execute(
                "SELECT ? < datetime('now')", (row["expires_at"],)
            ).fetchone()[0]
            if exp:
                return {"ok": False, "msg": "Код истёк"}
        nickname = row["nickname"]
        role = row.get("role") or "tester"
        # Помечаем код использованным
        conn.execute(
            "UPDATE auth_codes SET redeemed_at = datetime('now'), redeemed_by = ? "
            "WHERE code = ?",
            (session_id, code),
        )
        # Привязываем nickname + role + is_supporter (даём чтобы лимиты сняли)
        conn.execute(
            "UPDATE user_sessions SET nickname = ?, role = ?, is_supporter = 1 "
            "WHERE id = ?",
            (nickname, role, session_id),
        )
        conn.commit()
        return {"ok": True, "nickname": nickname, "role": role}
    finally:
        conn.close()


def get_identity(session_id: str | None) -> dict[str, Any]:
    """Кто эта сессия по логину. role: tester / owner / guest."""
    if not session_id:
        return {"nickname": None, "role": "guest", "is_owner": False}
    _ensure_tables()
    conn = open_db()
    try:
        row = fetch_one(
            conn,
            "SELECT nickname, role, is_supporter FROM user_sessions WHERE id = ?",
            (session_id,),
        )
        if not row or not row.get("nickname"):
            return {"nickname": None, "role": "guest", "is_owner": False}
        role = row.get("role") or "tester"
        return {
            "nickname": row["nickname"],
            "role": role,
            "is_owner": role in ("owner", "admin"),
            "is_supporter": bool(row.get("is_supporter")),
        }
    finally:
        conn.close()


def list_codes(only_unredeemed: bool = False) -> list[dict]:
    _ensure_tables()
    conn = open_db()
    try:
        wh = "WHERE redeemed_at IS NULL" if only_unredeemed else ""
        return fetch_all(
            conn,
            f"SELECT * FROM auth_codes {wh} ORDER BY created_at DESC LIMIT 200",
        )
    finally:
        conn.close()


def require_owner(identity: dict) -> bool:
    return bool(identity.get("is_owner"))
