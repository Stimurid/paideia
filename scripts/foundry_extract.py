"""Agent Foundry — извлечение кандидатов AgentSpec из PDF-донорских ботов.

Прогоняет PDF через pdfplumber → текст → gpt-4.1-mini c промптом
foundry_extract_agent.md → структурированный JSON с candidates.

Сохраняет в `db/foundry_candidates.json` для UI-ревью.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import pdfplumber
import typer

from api.agent import _extract_json
from api.llm import get_llm

app = typer.Typer(no_args_is_help=False, add_completion=False)
ROOT = Path(__file__).resolve().parent.parent
DONORS_DIR = ROOT / "donors" / "triz-bots"
PROMPT_PATH = ROOT / "prompts" / "foundry_extract_agent.md"
OUT_PATH = ROOT / "db" / "foundry_candidates.json"


def _extract_pdf_text(path: Path, max_chars: int = 25000) -> str:
    parts: list[str] = []
    total = 0
    try:
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                t = (page.extract_text() or "").strip()
                if not t:
                    continue
                parts.append(t)
                total += len(t)
                if total > max_chars:
                    break
    except Exception as exc:
        typer.echo(f"  pdfplumber error on {path.name}: {exc}")
    return "\n\n".join(parts)[:max_chars]


def _process_one(pdf_path: Path, llm, system_prompt: str) -> dict[str, Any]:
    text = _extract_pdf_text(pdf_path)
    if not text:
        return {"source": pdf_path.name, "status": "empty", "candidates": []}
    user_prompt = (
        f"Источник: {pdf_path.name}\n\n"
        f"=== ТЕКСТ ({len(text)} симв) ===\n\n{text}\n\n"
        f"Извлеки candidates по схеме."
    )
    started = time.time()
    try:
        raw = llm.chat_fast([
            {"role": "system", "content": system_prompt + "\n\nВыведи только JSON."},
            {"role": "user", "content": user_prompt},
        ])
        duration_ms = int((time.time() - started) * 1000)
        parsed = _extract_json(raw) or {}
        return {
            "source": pdf_path.name,
            "status": "ok" if parsed else "parse-fail",
            "duration_s": round(duration_ms / 1000, 1),
            "text_chars": len(text),
            "parsed": parsed,
            "candidates_count": len(parsed.get("candidates") or []) if parsed else 0,
        }
    except Exception as exc:
        return {"source": pdf_path.name, "status": "error",
                "error": str(exc)[:300]}


@app.command()
def main(
    only: str = typer.Option("", help="Только один PDF по имени"),
    out: str = typer.Option(str(OUT_PATH), help="куда сохранить JSON"),
) -> None:
    if not DONORS_DIR.exists():
        typer.echo(f"DONORS_DIR не найден: {DONORS_DIR}")
        raise typer.Exit(1)
    if not PROMPT_PATH.exists():
        typer.echo(f"PROMPT не найден: {PROMPT_PATH}")
        raise typer.Exit(1)

    pdfs = sorted(DONORS_DIR.glob("*.pdf"))
    if only:
        pdfs = [p for p in pdfs if only.lower() in p.name.lower()]
        if not pdfs:
            typer.echo(f"PDF '{only}' не найден")
            raise typer.Exit(1)

    typer.echo(f"экстрагирую из {len(pdfs)} PDF-доноров\n")
    system_prompt = PROMPT_PATH.read_text(encoding="utf-8")
    llm = get_llm()

    all_results: list[dict] = []
    for i, pdf_path in enumerate(pdfs, 1):
        typer.echo(f"  [{i}/{len(pdfs)}] {pdf_path.name}...")
        result = _process_one(pdf_path, llm, system_prompt)
        all_results.append(result)
        if result["status"] == "ok":
            typer.echo(
                f"    ✓ {result['candidates_count']} candidates, "
                f"{result['text_chars']}ch, {result.get('duration_s')}s"
            )
        else:
            typer.echo(f"    ✗ {result['status']}: {result.get('error', '')}")

    out_path = Path(out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump({"sources": all_results}, f, ensure_ascii=False, indent=2)

    total_candidates = sum(r.get("candidates_count", 0) for r in all_results)
    typer.echo(f"\n=== готово ===")
    typer.echo(f"  {len(all_results)} sources, {total_candidates} candidates")
    typer.echo(f"  → {out_path}")


if __name__ == "__main__":
    app()
