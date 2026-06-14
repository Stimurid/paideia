"""Миграционный скрипт: канвас 18 секций → EducationalSystemModel.

Для каждого проекта в content/projects/:
1. Читает канвас (18 секций).
2. Скармливает gpt-4.1-mini промптом canvas_to_system_model.md.
3. Валидирует через Pydantic EducationalSystemModel.
4. Сохраняет в БД (system_models).

Запуск:
    python -m scripts.build_system_models
    python -m scripts.build_system_models --only <project_id>
    python -m scripts.build_system_models --dry-run
"""

from __future__ import annotations

import json
import time
import uuid
from datetime import datetime
from pathlib import Path

import frontmatter
import typer

from api.agent import _extract_json
from api.db import open_db
from api.llm import get_llm
from api.triz.system_model import EducationalSystemModel

app = typer.Typer(no_args_is_help=False, add_completion=False)
ROOT = Path(__file__).resolve().parent.parent
PROJECTS_DIR = ROOT / "content" / "projects"
PROMPT_PATH = ROOT / "prompts" / "canvas_to_system_model.md"


def _normalize_empty_to_none(obj):
    """Рекурсивно: пустые строки и пустые dict/list для optional полей → None.
    Помогает Pydantic-валидации с Literal-типами, которые не принимают ""."""
    if isinstance(obj, dict):
        for k, v in list(obj.items()):
            if isinstance(v, str) and v.strip() == "":
                obj[k] = None
            elif isinstance(v, (dict, list)):
                _normalize_empty_to_none(v)
    elif isinstance(obj, list):
        for item in obj:
            if isinstance(item, (dict, list)):
                _normalize_empty_to_none(item)


def _build_one(project_path: Path, llm, system_prompt: str,
               dry_run: bool = False) -> dict:
    post = frontmatter.load(project_path)
    fm = post.metadata
    project_id = fm.get("id", project_path.stem)
    canvas = fm.get("canvas") or {}

    # Только заполненные секции
    filled = {
        sid: sdata.get("text", "")
        for sid, sdata in canvas.items()
        if isinstance(sdata, dict) and sdata.get("text", "").strip()
    }
    if not filled:
        return {"project_id": project_id, "status": "skipped",
                "reason": "канвас пуст"}

    canvas_text = "\n\n".join(f"### {sid}\n{text}" for sid, text in filled.items())
    user_prompt = (
        f"project_id: {project_id}\n"
        f"name: {fm.get('name', project_path.stem)}\n\n"
        f"=== КАНВАС 18 СЕКЦИЙ (заполнено: {len(filled)}/18) ===\n\n"
        f"{canvas_text}\n\n"
        f"Извлеки EducationalSystemModel по схеме из system-промпта."
    )

    if dry_run:
        return {"project_id": project_id, "status": "dry-run",
                "canvas_filled": len(filled),
                "canvas_chars": len(canvas_text)}

    started = time.time()
    try:
        raw = llm.chat_fast([
            {"role": "system", "content": system_prompt + "\n\nВыведи только JSON."},
            {"role": "user", "content": user_prompt},
        ])
        duration_ms = int((time.time() - started) * 1000)
        parsed = _extract_json(raw)
        if not parsed:
            return {"project_id": project_id, "status": "parse-fail",
                    "duration_s": round(duration_ms / 1000, 1),
                    "raw_preview": (raw or "")[:300]}

        # Гарантируем id и project_id
        parsed["project_id"] = project_id
        parsed.setdefault("id", f"system-{project_id}-{uuid.uuid4().hex[:8]}")
        parsed.setdefault("source", "imported-from-canvas")
        parsed.setdefault("title", fm.get("name", project_id))

        # Нормализация: пустые строки в None, дефолты на критичных Literal-полях
        _normalize_empty_to_none(parsed)
        if not parsed.get("kind"):
            parsed["kind"] = "course"
        if not parsed.get("maturity"):
            parsed["maturity"] = "seed"

        # Валидация
        model = EducationalSystemModel.model_validate(parsed)
    except Exception as exc:
        return {"project_id": project_id, "status": "error",
                "error": str(exc)[:300],
                "duration_s": round((time.time() - started), 1)}

    # Сохранение
    conn = open_db()
    try:
        now = datetime.utcnow().isoformat(timespec="seconds")
        ce = model.constraint_envelope
        conn.execute(
            """
            INSERT OR REPLACE INTO system_models
              (id, project_id, title, kind, function, maturity, parent_variant_id,
               source, invention_level, full_json, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                model.id, model.project_id, model.title, model.kind,
                model.function, model.maturity, model.parent_variant_id,
                model.source, ce.invention_level,
                model.model_dump_json(),
                now, now,
            ),
        )
        conn.commit()
    finally:
        conn.close()

    return {
        "project_id": project_id, "status": "ok",
        "system_model_id": model.id,
        "function_len": len(model.function),
        "contradictions": len(model.contradictions),
        "flows": len(model.flows),
        "roles": len(model.working_organ),
        "duration_s": round(duration_ms / 1000, 1),
    }


@app.command()
def main(
    only: str = typer.Option("", help="Только указанный project_id"),
    dry_run: bool = typer.Option(False, help="Не вызывать LLM"),
) -> None:
    if not PROMPT_PATH.exists():
        typer.echo(f"PROMPT not found: {PROMPT_PATH}")
        raise typer.Exit(1)
    if not PROJECTS_DIR.exists():
        typer.echo(f"PROJECTS_DIR not found: {PROJECTS_DIR}")
        raise typer.Exit(1)

    project_files = sorted(PROJECTS_DIR.glob("*.md"))
    if only:
        project_files = [p for p in project_files if p.stem == only]
        if not project_files:
            typer.echo(f"project '{only}' not found")
            raise typer.Exit(1)

    typer.echo(f"строю SystemModel для {len(project_files)} проектов\n")

    system_prompt = PROMPT_PATH.read_text(encoding="utf-8")
    llm = None if dry_run else get_llm()

    stats = {"ok": 0, "skipped": 0, "error": 0}
    for i, path in enumerate(project_files, 1):
        result = _build_one(path, llm, system_prompt, dry_run=dry_run)
        pid = result.get("project_id", path.stem)
        status = result.get("status")
        if status == "ok":
            stats["ok"] += 1
            typer.echo(
                f"  [{i}/{len(project_files)}] ✓ {pid}: "
                f"func={result['function_len']}ch, "
                f"flows={result['flows']}, roles={result['roles']}, "
                f"contrad={result['contradictions']} ({result['duration_s']}s)"
            )
        elif status == "dry-run":
            typer.echo(
                f"  [{i}/{len(project_files)}] {pid}: "
                f"{result['canvas_filled']}/18 секций, "
                f"{result['canvas_chars']}ch"
            )
        elif status == "skipped":
            stats["skipped"] += 1
            typer.echo(f"  [{i}/{len(project_files)}] · {pid}: {result.get('reason')}")
        else:
            stats["error"] += 1
            typer.echo(
                f"  [{i}/{len(project_files)}] ✗ {pid}: "
                f"{result.get('error') or status}"
            )

    typer.echo(f"\n=== готово ===")
    typer.echo(f"  ok:      {stats['ok']}")
    typer.echo(f"  skipped: {stats['skipped']}")
    typer.echo(f"  errors:  {stats['error']}")


if __name__ == "__main__":
    app()
