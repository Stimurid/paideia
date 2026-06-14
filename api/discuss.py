"""Discuss-агент ∇Kaiyona — дискуссия с настраиваемыми QMO-осями и целью.

Контекст:
    - проект (если discuss привязан к проекту): brief + canvas + аналоги + теория
    - курс (если активен paideia_course): лента событий + litops_extracts
    - библиотека: hierarchical RAG с F1-селектором школ
    - всегда: Kaiyona core + World Model + QMO axes
"""

from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any

import yaml

from .db import open_db, fetch_all, fetch_one
from .llm import get_llm

ROOT = Path(__file__).resolve().parent.parent
PROMPTS = ROOT / "prompts"


# ---------------------------------------------------------------------------
# Конфиг по умолчанию
# ---------------------------------------------------------------------------

DEFAULT_AXES = {"F": 6, "M": 6, "A": 6, "Ω": 5, "Ψ": 5, "Δ": 7,
                "T": 5, "I": 5, "S1": 7, "C3": 5, "Z3": 5, "Z8": 4}

DEFAULT_CONFIG = {
    "goal": "consult",
    "critique_level": 1,
    "qmo_preset": "balanced",
    "axes": DEFAULT_AXES,
    "boost_level": "medium",
    "model_role": "fast",
    "use_library": True,
    "use_corpus": True,
}


def _load_goals_cfg() -> dict:
    return yaml.safe_load((PROMPTS / "discuss_goals.yaml").read_text(encoding="utf-8"))


def list_goals() -> list[dict]:
    return _load_goals_cfg()["goals"]


def list_qmo_presets() -> list[dict]:
    return _load_goals_cfg()["qmo_presets"]


def list_critique_levels() -> dict:
    return _load_goals_cfg()["critique_levels"]


# ---------------------------------------------------------------------------
# Сборка системного промпта
# ---------------------------------------------------------------------------


def _build_system_prompt(config: dict, *, project: dict | None = None,
                         course: dict | None = None,
                         course_events: list[dict] | None = None,
                         my_role_in_course: str | None = None,
                         user_session_id: str | None = None,
                         project_dynamics: list[dict] | None = None) -> str:
    cfg = _load_goals_cfg()
    parts: list[str] = []

    # 1. Ядро Kaiyona + World Model + этика
    parts.append((PROMPTS / "discuss_kaiyona_core.md").read_text(encoding="utf-8"))

    # 2. QMO-слой с активными осями
    qmo_text = (PROMPTS / "discuss_qmo_axes.md").read_text(encoding="utf-8")
    axes = config.get("axes") or DEFAULT_AXES
    axes_line = " · ".join(f"{k}={v}" for k, v in axes.items())
    boost = config.get("boost_level", "medium")
    qmo_text += f"\n\n## АКТИВНАЯ КОНФИГУРАЦИЯ\n\nBOOST({boost})\nTUNE({{{axes_line}}})\n"
    parts.append(qmo_text)

    # 3. Цель агента
    goal_id = config.get("goal", "consult")
    goal = next((g for g in cfg["goals"] if g["id"] == goal_id), None)
    if goal:
        parts.append(f"\n# АКТИВНАЯ ЦЕЛЬ: {goal['icon']} {goal['name']}\n\n{goal['prompt']}")

    # 4. Уровень критики
    level = int(config.get("critique_level", 1))
    crit = cfg["critique_levels"].get(level) or cfg["critique_levels"][1]
    parts.append(f"\n# ТОН: {crit['label']}\n\n{crit['instruction']}")

    # 5. Проектный контекст
    if project:
        parts.append("\n# ПРОЕКТ\n")
        brief = {
            "id": project.get("id"),
            "name": project.get("name"),
            "facets": project.get("facets"),
            "ai": project.get("ai"),
            "axes": project.get("axes"),
            "canvas_filled": [
                f"{k}: {v.get('text', '')[:400]}"
                for k, v in (project.get("canvas") or {}).items()
                if v.get("text")
            ],
        }
        parts.append("```json\n" + json.dumps(brief, ensure_ascii=False, indent=2) + "\n```")

    # 6. Курсовой контекст (если активен) — со-педагог режим
    if course:
        parts.append(f"\n# АКТИВНЫЙ КУРС: {course.get('name')}\n")
        if course.get("description"):
            parts.append(course["description"])
        if my_role_in_course:
            parts.append(f"\n## Моя роль в курсе: **{my_role_in_course}**")
            if my_role_in_course == "student":
                parts.append("Видишь только: авторские материалы прошедших событий + свои собственные работы. "
                             "Не упоминай работы других студентов. Не спойлеришь будущие лекции.")
            elif my_role_in_course in ("author", "lecturer"):
                parts.append("Видишь всё: авторские материалы, сданные работы всех студентов, чаты, litops-извлечения.")
        if course_events:
            parts.append("\n## Лента курса (по событиям):\n")
            from . import course_packs as cp
            for e in course_events[:12]:
                ev_id = e.get("id")
                arts = cp.visible_artifacts_for_role(
                    ev_id, role=my_role_in_course, session_id=user_session_id,
                ) if ev_id else []
                chat = cp.list_chat_messages(ev_id) if ev_id else []
                line = f"\n### [{e.get('happened_at', '?')[:10]}] {e.get('kind')}: «{e.get('title') or '(без названия)'}»"
                parts.append(line)
                # group by package
                author_arts = [a for a in arts if a.get("package") == "author"]
                student_arts = [a for a in arts if a.get("package") == "student"]
                if author_arts:
                    parts.append("  Авторское:")
                    for a in author_arts[:5]:
                        line = f"  — {a['kind']}: {a.get('title') or ''}"
                        if a.get("body_md"):
                            line += f"\n    {a['body_md'][:300]}…"
                        parts.append(line)
                if student_arts:
                    parts.append("  От студентов:")
                    for a in student_arts[:8]:
                        nick = a.get("author_nickname") or "аноним"
                        line = f"  — [{nick}] {a['kind']}"
                        if a.get("body_md"):
                            line += f": {a['body_md'][:200]}…"
                        parts.append(line)
                if e.get("body_md") and not (author_arts or student_arts):
                    parts.append(f"  legacy body: {e['body_md'][:300]}…")
                if chat:
                    parts.append(f"  Чат ({len(chat)} сообщений):")
                    for m in chat[:10]:
                        parts.append(f"    {m.get('speaker') or '?'}: {m.get('content','')[:120]}")
        if project_dynamics:
            parts.append("\n## Динамика проекта по событиям курса:")
            for d in project_dynamics:
                c = d.get("project_commit") or {}
                if c:
                    parts.append(f"  [{d['when'][:10]}] {d.get('event_kind')}: commit {c.get('hash','')[:7]} — {c.get('msg','')[:80]}")
        if my_role_in_course in ("author", "lecturer", "seminarist", None):
            parts.append(
                "\n**Режим со-педагога активен.** Держишь сцену группового мышления (ОДИ: "
                "ориентация → проблематизация → проектирование → организация → действие → рефлексия). "
                "Не отвечаешь студенту вместо лектора — задаёшь вопросы, ведущие к рефлексии методов."
            )
        else:
            parts.append(
                "\n**Режим участника курса.** Объясняй простым языком, разбирай задания шаг за шагом. "
                "Без жаргона. Если студент путается — переформулируй, давай пример."
            )

    return "\n\n".join(parts)


# ---------------------------------------------------------------------------
# Контекст из RAG
# ---------------------------------------------------------------------------


def _build_rag_context(text: str, config: dict) -> str:
    parts: list[str] = []
    if config.get("use_library", True):
        try:
            from .library import search_library
            from .selector import annotate_chunks_with_schools
            chunks = annotate_chunks_with_schools(search_library(text, top_k=4))
            if chunks:
                schools = {c.get("school") for c in chunks if c.get("school")}
                if len(schools) >= 2:
                    parts.append("\n## БИБЛИОТЕКА — НАЙДЕНЫ ПРОТИВОРЕЧАЩИЕ ШКОЛЫ\n")
                    parts.append(f"школы: {', '.join(sorted(schools))} — не смешивай.")
                else:
                    parts.append("\n## БИБЛИОТЕКА\n")
                for ch in chunks:
                    sec = ch.get("section_title") or f"sec {ch.get('section_num')}"
                    school = f" [школа: {ch['school']}]" if ch.get("school") else ""
                    parts.append(f"— 📚 «{ch['book_title']}» / {ch.get('book_authors') or '?'} / {sec}{school}")
                    parts.append(f"  {ch['text'][:500].strip()}")
        except Exception:
            pass
    if config.get("use_corpus", True):
        try:
            from .retrieve import retrieve_archive
            chs = retrieve_archive(text, top_k=3)
            if chs:
                parts.append("\n## АРХИВ (твои md/pdf)\n")
                for ch in chs:
                    parts.append(f"— [{ch['file_path']}] {ch['text'][:400]}")
        except Exception:
            pass
    return "\n".join(parts) if parts else ""


# ---------------------------------------------------------------------------
# CRUD сессий
# ---------------------------------------------------------------------------


def create_session(*, session_id: str | None, project_id: str | None,
                   course_id: str | None, config: dict | None = None) -> str:
    did = "dsc-" + uuid.uuid4().hex[:10]
    final_config = {**DEFAULT_CONFIG, **(config or {})}
    conn = open_db()
    try:
        conn.execute(
            """INSERT INTO discuss_sessions
               (id, session_id, project_id, course_id, config_json)
               VALUES (?, ?, ?, ?, ?)""",
            (did, session_id, project_id, course_id,
             json.dumps(final_config, ensure_ascii=False)),
        )
        conn.commit()
    finally:
        conn.close()
    return did


def get_session(discuss_id: str) -> dict | None:
    conn = open_db()
    try:
        row = fetch_one(conn, "SELECT * FROM discuss_sessions WHERE id = ?",
                        (discuss_id,))
        if not row:
            return None
        row["config"] = json.loads(row.get("config_json") or "{}")
        row["messages"] = fetch_all(
            conn,
            "SELECT sender, content, created_at, tokens, duration_ms "
            "FROM discuss_messages WHERE discuss_id = ? ORDER BY id",
            (discuss_id,),
        )
        return row
    finally:
        conn.close()


def list_sessions(session_id: str | None, limit: int = 50) -> list[dict]:
    conn = open_db()
    try:
        wh = "WHERE session_id = ?" if session_id else ""
        params: tuple = (session_id,) if session_id else ()
        rows = fetch_all(
            conn,
            f"""SELECT id, title, project_id, course_id, config_json, updated_at,
                       (SELECT COUNT(*) FROM discuss_messages WHERE discuss_id=discuss_sessions.id) AS n_msgs
                FROM discuss_sessions {wh}
                ORDER BY updated_at DESC LIMIT ?""",
            params + (limit,),
        )
        for r in rows:
            r["config"] = json.loads(r.get("config_json") or "{}")
        return rows
    finally:
        conn.close()


def update_config(discuss_id: str, config: dict) -> None:
    conn = open_db()
    try:
        conn.execute(
            "UPDATE discuss_sessions SET config_json=?, updated_at=datetime('now') WHERE id=?",
            (json.dumps(config, ensure_ascii=False), discuss_id),
        )
        conn.commit()
    finally:
        conn.close()


def delete_session(discuss_id: str) -> None:
    conn = open_db()
    try:
        conn.execute("DELETE FROM discuss_sessions WHERE id = ?", (discuss_id,))
        conn.commit()
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Отправка сообщения
# ---------------------------------------------------------------------------


def _load_project_brief(project_id: str) -> dict | None:
    if not project_id:
        return None
    import frontmatter
    path = ROOT / "content" / "projects" / f"{project_id}.md"
    if not path.exists():
        return None
    post = frontmatter.load(path)
    return post.metadata


def _load_course_brief(course_id: str, *,
                        my_role: str | None = None) -> tuple[dict | None, list[dict]]:
    """Грузит курс + события. Для student-роли фильтрует timestamp ≤ now
    (не спойлерим будущие лекции — F3-G4 Participant Lens)."""
    if not course_id:
        return None, []
    conn = open_db()
    try:
        course = fetch_one(conn, "SELECT * FROM courses WHERE id = ?", (course_id,))
        if my_role == "student":
            events = fetch_all(
                conn,
                """SELECT id, kind, title, happened_at, body_md FROM course_events
                   WHERE course_id = ?
                     AND (happened_at IS NULL OR happened_at <= datetime('now'))
                   ORDER BY happened_at DESC LIMIT 15""",
                (course_id,),
            )
        else:
            events = fetch_all(
                conn,
                "SELECT id, kind, title, happened_at, body_md FROM course_events "
                "WHERE course_id = ? ORDER BY happened_at DESC LIMIT 15",
                (course_id,),
            )
        return course, events
    finally:
        conn.close()


def send_message(discuss_id: str, user_text: str) -> dict:
    if not user_text.strip():
        raise ValueError("пусто")
    sess = get_session(discuss_id)
    if not sess:
        raise ValueError("session not found")
    config = sess["config"] or DEFAULT_CONFIG

    project = _load_project_brief(sess.get("project_id"))
    # Узнаём роль юзера в курсе ДО загрузки событий (для timestamp-фильтра)
    my_role = None
    if sess.get("course_id") and sess.get("session_id"):
        conn = open_db()
        try:
            row = conn.execute(
                "SELECT role FROM course_role_bindings WHERE course_id=? AND session_id=?",
                (sess["course_id"], sess["session_id"]),
            ).fetchone()
            my_role = row[0] if row else None
        finally:
            conn.close()
    course, course_events = _load_course_brief(sess.get("course_id"), my_role=my_role)

    # Динамика проекта по курсу (если есть и проект, и курс)
    project_dynamics = None
    if course and sess.get("project_id"):
        try:
            from . import course_packs as cp
            project_dynamics = cp.project_dynamics_across_course(
                course["id"], sess["project_id"])
        except Exception:
            pass

    system_prompt = _build_system_prompt(
        config, project=project, course=course, course_events=course_events,
        my_role_in_course=my_role, user_session_id=sess.get("session_id"),
        project_dynamics=project_dynamics,
    )
    rag_context = _build_rag_context(user_text, config)

    # Сохраняем сообщение юзера
    conn = open_db()
    try:
        conn.execute(
            "INSERT INTO discuss_messages (discuss_id, sender, content, config_snapshot) VALUES (?, 'user', ?, ?)",
            (discuss_id, user_text[:8000], json.dumps(config, ensure_ascii=False)),
        )
        # История диалога
        history = fetch_all(
            conn,
            "SELECT sender, content FROM discuss_messages WHERE discuss_id=? "
            "AND sender IN ('user','kaiyona') ORDER BY id",
            (discuss_id,),
        )
        # авто-title из первого сообщения
        if not sess.get("title"):
            title = user_text.strip()[:80]
            conn.execute("UPDATE discuss_sessions SET title=? WHERE id=?", (title, discuss_id))
        conn.commit()
    finally:
        conn.close()

    # Собираем сообщения для LLM
    messages: list[dict[str, str]] = [
        {"role": "system", "content": system_prompt + (("\n\n" + rag_context) if rag_context else "")},
    ]
    for m in history:
        messages.append({
            "role": "user" if m["sender"] == "user" else "assistant",
            "content": m["content"],
        })

    # Вызов
    llm = get_llm()
    model_role = config.get("model_role", "fast")
    started = time.time()
    try:
        if model_role == "search":
            res = llm.chat_search(messages)
            reply = res["text"]
        else:
            method = llm.chat_deep if model_role == "deep" else llm.chat_fast
            reply = method(messages)
    except Exception as exc:
        raise RuntimeError(f"LLM error: {exc}")
    duration_ms = int((time.time() - started) * 1000)

    from .llm import LlmClient
    usage = LlmClient.last_usage() or {}
    tokens = usage.get("total_tokens")

    conn = open_db()
    try:
        conn.execute(
            """INSERT INTO discuss_messages
               (discuss_id, sender, content, config_snapshot, duration_ms, tokens)
               VALUES (?, 'kaiyona', ?, ?, ?, ?)""",
            (discuss_id, reply[:16000], json.dumps(config, ensure_ascii=False),
             duration_ms, tokens),
        )
        conn.execute("UPDATE discuss_sessions SET updated_at=datetime('now') WHERE id=?",
                     (discuss_id,))
        conn.commit()
    finally:
        conn.close()

    return {"reply": reply, "duration_ms": duration_ms, "tokens": tokens,
            "model_role": model_role}
