"""Orchestrator — регулятор метастабильности TRIZ-engine.

Не пайплайн, не роутер. Читает observables из БД (branches, system_model,
activity log) и принимает decisions: какого агента активировать, какой
конфликт усилить/погасить, нужно ли запустить KOSMOS, нужно ли остановить.

Source: architecture/04_ORCHESTRATOR_MODEL.md (FifthConstraint).
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Literal

from ..db import open_db, fetch_all
from .agents import active_agents_in_space


DecisionKind = Literal[
    "activate_agent", "deactivate_agent",
    "amplify_conflict", "suppress_conflict",
    "switch_space", "launch_kosmos",
    "stop_generation", "request_user_input",
    "propose_reconfiguration",
]


@dataclass
class Observables:
    """Что читает оркестратор из БД для принятия решений."""
    project_id: str
    space_id: str
    branch_count: int
    branches_by_maturity: dict[str, int] = field(default_factory=dict)
    contradiction_density: float = 0.0
    """contradictions / branches."""
    agent_activity: dict[str, int] = field(default_factory=dict)
    """agent_id → сколько раз применён в последних 20 ивентах."""
    minutes_since_last_event: float = 0.0
    cluster_imbalance: float = 0.0
    """0..1 — насколько кластеры неравномерны."""
    constraint_envelope_state: dict[str, int] = field(default_factory=dict)
    """{preserved, sacred, hidden, violated, suspended, redefined} → размер."""


@dataclass
class Decision:
    kind: DecisionKind
    target: str
    """agent_id / space_id / branch_id / 'system'."""
    rationale: str
    confidence: float = 0.5
    payload: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Observation
# ---------------------------------------------------------------------------


def observe(project_id: str, space_id: str | None = None) -> Observables:
    conn = open_db()
    try:
        # Branches
        branches = fetch_all(
            conn,
            "SELECT id, maturity, cluster FROM branches WHERE project_id = ?",
            (project_id,),
        )
        by_maturity: dict[str, int] = {}
        clusters: dict[str, int] = {}
        for b in branches:
            by_maturity[b["maturity"]] = by_maturity.get(b["maturity"], 0) + 1
            if b["cluster"]:
                clusters[b["cluster"]] = clusters.get(b["cluster"], 0) + 1

        # Contradictions из последнего system_model
        sm_row = conn.execute(
            "SELECT full_json FROM system_models WHERE project_id = ? "
            "ORDER BY updated_at DESC LIMIT 1",
            (project_id,),
        ).fetchone()
        contradictions = 0
        ce_state: dict[str, int] = {}
        if sm_row:
            import json as _json
            sm_data = _json.loads(sm_row["full_json"])
            contradictions = len(sm_data.get("contradictions") or [])
            ce = sm_data.get("constraint_envelope") or {}
            for k in ("preserved", "sacred", "hidden", "violated", "suspended", "redefined"):
                ce_state[k] = len(ce.get(k) or [])

        contradiction_density = (contradictions / branches.__len__()) if branches else 0.0

        # Agent activity за последние 20 ивентов
        activity_rows = fetch_all(
            conn,
            "SELECT actor_id, COUNT(*) AS n FROM triz_events "
            "WHERE actor_kind = 'agent' AND target_id IN "
            "  (SELECT id FROM branches WHERE project_id = ?) "
            "GROUP BY actor_id ORDER BY n DESC LIMIT 20",
            (project_id,),
        )
        agent_activity = {r["actor_id"]: r["n"] for r in activity_rows if r["actor_id"]}

        # Время с последнего ивента
        last = conn.execute(
            "SELECT MAX(created_at) AS t FROM triz_events "
            "WHERE target_id IN (SELECT id FROM branches WHERE project_id = ?)",
            (project_id,),
        ).fetchone()
        minutes_idle = 0.0
        if last and last["t"]:
            try:
                last_dt = datetime.fromisoformat(last["t"].replace(" ", "T"))
                delta = datetime.utcnow() - last_dt
                minutes_idle = delta.total_seconds() / 60.0
            except Exception:
                pass

        # Cluster imbalance: чем больше дисперсия размеров, тем выше
        if clusters and len(clusters) > 1:
            sizes = list(clusters.values())
            mean = sum(sizes) / len(sizes)
            var = sum((s - mean) ** 2 for s in sizes) / len(sizes)
            cluster_imb = min(1.0, var / (mean * mean + 1))
        else:
            cluster_imb = 0.0

        from .agents import default_space
        sp = space_id or default_space()["id"]

        return Observables(
            project_id=project_id,
            space_id=sp,
            branch_count=len(branches),
            branches_by_maturity=by_maturity,
            contradiction_density=contradiction_density,
            agent_activity=agent_activity,
            minutes_since_last_event=minutes_idle,
            cluster_imbalance=cluster_imb,
            constraint_envelope_state=ce_state,
        )
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Decisions
# ---------------------------------------------------------------------------


def decide(obs: Observables) -> list[Decision]:
    """По таблице из architecture/04_ORCHESTRATOR_MODEL.md."""
    decisions: list[Decision] = []
    active = set(active_agents_in_space(obs.space_id))

    # Слишком много вариантов → cluster+select
    if obs.branch_count > 30:
        decisions.append(Decision(
            kind="activate_agent", target="selector",
            rationale=f"branch_count={obs.branch_count} > 30 — нужен triage",
            confidence=0.9,
        ))

    # Слишком мало вариантов → push exploration через KOSMOS
    if obs.branch_count < 2:
        decisions.append(Decision(
            kind="launch_kosmos", target="system",
            rationale=f"branch_count={obs.branch_count} < 2 — нужна генерация",
            confidence=0.8,
            payload={"strategy_set": "default-6"},
        ))

    # Все seeds → push exploration
    seed_count = obs.branches_by_maturity.get("seed", 0)
    if seed_count > 0 and seed_count == obs.branch_count:
        decisions.append(Decision(
            kind="activate_agent", target="pedagogical-reconstructor",
            rationale="все branches на стадии seed — нужно surface ассумпций",
            confidence=0.7,
        ))

    # Много hidden ассумпций → activate frame-breaker
    hidden = obs.constraint_envelope_state.get("hidden", 0)
    if hidden >= 5:
        decisions.append(Decision(
            kind="activate_agent", target="frame-breaker",
            rationale=f"hidden constraints={hidden} — нужно радикализовать",
            confidence=0.6,
        ))

    # Нет противоречий → activate cutter
    if obs.contradiction_density < 0.1 and obs.branch_count >= 2:
        decisions.append(Decision(
            kind="activate_agent", target="pedagogical-contradiction-cutter",
            rationale="contradiction_density=0 — поле слишком гладкое",
            confidence=0.7,
        ))

    # Один и тот же агент применён 3+ раз подряд → diminishing returns
    for aid, n in obs.agent_activity.items():
        if n >= 3:
            decisions.append(Decision(
                kind="deactivate_agent", target=aid,
                rationale=f"agent {aid} применён {n} раз — diminishing returns",
                confidence=0.6,
            ))

    # Долгий idle → request user input
    if obs.minutes_since_last_event > 30 and obs.branch_count > 0:
        decisions.append(Decision(
            kind="request_user_input", target="system",
            rationale=f"idle {obs.minutes_since_last_event:.0f} min — нужна реплика юзера",
            confidence=0.5,
            payload={"suggestion": "выбери top-3 branches для углубления"},
        ))

    # Cluster imbalance > 0.7 → suggest cluster activation
    if obs.cluster_imbalance > 0.7:
        decisions.append(Decision(
            kind="activate_agent", target="frame-breaker",
            rationale=f"cluster_imbalance={obs.cluster_imbalance:.2f} — все идеи в одном кластере",
            confidence=0.5,
        ))

    # Все mutated/grounded но нет selected → triage
    grounded = obs.branches_by_maturity.get("grounded", 0)
    mutated = obs.branches_by_maturity.get("mutated", 0)
    selected = obs.branches_by_maturity.get("selected", 0)
    if (grounded + mutated) >= 4 and selected == 0:
        decisions.append(Decision(
            kind="activate_agent", target="selector",
            rationale=f"grounded+mutated={grounded+mutated} но selected=0 — нужен triage",
            confidence=0.8,
        ))

    # Quality gate всегда полезен перед export
    if "selected" in obs.branches_by_maturity:
        decisions.append(Decision(
            kind="activate_agent", target="quality-gate",
            rationale="есть selected branches — проверка перед export",
            confidence=0.4,
        ))

    return decisions


def explain_obs(obs: Observables) -> str:
    """Человекочитаемая сводка наблюдений (для UI)."""
    lines = [
        f"project: {obs.project_id} · space: {obs.space_id}",
        f"branches: {obs.branch_count} {obs.branches_by_maturity}",
        f"contradiction density: {obs.contradiction_density:.2f}",
        f"constraint envelope: {obs.constraint_envelope_state}",
        f"cluster imbalance: {obs.cluster_imbalance:.2f}",
        f"minutes idle: {obs.minutes_since_last_event:.1f}",
    ]
    if obs.agent_activity:
        lines.append(f"recent agents: {obs.agent_activity}")
    return "\n".join(lines)
