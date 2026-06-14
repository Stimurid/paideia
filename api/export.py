"""Сборщик выходных документов проекта: РПД, силлабус, заявка, бизнес-план.

Промпт лежит в prompts/docs/{doc_id}.md. Результат — JSON, который Jinja2
рендерит в md/docx. Сохраняется в content/exports/{project_id}/{doc_id}-{ts}.md.
"""

from __future__ import annotations

import json
import time
from datetime import date
from pathlib import Path
from typing import Any

import frontmatter
import yaml

from .agent import _audit, _extract_json
from .db import open_db, fetch_all
from .llm import get_llm
from .scenarios import _build_context

ROOT = Path(__file__).resolve().parent.parent
DOCS_PROMPTS = ROOT / "prompts" / "docs"
EXPORTS_DIR = ROOT / "content" / "exports"


DOCS = [
    {"id": "rpd",           "name": "РПД (Рабочая программа дисциплины)", "icon": "📋"},
    {"id": "syllabus",      "name": "Силлабус по неделям",               "icon": "🗓"},
    {"id": "application",   "name": "Заявка на грант/финансирование",     "icon": "💰"},
    {"id": "business_plan", "name": "Бизнес-план программы",              "icon": "📈"},
]


def list_exports(project_id: str) -> list[dict[str, Any]]:
    out_dir = EXPORTS_DIR / project_id
    if not out_dir.exists():
        return []
    items = []
    for p in sorted(out_dir.glob("*.md"), reverse=True):
        items.append({"file": p.name, "doc_id": p.stem.split("-")[0], "size": p.stat().st_size})
    return items


def build_document(project_id: str, doc_id: str) -> dict[str, Any]:
    prompt_path = DOCS_PROMPTS / f"{doc_id}.md"
    if not prompt_path.exists():
        raise ValueError(f"unknown doc '{doc_id}'")
    system_prompt = prompt_path.read_text(encoding="utf-8")

    # Контекст: канвас + аналоги + теория + RAG
    scenario_stub = {"name": f"document:{doc_id}", "model_role": "deep"}
    context, ctx_meta = _build_context(project_id, scenario_stub)

    llm = get_llm()
    started = time.time()
    conn = open_db()
    try:
        try:
            user_prompt = (
                f"{context}\n\nСобери документ «{doc_id}» по схеме в system-промпте. "
                f"Верни строгий JSON."
            )
            text_raw = llm.chat_deep([
                {"role": "system", "content": system_prompt + "\n\nВыведи только JSON, без markdown-обёртки."},
                {"role": "user", "content": user_prompt},
            ])
            duration_ms = int((time.time() - started) * 1000)
            parsed = _extract_json(text_raw) or {"_raw": text_raw}

            # Сохранение
            out_dir = EXPORTS_DIR / project_id
            out_dir.mkdir(parents=True, exist_ok=True)
            ts = date.today().isoformat()
            md_body = _render_md(doc_id, parsed)
            fm = {
                "id": f"{doc_id}-{ts}",
                "project_id": project_id,
                "doc_kind": doc_id,
                "generated_at": ts,
                "duration_ms": duration_ms,
            }
            post = frontmatter.Post(content=md_body, **fm)
            raw = frontmatter.dumps(
                post, handler=frontmatter.YAMLHandler(),
                default_flow_style=False, allow_unicode=True, sort_keys=False,
            )
            out_file = out_dir / f"{doc_id}-{ts}.md"
            out_file.write_text(raw + "\n", encoding="utf-8")

            _audit(conn, purpose=f"export:{doc_id}", model_role="deep",
                   target_kind="project", target_id=project_id, section_id=None,
                   input_obj={"doc": doc_id, **ctx_meta}, output_obj=parsed,
                   citations=[], status="ok", error=None, duration_ms=duration_ms)

            return {
                "doc_id": doc_id, "file": out_file.name,
                "content_md": md_body, "data": parsed,
                "duration_ms": duration_ms,
            }
        except Exception as exc:
            duration_ms = int((time.time() - started) * 1000)
            _audit(conn, purpose=f"export:{doc_id}", model_role="deep",
                   target_kind="project", target_id=project_id, section_id=None,
                   input_obj={"doc": doc_id}, output_obj=None, citations=[],
                   status="error", error=str(exc), duration_ms=duration_ms)
            raise
    finally:
        conn.close()


def _render_md(doc_id: str, data: dict[str, Any]) -> str:
    """Простой рендер JSON-структуры в markdown."""
    lines: list[str] = []
    lines.append(f"# {data.get('title') or data.get('course_title') or data.get('program_title') or doc_id}\n")
    _render_dict(data, lines, level=2)
    return "\n".join(lines)


def _render_dict(d: Any, lines: list[str], level: int = 2) -> None:
    if isinstance(d, dict):
        for k, v in d.items():
            if isinstance(v, (dict, list)):
                lines.append(f"\n{'#' * level} {_label(k)}\n")
                _render_dict(v, lines, level=min(level + 1, 6))
            else:
                lines.append(f"- **{_label(k)}**: {v}")
    elif isinstance(d, list):
        for item in d:
            if isinstance(item, dict):
                lines.append("")
                _render_dict(item, lines, level=min(level + 1, 6))
                lines.append("")
            else:
                lines.append(f"- {item}")


def _label(key: str) -> str:
    return key.replace("_", " ").capitalize()


def read_export(project_id: str, filename: str) -> str:
    path = EXPORTS_DIR / project_id / filename
    if not path.exists():
        raise FileNotFoundError(f"export '{filename}' not found")
    return path.read_text(encoding="utf-8")
