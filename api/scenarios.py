"""Универсальный движок сценариев лаборатории.

Каждый сценарий = (id, name, family, system-prompt в prompts/scenarios/<id>.md).
run_scenario собирает контекст (проект + аналоги + теория + RAG) и зовёт LLM.
Результаты сохраняются в scenario_runs.
"""

from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from typing import Any

import frontmatter
import yaml

from .db import open_db, fetch_all
from .llm import get_llm
from .agent import _audit, _extract_json
from .schemas import CANVAS_SECTIONS

ROOT = Path(__file__).resolve().parent.parent
SCENARIOS_DIR = ROOT / "prompts" / "scenarios"


def load_registry() -> list[dict[str, Any]]:
    with (SCENARIOS_DIR / "_registry.yaml").open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("scenarios") or []


def get_scenario(scenario_id: str) -> dict[str, Any] | None:
    for s in load_registry():
        if s["id"] == scenario_id:
            return s
    return None


def _load_project(project_id: str) -> dict[str, Any]:
    path = ROOT / "content" / "projects" / f"{project_id}.md"
    if not path.exists():
        raise FileNotFoundError(f"project '{project_id}' not found")
    post = frontmatter.load(path)
    return post.metadata


def _load_case(case_id: str) -> dict[str, Any] | None:
    path = ROOT / "content" / "cases" / f"{case_id}.md"
    if not path.exists():
        return None
    post = frontmatter.load(path)
    return post.metadata


def _project_brief(project: dict) -> dict:
    return {
        "id": project.get("id"),
        "name": project.get("name"),
        "facets": project.get("facets"),
        "ai": project.get("ai"),
        "axes": project.get("axes"),
        "transformation_mode": project.get("transformation_mode"),
        "analogues": project.get("analogues") or [],
        "canvas_filled": {
            sec_id: (project.get("canvas") or {}).get(sec_id, {}).get("text", "")[:600]
            for sec_id, _ in CANVAS_SECTIONS
            if (project.get("canvas") or {}).get(sec_id, {}).get("text")
        },
    }


def _build_context(project_id: str, scenario: dict, case_id: str | None = None) -> tuple[str, dict]:
    project = _load_project(project_id)
    parts: list[str] = []
    ctx_meta: dict[str, Any] = {}

    parts.append("ПРОЕКТ:\n```json\n" + json.dumps(_project_brief(project),
                 ensure_ascii=False, indent=2) + "\n```")

    # Аналоги-кейсы
    analogues = project.get("analogues") or []
    if scenario.get("needs_case_param") and case_id:
        analogues = [case_id]
    if analogues:
        conn = open_db()
        try:
            rows = fetch_all(
                conn,
                f"SELECT id, name, org_name, country, pattern, agentivity, body_md FROM cases WHERE id IN ({','.join('?'*len(analogues))})",
                tuple(analogues),
            )
            if rows:
                parts.append("\nКЕЙСЫ КОРПУСА:")
                for r in rows:
                    parts.append(f"- [[{r['id']}]] {r['name']} · {r['org_name']} · {r['country']} · pattern {r['pattern']} · a{r['agentivity']}")
                    parts.append(f"  body: {(r['body_md'] or '')[:600]}")
                ctx_meta["analogues"] = [r["id"] for r in rows]
        finally:
            conn.close()

    # Теория (типы, гипотезы, противоречия, моды, контр-сигналы)
    conn = open_db()
    try:
        types_ = fetch_all(conn, "SELECT id, name FROM types ORDER BY id")
        hyps = fetch_all(conn, "SELECT id, name, status_current FROM hypotheses ORDER BY id")
        tens = fetch_all(conn, "SELECT id, name FROM tensions ORDER BY id")
        modes = fetch_all(conn, "SELECT id, name FROM modes ORDER BY id")
        cs = fetch_all(conn, "SELECT id, name FROM counter_signals ORDER BY id")
        parts.append("\nТЕОРИЯ КОРПУСА (для использования в [[wikilinks]]):")
        parts.append("Типы: " + ", ".join(f"{t['id']}={t['name']}" for t in types_))
        parts.append("Гипотезы: " + "; ".join(f"{h['id']} ({h['status_current']})={h['name']}" for h in hyps))
        parts.append("Противоречия: " + ", ".join(f"{t['id']}={t['name']}" for t in tens))
        parts.append("Моды: " + ", ".join(f"{m['id']}={m['name']}" for m in modes))
        parts.append("Контр-сигналы: " + ", ".join(f"{c['id']}={c['name']}" for c in cs))
    finally:
        conn.close()

    # RAG из архива
    rag_query = f"{project.get('name','')} {scenario.get('name','')}"
    try:
        from .retrieve import retrieve_archive
        chunks = retrieve_archive(rag_query, top_k=4)
        if chunks:
            parts.append("\nКОНТЕКСТ ИЗ ТВОЕГО АРХИВА:")
            for ch in chunks:
                parts.append(f"--- [{ch['file_path']} @ {ch['offset']}, d={ch['distance']}] ---")
                parts.append(ch["text"][:900])
            ctx_meta["archive"] = [f"{c['file_path']}@{c['offset']}" for c in chunks]
    except Exception:
        pass

    # RAG из библиотеки (L1+) с F1-селектором противоречий
    try:
        from .library import search_library
        from .selector import annotate_chunks_with_schools
        lib_chunks = annotate_chunks_with_schools(search_library(rag_query, top_k=4))
        if lib_chunks:
            schools = {c.get("school") for c in lib_chunks if c.get("school")}
            if len(schools) >= 2:
                parts.append("\nБИБЛИОТЕКА — ВНИМАНИЕ, НАЙДЕНЫ ПРОТИВОРЕЧАЩИЕ ШКОЛЫ:")
                parts.append(f"  школы: {', '.join(sorted(schools))}")
                parts.append("  не смешивай позиции — явно противопоставь.")
            else:
                parts.append("\nКОНТЕКСТ ИЗ БИБЛИОТЕКИ:")
            for ch in lib_chunks:
                sec_label = (
                    f"sec {ch['section_num']}: {ch['section_title']}"
                    if ch.get('section_num') and ch.get('section_title')
                    else f"sec {ch.get('section_num') or '?'}"
                )
                d = f", d={ch['distance']}" if ch.get('distance') is not None else ""
                school = f" [школа: {ch['school']}]" if ch.get("school") else ""
                parts.append(
                    f"--- [📚 {ch['book_title']} / {ch['book_authors'] or '?'} / "
                    f"{sec_label}{d}]{school} ---"
                )
                parts.append(ch["text"][:900])
            ctx_meta["library"] = [
                {"book_id": c["book_id"], "chunk_id": c["id"],
                 "book_title": c["book_title"], "school": c.get("school")}
                for c in lib_chunks
            ]
    except Exception:
        pass

    return "\n".join(parts), ctx_meta


def _ensure_scenario_runs_table(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS scenario_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id TEXT NOT NULL,
            scenario_id TEXT NOT NULL,
            case_param TEXT,
            status TEXT,
            output_json TEXT,
            error TEXT,
            duration_ms INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_scenario_runs_proj ON scenario_runs(project_id, created_at DESC)")
    conn.commit()


def run_scenario(project_id: str, scenario_id: str, *,
                 case_param: str | None = None) -> dict[str, Any]:
    scenario = get_scenario(scenario_id)
    if not scenario:
        raise ValueError(f"unknown scenario '{scenario_id}'")

    system_prompt = (SCENARIOS_DIR / f"{scenario_id}.md").read_text(encoding="utf-8")
    context, ctx_meta = _build_context(project_id, scenario, case_param)

    llm = get_llm()
    started = time.time()
    conn = open_db()
    _ensure_scenario_runs_table(conn)

    try:
        try:
            user_prompt = f"{context}\n\nЗапусти сценарий «{scenario['name']}». Верни строгий JSON по схеме."
            method = llm.chat_deep if scenario.get("model_role") == "deep" else llm.chat_fast
            text_raw = method([
                {"role": "system", "content": system_prompt + "\n\nВыведи только JSON, без markdown-обёртки."},
                {"role": "user", "content": user_prompt},
            ])
            duration_ms = int((time.time() - started) * 1000)
            parsed = _extract_json(text_raw) or {"_raw": text_raw}

            cur = conn.execute(
                """INSERT INTO scenario_runs (project_id, scenario_id, case_param, status, output_json, duration_ms)
                   VALUES (?, ?, ?, 'ok', ?, ?)""",
                (project_id, scenario_id, case_param,
                 json.dumps(parsed, ensure_ascii=False), duration_ms),
            )
            run_id = cur.lastrowid
            conn.commit()

            _audit(conn, purpose=f"scenario:{scenario_id}", model_role=scenario.get("model_role","deep"),
                   target_kind="project", target_id=project_id, section_id=None,
                   input_obj={"scenario": scenario_id, "case_param": case_param, **ctx_meta},
                   output_obj=parsed, citations=[],
                   status="ok", error=None, duration_ms=duration_ms)

            return {
                "run_id": run_id,
                "scenario": scenario,
                "result": parsed,
                "duration_ms": duration_ms,
                "context_meta": ctx_meta,
            }
        except Exception as exc:
            duration_ms = int((time.time() - started) * 1000)
            conn.execute(
                """INSERT INTO scenario_runs (project_id, scenario_id, case_param, status, error, duration_ms)
                   VALUES (?, ?, ?, 'error', ?, ?)""",
                (project_id, scenario_id, case_param, str(exc), duration_ms),
            )
            conn.commit()
            _audit(conn, purpose=f"scenario:{scenario_id}", model_role=scenario.get("model_role","deep"),
                   target_kind="project", target_id=project_id, section_id=None,
                   input_obj={"scenario": scenario_id},
                   output_obj=None, citations=[],
                   status="error", error=str(exc), duration_ms=duration_ms)
            raise
    finally:
        conn.close()


def list_runs(project_id: str, limit: int = 50) -> list[dict[str, Any]]:
    conn = open_db()
    _ensure_scenario_runs_table(conn)
    try:
        return fetch_all(
            conn,
            """SELECT id, project_id, scenario_id, case_param, status, duration_ms, created_at
               FROM scenario_runs WHERE project_id = ? ORDER BY id DESC LIMIT ?""",
            (project_id, limit),
        )
    finally:
        conn.close()


def get_run(run_id: int) -> dict[str, Any] | None:
    conn = open_db()
    _ensure_scenario_runs_table(conn)
    try:
        rows = fetch_all(
            conn,
            "SELECT * FROM scenario_runs WHERE id = ?",
            (run_id,),
        )
        if not rows:
            return None
        r = rows[0]
        if r.get("output_json"):
            r["output"] = json.loads(r["output_json"])
        else:
            r["output"] = None
        return r
    finally:
        conn.close()
