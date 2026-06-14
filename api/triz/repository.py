"""Репозиторий TRIZ-engine — чтение/запись SystemModel/Branch/AgentRun из БД."""

from __future__ import annotations

import json
import sqlite3
from typing import Any

from ..db import open_db
from .system_model import EducationalSystemModel


def get_system_model(project_id: str) -> EducationalSystemModel | None:
    """Текущая (последняя) SystemModel проекта."""
    conn = open_db()
    try:
        row = conn.execute(
            """
            SELECT full_json FROM system_models
            WHERE project_id = ?
            ORDER BY updated_at DESC LIMIT 1
            """,
            (project_id,),
        ).fetchone()
        if not row:
            return None
        data = json.loads(row["full_json"])
        return EducationalSystemModel.model_validate(data)
    finally:
        conn.close()


def list_system_models(project_id: str) -> list[dict[str, Any]]:
    """Все варианты SystemModel проекта (для view вариантов)."""
    conn = open_db()
    try:
        rows = conn.execute(
            """
            SELECT id, title, kind, function, maturity, source,
                   invention_level, parent_variant_id, updated_at
            FROM system_models
            WHERE project_id = ?
            ORDER BY updated_at DESC
            """,
            (project_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def save_system_model(model: EducationalSystemModel) -> None:
    """Insert/replace SystemModel в БД."""
    from datetime import datetime
    conn = open_db()
    try:
        now = datetime.utcnow().isoformat(timespec="seconds")
        ce = model.constraint_envelope
        conn.execute(
            """
            INSERT OR REPLACE INTO system_models
              (id, project_id, title, kind, function, maturity, parent_variant_id,
               source, invention_level, full_json, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    COALESCE((SELECT created_at FROM system_models WHERE id=?), ?),
                    ?)
            """,
            (
                model.id, model.project_id, model.title, model.kind,
                model.function, model.maturity, model.parent_variant_id,
                model.source, ce.invention_level,
                model.model_dump_json(),
                model.id, now,
                now,
            ),
        )
        conn.commit()
    finally:
        conn.close()
