"""Курс как конвейер роста корпуса.

Из событий курса автоматически создаются кандидаты на:
- новые гипотезы (из litops kind=model с confidence ≥4)
- контр-сигналы (из student_question с маркером сомнения)
- новые кейсы (из homework_submission про реальное внедрение)
- сценарии лаборатории (из reflection session с methodological_recommendations)

Модератор (роль author / lecturer) принимает / отклоняет / редактирует
кандидата → он становится частью корпуса в content/.
"""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any

from .db import open_db, fetch_all, fetch_one

ROOT = Path(__file__).resolve().parent.parent

VALID_KINDS = {"hypothesis_candidate", "counter_signal_candidate",
               "case_candidate", "scenario_candidate"}


def add_candidate(*, kind: str, title: str, body_md: str = "",
                   source_event_id: str | None = None,
                   source_course_id: str | None = None,
                   source_type: str = "manual",
                   source_confidence: int = 3,
                   rationale: str = "") -> str:
    if kind not in VALID_KINDS:
        raise ValueError(f"unknown kind: {kind}")
    cid = "ccd-" + uuid.uuid4().hex[:10]
    conn = open_db()
    try:
        conn.execute(
            """INSERT INTO corpus_candidates
               (id, kind, title, body_md, source_event_id, source_course_id,
                source_type, source_confidence, rationale)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (cid, kind, title[:300], body_md[:8000] or None,
             source_event_id, source_course_id, source_type,
             source_confidence, rationale[:1000] or None),
        )
        conn.commit()
    finally:
        conn.close()
    return cid


def harvest_from_event(event_id: str) -> dict:
    """Прогон по событию курса: автогенерация кандидатов из его artefacts.

    Идемпотентно: не дублирует уже существующие (по source_event_id+source_type).
    """
    conn = open_db()
    try:
        event = fetch_one(
            conn,
            "SELECT id, course_id, kind FROM course_events WHERE id = ?",
            (event_id,),
        )
        if not event:
            return {"status": "error", "msg": "event not found"}

        existing = {
            (r["source_type"], r["title"])
            for r in fetch_all(
                conn,
                "SELECT source_type, title FROM corpus_candidates WHERE source_event_id = ?",
                (event_id,),
            )
        }

        # litops kind=model с confidence ≥4 → гипотеза-кандидат
        models = fetch_all(
            conn,
            """SELECT content, quote, confidence FROM litops_extracts
               WHERE event_id = ? AND kind = 'model' AND confidence >= 4""",
            (event_id,),
        )
        # litops kind=difficulty с confidence ≥4 → контр-сигнал
        difficulties = fetch_all(
            conn,
            """SELECT content, quote, confidence FROM litops_extracts
               WHERE event_id = ? AND kind = 'difficulty' AND confidence >= 4""",
            (event_id,),
        )
        # litops kind=open_loop с confidence ≥4 → сценарий-кандидат
        loops = fetch_all(
            conn,
            """SELECT content, quote, confidence FROM litops_extracts
               WHERE event_id = ? AND kind = 'open_loop' AND confidence >= 4""",
            (event_id,),
        )
        # student_question artifacts → counter_signal candidate
        questions = fetch_all(
            conn,
            """SELECT title, body_md, author_nickname FROM course_event_artifacts
               WHERE event_id = ? AND kind = 'student_question'""",
            (event_id,),
        )
        # homework_submission → case_candidate
        submissions = fetch_all(
            conn,
            """SELECT title, body_md, author_nickname FROM course_event_artifacts
               WHERE event_id = ? AND kind = 'homework_submission'""",
            (event_id,),
        )
    finally:
        conn.close()

    created = 0
    for m in models:
        title = m["content"][:160]
        if ("litops_model", title) in existing:
            continue
        add_candidate(
            kind="hypothesis_candidate", title=title,
            body_md=f"Цитата: «{m.get('quote','')}»\n\n— из лекции/семинара",
            source_event_id=event_id, source_course_id=event["course_id"],
            source_type="litops_model",
            source_confidence=m["confidence"],
            rationale="Модель, явно предъявленная аудитории, с confidence ≥4 — кандидат в гипотезу корпуса.",
        )
        created += 1

    for d in difficulties:
        title = d["content"][:160]
        if ("litops_difficulty", title) in existing:
            continue
        add_candidate(
            kind="counter_signal_candidate", title=title,
            body_md=f"Цитата: «{d.get('quote','')}»",
            source_event_id=event_id, source_course_id=event["course_id"],
            source_type="litops_difficulty",
            source_confidence=d["confidence"],
            rationale="Затруднение аудитории — потенциальный контр-сигнал к гипотезе корпуса.",
        )
        created += 1

    for l in loops:
        title = l["content"][:160]
        if ("litops_open_loop", title) in existing:
            continue
        add_candidate(
            kind="scenario_candidate", title=title,
            body_md=f"Открытая петля: «{l.get('quote','')}»",
            source_event_id=event_id, source_course_id=event["course_id"],
            source_type="litops_open_loop",
            source_confidence=l["confidence"],
            rationale="Незакрытый вопрос — кандидат на сценарий лаборатории.",
        )
        created += 1

    for q in questions:
        title = (q.get("title") or q.get("body_md") or "")[:160].strip()
        if not title or ("student_question", title) in existing:
            continue
        add_candidate(
            kind="counter_signal_candidate", title=title,
            body_md=f"Вопрос от {q.get('author_nickname','аноним')}:\n\n{q.get('body_md','')}",
            source_event_id=event_id, source_course_id=event["course_id"],
            source_type="student_question",
            source_confidence=4,
            rationale="Студенческий вопрос может указывать на слабое место в гипотезе.",
        )
        created += 1

    for s in submissions:
        title = (s.get("title") or s.get("body_md") or "")[:160].strip()
        if not title or ("homework_submission", title) in existing:
            continue
        add_candidate(
            kind="case_candidate", title=f"Студенческий проект: {title}",
            body_md=s.get("body_md", ""),
            source_event_id=event_id, source_course_id=event["course_id"],
            source_type="homework_submission",
            source_confidence=3,
            rationale=f"Замысел студента {s.get('author_nickname','аноним')} — возможный кандидат в кейс корпуса.",
        )
        created += 1

    return {"status": "ok", "created": created,
            "from_litops_model": len(models),
            "from_litops_difficulty": len(difficulties),
            "from_litops_open_loop": len(loops),
            "from_student_question": len(questions),
            "from_homework_submission": len(submissions)}


def list_candidates(status: str = "pending", kind: str | None = None,
                    limit: int = 200) -> list[dict]:
    conn = open_db()
    try:
        wh = "WHERE status = ?"
        params: list[Any] = [status]
        if kind:
            wh += " AND kind = ?"
            params.append(kind)
        return fetch_all(
            conn,
            f"""SELECT * FROM corpus_candidates {wh}
                ORDER BY created_at DESC LIMIT ?""",
            tuple(params) + (limit,),
        )
    finally:
        conn.close()


def decide(candidate_id: str, decision: str,
           decided_by: str | None = None) -> dict:
    """decision: accepted / rejected / edited (юзер изменил body)."""
    if decision not in ("accepted", "rejected", "edited"):
        raise ValueError(f"unknown decision: {decision}")
    conn = open_db()
    try:
        conn.execute(
            """UPDATE corpus_candidates
               SET status = ?, decided_at = datetime('now'), decided_by = ?
               WHERE id = ?""",
            (decision, decided_by, candidate_id),
        )
        conn.commit()
        return {"status": "ok", "decision": decision}
    finally:
        conn.close()


def stats() -> dict:
    conn = open_db()
    try:
        total = conn.execute("SELECT COUNT(*) FROM corpus_candidates").fetchone()[0]
        by_status = fetch_all(
            conn, "SELECT status, COUNT(*) AS n FROM corpus_candidates GROUP BY status"
        )
        by_kind = fetch_all(
            conn, "SELECT kind, COUNT(*) AS n FROM corpus_candidates GROUP BY kind"
        )
        return {
            "total": total,
            "by_status": {r["status"]: r["n"] for r in by_status},
            "by_kind": {r["kind"]: r["n"] for r in by_kind},
        }
    finally:
        conn.close()
