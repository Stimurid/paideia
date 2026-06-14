"""Подбор аналогов под ситуацию пользователя.

Считаем расстояние в пространстве осей:
- для ordinal/bool — нормированная евклидова разница;
- для categorical — Жаккар (одинаково/нет);
- веса по умолчанию 1 на каждую заданную ось.

Без векторных эмбеддингов работает на чистых осях; это даёт детерминированный
результат и работает локально без сетевых запросов.
"""

from __future__ import annotations

from typing import Any

from .db import fetch_all, open_db
from .schemas import _AXIS_DEFS


def _axis_distance(axis_id: str, query_value: Any, case_value: Any) -> float | None:
    """Расстояние 0..1 по одной оси, либо None если значения нет в кейсе."""
    if case_value is None or query_value is None:
        return None
    spec = _AXIS_DEFS.get(axis_id)
    if not spec:
        return None
    kind = spec["kind"]
    if kind == "ordinal":
        lo, hi = spec["scale"]
        span = hi - lo if hi > lo else 1
        return abs(float(query_value) - float(case_value)) / span
    if kind == "bool":
        return 0.0 if bool(query_value) == bool(case_value) else 1.0
    if kind == "categorical":
        return 0.0 if str(query_value) == str(case_value) else 1.0
    return None


def match_to_cases(query_axes: dict[str, Any], top_n: int = 10) -> list[dict[str, Any]]:
    """Найти top_n кейсов, ближайших к query_axes."""
    conn = open_db()
    try:
        # все осевые значения по всем кейсам
        rows = fetch_all(
            conn,
            """
            SELECT entity_id AS case_id, axis_id, value_num, value_text
            FROM axis_values WHERE entity_kind='case'
            """,
        )
        per_case: dict[str, dict[str, Any]] = {}
        for r in rows:
            v = r["value_text"] if r["value_text"] is not None else r["value_num"]
            per_case.setdefault(r["case_id"], {})[r["axis_id"]] = v

        scored: list[tuple[str, float, int, list[str]]] = []
        for case_id, axes in per_case.items():
            dists: list[float] = []
            matched: list[str] = []
            for axis_id, qv in query_axes.items():
                if axis_id not in axes:
                    continue
                d = _axis_distance(axis_id, qv, axes[axis_id])
                if d is None:
                    continue
                dists.append(d)
                if d < 0.2:
                    matched.append(axis_id)
            if not dists:
                continue
            avg = sum(dists) / len(dists)
            scored.append((case_id, avg, len(dists), matched))

        # Сортировка: сначала по числу заматчившихся осей DESC, потом по dist ASC
        scored.sort(key=lambda t: (-t[2], t[1]))
        top = scored[:top_n]

        case_meta = {r["id"]: r for r in fetch_all(
            conn,
            "SELECT id, name, org_name, country, pattern, agentivity FROM cases",
        )}
        return [
            {
                **case_meta[c[0]],
                "distance": round(c[1], 3),
                "matched_axes_count": c[2],
                "matched_axes": c[3],
            }
            for c in top if c[0] in case_meta
        ]
    finally:
        conn.close()


def match_project_to_cases(project_id: str, top_n: int = 10) -> list[dict[str, Any]]:
    """Подобрать аналоги для конкретного проекта по его осям."""
    conn = open_db()
    try:
        rows = fetch_all(
            conn,
            """
            SELECT axis_id, value_num, value_text FROM axis_values
            WHERE entity_kind='project' AND entity_id=?
            """,
            (project_id,),
        )
        query = {
            r["axis_id"]: r["value_text"] if r["value_text"] is not None else r["value_num"]
            for r in rows
        }
        return match_to_cases(query, top_n=top_n)
    finally:
        conn.close()
