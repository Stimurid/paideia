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


def extract_from_event(event_id: str, *, max_concepts_ctx: int = 30) -> dict:
    """Прогнать LLM по артефакту события и сохранить extracts. Идемпотентно:
    удаляет предыдущие extracts этого события перед вставкой.

    Возвращает {"status", "inserted", "duration_s"}.
    """
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
        conn.commit()
    finally:
        conn.close()

    return {"status": "ok", "inserted": inserted, "duration_s": round(duration, 1)}


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
