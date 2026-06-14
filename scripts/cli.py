"""paideia CLI.

Запуск:
    python -m scripts.cli init      # проверка скаффолда + ping LLM
    python -m scripts.cli ping      # ping LLM
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import typer

from api.config import get_settings
from api.llm import get_llm

ROOT = Path(__file__).resolve().parent.parent
app = typer.Typer(no_args_is_help=True, add_completion=False)


@app.command()
def init() -> None:
    """Проверить, что скаффолд цел, и пингануть LLM."""
    settings = get_settings()

    typer.echo("== scaffold ==")
    for sub in ["content", "taxonomy", "prompts", "api", "scripts", "db", "tests"]:
        path = ROOT / sub
        ok = path.exists() and path.is_dir()
        typer.echo(f"  {'OK ' if ok else 'XX '} {sub}/")
    raw = ROOT / settings.paideia_raw_dir
    typer.echo(f"  {'OK ' if raw.exists() else 'XX '} raw/ -> {raw.resolve() if raw.exists() else '(missing)'}")

    typer.echo("== db ==")
    schema = ROOT / "db" / "schema.sql"
    typer.echo(f"  {'OK ' if schema.exists() else 'XX '} db/schema.sql")
    db_path = settings.db_path
    if not db_path.exists():
        typer.echo(f"  -- creating empty {db_path.relative_to(ROOT)} from schema")
        db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(db_path) as conn:
            conn.executescript(schema.read_text(encoding="utf-8"))
        typer.echo("  OK  db created")
    else:
        typer.echo(f"  OK  db exists ({db_path.stat().st_size} bytes)")

    typer.echo("== llm ==")
    diag = get_llm().ping()
    if diag["ok"]:
        typer.echo(f"  OK  active provider: {diag['active']}")
    else:
        typer.echo("  WARN no provider responded")
    for p in diag.get("providers", []):
        status = "OK " if p.get("ok") else "XX "
        suffix = p.get("reply") if p.get("ok") else f"{p.get('status')}: {p.get('detail')}"
        typer.echo(f"   {status}{p['name']} ({p['model']}) — {suffix}")
    if "error" in diag:
        typer.echo(f"   XX {diag['error']}")


@app.command()
def ping() -> None:
    """Пингануть LLM-провайдеров."""
    diag = get_llm().ping()
    typer.echo(diag)


if __name__ == "__main__":
    app()
