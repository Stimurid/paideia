"""Kairon — третий слой Paideia: публикационная модель проекта/курса.

Анализирует проект как академический ход в многомерном координатном
пространстве (philosophy of education / STS / HCI / ...). Выдаёт pathway
matrix и mapping protected_core ↔ что нельзя ломать ради публикации.

См. prompts/kairon_field_position.md и эталон Kairoskopion (Мавринский).
"""

from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any

import frontmatter

from .agent import _extract_json
from .db import open_db, fetch_all, fetch_one
from .llm import get_llm

ROOT = Path(__file__).resolve().parent.parent


def _ensure_table() -> None:
    conn = open_db()
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS article_models (
                id              TEXT PRIMARY KEY,
                target_kind     TEXT NOT NULL,         -- project / course
                target_id       TEXT NOT NULL,
                model_json      TEXT NOT NULL,
                duration_ms     INTEGER,
                model_used      TEXT,
                created_at      TEXT NOT NULL DEFAULT (datetime('now'))
            );
            CREATE INDEX IF NOT EXISTS idx_article_models_target ON article_models(target_kind, target_id, created_at DESC);
        """)
        conn.commit()
    finally:
        conn.close()


def _load_project_context(project_id: str) -> str:
    """Собрать сырой контекст проекта для LLM."""
    path = ROOT / "content" / "projects" / f"{project_id}.md"
    if not path.exists():
        raise ValueError(f"project '{project_id}' not found")
    post = frontmatter.load(path)
    fm = post.metadata
    parts: list[str] = [
        f"# Проект: {fm.get('name')}",
        f"id: {project_id}",
    ]
    if fm.get("description"):
        parts.append(f"\n## Описание\n\n{fm['description']}")
    canvas = fm.get("canvas") or {}
    for sec_id, sec_data in canvas.items():
        text = (sec_data or {}).get("text", "").strip()
        if text:
            parts.append(f"\n## канвас: {sec_id}\n\n{text}")
    if post.content:
        parts.append(f"\n## body\n\n{post.content[:3000]}")
    # references — теория и аналоги
    facets = fm.get("facets") or {}
    if facets:
        parts.append(f"\n## фасеты\n\n```json\n{json.dumps(facets, ensure_ascii=False, indent=2)}\n```")
    return "\n".join(parts)


def _load_course_context(course_id: str) -> str:
    conn = open_db()
    try:
        course = fetch_one(conn, "SELECT * FROM courses WHERE id = ?", (course_id,))
        if not course:
            raise ValueError(f"course '{course_id}' not found")
        events = fetch_all(
            conn,
            "SELECT kind, title, body_md FROM course_events WHERE course_id = ? ORDER BY happened_at",
            (course_id,),
        )
    finally:
        conn.close()
    parts = [f"# Курс: {course.get('name')}"]
    if course.get("description"):
        parts.append(course["description"])
    if course.get("authors"):
        parts.append(f"Авторы: {course['authors']}")
    parts.append(f"\n## События ({len(events)}):")
    for e in events:
        parts.append(f"\n### {e['kind']}: {e.get('title') or ''}")
        if e.get("body_md"):
            parts.append(e["body_md"][:1500])
    return "\n".join(parts)


def analyze(target_kind: str, target_id: str, *,
            model_role: str = "deep") -> dict:
    """Прогон Kairon на проект или курс. Возвращает article_model JSON + id."""
    _ensure_table()
    if target_kind == "project":
        context = _load_project_context(target_id)
    elif target_kind == "course":
        context = _load_course_context(target_id)
    else:
        raise ValueError(f"unknown target_kind: {target_kind}")

    system_prompt = (ROOT / "prompts" / "kairon_field_position.md").read_text(encoding="utf-8")
    llm = get_llm()
    started = time.time()
    method = llm.chat_deep if model_role == "deep" else llm.chat_fast
    raw = method([
        {"role": "system", "content": system_prompt + "\n\nВыведи только JSON."},
        {"role": "user", "content": context[:50000]},
    ])
    duration_ms = int((time.time() - started) * 1000)
    parsed = _extract_json(raw)
    if not parsed:
        raise RuntimeError(f"parse-fail: {raw[:300]}")

    mid = "kar-" + uuid.uuid4().hex[:10]
    conn = open_db()
    try:
        conn.execute(
            """INSERT INTO article_models (id, target_kind, target_id, model_json,
                                            duration_ms, model_used)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (mid, target_kind, target_id,
             json.dumps(parsed, ensure_ascii=False), duration_ms, model_role),
        )
        conn.commit()
    finally:
        conn.close()
    return {"id": mid, "article_model": parsed, "duration_ms": duration_ms}


def latest(target_kind: str, target_id: str) -> dict | None:
    _ensure_table()
    conn = open_db()
    try:
        row = fetch_one(
            conn,
            """SELECT id, model_json, duration_ms, created_at, model_used
               FROM article_models
               WHERE target_kind=? AND target_id=?
               ORDER BY created_at DESC LIMIT 1""",
            (target_kind, target_id),
        )
        if not row:
            return None
        row["article_model"] = json.loads(row["model_json"])
        return row
    finally:
        conn.close()


def list_for_target(target_kind: str, target_id: str) -> list[dict]:
    _ensure_table()
    conn = open_db()
    try:
        rows = fetch_all(
            conn,
            """SELECT id, duration_ms, created_at, model_used
               FROM article_models
               WHERE target_kind=? AND target_id=?
               ORDER BY created_at DESC""",
            (target_kind, target_id),
        )
        return rows
    finally:
        conn.close()
