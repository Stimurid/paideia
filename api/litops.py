"""G3 · Litops Digestor.

Извлекает из артефакта события курса (transcript / chat / homework) пять типов
элементов: вопросы аудитории, предъявленные модели, затруднения, открытые
петли, инсайты. См. prompts/litops_extract.md.
"""

from __future__ import annotations

import json
import time
import uuid
from pathlib import Path

from .agent import _extract_json
from .db import open_db, fetch_all, fetch_one
from .llm import get_llm

ROOT = Path(__file__).resolve().parent.parent

VALID_KINDS = {"question", "model", "difficulty", "open_loop", "insight"}


def _ensure_cache_table() -> None:
    conn = open_db()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS litops_cache (
                body_hash TEXT PRIMARY KEY,
                event_id TEXT NOT NULL,
                extracts_json TEXT NOT NULL,
                cached_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)
        conn.commit()
    finally:
        conn.close()


def _body_hash(body: str) -> str:
    return hashlib.sha256(body.encode("utf-8")).hexdigest()[:32]


def extract_from_event(event_id: str, *, max_concepts_ctx: int = 30,
                        use_cache: bool = True) -> dict:
    """Прогнать LLM по артефакту события и сохранить extracts. Идемпотентно:
    удаляет предыдущие extracts этого события перед вставкой.
    Если кеш hit по body-hash — переиспользует extracts без LLM-вызова.

    Возвращает {"status", "inserted", "duration_s", "cached"}.
    """
    _ensure_cache_table()
    conn = open_db()
    try:
        event = fetch_one(
            conn,
            "SELECT id, course_id, kind, title, body_md FROM course_events WHERE id = ?",
            (event_id,),
        )
        if not event:
            return {"status": "error", "msg": f"event '{event_id}' not found"}
        body = (event.get("body_md") or "").strip()
        if not body or len(body) < 50:
            return {"status": "error", "msg": "event has no body_md (or too short)"}
        bhash = _body_hash(body)
        if use_cache:
            cached = fetch_one(
                conn, "SELECT extracts_json FROM litops_cache WHERE body_hash = ?",
                (bhash,),
            )
            if cached:
                parsed = {"extracts": json.loads(cached["extracts_json"])}
                conn.execute("DELETE FROM litops_extracts WHERE event_id = ?", (event_id,))
                inserted = _save_extracts(conn, event_id, parsed["extracts"])
                conn.commit()
                return {"status": "ok", "inserted": inserted, "duration_s": 0.0,
                        "cached": True}

        # Контекст: концепты библиотеки (имя + book_id) для cross-links
        concepts = fetch_all(
            conn,
            """SELECT c.name, c.book_id, b.title AS book_title
               FROM library_concepts c
               JOIN library_books b ON b.id = c.book_id
               ORDER BY c.importance DESC LIMIT ?""",
            (max_concepts_ctx,),
        )
    finally:
        conn.close()

    system_prompt = (ROOT / "prompts" / "litops_extract.md").read_text(encoding="utf-8")
    concepts_block = ""
    if concepts:
        concepts_block = "\n\nКОНЦЕПТЫ БИБЛИОТЕКИ (для related_concepts):\n" + "\n".join(
            f"- «{c['name']}» (book_id={c['book_id']}, «{c['book_title']}»)"
            for c in concepts
        )

    user_prompt = (
        f"event_kind: {event['kind']}\n"
        f"event_title: {event.get('title') or '(без названия)'}\n"
        f"course_id: {event['course_id']}"
        f"{concepts_block}\n\n"
        f"=== АРТЕФАКТ ===\n\n{body[:30000]}"
    )

    started = time.time()
    llm = get_llm()
    raw = llm.chat_fast([
        {"role": "system", "content": system_prompt + "\n\nВыведи только JSON."},
        {"role": "user", "content": user_prompt},
    ])
    duration = time.time() - started
    parsed = _extract_json(raw)
    if not parsed or "extracts" not in parsed:
        return {"status": "parse-fail", "duration_s": round(duration, 1),
                "raw_preview": raw[:300]}

    extracts = parsed["extracts"] or []
    conn = open_db()
    try:
        conn.execute("DELETE FROM litops_extracts WHERE event_id = ?", (event_id,))
        inserted = _save_extracts(conn, event_id, extracts)
        # запишем в кеш на будущее
        conn.execute(
            "INSERT OR REPLACE INTO litops_cache (body_hash, event_id, extracts_json) VALUES (?, ?, ?)",
            (bhash, event_id, json.dumps(extracts, ensure_ascii=False)),
        )
        conn.commit()
    finally:
        conn.close()

    return {"status": "ok", "inserted": inserted, "duration_s": round(duration, 1),
            "cached": False}


def _save_extracts(conn, event_id: str, extracts: list[dict]) -> int:
    inserted = 0
    for e in extracts:
        kind = (e.get("kind") or "").strip()
        content = (e.get("content") or "").strip()
        if kind not in VALID_KINDS or not content:
            continue
        ex_id = f"lx-{uuid.uuid4().hex[:10]}"
        related = e.get("related_concepts") or []
        conn.execute(
            """INSERT INTO litops_extracts
               (id, event_id, kind, content, speaker, quote, position_hint,
                related_concepts_json, confidence)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (ex_id, event_id, kind, content[:2000],
             (e.get("speaker") or "")[:120] or None,
             (e.get("quote") or "")[:2000] or None,
             (e.get("position_hint") or "")[:120] or None,
             json.dumps(related, ensure_ascii=False) if related else None,
             max(1, min(5, int(e.get("confidence", 3) or 3)))),
        )
        inserted += 1
    return inserted


def list_extracts(event_id: str) -> list[dict]:
    conn = open_db()
    try:
        rows = fetch_all(
            conn,
            """SELECT id, kind, content, speaker, quote, position_hint,
                      related_concepts_json, confidence, created_at
               FROM litops_extracts WHERE event_id = ?
               ORDER BY confidence DESC, id""",
            (event_id,),
        )
        for r in rows:
            r["related"] = json.loads(r.get("related_concepts_json") or "[]")
        return rows
    finally:
        conn.close()


def generate_course_reflection(course_id: str) -> dict:
    """F3-G6: собрать методологический протокол курса через LLM.

    Контекст: все события + артефакты автор/студент + чаты + litops.
    Использует deep-модель (gpt-5).
    """
    from . import course_packs as cp
    conn = open_db()
    try:
        course = fetch_one(conn, "SELECT * FROM courses WHERE id = ?", (course_id,))
        if not course:
            return {"status": "error", "msg": "course not found"}
        events = fetch_all(
            conn,
            "SELECT id, kind, title, happened_at, body_md FROM course_events "
            "WHERE course_id = ? ORDER BY happened_at",
            (course_id,),
        )
    finally:
        conn.close()
    if not events:
        return {"status": "error", "msg": "no events in course"}

    parts = [
        f"# Курс: {course.get('name')}",
        f"Период: {course.get('period_start') or '?'} – {course.get('period_end') or '?'}",
        f"Описание: {course.get('description') or ''}",
        "",
        f"# События ({len(events)}):",
    ]
    for e in events:
        arts = cp.list_artifacts(e["id"])
        chat = cp.list_chat_messages(e["id"])
        extracts = list_extracts(e["id"])
        parts.append(f"\n## {e.get('happened_at','?')[:16]} · {e['kind']}: {e.get('title') or '(без названия)'}")
        if e.get("body_md"):
            parts.append(f"body: {e['body_md'][:500]}…")
        for a in arts:
            line = f"  [{a['package']}/{a['kind']}] {a.get('title') or ''}"
            if a.get("body_md"):
                line += f" — {a['body_md'][:300]}"
            if a.get("author_nickname"):
                line += f" (автор: {a['author_nickname']})"
            parts.append(line)
        if chat:
            parts.append(f"  чат ({len(chat)} сообщений):")
            for m in chat[:8]:
                parts.append(f"    {m.get('speaker','?')}: {m.get('content','')[:150]}")
        if extracts:
            parts.append(f"  litops ({len(extracts)}):")
            for x in extracts[:6]:
                parts.append(f"    [{x['kind']}/★{x['confidence']}] {x['content'][:200]}")

    context = "\n".join(parts)
    system_prompt = (ROOT / "prompts" / "course_reflection.md").read_text(encoding="utf-8")

    llm = get_llm()
    started = time.time()
    raw = llm.chat_deep([
        {"role": "system", "content": system_prompt + "\n\nВыведи только JSON."},
        {"role": "user", "content": context[:60000]},
    ])
    duration = time.time() - started
    parsed = _extract_json(raw)
    if not parsed:
        return {"status": "parse-fail", "raw_preview": raw[:300],
                "duration_s": round(duration, 1)}
    return {"status": "ok", "protocol": parsed, "duration_s": round(duration, 1),
            "events_used": len(events)}


def list_extracts_for_course(course_id: str) -> dict:
    """Сводка litops по всему курсу: счётчики + последние 20 экстрактов."""
    conn = open_db()
    try:
        counts = fetch_all(
            conn,
            """SELECT lx.kind, COUNT(*) AS n
               FROM litops_extracts lx
               JOIN course_events ce ON ce.id = lx.event_id
               WHERE ce.course_id = ?
               GROUP BY lx.kind""",
            (course_id,),
        )
        recent = fetch_all(
            conn,
            """SELECT lx.id, lx.kind, lx.content, lx.quote, lx.confidence,
                      ce.title AS event_title, ce.id AS event_id, ce.happened_at
               FROM litops_extracts lx
               JOIN course_events ce ON ce.id = lx.event_id
               WHERE ce.course_id = ?
               ORDER BY ce.happened_at DESC, lx.confidence DESC LIMIT 30""",
            (course_id,),
        )
        return {
            "counts": {r["kind"]: r["n"] for r in counts},
            "recent": recent,
        }
    finally:
        conn.close()
