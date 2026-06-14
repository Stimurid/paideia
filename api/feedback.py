"""Feedback Acceptor — приём пользовательских соображений с LLM-уточнением.

Flow:
    1. start_thread(text, page) → создаёт thread, прогон LLM:
        - если действие "save" → сохраняем структуру + возвращаем thanks
        - если "clarify" → возвращаем вопрос, статус 'clarifying'
    2. reply(thread_id, text) → повторный прогон с историей диалога
"""

from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any

from .agent import _extract_json
from .db import open_db, fetch_all, fetch_one
from .llm import get_llm

ROOT = Path(__file__).resolve().parent.parent

MAX_CLARIFICATIONS = 2  # больше уточнений не задаём, сохраняем что есть


def _load_prompt() -> str:
    return (ROOT / "prompts" / "feedback_acceptor.md").read_text(encoding="utf-8")


def _llm_step(thread: dict, history: list[dict]) -> dict:
    """Один вызов LLM-приёмщика. Возвращает parsed JSON."""
    system_prompt = _load_prompt()
    # Подставим page-context в шаблон
    system_prompt = system_prompt.replace("{page_path}", thread.get("page_path") or "?")
    system_prompt = system_prompt.replace("{page_context}", thread.get("page_context") or "?")
    system_prompt = system_prompt.replace("{user_role}", thread.get("user_role") or "?")

    convo: list[dict[str, str]] = [{"role": "system", "content": system_prompt + "\n\nВыведи только JSON."}]
    for m in history:
        convo.append({
            "role": "user" if m["sender"] == "user" else "assistant",
            "content": m["content"],
        })

    llm = get_llm()
    raw = llm.chat_fast(convo)
    parsed = _extract_json(raw)
    if not parsed:
        # фоллбек — сохраняем как «прочее»
        return {
            "action": "save", "category": "прочее", "severity": "low",
            "summary": (history[-1]["content"] if history else "")[:200],
            "tags": [], "thanks": "Записал.",
        }
    return parsed


def _count_clarifications(thread_id: str) -> int:
    conn = open_db()
    try:
        return conn.execute(
            "SELECT COUNT(*) FROM feedback_messages "
            "WHERE thread_id = ? AND sender = 'llm'",
            (thread_id,),
        ).fetchone()[0] or 0
    finally:
        conn.close()


def start_thread(*, text: str, session_id: str | None,
                 user_role: str | None, page_path: str,
                 page_context: str | None) -> dict:
    text = (text or "").strip()
    if len(text) < 3:
        raise ValueError("слишком короткий текст")

    thread_id = "fbk-" + uuid.uuid4().hex[:10]
    conn = open_db()
    try:
        conn.execute(
            """INSERT INTO feedback_threads
               (id, session_id, user_role, page_path, page_context, status)
               VALUES (?, ?, ?, ?, ?, 'open')""",
            (thread_id, session_id, user_role, page_path[:200], (page_context or "")[:200]),
        )
        conn.execute(
            "INSERT INTO feedback_messages (thread_id, sender, content) VALUES (?, 'user', ?)",
            (thread_id, text[:8000]),
        )
        conn.commit()
    finally:
        conn.close()

    return _continue_thread(thread_id)


def reply(*, thread_id: str, text: str) -> dict:
    text = (text or "").strip()
    if len(text) < 1:
        raise ValueError("пусто")
    conn = open_db()
    try:
        existing = fetch_one(
            conn, "SELECT status FROM feedback_threads WHERE id = ?", (thread_id,)
        )
        if not existing:
            raise ValueError("thread not found")
        if existing.get("status") in ("saved", "dismissed"):
            raise ValueError("thread closed")
        conn.execute(
            "INSERT INTO feedback_messages (thread_id, sender, content) VALUES (?, 'user', ?)",
            (thread_id, text[:8000]),
        )
        conn.execute(
            "UPDATE feedback_threads SET updated_at = datetime('now') WHERE id = ?",
            (thread_id,),
        )
        conn.commit()
    finally:
        conn.close()
    return _continue_thread(thread_id)


def _continue_thread(thread_id: str) -> dict:
    conn = open_db()
    try:
        thread = fetch_one(
            conn, "SELECT * FROM feedback_threads WHERE id = ?", (thread_id,)
        )
        history = fetch_all(
            conn,
            "SELECT sender, content FROM feedback_messages WHERE thread_id = ? ORDER BY id",
            (thread_id,),
        )
    finally:
        conn.close()
    if not thread:
        raise ValueError("thread vanished")

    parsed = _llm_step(thread, history)

    # Принудительный save после MAX_CLARIFICATIONS уточнений
    forced = False
    if parsed.get("action") == "clarify" and _count_clarifications(thread_id) >= MAX_CLARIFICATIONS:
        parsed = {
            "action": "save", "category": parsed.get("category") or "прочее",
            "severity": "low",
            "summary": history[0]["content"][:200] if history else "",
            "tags": [], "thanks": "Окей, записал то что есть.",
        }
        forced = True

    action = parsed.get("action")
    conn = open_db()
    try:
        if action == "clarify":
            question = (parsed.get("question") or "").strip() or "Можешь уточнить?"
            conn.execute(
                "INSERT INTO feedback_messages (thread_id, sender, content) VALUES (?, 'llm', ?)",
                (thread_id, question),
            )
            conn.execute(
                "UPDATE feedback_threads SET status='clarifying', updated_at=datetime('now') WHERE id=?",
                (thread_id,),
            )
            conn.commit()
            return {
                "thread_id": thread_id,
                "status": "clarifying",
                "llm_message": question,
                "forced": forced,
            }
        else:
            # save
            category = (parsed.get("category") or "прочее")[:40]
            severity = (parsed.get("severity") or "low")[:20]
            summary = (parsed.get("summary") or "")[:500]
            tags = parsed.get("tags") or []
            thanks = (parsed.get("thanks") or "Спасибо, записал.")[:500]
            conn.execute(
                "INSERT INTO feedback_messages (thread_id, sender, content) VALUES (?, 'llm', ?)",
                (thread_id, thanks),
            )
            conn.execute(
                """UPDATE feedback_threads SET status='saved',
                   category=?, severity=?, summary=?, tags_json=?,
                   updated_at=datetime('now') WHERE id=?""",
                (category, severity, summary, json.dumps(tags, ensure_ascii=False), thread_id),
            )
            conn.commit()
            return {
                "thread_id": thread_id,
                "status": "saved",
                "category": category,
                "severity": severity,
                "summary": summary,
                "tags": tags,
                "llm_message": thanks,
            }
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Viewer + export
# ---------------------------------------------------------------------------


def list_feedback(status: str | None = None, category: str | None = None,
                  limit: int = 500) -> list[dict]:
    conn = open_db()
    try:
        wh = []
        params: list[Any] = []
        if status:
            wh.append("status = ?"); params.append(status)
        if category:
            wh.append("category = ?"); params.append(category)
        where = (" WHERE " + " AND ".join(wh)) if wh else ""
        rows = fetch_all(
            conn,
            f"""SELECT id, session_id, user_role, page_path, page_context, status,
                       category, severity, summary, tags_json, created_at, updated_at
                FROM feedback_threads {where}
                ORDER BY created_at DESC LIMIT ?""",
            tuple(params) + (limit,),
        )
        for r in rows:
            r["tags"] = json.loads(r.get("tags_json") or "[]")
        return rows
    finally:
        conn.close()


def get_thread(thread_id: str) -> dict | None:
    conn = open_db()
    try:
        t = fetch_one(
            conn, "SELECT * FROM feedback_threads WHERE id = ?", (thread_id,)
        )
        if not t:
            return None
        t["tags"] = json.loads(t.get("tags_json") or "[]")
        t["messages"] = fetch_all(
            conn,
            "SELECT sender, content, created_at FROM feedback_messages WHERE thread_id = ? ORDER BY id",
            (thread_id,),
        )
        return t
    finally:
        conn.close()


def export_markdown() -> str:
    """Все треды в md-формате — для выгрузки в файл."""
    threads = list_feedback(limit=10000)
    lines = [
        "# Paideia · feedback dump",
        f"\nЭкспорт {time.strftime('%Y-%m-%d %H:%M:%S')}. Всего тредов: {len(threads)}.\n",
    ]
    # счётчики
    by_status: dict[str, int] = {}
    by_cat: dict[str, int] = {}
    by_sev: dict[str, int] = {}
    for t in threads:
        by_status[t.get("status") or "?"] = by_status.get(t.get("status") or "?", 0) + 1
        by_cat[t.get("category") or "?"] = by_cat.get(t.get("category") or "?", 0) + 1
        by_sev[t.get("severity") or "?"] = by_sev.get(t.get("severity") or "?", 0) + 1
    lines.append("## Сводка\n")
    lines.append(f"- По статусу: {', '.join(f'{k}={v}' for k,v in by_status.items())}")
    lines.append(f"- По категориям: {', '.join(f'{k}={v}' for k,v in by_cat.items())}")
    lines.append(f"- По severity: {', '.join(f'{k}={v}' for k,v in by_sev.items())}")
    lines.append("\n---\n")

    for t in threads:
        thread = get_thread(t["id"])
        if not thread:
            continue
        lines.append(f"## {thread['summary'] or '(без сводки)'}")
        lines.append("")
        lines.append(f"- **id:** `{thread['id']}`")
        lines.append(f"- **создано:** {thread['created_at']}")
        lines.append(f"- **статус:** {thread.get('status') or '?'}")
        lines.append(f"- **категория:** {thread.get('category') or '?'}")
        lines.append(f"- **severity:** {thread.get('severity') or '?'}")
        lines.append(f"- **страница:** `{thread.get('page_path') or '?'}` ({thread.get('page_context') or ''})")
        lines.append(f"- **роль:** {thread.get('user_role') or '?'}")
        if thread.get("tags"):
            lines.append(f"- **теги:** {', '.join(thread['tags'])}")
        lines.append("\n### Диалог\n")
        for m in thread.get("messages", []):
            who = "🙋 юзер" if m["sender"] == "user" else "🤖 acceptor"
            lines.append(f"**{who}** _{m['created_at'][:16]}_  ")
            lines.append(m["content"])
            lines.append("")
        lines.append("\n---\n")
    return "\n".join(lines)


def stats() -> dict:
    conn = open_db()
    try:
        total = conn.execute("SELECT COUNT(*) FROM feedback_threads").fetchone()[0]
        by_status = fetch_all(
            conn, "SELECT status, COUNT(*) AS n FROM feedback_threads GROUP BY status"
        )
        return {
            "total": total,
            "by_status": {r["status"]: r["n"] for r in by_status},
        }
    finally:
        conn.close()
