"""Индексация твоего архива C:/projects/Paideia в sqlite-vec.

Запуск:
    python -m scripts.reindex_archive --archive C:/projects/Paideia

Что делает:
1. Идёт по архиву, парсит .md/.pdf/.docx/.pptx через api.extractors.
2. Режет на чанки ~1000 символов с overlap 150.
3. Считает эмбеддинги через 302.ai (text-embedding-3-small, 1536 dims).
4. Сохраняет в archive_vec.
5. Сохраняет meta (filename, offset, snippet) в archive_chunks.
"""

from __future__ import annotations

import sqlite3
import struct
from pathlib import Path
from typing import Any

import typer
from openai import OpenAI

from api.config import get_settings
from api.db import open_db
from api.extractors import extract_file

app = typer.Typer(no_args_is_help=False, add_completion=False)

EMBED_MODEL = "text-embedding-3-small"
EMBED_DIM = 1536


def _chunk(text: str, *, max_chars: int = 1200, overlap: int = 150) -> list[tuple[int, str]]:
    """Простое чанкование с overlap. Возвращает [(offset, chunk_text), ...]."""
    chunks: list[tuple[int, str]] = []
    step = max_chars - overlap
    text = text.strip()
    if not text:
        return chunks
    for start in range(0, len(text), step):
        ch = text[start:start + max_chars].strip()
        if len(ch) > 80:
            chunks.append((start, ch))
    return chunks


def _ensure_schema(conn: sqlite3.Connection) -> None:
    conn.executescript("""
        DROP TABLE IF EXISTS archive_chunks;
        CREATE TABLE archive_chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT NOT NULL,
            file_kind TEXT,
            offset INTEGER,
            text TEXT NOT NULL,
            snippet TEXT
        );
        CREATE INDEX idx_archive_file ON archive_chunks(file_path);

        DROP TABLE IF EXISTS archive_fts;
        CREATE VIRTUAL TABLE archive_fts USING fts5(
            chunk_id UNINDEXED, file_path, text
        );
    """)
    # vec0-таблица: dim = EMBED_DIM
    conn.execute("DROP TABLE IF EXISTS archive_vec")
    conn.execute(f"CREATE VIRTUAL TABLE archive_vec USING vec0(chunk_id INTEGER PRIMARY KEY, embedding FLOAT[{EMBED_DIM}])")
    conn.commit()


def _embed_batch(client: OpenAI, texts: list[str]) -> list[list[float]]:
    res = client.embeddings.create(model=EMBED_MODEL, input=texts)
    return [d.embedding for d in res.data]


def _floats_to_blob(values: list[float]) -> bytes:
    return struct.pack(f"{len(values)}f", *values)


@app.command()
def main(
    archive: str = typer.Option("C:/projects/Paideia", help="Корень архива"),
    batch: int = typer.Option(16, help="Размер батча эмбеддингов"),
    max_chars: int = typer.Option(1200, help="Размер чанка"),
    overlap: int = typer.Option(150, help="Overlap"),
    skip_large: int = typer.Option(20_000_000, help="Пропускать файлы больше N байт"),
) -> None:
    settings = get_settings()
    client = OpenAI(
        api_key=settings.llm_primary_api_key,
        base_url=settings.llm_primary_base_url,
    )

    root = Path(archive)
    if not root.exists():
        typer.echo(f"архив не найден: {root}")
        raise typer.Exit(1)

    conn = open_db()
    _ensure_schema(conn)

    files = []
    for ext in (".md", ".pdf", ".docx", ".pptx", ".txt"):
        files.extend(root.rglob(f"*{ext}"))
    files = sorted(set(p for p in files if not any(s.startswith(".") for s in p.parts)))

    typer.echo(f"архив: {root}; файлов: {len(files)}")

    pending_chunks: list[dict[str, Any]] = []
    inserted_total = 0

    def flush() -> int:
        nonlocal inserted_total
        if not pending_chunks:
            return 0
        texts = [c["text"] for c in pending_chunks]
        embs = _embed_batch(client, texts)
        for c, e in zip(pending_chunks, embs):
            cur = conn.execute(
                "INSERT INTO archive_chunks (file_path, file_kind, offset, text, snippet) VALUES (?, ?, ?, ?, ?)",
                (c["file_path"], c["file_kind"], c["offset"], c["text"], c["text"][:200]),
            )
            chunk_id = cur.lastrowid
            conn.execute("INSERT INTO archive_fts (chunk_id, file_path, text) VALUES (?, ?, ?)",
                         (chunk_id, c["file_path"], c["text"]))
            conn.execute("INSERT INTO archive_vec (chunk_id, embedding) VALUES (?, ?)",
                         (chunk_id, _floats_to_blob(e)))
        conn.commit()
        n = len(pending_chunks)
        inserted_total += n
        pending_chunks.clear()
        return n

    for fpath in files:
        try:
            size = fpath.stat().st_size
            if size > skip_large:
                typer.echo(f"  skip {fpath.name}: {size/1e6:.1f}MB")
                continue
            data = fpath.read_bytes()
            try:
                extracted = extract_file(fpath.name, data)
            except ValueError:
                continue
            text = extracted["text"]
            if not text:
                continue
            chunks = _chunk(text, max_chars=max_chars, overlap=overlap)
            for offset, ch in chunks:
                pending_chunks.append({
                    "file_path": str(fpath.relative_to(root)).replace("\\", "/"),
                    "file_kind": extracted.get("format"),
                    "offset": offset,
                    "text": ch,
                })
                if len(pending_chunks) >= batch:
                    n = flush()
                    typer.echo(f"  + {n} chunks (total {inserted_total})")
            typer.echo(f"  done {fpath.name}: {len(chunks)} chunks")
        except Exception as exc:
            typer.echo(f"  ERR {fpath.name}: {exc}")

    flush()
    typer.echo(f"\n=== готово: {inserted_total} chunks ===")
    conn.close()


if __name__ == "__main__":
    app()
