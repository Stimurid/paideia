"""RAG-поиск по индексу твоего архива (archive_chunks + archive_vec).

Используется LLM-агентами как дополнение к веб-поиску: после/до sonar-pro
вызывается retrieve_archive(query, top_k) и результаты вставляются в промпт
как «контекст из архива пользователя».
"""

from __future__ import annotations

import struct
from typing import Any

from openai import OpenAI

from .config import get_settings
from .db import open_db, fetch_all

EMBED_MODEL = "text-embedding-3-small"


def _embed(query: str) -> list[float]:
    s = get_settings()
    client = OpenAI(api_key=s.llm_primary_api_key, base_url=s.llm_primary_base_url)
    res = client.embeddings.create(model=EMBED_MODEL, input=[query])
    return res.data[0].embedding


def _floats_to_blob(values: list[float]) -> bytes:
    return struct.pack(f"{len(values)}f", *values)


def retrieve_archive(query: str, *, top_k: int = 6,
                     prefer_files: list[str] | None = None) -> list[dict[str, Any]]:
    """Найти top_k чанков твоего архива, ближайших к query.

    Возвращает [{file_path, snippet, text, offset, distance}, ...].
    Если индекс пуст — возвращает пустой список (не падает).
    """
    if not query.strip():
        return []
    conn = open_db()
    try:
        # есть ли индекс?
        row = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='archive_vec'"
        ).fetchone()
        if not row:
            return []
        emb = _embed(query)
        blob = _floats_to_blob(emb)
        rows = fetch_all(
            conn,
            """
            SELECT c.id, c.file_path, c.file_kind, c.offset, c.text, c.snippet,
                   v.distance
            FROM archive_vec v
            JOIN archive_chunks c ON c.id = v.chunk_id
            WHERE v.embedding MATCH ?
              AND k = ?
            ORDER BY v.distance
            """,
            (blob, top_k * 3 if prefer_files else top_k),
        )
        if prefer_files:
            preferred = [r for r in rows if r["file_path"] in prefer_files]
            others = [r for r in rows if r["file_path"] not in prefer_files]
            rows = (preferred + others)[:top_k]
        else:
            rows = rows[:top_k]
        return [
            {
                "file_path": r["file_path"],
                "file_kind": r["file_kind"],
                "offset": r["offset"],
                "snippet": r["snippet"],
                "text": r["text"],
                "distance": round(r["distance"], 4),
            }
            for r in rows
        ]
    finally:
        conn.close()


def list_archive_files() -> list[dict[str, Any]]:
    """Сколько чанков на файл — для UI /archive."""
    conn = open_db()
    try:
        row = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='archive_chunks'"
        ).fetchone()
        if not row:
            return []
        return fetch_all(
            conn,
            """
            SELECT file_path, file_kind, COUNT(*) AS chunk_count
            FROM archive_chunks GROUP BY file_path
            ORDER BY chunk_count DESC
            """,
        )
    finally:
        conn.close()


def archive_stats() -> dict[str, Any]:
    conn = open_db()
    try:
        row = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='archive_chunks'"
        ).fetchone()
        if not row:
            return {"chunks": 0, "files": 0}
        total = conn.execute("SELECT COUNT(*) FROM archive_chunks").fetchone()[0]
        files = conn.execute("SELECT COUNT(DISTINCT file_path) FROM archive_chunks").fetchone()[0]
        return {"chunks": total, "files": files}
    finally:
        conn.close()
