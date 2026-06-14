"""Артефакты события курса: пакеты автора и студентов, цепочки д/з, чаты.

Каждое event имеет два пакета:
    - author    — материалы преподавателя (слайды, транскрипт, материалы для чтения, бриф д/з)
    - student   — материалы участников (сданные д/з, вопросы из чата, заметки)

Цепочка homework:
    event(kind=homework_release) → artifact(kind=homework_brief, package=author)
        ← artifact(kind=homework_submission, package=student, in_response_to=brief.id)
"""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any

from .db import open_db, fetch_all, fetch_one

ROOT = Path(__file__).resolve().parent.parent

VALID_PACKAGES = {"author", "student", "course_meta"}
VALID_KINDS = {
    "slides", "transcript", "reading", "homework_brief",
    "homework_submission", "chat_export", "student_question",
    "notes", "exam_brief", "exam_response",
}

# Какие kinds к какому пакету по умолчанию относятся
DEFAULT_PACKAGE_BY_KIND = {
    "slides": "author", "transcript": "author", "reading": "author",
    "homework_brief": "author", "exam_brief": "author",
    "homework_submission": "student", "student_question": "student",
    "chat_export": "student", "exam_response": "student",
    "notes": "course_meta",
}


def add_artifact(*, event_id: str, package: str, kind: str,
                 title: str = "", body_md: str = "",
                 file_path: str = "", author_nickname: str = "",
                 author_session_id: str | None = None,
                 in_response_to: str | None = None) -> str:
    if package not in VALID_PACKAGES:
        raise ValueError(f"unknown package: {package}")
    if kind not in VALID_KINDS:
        raise ValueError(f"unknown kind: {kind}")
    if not body_md and not file_path and not title:
        raise ValueError("at least title, body_md, or file_path required")
    aid = "art-" + uuid.uuid4().hex[:10]
    conn = open_db()
    try:
        conn.execute(
            """INSERT INTO course_event_artifacts
               (id, event_id, package, kind, title, body_md, file_path,
                author_nickname, author_session_id, in_response_to)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (aid, event_id, package, kind, title or None,
             body_md or None, file_path or None,
             author_nickname or None, author_session_id, in_response_to),
        )
        conn.commit()
    finally:
        conn.close()
    return aid


def list_artifacts(event_id: str, package: str | None = None) -> list[dict]:
    conn = open_db()
    try:
        wh = "WHERE event_id = ?"
        params: list[Any] = [event_id]
        if package:
            wh += " AND package = ?"
            params.append(package)
        return fetch_all(
            conn,
            f"""SELECT id, package, kind, title, body_md, file_path,
                       author_nickname, author_session_id, in_response_to, created_at
                FROM course_event_artifacts {wh}
                ORDER BY package, kind, created_at""",
            tuple(params),
        )
    finally:
        conn.close()


def delete_artifact(artifact_id: str) -> None:
    conn = open_db()
    try:
        conn.execute("DELETE FROM course_event_artifacts WHERE id = ?", (artifact_id,))
        conn.commit()
    finally:
        conn.close()


def get_homework_thread(release_artifact_id: str) -> dict:
    """Бриф д/з + все сдачи на него."""
    conn = open_db()
    try:
        brief = fetch_one(
            conn,
            "SELECT * FROM course_event_artifacts WHERE id = ?", (release_artifact_id,),
        )
        submissions = fetch_all(
            conn,
            """SELECT * FROM course_event_artifacts WHERE in_response_to = ?
               ORDER BY created_at""",
            (release_artifact_id,),
        )
        return {"brief": brief, "submissions": submissions}
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Chat messages
# ---------------------------------------------------------------------------


def add_chat_messages(event_id: str, messages: list[dict]) -> int:
    """Добавить пачку сообщений чата.
    messages = [{speaker, content, role_at_time?, sent_at?}, ...]
    """
    conn = open_db()
    try:
        existing = conn.execute(
            "SELECT COALESCE(MAX(sequence), 0) FROM course_chat_messages WHERE event_id = ?",
            (event_id,),
        ).fetchone()[0] or 0
        seq = existing
        for m in messages:
            content = (m.get("content") or "").strip()
            if not content:
                continue
            seq += 1
            mid = "chm-" + uuid.uuid4().hex[:10]
            conn.execute(
                """INSERT INTO course_chat_messages
                   (id, event_id, speaker, role_at_time, content, sent_at, sequence)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (mid, event_id, (m.get("speaker") or "")[:120] or None,
                 (m.get("role_at_time") or "")[:40] or None,
                 content[:4000], m.get("sent_at") or None, seq),
            )
        conn.commit()
        return seq - existing
    finally:
        conn.close()


def list_chat_messages(event_id: str) -> list[dict]:
    conn = open_db()
    try:
        return fetch_all(
            conn,
            "SELECT speaker, role_at_time, content, sent_at, sequence "
            "FROM course_chat_messages WHERE event_id = ? ORDER BY sequence",
            (event_id,),
        )
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Role-aware view: что видит участник с конкретной ролью
# ---------------------------------------------------------------------------


def visible_artifacts_for_role(event_id: str, *, role: str | None,
                               session_id: str | None) -> list[dict]:
    """Фильтр: что юзер с такой ролью видит в этом событии."""
    all_arts = list_artifacts(event_id)
    if role in ("author", "lecturer", "ta", "observer"):
        return all_arts  # всё
    if role == "seminarist":
        return [a for a in all_arts if a["package"] != "student"
                or a["kind"] in ("student_question", "chat_export")]
    if role == "student":
        # видит: author + course_meta + СВОИ student-артефакты
        return [a for a in all_arts
                if a["package"] in ("author", "course_meta")
                or (a["package"] == "student" and a.get("author_session_id") == session_id)]
    # без роли — только author + course_meta
    return [a for a in all_arts if a["package"] in ("author", "course_meta")]


# ---------------------------------------------------------------------------
# Course-wide stats
# ---------------------------------------------------------------------------


def artifact_counts_for_event(event_id: str) -> dict[str, int]:
    conn = open_db()
    try:
        rows = fetch_all(
            conn,
            "SELECT package, COUNT(*) AS n FROM course_event_artifacts "
            "WHERE event_id = ? GROUP BY package",
            (event_id,),
        )
        result = {"author": 0, "student": 0, "course_meta": 0}
        for r in rows:
            result[r["package"]] = r["n"]
        return result
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Project dynamics через git history
# ---------------------------------------------------------------------------


def project_dynamics_across_course(course_id: str, project_id: str) -> list[dict]:
    """Для каждого события курса показать состояние проекта в этот момент.
    Использует git log content/projects/<project_id>.md
    """
    import subprocess
    path = ROOT / "content" / "projects" / f"{project_id}.md"
    if not path.exists():
        return []
    conn = open_db()
    try:
        events = fetch_all(
            conn,
            "SELECT id, kind, title, happened_at FROM course_events "
            "WHERE course_id = ? ORDER BY happened_at",
            (course_id,),
        )
    finally:
        conn.close()
    if not events:
        return []
    # git log: список коммитов по файлу с датами
    try:
        out = subprocess.check_output(
            ["git", "log", "--format=%H|%cI|%s", "--", str(path.relative_to(ROOT))],
            cwd=ROOT, text=True, timeout=10,
        )
    except Exception:
        return []
    commits = []
    for line in out.strip().splitlines():
        parts = line.split("|", 2)
        if len(parts) == 3:
            commits.append({"hash": parts[0], "date": parts[1], "msg": parts[2]})

    timeline = []
    for e in events:
        # ближайший коммит ≤ happened_at
        when = (e.get("happened_at") or "")[:19]
        nearest = next((c for c in commits if c["date"] <= when), None)
        timeline.append({
            "event_id": e["id"], "event_title": e.get("title"),
            "event_kind": e["kind"], "when": when,
            "project_commit": nearest,
        })
    return timeline
