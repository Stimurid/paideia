"""Обогащение карточек кейсов из исходных волн анализа.

Для каждого кейса в content/cases/:
1. Собирает все упоминания из C:/projects/Paideia/*.md (через имя организации,
   ключевые токены, имя кейса).
2. Берёт ±2000 символов контекста вокруг каждого совпадения.
3. Объединяет, режет до 40 КБ.
4. Скармливает LLM с промптом enrich_from_waves.md.
5. Сохраняет результат **только в пустые секции** канваса.

Запуск:
    python -m scripts.enrich_cases_from_waves [--only <case_id>] [--limit N]
    python -m scripts.enrich_cases_from_waves --dry-run   # только покажет что нашёл
"""

from __future__ import annotations

import json
import re
import time
from datetime import date
from pathlib import Path
from typing import Any

import frontmatter
import typer

from api.agent import _extract_json
from api.config import get_settings
from api.llm import get_llm
from api.schemas import CANVAS_SECTIONS

app = typer.Typer(no_args_is_help=False, add_completion=False)
ROOT = Path(__file__).resolve().parent.parent
CASES_DIR = ROOT / "content" / "cases"
ARCHIVE_DIR = Path("C:/projects/Paideia")
PROMPT_PATH = ROOT / "prompts" / "enrich_from_waves.md"

CONTEXT_RADIUS = 2000  # символов вокруг каждого hit
MAX_TOTAL = 40000      # общий лимит сырого текста для одного кейса
MIN_TOTAL = 400        # если меньше — пропускаем (нет смысла звать LLM)


def _load_archive_files() -> list[tuple[Path, str]]:
    """Грузим все md из архива в память (они там небольшие в сумме)."""
    files: list[tuple[Path, str]] = []
    for p in sorted(ARCHIVE_DIR.glob("*.md")):
        try:
            files.append((p, p.read_text(encoding="utf-8", errors="replace")))
        except Exception as exc:
            typer.echo(f"  skip {p.name}: {exc}")
    return files


def _build_search_patterns(fm: dict, name: str) -> list[re.Pattern]:
    """Какие токены искать в волнах."""
    org = (fm.get("organization") or {}).get("name", "")
    patterns: list[str] = []
    if org:
        patterns.append(re.escape(org))
    # имя кейса без org-префикса
    if " · " in name:
        tail = name.split(" · ", 1)[1].split(" (")[0]
        if len(tail) > 4:
            patterns.append(re.escape(tail))
    # ключевые продукты/имена из id
    id_tokens = fm.get("id", "").split("-")
    for tok in id_tokens:
        if len(tok) > 4 and tok.lower() not in {
            "case", "edu", "with", "and", "the", "campus", "university",
            "school", "college", "institute",
        }:
            patterns.append(re.escape(tok))
    # технологии из ai.technologies
    techs = ((fm.get("ai") or {}).get("technologies") or [])
    for t in techs:
        if isinstance(t, str) and len(t) > 4:
            patterns.append(re.escape(t))
    # уникальные
    seen = set()
    out = []
    for p in patterns:
        if p.lower() not in seen:
            seen.add(p.lower())
            out.append(re.compile(p, re.IGNORECASE))
    return out


def _gather_context(archive_files: list[tuple[Path, str]],
                    patterns: list[re.Pattern]) -> tuple[str, dict]:
    """Найти все упоминания и собрать ±CONTEXT_RADIUS контекст."""
    chunks: list[tuple[str, str]] = []  # (filename, text)
    stats = {"hits": 0, "files": set(), "by_file": {}}

    for path, text in archive_files:
        spans: list[tuple[int, int]] = []
        for pat in patterns:
            for m in pat.finditer(text):
                spans.append((max(0, m.start() - CONTEXT_RADIUS),
                              min(len(text), m.end() + CONTEXT_RADIUS)))
        if not spans:
            continue
        # объединяем перекрывающиеся
        spans.sort()
        merged = [spans[0]]
        for s, e in spans[1:]:
            if s <= merged[-1][1] + 100:  # рядом — сливаем
                merged[-1] = (merged[-1][0], max(merged[-1][1], e))
            else:
                merged.append((s, e))
        # вырезаем
        for s, e in merged:
            chunks.append((path.name, text[s:e].strip()))
            stats["hits"] += 1
        stats["files"].add(path.name)
        stats["by_file"][path.name] = stats["by_file"].get(path.name, 0) + len(merged)

    # сборка
    parts: list[str] = []
    total = 0
    for fname, ch in chunks:
        block = f"\n\n--- {fname} ---\n\n{ch}"
        if total + len(block) > MAX_TOTAL:
            # если этот блок слишком большой, режем его
            remaining = MAX_TOTAL - total
            if remaining > 500:
                parts.append(block[:remaining])
            break
        parts.append(block)
        total += len(block)

    stats["files"] = sorted(stats["files"])
    stats["total_chars"] = total
    return "\n".join(parts), stats


def _enrich_one(case_path: Path, archive_files: list[tuple[Path, str]],
                llm, system_prompt: str, dry_run: bool = False) -> dict:
    if not case_path.exists():
        return {"case_id": case_path.stem, "status": "skipped", "reason": "file disappeared"}
    post = frontmatter.load(case_path)
    fm = post.metadata
    name = fm.get("name", case_path.stem)
    canvas = fm.get("canvas") or {}

    # пропускаем секции, у которых уже есть text
    existing = [sid for sid, sdata in canvas.items()
                if isinstance(sdata, dict) and sdata.get("text", "").strip()]
    empty = [sid for sid, _ in CANVAS_SECTIONS if sid not in existing]

    patterns = _build_search_patterns(fm, name)
    if not patterns:
        return {"case_id": fm.get("id"), "status": "skipped", "reason": "no patterns"}

    context, stats = _gather_context(archive_files, patterns)
    if stats["total_chars"] < MIN_TOTAL:
        return {"case_id": fm.get("id"), "status": "skipped",
                "reason": f"insufficient context ({stats['total_chars']} chars)", "stats": stats}

    if dry_run:
        return {"case_id": fm.get("id"), "status": "dry-run",
                "would_fill": empty, "existing": existing, "stats": stats,
                "context_preview": context[:500]}

    # вызов LLM
    case_brief = {
        "id": fm.get("id"), "name": name,
        "organization": fm.get("organization"),
        "ai": fm.get("ai"),
        "facets": fm.get("facets"),
    }
    user_prompt = (
        f"Кейс: {json.dumps(case_brief, ensure_ascii=False)}\n\n"
        f"existing_sections: {existing}\n\n"
        f"empty_sections: {empty}\n\n"
        f"=== ФРАГМЕНТЫ ИЗ ВОЛН ({stats['total_chars']} символов из {len(stats['files'])} файлов) ===\n\n"
        f"{context}"
    )

    started = time.time()
    try:
        text_raw = llm.chat_fast([
            {"role": "system", "content": system_prompt + "\n\nВыведи только JSON."},
            {"role": "user", "content": user_prompt},
        ])
        duration = time.time() - started
        parsed = _extract_json(text_raw)
        if not parsed or "sections" not in parsed:
            return {"case_id": fm.get("id"), "status": "parse-fail",
                    "duration_s": round(duration, 1), "raw_preview": text_raw[:300]}

        # merge: только пустые секции
        today = date.today().isoformat()
        added = []
        for sid, sec_data in (parsed.get("sections") or {}).items():
            if sid not in empty:
                continue
            text = (sec_data.get("text") or "").strip() if isinstance(sec_data, dict) else ""
            if not text:
                continue
            canvas[sid] = {
                "text": text,
                "status": "draft",
                "source": "enriched-from-waves",
                "updated_at": today,
            }
            added.append(sid)

        fm["canvas"] = canvas
        # перезаписываем
        new_post = frontmatter.Post(content=post.content, **fm)
        raw = frontmatter.dumps(new_post, handler=frontmatter.YAMLHandler(),
                                default_flow_style=False, allow_unicode=True, sort_keys=False)
        case_path.write_text(raw + "\n", encoding="utf-8")

        return {
            "case_id": fm.get("id"), "status": "ok",
            "duration_s": round(duration, 1),
            "context_chars": stats["total_chars"],
            "context_files": len(stats["files"]),
            "filled_sections": added,
            "skipped_by_llm": parsed.get("skipped_sections", []),
        }
    except Exception as exc:
        return {"case_id": fm.get("id"), "status": "error",
                "error": str(exc), "duration_s": round(time.time() - started, 1)}


@app.command()
def main(
    only: str = typer.Option("", help="Обогатить только один кейс по id"),
    limit: int = typer.Option(0, help="Ограничить число кейсов (0 = все)"),
    dry_run: bool = typer.Option(False, help="Только показать, что нашёл, без LLM"),
    start_from: str = typer.Option("", help="Начать с этого case_id (для возобновления)"),
) -> None:
    if not PROMPT_PATH.exists():
        typer.echo(f"PROMPT not found: {PROMPT_PATH}")
        raise typer.Exit(1)
    if not ARCHIVE_DIR.exists():
        typer.echo(f"ARCHIVE not found: {ARCHIVE_DIR}")
        raise typer.Exit(1)

    system_prompt = PROMPT_PATH.read_text(encoding="utf-8")
    llm = None if dry_run else get_llm()

    typer.echo("loading archive...")
    archive_files = _load_archive_files()
    typer.echo(f"  {len(archive_files)} files loaded")

    case_files = sorted(CASES_DIR.glob("*.md"))
    if only:
        case_files = [p for p in case_files if p.stem == only]
        if not case_files:
            typer.echo(f"case '{only}' not found")
            raise typer.Exit(1)
    if start_from:
        case_files = [p for p in case_files if p.stem >= start_from]
    if limit:
        case_files = case_files[:limit]

    typer.echo(f"\nenriching {len(case_files)} cases\n")
    stats = {"ok": 0, "skipped": 0, "error": 0, "filled_sections_total": 0}

    for i, path in enumerate(case_files, 1):
        result = _enrich_one(path, archive_files, llm, system_prompt, dry_run=dry_run)
        cid = result.get("case_id", path.stem)
        status = result.get("status")
        if status == "ok":
            filled = result.get("filled_sections") or []
            stats["ok"] += 1
            stats["filled_sections_total"] += len(filled)
            typer.echo(f"  [{i}/{len(case_files)}] ✓ {cid}: +{len(filled)} секций "
                       f"({result['context_chars']}ch/{result['context_files']}f, "
                       f"{result['duration_s']}s) → {filled}")
        elif status == "dry-run":
            typer.echo(f"  [{i}/{len(case_files)}] {cid}: ctx={result['stats']['total_chars']}ch "
                       f"from {len(result['stats']['files'])} files, would fill {len(result['would_fill'])} sections")
        elif status == "skipped":
            stats["skipped"] += 1
            typer.echo(f"  [{i}/{len(case_files)}] · {cid}: {result.get('reason')}")
        else:
            stats["error"] += 1
            typer.echo(f"  [{i}/{len(case_files)}] ✗ {cid}: {result.get('error') or result.get('status')}")

    typer.echo(f"\n=== готово ===")
    typer.echo(f"  ok:              {stats['ok']}")
    typer.echo(f"  skipped:         {stats['skipped']}")
    typer.echo(f"  errors:          {stats['error']}")
    typer.echo(f"  sections filled: {stats['filled_sections_total']}")


if __name__ == "__main__":
    app()
