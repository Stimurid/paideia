"""F1 · Selector противоречий концептов библиотеки.

Pipeline:
    1. embed_concepts() — посчитать embeddings для всех library_concepts
    2. find_candidate_pairs() — для каждого концепта найти top-K похожих
       (cosine > THRESHOLD), вернуть кандидатные пары
    3. classify_pairs() — LLM-разметка каждой пары (equivalent / complements /
       conflicts / unrelated) → concept_conflicts таблица
    4. retrieve_with_selector() — при RAG-поиске группирует найденные чанки
       по школам, помечает противоречия, отдаёт «consistent ветку» или явно
       список из двух противопоставленных
"""

from __future__ import annotations

import json
import math
import struct
import time
import uuid
from pathlib import Path

from .agent import _extract_json
from .db import open_db, fetch_all, fetch_one
from .library import _embed_batch, _floats_to_blob

ROOT = Path(__file__).resolve().parent.parent

SIMILARITY_THRESHOLD = 0.78   # outside conflict-candidate zone
MAX_PAIRS_PER_CONCEPT = 4
EMBED_BATCH = 32


def _ensure_concept_vec_table() -> None:
    conn = open_db()
    try:
        conn.execute(
            "CREATE VIRTUAL TABLE IF NOT EXISTS concept_vec USING vec0("
            "concept_id TEXT PRIMARY KEY, embedding FLOAT[1536])"
        )
        conn.commit()
    finally:
        conn.close()


def _cos(a: list[float], b: list[float]) -> float:
    s = na = nb = 0.0
    for x, y in zip(a, b):
        s += x * y
        na += x * x
        nb += y * y
    if na == 0 or nb == 0:
        return 0.0
    return s / (math.sqrt(na) * math.sqrt(nb))


def embed_concepts(force: bool = False) -> dict:
    """Посчитать embeddings для всех library_concepts. Идемпотентно.

    Embedding = name + ' — ' + definition.
    """
    _ensure_concept_vec_table()
    conn = open_db()
    try:
        if force:
            conn.execute("DELETE FROM concept_vec")
            conn.commit()
        # концепты у которых ещё нет embedding-а
        rows = fetch_all(
            conn,
            """SELECT c.id, c.name, c.definition
               FROM library_concepts c
               LEFT JOIN concept_vec v ON v.concept_id = c.id
               WHERE v.concept_id IS NULL""",
        )
    finally:
        conn.close()
    if not rows:
        return {"status": "ok", "embedded": 0, "msg": "all concepts already embedded"}

    total = 0
    for i in range(0, len(rows), EMBED_BATCH):
        batch = rows[i:i + EMBED_BATCH]
        texts = [(c["name"] or "") + " — " + (c.get("definition") or "")[:500]
                 for c in batch]
        embs = _embed_batch(texts)
        conn = open_db()
        try:
            for c, e in zip(batch, embs):
                conn.execute(
                    "INSERT OR REPLACE INTO concept_vec (concept_id, embedding) VALUES (?, ?)",
                    (c["id"], _floats_to_blob(e)),
                )
                total += 1
            conn.commit()
        finally:
            conn.close()
    return {"status": "ok", "embedded": total}


def find_candidate_pairs(threshold: float = SIMILARITY_THRESHOLD,
                         max_per_concept: int = MAX_PAIRS_PER_CONCEPT) -> list[dict]:
    """Для каждого концепта найти top-N похожих по embedding > threshold.
    Возвращает дедуплицированный список пар (A,B где A.id < B.id).
    """
    _ensure_concept_vec_table()
    conn = open_db()
    try:
        ids = [r["concept_id"] for r in fetch_all(conn, "SELECT concept_id FROM concept_vec")]
        if len(ids) < 2:
            return []
        pairs: dict[tuple[str, str], float] = {}
        for cid in ids:
            row = conn.execute(
                "SELECT embedding FROM concept_vec WHERE concept_id = ?", (cid,)
            ).fetchone()
            blob = row[0]
            # k+1 чтобы исключить себя
            neighbors = fetch_all(
                conn,
                """SELECT concept_id, distance FROM concept_vec
                   WHERE embedding MATCH ? AND k = ?
                   ORDER BY distance""",
                (blob, max_per_concept + 1),
            )
            for n in neighbors:
                if n["concept_id"] == cid:
                    continue
                # vec0 distance == 1 - cosine для нормализованных; для openai не норм. — approx
                # перестрахуемся: используем «маленькое distance» как сильную близость
                sim = 1.0 - min(n["distance"], 1.0)
                if sim < threshold:
                    continue
                a, b = sorted([cid, n["concept_id"]])
                key = (a, b)
                if key not in pairs or sim > pairs[key]:
                    pairs[key] = sim
        return [{"a": a, "b": b, "similarity": round(s, 4)}
                for (a, b), s in pairs.items()]
    finally:
        conn.close()


def classify_pairs(pairs: list[dict], *, skip_existing: bool = True,
                   max_calls: int = 60) -> dict:
    """LLM-разметка каждой пары. Пишет в concept_conflicts."""
    if not pairs:
        return {"status": "ok", "classified": 0, "msg": "no pairs"}

    from .llm import get_llm
    llm = get_llm()
    system_prompt = (ROOT / "prompts" / "concept_conflict.md").read_text(encoding="utf-8")

    classified = 0
    skipped = 0
    failed = 0
    conn = open_db()
    try:
        # отсечь те что уже размечены
        existing = set()
        if skip_existing:
            for r in fetch_all(
                conn, "SELECT concept_a_id, concept_b_id FROM concept_conflicts",
            ):
                existing.add((r["concept_a_id"], r["concept_b_id"]))

        for p in pairs:
            if (p["a"], p["b"]) in existing:
                skipped += 1
                continue
            if classified >= max_calls:
                break
            a = fetch_one(
                conn,
                """SELECT c.id, c.name, c.definition, b.title AS book, b.authors AS author
                   FROM library_concepts c JOIN library_books b ON b.id=c.book_id
                   WHERE c.id = ?""",
                (p["a"],),
            )
            b = fetch_one(
                conn,
                """SELECT c.id, c.name, c.definition, b.title AS book, b.authors AS author
                   FROM library_concepts c JOIN library_books b ON b.id=c.book_id
                   WHERE c.id = ?""",
                (p["b"],),
            )
            if not a or not b:
                continue
            # одна книга — не интересно для конфликта позиций
            if (a["book"] or "").strip() == (b["book"] or "").strip():
                # сохраним как complements автоматически
                conn.execute(
                    """INSERT OR REPLACE INTO concept_conflicts
                       (concept_a_id, concept_b_id, relation, similarity, rationale)
                       VALUES (?, ?, ?, ?, ?)""",
                    (p["a"], p["b"], "complements", p["similarity"],
                     "auto: same book"),
                )
                classified += 1
                continue

            user_prompt = (
                f"A: {a['name']} (из «{a['book']}» / автор {a.get('author') or '?'})\n"
                f"   определение: {(a.get('definition') or '')[:600]}\n\n"
                f"B: {b['name']} (из «{b['book']}» / автор {b.get('author') or '?'})\n"
                f"   определение: {(b.get('definition') or '')[:600]}\n"
            )
            try:
                raw = llm.chat_fast([
                    {"role": "system", "content": system_prompt + "\n\nВыведи только JSON."},
                    {"role": "user", "content": user_prompt},
                ])
                parsed = _extract_json(raw)
                if not parsed or "relation" not in parsed:
                    failed += 1
                    continue
                rel = parsed["relation"].strip().lower()
                if rel not in ("equivalent", "complements", "conflicts", "unrelated"):
                    failed += 1
                    continue
                conn.execute(
                    """INSERT OR REPLACE INTO concept_conflicts
                       (concept_a_id, concept_b_id, relation, similarity, rationale,
                        school_a, school_b)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (p["a"], p["b"], rel, p["similarity"],
                     (parsed.get("rationale") or "")[:1000] or None,
                     (parsed.get("school_a") or "")[:120] or None,
                     (parsed.get("school_b") or "")[:120] or None),
                )
                conn.commit()
                classified += 1
            except Exception as exc:
                failed += 1
                continue
    finally:
        conn.close()
    return {"status": "ok", "classified": classified, "skipped": skipped,
            "failed": failed}


def rebuild_concept_conflicts() -> dict:
    """Полный pipeline: embed → find pairs → classify. Без force-сброса
    (идемпотентно добавляет новое)."""
    started = time.time()
    e = embed_concepts()
    pairs = find_candidate_pairs()
    c = classify_pairs(pairs)
    return {
        "duration_s": round(time.time() - started, 1),
        "embedded": e.get("embedded", 0),
        "candidate_pairs": len(pairs),
        "classified": c.get("classified", 0),
        "skipped": c.get("skipped", 0),
        "failed": c.get("failed", 0),
    }


def conflicts_for_concepts(concept_ids: list[str]) -> list[dict]:
    """Для набора concept_id вернуть конфликты с любым из них."""
    if not concept_ids:
        return []
    conn = open_db()
    try:
        placeholders = ",".join("?" * len(concept_ids))
        rows = fetch_all(
            conn,
            f"""SELECT cc.relation, cc.school_a, cc.school_b, cc.rationale, cc.similarity,
                       a.id AS a_id, a.name AS a_name, a.book_id AS a_book_id,
                       ba.title AS a_book,
                       b.id AS b_id, b.name AS b_name, b.book_id AS b_book_id,
                       bb.title AS b_book
                FROM concept_conflicts cc
                JOIN library_concepts a ON a.id = cc.concept_a_id
                JOIN library_concepts b ON b.id = cc.concept_b_id
                JOIN library_books ba ON ba.id = a.book_id
                JOIN library_books bb ON bb.id = b.book_id
                WHERE cc.relation = 'conflicts'
                  AND (cc.concept_a_id IN ({placeholders})
                       OR cc.concept_b_id IN ({placeholders}))""",
            concept_ids + concept_ids,
        )
        return rows
    finally:
        conn.close()


def annotate_chunks_with_schools(chunks: list[dict]) -> list[dict]:
    """Добавить к каждому найденному library-чанку метку 'школы' через
    concept_conflicts (если есть). Используется в RAG-pipeline.

    Стратегия: для каждого чанка ищем концепты этой же книги, смотрим
    есть ли они в conflicts → берём метку школы из неё.
    """
    if not chunks:
        return chunks
    conn = open_db()
    try:
        book_ids = list({c.get("book_id") for c in chunks if c.get("book_id")})
        if not book_ids:
            return chunks
        placeholders = ",".join("?" * len(book_ids))
        # все концепты этих книг
        concepts_by_book: dict[str, list[str]] = {}
        for r in fetch_all(
            conn,
            f"SELECT id, book_id FROM library_concepts WHERE book_id IN ({placeholders})",
            book_ids,
        ):
            concepts_by_book.setdefault(r["book_id"], []).append(r["id"])
        # для каждой книги — её школа (по первому найденному conflict-у)
        book_school: dict[str, str] = {}
        for book_id, cids in concepts_by_book.items():
            ph = ",".join("?" * len(cids))
            row = conn.execute(
                f"""SELECT school_a, school_b, concept_a_id, concept_b_id
                    FROM concept_conflicts
                    WHERE relation = 'conflicts'
                      AND (concept_a_id IN ({ph}) OR concept_b_id IN ({ph}))
                    LIMIT 1""",
                cids + cids,
            ).fetchone()
            if not row:
                continue
            # если книга в concept_a — берём school_a, иначе school_b
            if row["concept_a_id"] in cids and row["school_a"]:
                book_school[book_id] = row["school_a"]
            elif row["concept_b_id"] in cids and row["school_b"]:
                book_school[book_id] = row["school_b"]
    finally:
        conn.close()
    for ch in chunks:
        ch["school"] = book_school.get(ch.get("book_id"))
    return chunks


def stats() -> dict:
    conn = open_db()
    try:
        total_concepts = conn.execute("SELECT COUNT(*) FROM library_concepts").fetchone()[0]
        embedded = conn.execute("SELECT COUNT(*) FROM concept_vec").fetchone()[0] \
                   if conn.execute("SELECT name FROM sqlite_master WHERE name='concept_vec'").fetchone() else 0
        by_rel = fetch_all(
            conn,
            "SELECT relation, COUNT(*) AS n FROM concept_conflicts GROUP BY relation",
        )
        return {
            "concepts_total": total_concepts,
            "concepts_embedded": embedded,
            "by_relation": {r["relation"]: r["n"] for r in by_rel},
        }
    finally:
        conn.close()
