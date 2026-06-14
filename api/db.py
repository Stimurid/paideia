"""Подключение к SQLite + sqlite-vec.

Грузим vec0-расширение, отдаём соединение прикладному коду.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

import sqlite_vec

from .config import get_settings


def open_db(db_path: Path | None = None) -> sqlite3.Connection:
    settings = get_settings()
    path = Path(db_path) if db_path else settings.db_path
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)
    return conn


def init_schema(conn: sqlite3.Connection) -> None:
    """Прогнать db/schema.sql + создать vec0-таблицы (не лежат в schema.sql)."""
    root = Path(__file__).resolve().parent.parent
    schema = (root / "db" / "schema.sql").read_text(encoding="utf-8")
    conn.executescript(schema)
    conn.execute(
        """
        CREATE VIRTUAL TABLE IF NOT EXISTS cases_vec USING vec0(
            case_id TEXT PRIMARY KEY,
            embedding FLOAT[384]
        )
        """
    )
    conn.execute(
        """
        CREATE VIRTUAL TABLE IF NOT EXISTS theory_vec USING vec0(
            entity_kind TEXT,
            entity_id TEXT,
            embedding FLOAT[384]
        )
        """
    )
    conn.execute(
        """
        CREATE VIRTUAL TABLE IF NOT EXISTS library_vec USING vec0(
            chunk_id TEXT PRIMARY KEY,
            embedding FLOAT[1536]
        )
        """
    )
    conn.commit()


def fetch_one(conn: sqlite3.Connection, sql: str, params: tuple[Any, ...] = ()) -> dict[str, Any] | None:
    row = conn.execute(sql, params).fetchone()
    return dict(row) if row else None


def fetch_all(conn: sqlite3.Connection, sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    return [dict(r) for r in conn.execute(sql, params).fetchall()]
