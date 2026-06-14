"""γ · Reflexive corpus — Paideia мониторит свои собственные проекты.

Pipeline:
    1. embed_projects() — embeddings всех проектов в content/projects/*.md
    2. cluster_projects() — DBSCAN-like: пары с cosine > THRESHOLD сливаются
       в кластер; одиночки игнорируются
    3. analyze_cluster() — LLM-промпт на кластер → паттерны
    4. сохранение в reflexive_patterns
    5. promote() — превращение паттерна в corpus_candidate

Это вторая обратная связь к корпусу (после course-conveyor).
"""

from __future__ import annotations

import hashlib
import json
import time
import uuid
from pathlib import Path
from typing import Any

import frontmatter

from .agent import _extract_json
from .db import open_db, fetch_all, fetch_one
from .library import _embed_batch, _floats_to_blob
from .llm import get_llm

ROOT = Path(__file__).resolve().parent.parent
PROMPTS = ROOT / "prompts"

CLUSTER_SIM_THRESHOLD = 0.72  # cosine similarity для слипания пар в кластер
MIN_CLUSTER_SIZE = 2
MAX_CLUSTERS_PER_SCAN = 8


def _ensure_tables() -> None:
    conn = open_db()
    try:
        conn.execute(
            "CREATE VIRTUAL TABLE IF NOT EXISTS projects_vec USING vec0("
            "project_id TEXT PRIMARY KEY, embedding FLOAT[1536])"
        )
        conn.commit()
    finally:
        conn.close()


def _project_text(project_id: str) -> str | None:
    """Текстовое представление проекта для embedding/анализа."""
    path = ROOT / "content" / "projects" / f"{project_id}.md"
    if not path.exists():
        return None
    post = frontmatter.load(path)
    fm = post.metadata
    parts: list[str] = [
        f"проект: {fm.get('name')}",
        f"id: {project_id}",
    ]
    if fm.get("facets"):
        parts.append("фасеты: " + json.dumps(fm["facets"], ensure_ascii=False))
    if fm.get("transformation_mode"):
        parts.append(f"режим трансформации: {fm['transformation_mode']}")
    canvas = fm.get("canvas") or {}
    for sec_id, sec in canvas.items():
        text = (sec or {}).get("text", "").strip()
        if text:
            parts.append(f"{sec_id}: {text[:600]}")
    return "\n\n".join(parts)


def embed_projects(force: bool = False) -> dict:
    """Посчитать embeddings всех проектов в content/projects/."""
    _ensure_tables()
    projects_dir = ROOT / "content" / "projects"
    if not projects_dir.exists():
        return {"status": "error", "msg": "content/projects/ not found"}

    all_ids = [p.stem for p in projects_dir.glob("*.md")]
    if not all_ids:
        return {"status": "error", "msg": "no projects"}

    conn = open_db()
    try:
        if force:
            conn.execute("DELETE FROM projects_vec")
            conn.commit()
        existing = {r["project_id"] for r in fetch_all(
            conn, "SELECT project_id FROM projects_vec",
        )}
    finally:
        conn.close()

    todo = [pid for pid in all_ids if pid not in existing]
    if not todo:
        return {"status": "ok", "embedded": 0, "total": len(all_ids),
                "msg": "all embedded"}

    # батчем
    total = 0
    for i in range(0, len(todo), 16):
        batch_ids = todo[i:i + 16]
        texts = []
        valid_ids = []
        for pid in batch_ids:
            text = _project_text(pid)
            if text:
                texts.append(text[:8000])
                valid_ids.append(pid)
        if not texts:
            continue
        embs = _embed_batch(texts)
        conn = open_db()
        try:
            for pid, e in zip(valid_ids, embs):
                conn.execute(
                    "INSERT OR REPLACE INTO projects_vec (project_id, embedding) VALUES (?, ?)",
                    (pid, _floats_to_blob(e)),
                )
                total += 1
            conn.commit()
        finally:
            conn.close()
    return {"status": "ok", "embedded": total, "total": len(all_ids)}


def find_clusters(threshold: float = CLUSTER_SIM_THRESHOLD,
                   min_size: int = MIN_CLUSTER_SIZE) -> list[list[str]]:
    """Простая union-find кластеризация по cosine similarity.
    Возвращает [[project_id, ...], ...] для кластеров size >= min_size."""
    _ensure_tables()
    conn = open_db()
    try:
        all_ids = [r["project_id"] for r in fetch_all(
            conn, "SELECT project_id FROM projects_vec",
        )]
        if len(all_ids) < 2:
            return []
        # union-find
        parent = {pid: pid for pid in all_ids}
        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x
        def union(a, b):
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[ra] = rb

        # для каждого id ищем top-k соседей через vec0
        for pid in all_ids:
            row = conn.execute(
                "SELECT embedding FROM projects_vec WHERE project_id = ?", (pid,)
            ).fetchone()
            if not row:
                continue
            neighbors = fetch_all(
                conn,
                """SELECT project_id, distance FROM projects_vec
                   WHERE embedding MATCH ? AND k = 6
                   ORDER BY distance""",
                (row[0],),
            )
            for n in neighbors:
                if n["project_id"] == pid:
                    continue
                sim = 1.0 - min(n["distance"], 1.0)
                if sim >= threshold:
                    union(pid, n["project_id"])
    finally:
        conn.close()

    # собираем группы
    groups: dict[str, list[str]] = {}
    for pid in all_ids:
        root = pid
        while parent[root] != root:
            root = parent[root]
        groups.setdefault(root, []).append(pid)
    return [g for g in groups.values() if len(g) >= min_size]


def _cluster_signature(project_ids: list[str]) -> str:
    return hashlib.sha256(",".join(sorted(project_ids)).encode()).hexdigest()[:16]


def _project_brief_for_llm(project_id: str) -> str | None:
    path = ROOT / "content" / "projects" / f"{project_id}.md"
    if not path.exists():
        return None
    post = frontmatter.load(path)
    fm = post.metadata
    parts = [f"### {project_id}: {fm.get('name')}"]
    if fm.get("facets"):
        parts.append(f"фасеты: {json.dumps(fm['facets'], ensure_ascii=False)}")
    if fm.get("transformation_mode"):
        parts.append(f"режим: {fm['transformation_mode']}")
    canvas = fm.get("canvas") or {}
    # топ-5 заполненных секций
    filled = [(sid, (s or {}).get("text", "").strip())
              for sid, s in canvas.items() if (s or {}).get("text")]
    for sid, text in filled[:5]:
        parts.append(f"\n**{sid}**: {text[:500]}")
    return "\n".join(parts)


def analyze_cluster(project_ids: list[str], scan_id: str) -> dict:
    """LLM-анализ одного кластера. Сохраняет найденные паттерны."""
    if len(project_ids) < MIN_CLUSTER_SIZE:
        return {"status": "skipped", "reason": "cluster too small"}

    briefs = [_project_brief_for_llm(pid) for pid in project_ids]
    briefs = [b for b in briefs if b]
    if not briefs:
        return {"status": "error", "reason": "no project briefs"}

    system_prompt = (PROMPTS / "reflexive_pattern.md").read_text(encoding="utf-8")
    user_prompt = f"Кластер из {len(briefs)} проектов:\n\n" + "\n\n---\n\n".join(briefs)

    llm = get_llm()
    started = time.time()
    raw = llm.chat_deep([
        {"role": "system", "content": system_prompt + "\n\nВыведи только JSON."},
        {"role": "user", "content": user_prompt[:50000]},
    ])
    duration = time.time() - started
    parsed = _extract_json(raw)
    if not parsed or "patterns" not in parsed:
        return {"status": "parse-fail", "duration_s": round(duration, 1),
                "raw_preview": raw[:300]}

    patterns = parsed.get("patterns") or []
    if not patterns:
        return {"status": "ok", "patterns_saved": 0,
                "unknowns": parsed.get("unknowns", []),
                "duration_s": round(duration, 1)}

    sig = _cluster_signature(project_ids)
    saved = 0
    conn = open_db()
    try:
        for p in patterns[:3]:
            pid = "rfx-" + uuid.uuid4().hex[:10]
            kind = (p.get("kind") or "").strip()
            if kind not in ("recurring_failure", "recurring_success",
                            "emerging_theme", "blind_spot",
                            "hidden_contradiction"):
                continue
            conn.execute(
                """INSERT INTO reflexive_patterns
                   (id, scan_id, cluster_signature, cluster_size,
                    project_ids_json, pattern_kind, title, description,
                    evidence_json, proposed_corpus_action,
                    proposed_artifact_json, confidence)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (pid, scan_id, sig, len(project_ids),
                 json.dumps(project_ids, ensure_ascii=False),
                 kind, p.get("title", "")[:300],
                 (p.get("description") or "")[:2000],
                 json.dumps(p.get("evidence") or [], ensure_ascii=False),
                 p.get("proposed_corpus_action"),
                 json.dumps(p.get("proposed_artifact") or {}, ensure_ascii=False)
                 if p.get("proposed_artifact") else None,
                 max(1, min(5, int(p.get("confidence", 3) or 3)))),
            )
            saved += 1
        conn.commit()
    finally:
        conn.close()

    return {"status": "ok", "patterns_saved": saved,
            "duration_s": round(duration, 1)}


def run_scan() -> dict:
    """Полный прогон: embed → cluster → analyze. Один scan."""
    _ensure_tables()
    scan_id = "scan-" + uuid.uuid4().hex[:10]
    started = time.time()

    e_result = embed_projects()
    clusters = find_clusters()
    clusters = clusters[:MAX_CLUSTERS_PER_SCAN]

    cluster_results = []
    total_patterns = 0
    for cluster in clusters:
        r = analyze_cluster(cluster, scan_id)
        cluster_results.append({"size": len(cluster), **r})
        total_patterns += r.get("patterns_saved", 0)

    return {
        "scan_id": scan_id,
        "embedded": e_result.get("embedded", 0),
        "projects_total": e_result.get("total", 0),
        "clusters_analyzed": len(clusters),
        "patterns_saved": total_patterns,
        "duration_s": round(time.time() - started, 1),
        "cluster_results": cluster_results,
    }


def list_patterns(status: str = "pending", limit: int = 200) -> list[dict]:
    _ensure_tables()
    conn = open_db()
    try:
        rows = fetch_all(
            conn,
            """SELECT * FROM reflexive_patterns
               WHERE status = ? ORDER BY confidence DESC, created_at DESC LIMIT ?""",
            (status, limit),
        )
        for r in rows:
            r["project_ids"] = json.loads(r.get("project_ids_json") or "[]")
            r["evidence"] = json.loads(r.get("evidence_json") or "[]")
            r["proposed_artifact"] = (
                json.loads(r["proposed_artifact_json"])
                if r.get("proposed_artifact_json") else None
            )
        return rows
    finally:
        conn.close()


def promote_to_candidate(pattern_id: str, decided_by: str | None = None) -> dict:
    """Превратить паттерн в corpus_candidate."""
    from . import corpus_conveyor as cc
    conn = open_db()
    try:
        row = fetch_one(
            conn,
            "SELECT * FROM reflexive_patterns WHERE id = ?", (pattern_id,),
        )
        if not row:
            return {"status": "error", "msg": "pattern not found"}
        if row.get("status") == "promoted":
            return {"status": "ok", "msg": "already promoted",
                    "candidate_id": row.get("candidate_id")}
    finally:
        conn.close()

    action = row.get("proposed_corpus_action") or "none"
    mapping = {
        "new_hypothesis": "hypothesis_candidate",
        "new_counter_signal": "counter_signal_candidate",
        "new_scenario": "scenario_candidate",
        "new_type": "case_candidate",  # типы как кейсы для ручной правки
    }
    candidate_kind = mapping.get(action)
    if not candidate_kind:
        return {"status": "error", "msg": f"action '{action}' не promotable"}

    artifact = (
        json.loads(row["proposed_artifact_json"])
        if row.get("proposed_artifact_json") else {}
    )
    title = (artifact.get("name") or row["title"])[:300]
    body = artifact.get("thesis_or_description") or row.get("description", "")
    rationale = f"Reflexive-паттерн ({row['pattern_kind']}) из {row['cluster_size']} проектов."

    candidate_id = cc.add_candidate(
        kind=candidate_kind, title=title, body_md=body,
        source_type=f"reflexive_{row['pattern_kind']}",
        source_confidence=row.get("confidence") or 3,
        rationale=rationale,
    )

    conn = open_db()
    try:
        conn.execute(
            """UPDATE reflexive_patterns
               SET status = 'promoted', candidate_id = ?, decided_at = datetime('now'),
                   decided_by = ?
               WHERE id = ?""",
            (candidate_id, decided_by, pattern_id),
        )
        conn.commit()
    finally:
        conn.close()
    return {"status": "ok", "candidate_id": candidate_id}


def dismiss(pattern_id: str, decided_by: str | None = None) -> None:
    conn = open_db()
    try:
        conn.execute(
            """UPDATE reflexive_patterns
               SET status = 'dismissed', decided_at = datetime('now'),
                   decided_by = ?
               WHERE id = ?""",
            (decided_by, pattern_id),
        )
        conn.commit()
    finally:
        conn.close()


def stats() -> dict:
    _ensure_tables()
    conn = open_db()
    try:
        total = conn.execute("SELECT COUNT(*) FROM reflexive_patterns").fetchone()[0]
        embedded = conn.execute("SELECT COUNT(*) FROM projects_vec").fetchone()[0]
        by_status = fetch_all(
            conn, "SELECT status, COUNT(*) AS n FROM reflexive_patterns GROUP BY status"
        )
        by_kind = fetch_all(
            conn, "SELECT pattern_kind, COUNT(*) AS n FROM reflexive_patterns GROUP BY pattern_kind"
        )
        last_scan = conn.execute(
            "SELECT scan_id, MAX(created_at) AS at FROM reflexive_patterns GROUP BY scan_id ORDER BY at DESC LIMIT 1"
        ).fetchone()
        return {
            "total": total,
            "projects_embedded": embedded,
            "by_status": {r["status"]: r["n"] for r in by_status},
            "by_kind": {r["pattern_kind"]: r["n"] for r in by_kind},
            "last_scan_at": last_scan["at"] if last_scan else None,
        }
    finally:
        conn.close()
