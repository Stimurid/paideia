"""Целевое извлечение AI-персон и подкейсов из ТюмГУ-презентации.

Запуск:
    python -m scripts.extract_tyumgu_personas --pptx "<путь>"
    python -m scripts.extract_tyumgu_personas --pptx "..." --save   # сохранить в content/cases/

Без --save выводит только список найденного для ревью.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import frontmatter
import typer

from api.agent import _extract_json
from api.extractors import extract_file
from api.llm import get_llm

app = typer.Typer(no_args_is_help=False, add_completion=False)
ROOT = Path(__file__).resolve().parent.parent
CASES_DIR = ROOT / "content" / "cases"
PROMPT_PATH = ROOT / "prompts" / "extract_tyumgu_personas.md"


def _save_persona(cand: dict, today: str) -> tuple[Path, bool]:
    cid = cand.get("id")
    if not cid:
        return Path(), False
    path = CASES_DIR / f"{cid}.md"
    if path.exists():
        return path, False

    fm = {
        "id": cid,
        "name": cand.get("name") or cid,
        "organization": {"name": "Tyumen State University (ТюмГУ)", "type": "U", "country": "RU"},
        "ai": {
            "pattern": "C",
            "agentivity": 2,
            "technologies": [],
            "role": cand.get("function") or "AI-персона",
        },
        "facets": {"orchestration": "MOD", "pedagogy": "ROLE", "control": "HYBR"},
        "transformation_mode": "experimental-cell",
        "lifecycle": {"stage": "rollout", "first_seen": "tyumgu-extract-" + today[:7]},
        "sources": [{"url": "Раведовская_ИИ_в_образовании.pptx", "type": "official", "accessed": today[:7]}],
        "verified": False,
        "canvas": {
            "signature_context": {
                "text": (
                    f"AI-персона {cand.get('name','?').split('·')[-1].strip()}, описанная в презентации "
                    f"ТюмГУ SAS. Функция: {cand.get('function') or 'не указана'}. "
                    f"Используется в курсах: {', '.join(cand.get('host_courses') or []) or 'не указано'}."
                ),
                "status": "draft", "source": "imported", "updated_at": today,
            },
        },
    }
    if cand.get("anthropomorphic_traits"):
        fm["canvas"]["ai_role"] = {
            "text": cand["anthropomorphic_traits"],
            "status": "draft", "source": "imported", "updated_at": today,
        }
    if cand.get("interaction_mode"):
        fm["canvas"]["interaction_scenario"] = {
            "text": cand["interaction_mode"],
            "status": "draft", "source": "imported", "updated_at": today,
        }
    if cand.get("evaluation_evidence"):
        fm["canvas"]["metrics_evidence"] = {
            "text": cand["evaluation_evidence"],
            "status": "draft", "source": "imported", "updated_at": today,
        }
    if cand.get("source_excerpt"):
        fm["canvas"]["sources_verification"] = {
            "text": f"Извлечено из ТюмГУ-презентации (confidence: {cand.get('confidence','?')}).\n\n{cand['source_excerpt']}",
            "status": "draft", "source": "imported", "updated_at": today,
        }
    body = f"\n## Описание\n\nAI-персона из ТюмГУ-программы. См. родительский кейс tyumgu-sas-ai-program.\n"
    post = frontmatter.Post(content=body, **fm)
    raw = frontmatter.dumps(post, handler=frontmatter.YAMLHandler(),
                            default_flow_style=False, allow_unicode=True, sort_keys=False)
    path.write_text(raw + "\n", encoding="utf-8")
    return path, True


def _save_course(cand: dict, today: str) -> tuple[Path, bool]:
    cid = cand.get("id")
    if not cid:
        return Path(), False
    path = CASES_DIR / f"{cid}.md"
    if path.exists():
        return path, False
    fm = {
        "id": cid,
        "name": cand.get("name") or cid,
        "organization": {"name": "Tyumen State University (ТюмГУ)", "type": "U", "country": "RU"},
        "ai": {
            "pattern": "C",
            "agentivity": 2,
            "technologies": [],
            "role": cand.get("ai_role_in_course") or "AI-роли в курсе",
        },
        "facets": {"orchestration": "MOD", "pedagogy": "ROLE", "control": "HYBR"},
        "transformation_mode": "experimental-cell",
        "lifecycle": {"stage": "pilot", "first_seen": "tyumgu-extract-" + today[:7]},
        "sources": [{"url": "Раведовская_ИИ_в_образовании.pptx", "type": "official", "accessed": today[:7]}],
        "verified": False,
        "canvas": {
            "signature_context": {
                "text": (
                    f"Курс-эксперимент ТюмГУ SAS: {cand.get('discipline') or cand.get('name')}. "
                    f"{('Студентов: ' + str(cand['students_count']) + '. ') if cand.get('students_count') else ''}"
                    f"AI-персоны: {', '.join(cand.get('personas_used') or []) or 'не указаны'}."
                ),
                "status": "draft", "source": "imported", "updated_at": today,
            },
        },
    }
    if cand.get("architecture"):
        fm["canvas"]["interaction_scenario"] = {
            "text": cand["architecture"],
            "status": "draft", "source": "imported", "updated_at": today,
        }
    if cand.get("assessment"):
        fm["canvas"]["metrics_evidence"] = {
            "text": cand["assessment"],
            "status": "draft", "source": "imported", "updated_at": today,
        }
    if cand.get("source_excerpt"):
        fm["canvas"]["sources_verification"] = {
            "text": f"Извлечено из ТюмГУ-презентации (confidence: {cand.get('confidence','?')}).\n\n{cand['source_excerpt']}",
            "status": "draft", "source": "imported", "updated_at": today,
        }
    body = f"\n## Описание\n\n{cand.get('name','')}\n"
    post = frontmatter.Post(content=body, **fm)
    raw = frontmatter.dumps(post, handler=frontmatter.YAMLHandler(),
                            default_flow_style=False, allow_unicode=True, sort_keys=False)
    path.write_text(raw + "\n", encoding="utf-8")
    return path, True


def _save_parent(parent: dict, today: str) -> tuple[Path, bool]:
    cid = parent.get("id") or "tyumgu-sas-ai-program"
    path = CASES_DIR / f"{cid}.md"
    fm = {
        "id": cid,
        "name": parent.get("name") or "ТюмГУ SAS · Программа AI в образовании",
        "organization": {"name": "Tyumen State University (ТюмГУ)", "type": "U", "country": "RU"},
        "ai": {
            "pattern": parent.get("ai_pattern") or "D",
            "agentivity": parent.get("agentivity") or 3,
            "technologies": [],
            "role": "распределённая команда AI-персон + ролевая модель преподавателей",
        },
        "facets": {"orchestration": "META", "pedagogy": "ROLE", "control": "HYBR", "economy": "BUD"},
        "transformation_mode": "rectoral-initiative",
        "lifecycle": {"stage": parent.get("lifecycle_stage") or "rollout",
                      "first_seen": "tyumgu-extract-" + today[:7]},
        "sources": [{"url": "Раведовская_ИИ_в_образовании.pptx", "type": "official", "accessed": today[:7]}],
        "verified": False,
        "canvas": {
            "signature_context": {
                "text": parent.get("summary") or "ТюмГУ SAS — программа замены/дополнения профессора AI-персонами + распределённая ролевая модель.",
                "status": "draft", "source": "imported", "updated_at": today,
            },
        },
    }
    if parent.get("key_roles"):
        fm["canvas"]["team_roles"] = {
            "text": "Ролевая модель команды:\n\n- " + "\n- ".join(parent["key_roles"]),
            "status": "draft", "source": "imported", "updated_at": today,
        }
    if parent.get("metrics_mentioned"):
        fm["canvas"]["metrics_evidence"] = {
            "text": "Метрики/масштаб, упомянутые в презентации:\n\n- " + "\n- ".join(parent["metrics_mentioned"]),
            "status": "draft", "source": "imported", "updated_at": today,
        }
    body = "\n## Описание\n\nМатеринский кейс ТюмГУ — рамочный проект. См. дочерние кейсы AI-персон и курсов-экспериментов с префиксом tyumgu-.\n"
    if path.exists():
        # для родителя обновляем (всегда), но безопасно — мерджим канвас
        post = frontmatter.load(path)
        existing_canvas = post.metadata.get("canvas") or {}
        for k, v in fm["canvas"].items():
            if k not in existing_canvas or not existing_canvas[k].get("text"):
                existing_canvas[k] = v
        fm["canvas"] = existing_canvas
        for k in ["organization", "ai", "facets", "transformation_mode", "lifecycle"]:
            if k in post.metadata and post.metadata[k] and not fm.get(k):
                fm[k] = post.metadata[k]
    post = frontmatter.Post(content=body, **fm)
    raw = frontmatter.dumps(post, handler=frontmatter.YAMLHandler(),
                            default_flow_style=False, allow_unicode=True, sort_keys=False)
    path.write_text(raw + "\n", encoding="utf-8")
    return path, True


@app.command()
def main(
    pptx: str = typer.Option(..., help="Путь к презентации"),
    save: bool = typer.Option(False, help="Сохранить в content/cases/"),
    model: str = typer.Option("deep", help="deep (gpt-5) или fast (gpt-4.1-mini)"),
) -> None:
    pptx_path = Path(pptx)
    if not pptx_path.exists():
        typer.echo(f"file not found: {pptx_path}")
        raise typer.Exit(1)

    data = pptx_path.read_bytes()
    extracted = extract_file(pptx_path.name, data)
    text = extracted["text"]
    typer.echo(f"extracted {len(text)} chars from {extracted.get('slide_count')} slides")

    # кеш: если уже извлекали — переиспользуем JSON, не дёргаем LLM повторно
    cache_path = ROOT / "db" / f"_extract_cache_{pptx_path.stem}.json"
    parsed = None
    if cache_path.exists():
        try:
            parsed = json.loads(cache_path.read_text(encoding="utf-8"))
            typer.echo(f"using cached result: {cache_path.name}")
        except Exception:
            parsed = None

    if not parsed:
        system_prompt = PROMPT_PATH.read_text(encoding="utf-8")
        llm = get_llm()
        typer.echo(f"calling LLM ({model}) ...")
        method = llm.chat_deep if model == "deep" else llm.chat_fast
        raw = method([
            {"role": "system", "content": system_prompt + "\n\nВыведи только JSON."},
            {"role": "user", "content": f"ПРЕЗЕНТАЦИЯ:\n\n{text}\n\nВыдай строгий JSON."},
        ])
        parsed = _extract_json(raw)
        if not parsed:
            typer.echo("could not parse JSON:")
            typer.echo(raw[:500])
            raise typer.Exit(2)
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps(parsed, ensure_ascii=False, indent=2), encoding="utf-8")
        typer.echo(f"cached: {cache_path.name}")

    parent = parsed.get("parent_case") or {}
    personas = parsed.get("personas") or []
    courses = parsed.get("course_experiments") or []

    typer.echo(f"\n=== РОДИТЕЛЬСКИЙ КЕЙС ===")
    typer.echo(f"  {parent.get('id')}: {parent.get('name')}")
    typer.echo(f"  agentivity={parent.get('agentivity')}, pattern={parent.get('ai_pattern')}")

    typer.echo(f"\n=== AI-ПЕРСОНЫ ({len(personas)}) ===")
    for p in personas:
        typer.echo(f"  · {p.get('id')}: {p.get('name')} [{p.get('confidence')}]")
        if p.get('function'): typer.echo(f"      функция: {p['function']}")

    typer.echo(f"\n=== КУРСЫ-ЭКСПЕРИМЕНТЫ ({len(courses)}) ===")
    for c in courses:
        typer.echo(f"  · {c.get('id')}: {c.get('name')} [{c.get('confidence')}]")
        if c.get('discipline'): typer.echo(f"      дисциплина: {c['discipline']}")

    typer.echo(f"\nnotes: {parsed.get('notes','')}\n")

    if not save:
        typer.echo("dry-run, ничего не сохранено. Запусти с --save чтобы создать карточки.")
        return

    today = date.today().isoformat()
    saved, skipped = [], []

    p, created = _save_parent(parent, today)
    if created or p.exists():
        saved.append(parent.get("id", "tyumgu-sas-ai-program"))

    for cand in personas:
        _, created = _save_persona(cand, today)
        (saved if created else skipped).append(cand.get("id"))
    for cand in courses:
        _, created = _save_course(cand, today)
        (saved if created else skipped).append(cand.get("id"))

    typer.echo(f"\nsaved: {len(saved)} ({', '.join(s for s in saved if s)})")
    if skipped:
        typer.echo(f"skipped (already exist): {len(skipped)}")


if __name__ == "__main__":
    app()
