"""Library v1 — пользовательская библиотека книг/статей.

Иерархия: Book → Section → Chunk. Дополнительно: Concept как первоклассная
сущность с links на корпус.

Workflow:
    register_book() → save_source_file() → extract_text() → split_sections()
        → embed_chunks() → summarize() → extract_concepts()
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import struct

from .db import open_db, fetch_all
from .extractors import extract_file

LIBRARY_DIR_NAME = "library"
SECTION_TARGET_CHARS = 4000   # размер секции при отсутствии явных заголовков
CHUNK_CHARS = 700              # размер чанка для embeddings
CHUNK_OVERLAP = 100

EMBED_MODEL = "text-embedding-3-small"
EMBED_DIM = 1536
EMBED_BATCH = 32


def _floats_to_blob(values: list[float]) -> bytes:
    return struct.pack(f"{len(values)}f", *values)


def _embed_batch(texts: list[str]) -> list[list[float]]:
    from openai import OpenAI
    from .config import get_settings
    s = get_settings()
    client = OpenAI(api_key=s.llm_primary_api_key, base_url=s.llm_primary_base_url)
    res = client.embeddings.create(model=EMBED_MODEL, input=texts)
    return [d.embedding for d in res.data]


def embed_chunks_for_book(book_id: str) -> int:
    """Посчитать embeddings для всех library_chunks книги и записать в library_vec.
    Идемпотентно: предварительно удаляет старые вектора этой книги.
    Возвращает число записанных векторов."""
    conn = open_db()
    try:
        chunks = fetch_all(
            conn,
            "SELECT id, text FROM library_chunks WHERE book_id = ? ORDER BY chunk_num",
            (book_id,),
        )
        if not chunks:
            return 0
        # очистка старых
        ids = [c["id"] for c in chunks]
        placeholders = ",".join("?" * len(ids))
        conn.execute(f"DELETE FROM library_vec WHERE chunk_id IN ({placeholders})", ids)
        conn.commit()

        total = 0
        for i in range(0, len(chunks), EMBED_BATCH):
            batch = chunks[i:i + EMBED_BATCH]
            embs = _embed_batch([c["text"] for c in batch])
            for c, e in zip(batch, embs):
                conn.execute(
                    "INSERT INTO library_vec (chunk_id, embedding) VALUES (?, ?)",
                    (c["id"], _floats_to_blob(e)),
                )
                total += 1
            conn.commit()
        return total
    finally:
        conn.close()


def _content_root() -> Path:
    return Path(__file__).resolve().parent.parent / "content"


def _book_dir(book_id: str) -> Path:
    d = _content_root() / LIBRARY_DIR_NAME / book_id
    d.mkdir(parents=True, exist_ok=True)
    return d


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------


def register_book(
    *, title: str, authors: str = "", year: int | None = None,
    source_kind: str = "txt", source_url: str | None = None,
) -> str:
    """Создать запись о книге в БД (status='uploading'). Возвращает book_id."""
    book_id = f"book-{uuid.uuid4().hex[:10]}"
    conn = open_db()
    try:
        conn.execute(
            """INSERT INTO library_books
               (id, title, authors, year, source_kind, source_url, status)
               VALUES (?, ?, ?, ?, ?, ?, 'uploading')""",
            (book_id, title, authors, year, source_kind, source_url),
        )
        conn.commit()
    finally:
        conn.close()
    return book_id


def save_source_file(book_id: str, filename: str, data: bytes) -> Path:
    """Сохранить оригинал в content/library/<book_id>/source.<ext>."""
    ext = Path(filename).suffix.lower().lstrip(".") or "bin"
    path = _book_dir(book_id) / f"source.{ext}"
    path.write_bytes(data)
    _update_book(book_id, source_path=str(path.relative_to(Path(__file__).resolve().parent.parent)).replace("\\", "/"))
    return path


def _update_book(book_id: str, **fields: Any) -> None:
    if not fields:
        return
    conn = open_db()
    try:
        fields["updated_at"] = datetime.utcnow().isoformat(timespec="seconds")
        cols = ", ".join(f"{k} = ?" for k in fields)
        values = list(fields.values()) + [book_id]
        conn.execute(f"UPDATE library_books SET {cols} WHERE id = ?", values)
        conn.commit()
    finally:
        conn.close()


def set_status(book_id: str, status: str, error: str | None = None) -> None:
    _update_book(book_id, status=status, **({"error": error} if error else {}))


def get_book(book_id: str) -> dict | None:
    conn = open_db()
    try:
        rows = fetch_all(conn, "SELECT * FROM library_books WHERE id = ?", (book_id,))
        if not rows:
            return None
        b = rows[0]
        b["topics"] = json.loads(b.get("topics_json") or "[]")
        b["sections"] = fetch_all(
            conn,
            "SELECT id, section_num, title, summary, chunk_count, char_start, char_end "
            "FROM library_sections WHERE book_id = ? ORDER BY section_num",
            (book_id,),
        )
        b["concepts"] = fetch_all(
            conn,
            "SELECT id, name, definition, quote, page_hint, importance, links_json, section_id "
            "FROM library_concepts WHERE book_id = ? ORDER BY importance DESC, name",
            (book_id,),
        )
        for c in b["concepts"]:
            c["links"] = json.loads(c.get("links_json") or "[]")
        return b
    finally:
        conn.close()


def list_books(status: str | None = None, limit: int = 200) -> list[dict]:
    conn = open_db()
    try:
        where = ""
        params: tuple = ()
        if status:
            where = "WHERE status = ?"
            params = (status,)
        rows = fetch_all(
            conn,
            f"""SELECT id, title, authors, year, source_kind, summary, topics_json,
                       chunk_count, concept_count, status, uploaded_at
                FROM library_books {where}
                ORDER BY uploaded_at DESC LIMIT ?""",
            (*params, limit),
        )
        for b in rows:
            b["topics"] = json.loads(b.get("topics_json") or "[]")
        return rows
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Ingest pipeline
# ---------------------------------------------------------------------------


def extract_text(book_id: str) -> str:
    """Извлечь текст из source-файла через universal extractor."""
    book = get_book(book_id)
    if not book or not book.get("source_path"):
        raise ValueError(f"book {book_id} has no source")
    path = Path(__file__).resolve().parent.parent / book["source_path"]
    data = path.read_bytes()
    result = extract_file(path.name, data)
    text = result.get("text", "")
    if not text.strip():
        raise ValueError("empty text after extract")
    # сохраним plain-text копию для воспроизводимости
    (_book_dir(book_id) / "extracted.txt").write_text(text, encoding="utf-8")
    set_status(book_id, "text_extracted")
    return text


def split_into_sections(book_id: str, text: str) -> list[dict]:
    """Простой split на секции. Если в тексте есть Markdown-заголовки или
    нумерованные главы — режем по ним. Иначе — равномерно по SECTION_TARGET_CHARS.
    """
    import re
    sections: list[dict] = []

    # Эвристика: ищем заголовки вида "## ..." или "Глава N." или "Chapter N." или "N.N "
    pattern = re.compile(
        r"^(?:#{1,3}\s+.+|(?:Глава|Chapter|Раздел|Section)\s+\d+[\.:]\s+.+|\d{1,2}\.\s+[A-ЯA-Z].+)$",
        re.MULTILINE,
    )
    matches = list(pattern.finditer(text))

    if len(matches) >= 3 and len(matches) <= 200:
        # хорошие заголовки
        for i, m in enumerate(matches):
            start = m.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            title = m.group().strip()[:200]
            sections.append({
                "num": i + 1, "title": title,
                "char_start": start, "char_end": end,
                "text": text[start:end],
            })
    else:
        # фиксированное окно
        i = 0
        num = 0
        while i < len(text):
            end = min(i + SECTION_TARGET_CHARS, len(text))
            sections.append({
                "num": num + 1, "title": None,
                "char_start": i, "char_end": end,
                "text": text[i:end],
            })
            num += 1
            i = end

    # сохраняем в БД
    conn = open_db()
    try:
        # удаляем старые секции для этого book (idempotent)
        conn.execute("DELETE FROM library_sections WHERE book_id = ?", (book_id,))
        for s in sections:
            sid = f"sec-{book_id}-{s['num']:04d}"
            s["id"] = sid
            conn.execute(
                """INSERT INTO library_sections
                   (id, book_id, section_num, title, char_start, char_end)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (sid, book_id, s["num"], s["title"], s["char_start"], s["char_end"]),
            )
        conn.commit()
    finally:
        conn.close()
    return sections


def chunk_sections(book_id: str, sections: list[dict]) -> int:
    """Порезать секции на чанки для embeddings. Возвращает общее число чанков."""
    conn = open_db()
    try:
        # очистка
        conn.execute("DELETE FROM library_chunks WHERE book_id = ?", (book_id,))
        total = 0
        for sec in sections:
            text = sec["text"]
            chunks: list[str] = []
            i = 0
            while i < len(text):
                end = min(i + CHUNK_CHARS, len(text))
                chunks.append(text[i:end])
                if end >= len(text):
                    break
                i = end - CHUNK_OVERLAP
            for ci, ch in enumerate(chunks):
                cid = f"chk-{book_id}-{sec['num']:04d}-{ci:03d}"
                conn.execute(
                    """INSERT INTO library_chunks
                       (id, book_id, section_id, chunk_num, char_start, char_end, text)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (cid, book_id, sec["id"], ci,
                     sec["char_start"] + i, sec["char_start"] + i + len(ch), ch),
                )
                total += 1
            conn.execute(
                "UPDATE library_sections SET chunk_count = ? WHERE id = ?",
                (len(chunks), sec["id"]),
            )
        conn.execute(
            "UPDATE library_books SET chunk_count = ?, status = ? WHERE id = ?",
            (total, "chunks_embedded", book_id),
        )
        conn.commit()
    finally:
        conn.close()
    return total


def list_concepts_for_book(book_id: str) -> list[dict]:
    conn = open_db()
    try:
        rows = fetch_all(
            conn,
            "SELECT id, name, definition, importance FROM library_concepts WHERE book_id = ?",
            (book_id,),
        )
        return rows
    finally:
        conn.close()


def save_concepts(book_id: str, concepts: list[dict], section_id: str | None = None) -> int:
    """Сохранить извлечённые концепты. Возвращает число вставленных."""
    conn = open_db()
    inserted = 0
    try:
        existing = {
            r["name"].lower().strip()
            for r in fetch_all(
                conn, "SELECT name FROM library_concepts WHERE book_id = ?", (book_id,)
            )
        }
        for c in concepts:
            name = (c.get("name") or "").strip()
            if not name or name.lower() in existing:
                continue
            cid = f"cnc-{uuid.uuid4().hex[:10]}"
            conn.execute(
                """INSERT INTO library_concepts
                   (id, book_id, section_id, name, definition, quote,
                    page_hint, importance, links_json)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (cid, book_id, section_id,
                 name[:300],
                 c.get("definition", "")[:2000],
                 c.get("quote", "")[:1500] if c.get("quote") else None,
                 c.get("page_hint"),
                 max(1, min(5, int(c.get("importance", 3) or 3))),
                 json.dumps(c.get("links") or [], ensure_ascii=False)),
            )
            existing.add(name.lower())
            inserted += 1
        # обновим счётчик
        conn.execute(
            "UPDATE library_books SET concept_count = "
            "(SELECT COUNT(*) FROM library_concepts WHERE book_id = ?) WHERE id = ?",
            (book_id, book_id),
        )
        conn.commit()
    finally:
        conn.close()
    return inserted


# ---------------------------------------------------------------------------
# Retrieval — hierarchical search
# ---------------------------------------------------------------------------


def search_library(query: str, top_k: int = 5,
                   book_id: str | None = None,
                   prefer_books: list[str] | None = None) -> list[dict]:
    """Векторный поиск по library_chunks (sqlite-vec + text-embedding-3-small).
    Если library_vec пуст — фоллбек на LIKE.

    Возвращает [{chunk_id, book_id, section_id, text, book_title, book_authors,
                  section_title, section_num, distance, char_start, char_end}, ...].
    """
    if not query.strip():
        return []
    conn = open_db()
    try:
        # Есть ли вообще векторный индекс?
        has_vec = conn.execute(
            "SELECT COUNT(*) FROM library_vec"
        ).fetchone()[0] > 0
        if not has_vec:
            return _search_library_like(conn, query, top_k, book_id)

        emb = _embed_batch([query])[0]
        blob = _floats_to_blob(emb)
        k = max(top_k * 4, 20)  # перебираем больше — потом фильтруем
        rows = fetch_all(
            conn,
            """
            SELECT c.id, c.book_id, c.section_id, c.text, c.char_start, c.char_end,
                   c.chunk_num,
                   b.title AS book_title, b.authors AS book_authors,
                   s.title AS section_title, s.section_num,
                   v.distance
            FROM library_vec v
            JOIN library_chunks c ON c.id = v.chunk_id
            JOIN library_books b ON b.id = c.book_id
            LEFT JOIN library_sections s ON s.id = c.section_id
            WHERE v.embedding MATCH ? AND k = ?
            ORDER BY v.distance
            """,
            (blob, k),
        )
        # Фильтры
        if book_id:
            rows = [r for r in rows if r["book_id"] == book_id]
        if prefer_books:
            pref = [r for r in rows if r["book_id"] in prefer_books]
            other = [r for r in rows if r["book_id"] not in prefer_books]
            rows = pref + other
        # MMR-lite: не повторять одну и ту же секцию более 2 раз подряд
        out: list[dict] = []
        per_section: dict[str | None, int] = {}
        for r in rows:
            if per_section.get(r["section_id"], 0) >= 2:
                continue
            per_section[r["section_id"]] = per_section.get(r["section_id"], 0) + 1
            out.append({
                **r,
                "distance": round(r["distance"], 4),
            })
            if len(out) >= top_k:
                break
        return out
    finally:
        conn.close()


def _search_library_like(conn, query: str, top_k: int, book_id: str | None) -> list[dict]:
    q = f"%{query.lower()}%"
    where = "WHERE LOWER(c.text) LIKE ?"
    params: list[Any] = [q]
    if book_id:
        where += " AND c.book_id = ?"
        params.append(book_id)
    rows = fetch_all(
        conn,
        f"""SELECT c.id, c.book_id, c.section_id, c.text, c.char_start, c.char_end,
                   c.chunk_num,
                   b.title AS book_title, b.authors AS book_authors,
                   s.title AS section_title, s.section_num
            FROM library_chunks c
            JOIN library_books b ON b.id = c.book_id
            LEFT JOIN library_sections s ON s.id = c.section_id
            {where}
            ORDER BY c.book_id, c.chunk_num
            LIMIT ?""",
        (*params, top_k),
    )
    for r in rows:
        r["distance"] = None
    return rows


def library_stats() -> dict[str, Any]:
    conn = open_db()
    try:
        books = conn.execute("SELECT COUNT(*) FROM library_books").fetchone()[0]
        chunks = conn.execute("SELECT COUNT(*) FROM library_chunks").fetchone()[0]
        embedded = conn.execute("SELECT COUNT(*) FROM library_vec").fetchone()[0]
        concepts = conn.execute("SELECT COUNT(*) FROM library_concepts").fetchone()[0]
        return {"books": books, "chunks": chunks, "embedded": embedded,
                "concepts": concepts}
    finally:
        conn.close()


def list_concepts_global(limit: int = 200, q: str | None = None) -> list[dict]:
    """Все концепты для каталога."""
    conn = open_db()
    try:
        where = ""
        params: tuple = ()
        if q:
            where = "WHERE LOWER(c.name) LIKE ? OR LOWER(c.definition) LIKE ?"
            params = (f"%{q.lower()}%", f"%{q.lower()}%")
        rows = fetch_all(
            conn,
            f"""SELECT c.id, c.name, c.definition, c.importance, c.book_id, c.links_json,
                       b.title AS book_title, b.authors AS book_authors
                FROM library_concepts c
                JOIN library_books b ON b.id = c.book_id
                {where}
                ORDER BY c.importance DESC, c.name LIMIT ?""",
            (*params, limit),
        )
        for r in rows:
            r["links"] = json.loads(r.get("links_json") or "[]")
        return rows
    finally:
        conn.close()
