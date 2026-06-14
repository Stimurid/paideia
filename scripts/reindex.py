"""Пересборка SQLite-индекса из content/*.md.

Запуск:
    python -m scripts.reindex

Что делает:
1. Дропает все runtime-таблицы и пересоздаёт по db/schema.sql.
2. Читает content/{cases,projects,types,hypotheses,tensions,modes,counter-signals}/*.md.
3. Валидирует фронтматтер через api/schemas.py (как тесты).
4. Заполняет основные таблицы, axis_values, evidence_links, FTS5.
5. Если в .env есть LLM_PRIMARY_API_KEY — считает эмбеддинги и кладёт в vec0.
   Иначе — пропускает (поиск будет работать на FTS+фасетах без векторов).
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import frontmatter
import typer

from api.config import get_settings
from api.db import open_db
from api.schemas import (
    CaseFrontmatter,
    CounterSignalFrontmatter,
    HypothesisFrontmatter,
    ModeFrontmatter,
    ProjectFrontmatter,
    TensionFrontmatter,
    TypeFrontmatter,
    _AXIS_DEFS,
)

app = typer.Typer(no_args_is_help=False, add_completion=False)
ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"

_SCHEMAS = {
    "cases": CaseFrontmatter,
    "projects": ProjectFrontmatter,
    "types": TypeFrontmatter,
    "hypotheses": HypothesisFrontmatter,
    "tensions": TensionFrontmatter,
    "modes": ModeFrontmatter,
    "counter-signals": CounterSignalFrontmatter,
}

# Сущности без Pydantic-схемы — читаются как dict, сохраняются в БД с ключевыми
# полями + полный frontmatter в json. Это позволяет UI делать фильтрацию/группировку
# без переусложнения, не привязываясь к строгой схеме на этом этапе.
_LOOSE_KINDS = ["agents", "stakeholders"]


def _wipe(conn: sqlite3.Connection) -> None:
    for tbl in [
        "evidence_links", "axis_values", "wave_snapshots", "waves",
        "sources", "project_analogues",
        "cases_fts", "projects_fts", "theory_fts",
        "cases_vec", "theory_vec",
        "cases", "projects", "types", "hypotheses", "tensions", "modes", "counter_signals",
    ]:
        try:
            conn.execute(f"DROP TABLE IF EXISTS {tbl}")
        except sqlite3.OperationalError:
            pass
    conn.commit()


def _split_org_type(value: str) -> tuple[str, str]:
    return value, value.split("/")[0]


def _norm_economy(value: str | None) -> str | None:
    return value


def _index_case(conn: sqlite3.Connection, fm: CaseFrontmatter, path: Path, body: str, raw: dict) -> None:
    conn.execute(
        """
        INSERT INTO cases (
            id, name, org_name, org_type, country,
            pattern, agentivity, orchestration, pedagogy, control, economy,
            transformation_mode, lifecycle_stage, first_seen, verified,
            file_path, body_md, frontmatter_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            fm.id, fm.name,
            fm.organization.name, fm.organization.type, fm.organization.country,
            fm.ai.pattern, fm.ai.agentivity,
            fm.facets.orchestration, fm.facets.pedagogy, fm.facets.control, fm.facets.economy,
            fm.transformation_mode, fm.lifecycle.stage, fm.lifecycle.first_seen,
            1 if fm.verified else 0,
            str(path.relative_to(ROOT)).replace("\\", "/"),
            body,
            json.dumps(raw, ensure_ascii=False),
        ),
    )
    conn.execute(
        "INSERT INTO cases_fts (case_id, name, org_name, body) VALUES (?, ?, ?, ?)",
        (fm.id, fm.name, fm.organization.name, body),
    )
    for src in fm.sources:
        conn.execute(
            "INSERT INTO sources (owner_kind, owner_id, url, source_type, accessed_at) VALUES (?, ?, ?, ?, ?)",
            ("case", fm.id, src.url, src.type, src.accessed),
        )
    for link in fm.links:
        conn.execute(
            """
            INSERT OR IGNORE INTO evidence_links
            (case_id, target_kind, target_id, relation, confidence, note)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (fm.id, link.kind, link.id, link.relation, link.confidence, link.note),
        )
    _index_axes(conn, "case", fm.id, fm.axes)


def _index_project(conn: sqlite3.Connection, fm: ProjectFrontmatter, path: Path, body: str, raw: dict) -> None:
    org = fm.organization
    ai = fm.ai
    conn.execute(
        """
        INSERT INTO projects (
            id, name, author, status,
            org_name, org_type, country,
            pattern, agentivity, orchestration, pedagogy, control, economy,
            transformation_mode, portfolio_slot,
            file_path, body_md, frontmatter_json, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            fm.id, fm.name, fm.author, fm.status,
            org.name if org else None, org.type if org else None, org.country if org else None,
            ai.pattern if ai else None, ai.agentivity if ai else None,
            fm.facets.orchestration, fm.facets.pedagogy, fm.facets.control, fm.facets.economy,
            fm.transformation_mode, fm.portfolio_slot,
            str(path.relative_to(ROOT)).replace("\\", "/"),
            body,
            json.dumps(raw, ensure_ascii=False),
            fm.created_at,
        ),
    )
    conn.execute(
        "INSERT INTO projects_fts (project_id, name, author, body) VALUES (?, ?, ?, ?)",
        (fm.id, fm.name, fm.author or "", body),
    )
    for analogue_id in fm.analogues:
        conn.execute(
            "INSERT OR IGNORE INTO project_analogues (project_id, case_id) VALUES (?, ?)",
            (fm.id, analogue_id),
        )
    _index_axes(conn, "project", fm.id, fm.axes)


def _index_axes(conn: sqlite3.Connection, kind: str, entity_id: str, axes: dict[str, object]) -> None:
    for axis_id, value in axes.items():
        spec = _AXIS_DEFS.get(axis_id, {})
        family = spec.get("family")
        if isinstance(value, bool):
            value_num, value_text = (1.0 if value else 0.0), None
        elif isinstance(value, (int, float)):
            value_num, value_text = float(value), None
        else:
            value_num, value_text = None, str(value)
        conn.execute(
            """
            INSERT OR REPLACE INTO axis_values
            (entity_kind, entity_id, axis_id, value_num, value_text, family)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (kind, entity_id, axis_id, value_num, value_text, family),
        )


def _index_type(conn: sqlite3.Connection, fm: TypeFrontmatter, path: Path, body: str) -> None:
    conn.execute(
        """
        INSERT INTO types (id, name, description, markers_json, file_path, body_md)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            fm.id, fm.name, fm.full_name or fm.name,
            json.dumps(fm.markers, ensure_ascii=False),
            str(path.relative_to(ROOT)).replace("\\", "/"),
            body,
        ),
    )
    conn.execute(
        "INSERT INTO theory_fts (entity_kind, entity_id, name, body) VALUES (?, ?, ?, ?)",
        ("type", fm.id, fm.name, body),
    )


def _index_hypothesis(conn: sqlite3.Connection, fm: HypothesisFrontmatter, path: Path, body: str) -> None:
    conn.execute(
        """
        INSERT INTO hypotheses
        (id, name, wave_introduced, status_current, status_history_json, markers_json, file_path, body_md)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            fm.id, fm.name, fm.wave_introduced, fm.status.current,
            json.dumps([h.model_dump() for h in fm.status.history], ensure_ascii=False),
            json.dumps(fm.markers, ensure_ascii=False),
            str(path.relative_to(ROOT)).replace("\\", "/"),
            body,
        ),
    )
    conn.execute(
        "INSERT INTO theory_fts (entity_kind, entity_id, name, body) VALUES (?, ?, ?, ?)",
        ("hypothesis", fm.id, fm.name, body),
    )


def _index_tension(conn: sqlite3.Connection, fm: TensionFrontmatter, path: Path, body: str) -> None:
    conn.execute(
        "INSERT INTO tensions (id, name, pole_a, pole_b, file_path, body_md) VALUES (?, ?, ?, ?, ?, ?)",
        (fm.id, fm.name, fm.pole_a, fm.pole_b, str(path.relative_to(ROOT)).replace("\\", "/"), body),
    )
    conn.execute(
        "INSERT INTO theory_fts (entity_kind, entity_id, name, body) VALUES (?, ?, ?, ?)",
        ("tension", fm.id, fm.name, body),
    )


def _index_mode(conn: sqlite3.Connection, fm: ModeFrontmatter, path: Path, body: str) -> None:
    conn.execute(
        "INSERT INTO modes (id, name, description, file_path, body_md) VALUES (?, ?, ?, ?, ?)",
        (fm.id, fm.name, "", str(path.relative_to(ROOT)).replace("\\", "/"), body),
    )
    conn.execute(
        "INSERT INTO theory_fts (entity_kind, entity_id, name, body) VALUES (?, ?, ?, ?)",
        ("mode", fm.id, fm.name, body),
    )


def _index_content_agent(conn: sqlite3.Connection, fm: dict, path: Path, body: str) -> None:
    """L1-агент из content/agents/L1/*.md — читается как dict."""
    conn.execute(
        """
        INSERT OR REPLACE INTO content_agents
          (agent_id, name, level, purpose, status,
           cooperates_with_json, conflicts_with_json,
           file_path, body_md, frontmatter_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            fm.get("agent_id") or path.stem,
            fm.get("name") or path.stem,
            fm.get("level", "L1"),
            fm.get("purpose", ""),
            fm.get("status", "draft"),
            json.dumps(fm.get("cooperates_with") or [], ensure_ascii=False),
            json.dumps(fm.get("conflicts_with") or [], ensure_ascii=False),
            str(path.relative_to(ROOT)).replace("\\", "/"),
            body,
            json.dumps(fm, ensure_ascii=False),
        ),
    )


def _index_stakeholder(conn: sqlite3.Connection, fm: dict, path: Path, body: str) -> None:
    """Стейкхолдер из content/stakeholders/*.md."""
    conn.execute(
        """
        INSERT OR REPLACE INTO stakeholders
          (stakeholder_id, name, kind, group_name, attack_style,
           typical_questions_json, interests_json, fears_json, levers_json,
           file_path, body_md, frontmatter_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            fm.get("stakeholder_id") or path.stem,
            fm.get("name") or path.stem,
            fm.get("kind"),
            fm.get("group"),
            fm.get("attack_style"),
            json.dumps(fm.get("typical_questions") or [], ensure_ascii=False),
            json.dumps(fm.get("interests") or [], ensure_ascii=False),
            json.dumps(fm.get("fears") or [], ensure_ascii=False),
            json.dumps(fm.get("levers") or [], ensure_ascii=False),
            str(path.relative_to(ROOT)).replace("\\", "/"),
            body,
            json.dumps(fm, ensure_ascii=False),
        ),
    )


def _index_counter_signal(conn: sqlite3.Connection, fm: CounterSignalFrontmatter, path: Path, body: str, raw: dict) -> None:
    conn.execute(
        """
        INSERT INTO counter_signals
        (id, name, org_name, target_hypothesis, wave_introduced, file_path, body_md, frontmatter_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            fm.id, fm.name, fm.org_name, fm.target_hypothesis, fm.wave_introduced,
            str(path.relative_to(ROOT)).replace("\\", "/"),
            body,
            json.dumps(raw, ensure_ascii=False),
        ),
    )
    conn.execute(
        "INSERT INTO theory_fts (entity_kind, entity_id, name, body) VALUES (?, ?, ?, ?)",
        ("counter-signal", fm.id, fm.name, body),
    )


@app.command()
def main() -> None:
    settings = get_settings()
    conn = open_db()
    _wipe(conn)
    schema = (ROOT / "db" / "schema.sql").read_text(encoding="utf-8")
    conn.executescript(schema)
    conn.commit()

    counts: dict[str, int] = {}
    for kind, schema_cls in _SCHEMAS.items():
        kind_dir = CONTENT / kind
        if not kind_dir.exists():
            continue
        for path in sorted(kind_dir.glob("*.md")):
            post = frontmatter.load(path)
            fm = schema_cls.model_validate(post.metadata)
            body = post.content
            raw = post.metadata
            if kind == "cases":
                _index_case(conn, fm, path, body, raw)
            elif kind == "projects":
                _index_project(conn, fm, path, body, raw)
            elif kind == "types":
                _index_type(conn, fm, path, body)
            elif kind == "hypotheses":
                _index_hypothesis(conn, fm, path, body)
            elif kind == "tensions":
                _index_tension(conn, fm, path, body)
            elif kind == "modes":
                _index_mode(conn, fm, path, body)
            elif kind == "counter-signals":
                _index_counter_signal(conn, fm, path, body, raw)
            counts[kind] = counts.get(kind, 0) + 1

    # Loose kinds: agents (рекурсивно по L0/L1/L2/L3), stakeholders
    for loose in _LOOSE_KINDS:
        kind_dir = CONTENT / loose
        if not kind_dir.exists():
            continue
        files = list(kind_dir.rglob("*.md")) if loose == "agents" else list(kind_dir.glob("*.md"))
        for path in sorted(files):
            if path.name in ("index.md", "_index.md", "_registry.md"):
                continue
            try:
                post = frontmatter.load(path)
                fm = post.metadata or {}
                body = post.content
                if loose == "agents":
                    _index_content_agent(conn, fm, path, body)
                elif loose == "stakeholders":
                    _index_stakeholder(conn, fm, path, body)
                counts[loose] = counts.get(loose, 0) + 1
            except Exception as exc:
                typer.echo(f"  skip {path.relative_to(ROOT)}: {exc}")

    conn.commit()
    typer.echo(f"db: {settings.db_path}")
    for kind, n in counts.items():
        typer.echo(f"  {kind:20s} {n}")
    typer.echo(f"  evidence_links       {conn.execute('SELECT count(*) FROM evidence_links').fetchone()[0]}")
    typer.echo(f"  axis_values          {conn.execute('SELECT count(*) FROM axis_values').fetchone()[0]}")
    typer.echo(f"  sources              {conn.execute('SELECT count(*) FROM sources').fetchone()[0]}")
    conn.close()


if __name__ == "__main__":
    app()
