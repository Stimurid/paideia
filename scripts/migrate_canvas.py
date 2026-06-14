"""Миграция существующих кейсов на 18-секционный канвас.

Что делает:
- читает все content/cases/*.md;
- если в фронтматтере нет блока `canvas:` или он пуст, парсит body_md по эвристикам
  ## Описание → signature_context (+ effect_hypothesis при наличии гипотезы)
  ## Что переиспользуемо → transferability
  ## Риски / контрсигналы → countersignals
- остальные секции остаются пустыми (status="empty"), в UI это даст «нет данных»
  с кнопками «уточнить через LLM» / «добавить вручную»;
- пишет фронтматтер обратно в файл, body_md не трогает.

Запуск:
    python -m scripts.migrate_canvas              # все кейсы
    python -m scripts.migrate_canvas --force      # перезаписать даже непустой canvas
    python -m scripts.migrate_canvas --case asu-createai
"""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

import frontmatter
import typer
import yaml

from api.schemas import CANVAS_KEYS

ROOT = Path(__file__).resolve().parent.parent
CASES = ROOT / "content" / "cases"

app = typer.Typer(no_args_is_help=False, add_completion=False)


# Эвристики для распила body_md существующих карточек.
# Заголовок -> ключ секции в канвасе.
HEADING_MAP: dict[str, str] = {
    "описание":               "signature_context",
    "что переиспользуемо":    "transferability",
    "что переносимо":         "transferability",
    "риски":                  "risks",
    "риски / контрсигналы":   "countersignals",
    "контрсигналы":           "countersignals",
    "проблема":               "problem_situation",
    "гипотеза":               "effect_hypothesis",
    "гипотеза эффекта":       "effect_hypothesis",
    "архитектура":            "ai_architecture",
    "роли":                   "team_roles",
    "сценарий":               "interaction_scenario",
    "метрики":                "metrics_evidence",
    "источники":              "sources_verification",
    "открытые вопросы":       "open_questions",
    "минимальная версия":     "interaction_scenario",
    "радикальная версия":     "next_wave_followup",
}


def _split_body(body_md: str) -> dict[str, str]:
    """Парсит markdown с ## заголовками в {section_key: text}."""
    if not body_md.strip():
        return {}
    chunks = re.split(r"(?m)^##\s+(.+?)\s*$", body_md)
    # chunks: [preamble, heading1, body1, heading2, body2, ...]
    out: dict[str, str] = {}
    preamble = chunks[0].strip()
    if preamble:
        out["signature_context"] = preamble
    for i in range(1, len(chunks), 2):
        heading = chunks[i].strip().lower()
        text = chunks[i + 1].strip() if i + 1 < len(chunks) else ""
        if not text:
            continue
        key = HEADING_MAP.get(heading)
        if not key:
            # пытаемся через startswith
            for h, k in HEADING_MAP.items():
                if heading.startswith(h):
                    key = k
                    break
        if not key:
            continue
        if key in out:
            out[key] = out[key] + "\n\n" + text
        else:
            out[key] = text
    return out


def _migrate_one(path: Path, force: bool = False) -> tuple[bool, int]:
    post = frontmatter.load(path)
    existing = post.metadata.get("canvas") or {}
    if existing and not force:
        return False, 0

    split = _split_body(post.content)
    canvas: dict[str, dict[str, str]] = {}
    today = date.today().isoformat()
    for key, text in split.items():
        if key not in CANVAS_KEYS:
            continue
        canvas[key] = {
            "text": text,
            "status": "draft",
            "source": "imported",
            "updated_at": today,
        }

    post.metadata["canvas"] = canvas
    raw = frontmatter.dumps(post, handler=frontmatter.YAMLHandler(), default_flow_style=False, allow_unicode=True, sort_keys=False)
    path.write_text(raw + "\n" if not raw.endswith("\n") else raw, encoding="utf-8")
    return True, len(canvas)


@app.command()
def main(case: str | None = None, force: bool = False) -> None:
    files = [CASES / f"{case}.md"] if case else sorted(CASES.glob("*.md"))
    total, changed, sections = 0, 0, 0
    for path in files:
        if not path.exists():
            typer.echo(f"  XX {path.name}: missing")
            continue
        total += 1
        was_changed, n_sections = _migrate_one(path, force=force)
        if was_changed:
            changed += 1
            sections += n_sections
            typer.echo(f"  +  {path.name:50s} {n_sections} sections")
        else:
            typer.echo(f"  =  {path.name:50s} skipped (canvas exists, use --force)")
    typer.echo(f"\nTotal: {total} cases · {changed} migrated · {sections} sections filled")


if __name__ == "__main__":
    app()
