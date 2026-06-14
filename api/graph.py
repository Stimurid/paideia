"""Эмпирический граф: что поддерживает/опровергает теоретическую сущность."""

from __future__ import annotations

from typing import Any

from .db import fetch_all, open_db


def get_type(type_id: str) -> dict[str, Any] | None:
    conn = open_db()
    try:
        row = fetch_all(conn, "SELECT * FROM types WHERE id = ?", (type_id,))
        if not row:
            return None
        out = row[0]
        out["evidence"] = _evidence_for("type", type_id)
        return out
    finally:
        conn.close()


def get_hypothesis(h_id: str) -> dict[str, Any] | None:
    conn = open_db()
    try:
        row = fetch_all(conn, "SELECT * FROM hypotheses WHERE id = ?", (h_id,))
        if not row:
            return None
        out = row[0]
        out["evidence"] = _evidence_for("hypothesis", h_id)
        return out
    finally:
        conn.close()


def get_tension(t_id: str) -> dict[str, Any] | None:
    conn = open_db()
    try:
        row = fetch_all(conn, "SELECT * FROM tensions WHERE id = ?", (t_id,))
        if not row:
            return None
        out = row[0]
        out["evidence"] = _evidence_for("tension", t_id)
        return out
    finally:
        conn.close()


def get_mode(m_id: str) -> dict[str, Any] | None:
    conn = open_db()
    try:
        row = fetch_all(conn, "SELECT * FROM modes WHERE id = ?", (m_id,))
        if not row:
            return None
        out = row[0]
        out["evidence"] = _evidence_for("mode", m_id)
        return out
    finally:
        conn.close()


def get_counter_signal(cs_id: str) -> dict[str, Any] | None:
    conn = open_db()
    try:
        row = fetch_all(conn, "SELECT * FROM counter_signals WHERE id = ?", (cs_id,))
        if not row:
            return None
        out = row[0]
        out["evidence"] = _evidence_for("counter-signal", cs_id)
        return out
    finally:
        conn.close()


def _evidence_for(target_kind: str, target_id: str) -> dict[str, list[dict[str, Any]]]:
    """Сгруппировать кейсы, ссылающиеся на сущность, по типу отношения."""
    conn = open_db()
    try:
        rows = fetch_all(
            conn,
            """
            SELECT el.relation, el.confidence, el.note,
                   c.id AS case_id, c.name, c.org_name, c.country,
                   c.pattern, c.agentivity
            FROM evidence_links el
            JOIN cases c ON c.id = el.case_id
            WHERE el.target_kind = ? AND el.target_id = ?
            ORDER BY el.relation, c.name
            """,
            (target_kind, target_id),
        )
        grouped: dict[str, list[dict[str, Any]]] = {}
        for r in rows:
            grouped.setdefault(r["relation"], []).append(r)
        return grouped
    finally:
        conn.close()


def list_all_theory() -> dict[str, list[dict[str, Any]]]:
    """Сводка всех теоретических сущностей для главной страницы."""
    conn = open_db()
    try:
        return {
            "types": fetch_all(conn, "SELECT id, name FROM types ORDER BY id"),
            "hypotheses": fetch_all(conn, "SELECT id, name, status_current FROM hypotheses ORDER BY id"),
            "tensions": fetch_all(conn, "SELECT id, name FROM tensions ORDER BY name"),
            "modes": fetch_all(conn, "SELECT id, name FROM modes ORDER BY name"),
            "counter_signals": fetch_all(conn, "SELECT id, name FROM counter_signals ORDER BY name"),
        }
    finally:
        conn.close()
