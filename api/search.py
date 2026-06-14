"""Поиск + фасетные фильтры по кейсам.

GET /api/search?q=tutor&country=US&pattern=B&agentivity_min=3&agentivity_max=5
                &orchestration=NET&transformation_mode=experimental-cell&limit=50

Логика:
- если q пустой → SELECT по фильтрам;
- если q есть → JOIN с cases_fts MATCH q;
- сортировка по релевантности (если есть q) или по agentivity DESC.
"""

from __future__ import annotations

from typing import Any

from .db import fetch_all, open_db


def search_cases(
    q: str | None = None,
    country: str | None = None,
    pattern: str | None = None,
    agentivity_min: int | None = None,
    agentivity_max: int | None = None,
    orchestration: str | None = None,
    pedagogy: str | None = None,
    control: str | None = None,
    org_type: str | None = None,
    lifecycle_stage: str | None = None,
    transformation_mode: str | None = None,
    verified_only: bool = False,
    limit: int = 50,
) -> list[dict[str, Any]]:
    conn = open_db()
    try:
        params: list[Any] = []
        where: list[str] = []
        joins: list[str] = []
        select_extra = ""
        order = "ORDER BY COALESCE(c.agentivity, 0) DESC, c.name"

        if q:
            joins.append("JOIN cases_fts ON cases_fts.case_id = c.id")
            where.append("cases_fts MATCH ?")
            params.append(q)
            select_extra = ", bm25(cases_fts) AS rank"
            order = "ORDER BY rank"

        if country:
            where.append("c.country = ?")
            params.append(country)
        if pattern:
            where.append("c.pattern = ?")
            params.append(pattern)
        if agentivity_min is not None:
            where.append("c.agentivity >= ?")
            params.append(agentivity_min)
        if agentivity_max is not None:
            where.append("c.agentivity <= ?")
            params.append(agentivity_max)
        if orchestration:
            where.append("c.orchestration = ?")
            params.append(orchestration)
        if pedagogy:
            where.append("c.pedagogy = ?")
            params.append(pedagogy)
        if control:
            where.append("c.control = ?")
            params.append(control)
        if org_type:
            where.append("c.org_type LIKE ?")
            params.append(f"%{org_type}%")
        if lifecycle_stage:
            where.append("c.lifecycle_stage = ?")
            params.append(lifecycle_stage)
        if transformation_mode:
            where.append("c.transformation_mode = ?")
            params.append(transformation_mode)
        if verified_only:
            where.append("c.verified = 1")

        sql = f"""
            SELECT c.id, c.name, c.org_name, c.org_type, c.country,
                   c.pattern, c.agentivity, c.orchestration, c.pedagogy,
                   c.control, c.transformation_mode, c.lifecycle_stage, c.verified
                   {select_extra}
            FROM cases c
            {' '.join(joins)}
            {'WHERE ' + ' AND '.join(where) if where else ''}
            {order}
            LIMIT ?
        """
        params.append(limit)
        return fetch_all(conn, sql, tuple(params))
    finally:
        conn.close()


def get_case(case_id: str) -> dict[str, Any] | None:
    conn = open_db()
    try:
        case = fetch_all(conn, "SELECT * FROM cases WHERE id = ?", (case_id,))
        if not case:
            return None
        case = case[0]
        case["sources"] = fetch_all(
            conn,
            "SELECT url, source_type, accessed_at FROM sources WHERE owner_kind='case' AND owner_id=?",
            (case_id,),
        )
        case["links"] = fetch_all(
            conn,
            "SELECT target_kind, target_id, relation, confidence, note FROM evidence_links WHERE case_id=?",
            (case_id,),
        )
        case["axes"] = fetch_all(
            conn,
            """
            SELECT axis_id, value_num, value_text, family
            FROM axis_values WHERE entity_kind='case' AND entity_id=?
            ORDER BY family, axis_id
            """,
            (case_id,),
        )
        return case
    finally:
        conn.close()


def list_facet_values() -> dict[str, list[str]]:
    """Какие значения фасетов реально встречаются в корпусе — для UI-селектов."""
    conn = open_db()
    try:
        return {
            "country": [r["v"] for r in fetch_all(conn, "SELECT DISTINCT country AS v FROM cases ORDER BY country")],
            "pattern": [r["v"] for r in fetch_all(conn, "SELECT DISTINCT pattern AS v FROM cases WHERE pattern IS NOT NULL ORDER BY pattern")],
            "orchestration": [r["v"] for r in fetch_all(conn, "SELECT DISTINCT orchestration AS v FROM cases WHERE orchestration IS NOT NULL ORDER BY orchestration")],
            "pedagogy": [r["v"] for r in fetch_all(conn, "SELECT DISTINCT pedagogy AS v FROM cases WHERE pedagogy IS NOT NULL ORDER BY pedagogy")],
            "control": [r["v"] for r in fetch_all(conn, "SELECT DISTINCT control AS v FROM cases WHERE control IS NOT NULL ORDER BY control")],
            "lifecycle_stage": [r["v"] for r in fetch_all(conn, "SELECT DISTINCT lifecycle_stage AS v FROM cases ORDER BY lifecycle_stage")],
            "transformation_mode": [r["v"] for r in fetch_all(conn, "SELECT DISTINCT transformation_mode AS v FROM cases WHERE transformation_mode IS NOT NULL ORDER BY transformation_mode")],
        }
    finally:
        conn.close()
