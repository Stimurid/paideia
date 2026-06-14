"""Library ingest pipeline.

Запуск:
    python -m scripts.library_ingest <book_id>             # пройти все фазы
    python -m scripts.library_ingest <book_id> --only summarize
    python -m scripts.library_ingest <book_id> --only concepts

Фазы:
    1. extract_text  — текст из source-файла (pdfplumber/python-docx/...)
    2. split         — секции (по заголовкам или равномерно)
    3. chunk         — чанки для будущих embeddings (L5)
    4. summarize     — LLM-summary + topics
    5. concepts      — LLM concept extraction (по 2 секции за вызов)
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import typer

from api.agent import _extract_json
from api.db import open_db, fetch_all
from api.library import (
    chunk_sections, embed_chunks_for_book, extract_text, get_book,
    register_book, save_concepts, save_source_file, set_status,
    split_into_sections, _update_book,
)
from api.llm import get_llm

app = typer.Typer(no_args_is_help=False, add_completion=False)
ROOT = Path(__file__).resolve().parent.parent


def phase_summarize(book_id: str) -> dict:
    book = get_book(book_id)
    if not book:
        return {"status": "error", "msg": "book not found"}

    text_path = ROOT / "content" / "library" / book_id / "extracted.txt"
    if not text_path.exists():
        return {"status": "error", "msg": "extracted.txt missing — run extract first"}

    full = text_path.read_text(encoding="utf-8")
    # для саммари: первые 12k + кусок из середины + кусок из конца
    n = len(full)
    head = full[:12000]
    mid = full[n//2 : n//2 + 3000] if n > 18000 else ""
    tail = full[-3000:] if n > 25000 else ""
    sample = head + ("\n\n[...]\n\n" + mid if mid else "") + ("\n\n[...]\n\n" + tail if tail else "")

    prompt_path = ROOT / "prompts" / "library_summarize.md"
    system_prompt = prompt_path.read_text(encoding="utf-8")
    user_prompt = (
        f"title: {book['title']}\nauthors: {book.get('authors') or '?'}\n"
        f"year: {book.get('year') or '?'}\n"
        f"text length: {n} chars\n\n=== ТЕКСТ ===\n\n{sample}"
    )

    started = time.time()
    llm = get_llm()
    raw = llm.chat_fast([
        {"role": "system", "content": system_prompt + "\n\nВыведи только JSON."},
        {"role": "user", "content": user_prompt},
    ])
    duration = time.time() - started
    parsed = _extract_json(raw)
    if not parsed:
        return {"status": "parse-fail", "raw_preview": raw[:300]}

    _update_book(
        book_id,
        summary=parsed.get("summary", "")[:5000],
        topics_json=json.dumps(parsed.get("topics") or [], ensure_ascii=False),
        status="summary_ready",
    )
    return {
        "status": "ok",
        "summary_chars": len(parsed.get("summary", "")),
        "topics": parsed.get("topics", []),
        "depth": parsed.get("depth_level"),
        "value": parsed.get("estimated_value_for_paideia"),
        "duration_s": round(duration, 1),
    }


def phase_concepts(book_id: str, max_sections: int = 0) -> dict:
    """LLM-extraction концептов. По 2 секции за вызов."""
    book = get_book(book_id)
    if not book:
        return {"status": "error", "msg": "book not found"}

    sections = book.get("sections") or []
    if not sections:
        return {"status": "error", "msg": "no sections — run split first"}

    # ограничение для длинных книг (чтобы не разорить токенами)
    if max_sections > 0:
        sections = sections[:max_sections]

    prompt_path = ROOT / "prompts" / "library_concepts.md"
    system_prompt = prompt_path.read_text(encoding="utf-8")

    # Каталог теории — компактно
    conn = open_db()
    try:
        types_ = fetch_all(conn, "SELECT id, name FROM types ORDER BY id")
        hyps = fetch_all(conn, "SELECT id, name FROM hypotheses ORDER BY id")
        tens = fetch_all(conn, "SELECT id, name FROM tensions ORDER BY id")
        modes = fetch_all(conn, "SELECT id, name FROM modes ORDER BY id")
    finally:
        conn.close()
    theory_ctx = (
        "Типы: " + ", ".join(f"{t['id']}={t['name']}" for t in types_) + "\n"
        "Гипотезы: " + ", ".join(f"{h['id']}={h['name']}" for h in hyps) + "\n"
        "Противоречия: " + ", ".join(f"{t['id']}={t['name']}" for t in tens) + "\n"
        "Моды: " + ", ".join(f"{m['id']}={m['name']}" for m in modes)
    )

    # Группируем секции по 2 в одном вызове
    llm = get_llm()
    total_extracted = 0
    failed: list[dict] = []

    for i in range(0, len(sections), 2):
        batch = sections[i:i+2]
        # текст секций — берём из library_chunks (склеиваем)
        conn = open_db()
        try:
            chunks_text = []
            for sec in batch:
                rows = fetch_all(
                    conn,
                    "SELECT text FROM library_chunks WHERE section_id = ? ORDER BY chunk_num",
                    (sec["id"],),
                )
                txt = "".join(r["text"] for r in rows)
                chunks_text.append(f"=== Section {sec['section_num']}: {sec.get('title') or '(без заголовка)'} ===\n{txt}")
        finally:
            conn.close()

        existing = [c["name"] for c in fetch_all(
            open_db(), "SELECT name FROM library_concepts WHERE book_id = ?", (book_id,),
        )]

        user_prompt = (
            f"book: {book['title']} / {book.get('authors') or '?'}\n"
            f"book_summary: {(book.get('summary') or '')[:800]}\n\n"
            f"=== ТЕОРИЯ PAIDEIA ===\n{theory_ctx}\n\n"
            f"=== СУЩЕСТВУЮЩИЕ КОНЦЕПТЫ ({len(existing)}) ===\n"
            f"{', '.join(existing[:30])}\n\n"
            f"=== ФРАГМЕНТ ({len(batch)} секции) ===\n\n"
            + "\n\n".join(chunks_text)[:14000]
        )

        try:
            started = time.time()
            raw = llm.chat_fast([
                {"role": "system", "content": system_prompt + "\n\nВыведи только JSON."},
                {"role": "user", "content": user_prompt},
            ])
            duration = time.time() - started
            parsed = _extract_json(raw)
            if not parsed or "concepts" not in parsed:
                failed.append({"section_idx": i, "reason": "parse-fail"})
                continue
            n = save_concepts(book_id, parsed["concepts"], section_id=batch[0]["id"])
            total_extracted += n
            typer.echo(f"  sec {batch[0]['section_num']}-{batch[-1]['section_num']}: +{n} ({duration:.1f}s)")
        except Exception as exc:
            failed.append({"section_idx": i, "error": str(exc)[:200]})

    set_status(book_id, "ready")
    return {
        "status": "ok",
        "extracted": total_extracted,
        "failed_batches": failed,
        "sections_processed": len(sections),
    }


def phase_full(book_id: str, max_sections: int = 0) -> dict:
    typer.echo(f"  [1/6] extract text...")
    text = extract_text(book_id)
    typer.echo(f"        ✓ {len(text)} chars")
    typer.echo(f"  [2/6] split sections...")
    sections = split_into_sections(book_id, text)
    typer.echo(f"        ✓ {len(sections)} sections")
    typer.echo(f"  [3/6] chunk for embeddings...")
    n_chunks = chunk_sections(book_id, sections)
    typer.echo(f"        ✓ {n_chunks} chunks")
    typer.echo(f"  [4/6] embed chunks...")
    n_emb = embed_chunks_for_book(book_id)
    typer.echo(f"        ✓ {n_emb} embeddings")
    typer.echo(f"  [5/6] summarize...")
    s = phase_summarize(book_id)
    typer.echo(f"        ✓ {s.get('status')} · {len(s.get('topics') or [])} topics")
    typer.echo(f"  [6/6] extract concepts...")
    c = phase_concepts(book_id, max_sections=max_sections)
    typer.echo(f"        ✓ {c.get('extracted')} concepts")
    return {"sections": len(sections), "chunks": n_chunks,
            "embeddings": n_emb, "summary": s, "concepts": c}


@app.command()
def main(
    book_id: str = typer.Argument(...),
    only: str = typer.Option("", help="extract | split | chunk | embed | summarize | concepts | full"),
    max_sections: int = typer.Option(0, help="ограничить число секций для concept extraction"),
) -> None:
    if only == "extract":
        text = extract_text(book_id)
        typer.echo(f"extracted {len(text)} chars")
    elif only == "split":
        from api.library import get_book as _gb
        text_path = ROOT / "content" / "library" / book_id / "extracted.txt"
        if not text_path.exists():
            typer.echo("run extract first"); raise typer.Exit(1)
        sections = split_into_sections(book_id, text_path.read_text(encoding="utf-8"))
        typer.echo(f"{len(sections)} sections")
    elif only == "chunk":
        book = get_book(book_id)
        text_path = ROOT / "content" / "library" / book_id / "extracted.txt"
        full = text_path.read_text(encoding="utf-8")
        n = chunk_sections(book_id, [{"id": s["id"], "num": s["section_num"],
                                       "text": full[s["char_start"]:s["char_end"]],
                                       "char_start": s["char_start"],
                                       "char_end": s["char_end"]} for s in book["sections"]])
        typer.echo(f"{n} chunks")
    elif only == "embed":
        n = embed_chunks_for_book(book_id)
        typer.echo(f"{n} embeddings written")
    elif only == "summarize":
        r = phase_summarize(book_id)
        typer.echo(json.dumps(r, ensure_ascii=False, indent=2))
    elif only == "concepts":
        r = phase_concepts(book_id, max_sections=max_sections)
        typer.echo(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        r = phase_full(book_id, max_sections=max_sections)
        typer.echo("\n=== готово ===")
        typer.echo(json.dumps(r, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    app()
