"""2D-проекция кейсов по любой паре осей.

Главная страница «карта корпуса» строится так: пользователь выбирает X и Y из
osей taxonomy/axes.yaml, бэк возвращает точки (case_id, x, y, label).
Точки с не-числовыми значениями (categorical) превращаются в индексы по
порядку появления значений (jitter добавляется на фронте).
"""

from __future__ import annotations

from typing import Any

from .db import fetch_all, open_db
from .schemas import _AXIS_DEFS


def _value_for_projection(axis_id: str, value_num: float | None, value_text: str | None,
                          enum_map: dict[str, int]) -> float | None:
    spec = _AXIS_DEFS.get(axis_id)
    if not spec:
        return None
    kind = spec["kind"]
    if kind in ("ordinal", "bool"):
        return value_num
    if kind == "categorical":
        if value_text is None:
            return None
        if value_text not in enum_map:
            enum_map[value_text] = len(enum_map)
        return float(enum_map[value_text])
    return None


def projection(x_axis: str, y_axis: str, entity_kind: str = "case") -> dict[str, Any]:
    if x_axis not in _AXIS_DEFS:
        raise ValueError(f"unknown axis '{x_axis}'")
    if y_axis not in _AXIS_DEFS:
        raise ValueError(f"unknown axis '{y_axis}'")

    conn = open_db()
    try:
        rows = fetch_all(
            conn,
            """
            SELECT entity_id, axis_id, value_num, value_text
            FROM axis_values WHERE entity_kind = ? AND axis_id IN (?, ?)
            """,
            (entity_kind, x_axis, y_axis),
        )
        per_entity: dict[str, dict[str, tuple]] = {}
        for r in rows:
            per_entity.setdefault(r["entity_id"], {})[r["axis_id"]] = (
                r["value_num"], r["value_text"]
            )

        meta_table = "cases" if entity_kind == "case" else "projects"
        meta = {
            r["id"]: r for r in fetch_all(
                conn,
                f"SELECT id, name, org_name, country, pattern, agentivity FROM {meta_table}",
            )
        }

        x_enum: dict[str, int] = {}
        y_enum: dict[str, int] = {}
        points: list[dict[str, Any]] = []
        for eid, axes in per_entity.items():
            if x_axis not in axes or y_axis not in axes:
                continue
            x_val = _value_for_projection(x_axis, *axes[x_axis], x_enum)
            y_val = _value_for_projection(y_axis, *axes[y_axis], y_enum)
            if x_val is None or y_val is None:
                continue
            m = meta.get(eid, {})
            points.append({
                "id": eid,
                "x": x_val,
                "y": y_val,
                "name": m.get("name", eid),
                "org_name": m.get("org_name"),
                "country": m.get("country"),
                "pattern": m.get("pattern"),
                "agentivity": m.get("agentivity"),
            })

        return {
            "x_axis": x_axis,
            "y_axis": y_axis,
            "x_spec": _AXIS_DEFS[x_axis],
            "y_spec": _AXIS_DEFS[y_axis],
            "x_enum": x_enum,
            "y_enum": y_enum,
            "points": points,
            "count": len(points),
        }
    finally:
        conn.close()


def list_axes() -> list[dict[str, Any]]:
    """Список осей для UI-селектора, с группировкой по семействам."""
    out = []
    for axis_id, spec in _AXIS_DEFS.items():
        out.append({
            "id": axis_id,
            "family": spec.get("family"),
            "kind": spec.get("kind"),
            "scale": spec.get("scale"),
            "direction": spec.get("direction"),
            "hint": spec.get("hint"),
        })
    return out
