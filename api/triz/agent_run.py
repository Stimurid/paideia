"""AgentRun — process container с preview/apply/EventLog.

Все мутации в TRIZ-engine идут только через AgentRun, никаких прямых
записей. Жизненный цикл:

    start(profile) → запускается фоновая работа
        ↓
    run собирает PreviewOp[] от L1 агентов
        ↓
    status='awaiting_approval' + сохранение ops в artifacts
        ↓
    пользователь approve / reject через UI
        ↓
    apply() мутирует БД/файлы по approved ops
        ↓
    EventLog заполняется на каждом шаге
        ↓
    status='applied' или 'cancelled'/'failed'
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Literal

from ..db import open_db, fetch_all
from .agents import PreviewOp, active_agents_in_space, run_agent
from .repository import get_system_model, save_system_model
from .system_model import Branch, EducationalSystemModel


RunStatus = Literal[
    "pending", "running", "awaiting_approval", "applying",
    "applied", "failed", "cancelled",
]


@dataclass
class AgentRunSpec:
    project_id: str
    profile: str
    """kosmos | stakeholder_pressure | semester_sim | anti_washing | export_rpd | ..."""
    target_object_kind: str
    target_object_id: str
    goal: str = ""
    space_id: str | None = None
    policy: Literal["preview-required", "auto-apply", "hybrid"] = "preview-required"
    budget: dict[str, Any] = field(default_factory=lambda: {"max_steps": 20, "max_seconds": 300})
    stop_criteria: str = "ops_collected_or_max_steps"


# ---------------------------------------------------------------------------
# CRUD: AgentRun в БД
# ---------------------------------------------------------------------------


def create_run(spec: AgentRunSpec) -> str:
    """Создать AgentRun в pending. Возвращает run_id."""
    run_id = f"run-{uuid.uuid4().hex[:10]}"
    conn = open_db()
    try:
        now = datetime.utcnow().isoformat(timespec="seconds")
        conn.execute(
            """INSERT INTO agent_runs
               (id, project_id, target_object_kind, target_object_id, profile,
                goal, space_id, policy, budget_json, status, stop_criteria,
                artifacts_json, trace_json, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?, '[]', '[]', ?, ?)""",
            (run_id, spec.project_id, spec.target_object_kind,
             spec.target_object_id, spec.profile, spec.goal, spec.space_id,
             spec.policy, json.dumps(spec.budget), spec.stop_criteria,
             now, now),
        )
        conn.commit()
        _log_event(conn, run_id, "user", None, "propose",
                   spec.target_object_kind, spec.target_object_id,
                   payload={"profile": spec.profile, "goal": spec.goal})
    finally:
        conn.close()
    return run_id


def get_run(run_id: str) -> dict[str, Any] | None:
    conn = open_db()
    try:
        row = conn.execute(
            "SELECT * FROM agent_runs WHERE id = ?", (run_id,),
        ).fetchone()
        if not row:
            return None
        run = dict(row)
        run["budget"] = json.loads(run.get("budget_json") or "{}")
        run["artifacts"] = json.loads(run.get("artifacts_json") or "[]")
        run["trace"] = json.loads(run.get("trace_json") or "[]")
        return run
    finally:
        conn.close()


def list_runs(project_id: str, limit: int = 50) -> list[dict[str, Any]]:
    conn = open_db()
    try:
        return fetch_all(
            conn,
            "SELECT id, profile, goal, status, target_object_kind, "
            "target_object_id, space_id, created_at, updated_at "
            "FROM agent_runs WHERE project_id = ? "
            "ORDER BY created_at DESC LIMIT ?",
            (project_id, limit),
        )
    finally:
        conn.close()


def _set_run_status(conn: sqlite3.Connection, run_id: str, status: str,
                    artifacts: list[dict] | None = None,
                    trace: list[dict] | None = None) -> None:
    now = datetime.utcnow().isoformat(timespec="seconds")
    fields = ["status = ?", "updated_at = ?"]
    values: list[Any] = [status, now]
    if artifacts is not None:
        fields.append("artifacts_json = ?")
        values.append(json.dumps(artifacts, ensure_ascii=False))
    if trace is not None:
        fields.append("trace_json = ?")
        values.append(json.dumps(trace, ensure_ascii=False))
    values.append(run_id)
    conn.execute(
        f"UPDATE agent_runs SET {', '.join(fields)} WHERE id = ?",
        values,
    )
    conn.commit()


def _log_event(conn: sqlite3.Connection, run_id: str | None,
               actor_kind: str, actor_id: str | None,
               event_type: str, target_kind: str, target_id: str,
               operator_id: str | None = None,
               payload: dict | None = None,
               result: dict | None = None) -> None:
    conn.execute(
        """INSERT INTO triz_events
           (agent_run_id, actor_kind, actor_id, event_type,
            target_kind, target_id, operator_id, payload_json, result_json)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (run_id, actor_kind, actor_id, event_type, target_kind, target_id,
         operator_id,
         json.dumps(payload, ensure_ascii=False) if payload else None,
         json.dumps(result, ensure_ascii=False) if result else None),
    )
    conn.commit()


# ---------------------------------------------------------------------------
# Execute: собрать PreviewOp'ы от агентов
# ---------------------------------------------------------------------------


def execute_run(run_id: str) -> dict[str, Any]:
    """Собрать ops от агентов согласно profile.

    Для каждого profile — свой набор агентов и порядок вызова.
    Не мутирует state — только заполняет artifacts.
    """
    run = get_run(run_id)
    if not run:
        raise ValueError(f"run '{run_id}' not found")
    if run["status"] != "pending":
        raise ValueError(f"run '{run_id}' status='{run['status']}', expected 'pending'")

    conn = open_db()
    try:
        _set_run_status(conn, run_id, "running")

        # Загружаем target
        model = get_system_model(run["project_id"])
        if not model:
            _set_run_status(conn, run_id, "failed")
            return {"run_id": run_id, "status": "failed",
                    "error": "system_model not found for project"}

        # Branch = либо передан, либо создаём виртуальный «текущий» Branch из model
        branch = _virtual_branch_from_model(model)

        # Какие агенты запускать — по profile
        profile = run["profile"]
        agents_to_run = _agents_for_profile(profile, run.get("space_id"))

        all_ops: list[dict] = []
        trace: list[dict] = []

        for aid in agents_to_run:
            try:
                ops, meta = run_agent(aid, branch, model)
                trace.append({
                    "step": len(trace) + 1, "agent_id": aid,
                    "status": meta.get("status"),
                    "duration_ms": meta.get("duration_ms"),
                    "ops_count": len(ops),
                })
                for op in ops:
                    all_ops.append({
                        "op_id": f"op-{uuid.uuid4().hex[:8]}",
                        "agent_id": op.agent_id, "op_kind": op.op_kind,
                        "target_kind": op.target_kind, "target_id": op.target_id,
                        "payload": op.payload, "rationale": op.rationale,
                        "confidence": op.confidence, "decision": None,
                    })
                _log_event(conn, run_id, "agent", aid, "preview",
                           branch.id if op.target_kind == "branch" else model.id,
                           branch.id if op.target_kind == "branch" else model.id,
                           payload={"ops_count": len(ops)})
            except Exception as exc:
                trace.append({
                    "step": len(trace) + 1, "agent_id": aid,
                    "status": "error", "error": str(exc)[:300],
                })

        # auto-apply или ждать пользователя
        next_status = "applied" if run.get("policy") == "auto-apply" else "awaiting_approval"
        _set_run_status(conn, run_id, next_status,
                        artifacts=all_ops, trace=trace)

        if next_status == "applied":
            apply_run(run_id, approved_op_ids=[op["op_id"] for op in all_ops])

        return {"run_id": run_id, "status": next_status,
                "ops_count": len(all_ops), "trace": trace}
    finally:
        conn.close()


def _agents_for_profile(profile: str, space_id: str | None) -> list[str]:
    """Какие L1 агенты запускаются в каком profile."""
    if profile == "kosmos":
        from .kosmos import KOSMOS_DEFAULT_AGENTS
        return KOSMOS_DEFAULT_AGENTS
    if profile == "stakeholder_pressure":
        return ["quality-gate", "stabilizer", "pedagogical-contradiction-cutter"]
    if profile == "semester_sim":
        return ["methodological-grounder", "stabilizer", "quality-gate"]
    if profile == "anti_washing":
        return ["quality-gate", "stabilizer", "pedagogical-reconstructor"]
    if profile == "export_rpd":
        return ["quality-gate", "stabilizer", "methodological-grounder"]
    if profile == "time_machine":
        return ["pedagogical-reconstructor", "frame-breaker", "ideal-tracer"]
    if profile == "genealogy":
        return ["pedagogical-reconstructor", "curriculum-chimerizer"]
    if profile == "counter_corpus":
        return ["quality-gate", "stabilizer", "pedagogical-reconstructor"]
    if profile == "hypothesis_forge":
        return ["pedagogical-reconstructor", "pedagogical-contradiction-cutter",
                "ideal-tracer", "quality-gate"]
    if profile == "default":
        return active_agents_in_space(space_id) or [
            "pedagogical-reconstructor", "pedagogical-contradiction-cutter",
            "methodological-grounder", "quality-gate",
        ]
    return active_agents_in_space(space_id) or []


def _virtual_branch_from_model(model: EducationalSystemModel) -> Branch:
    """Если у проекта нет явных Branch — создаём виртуальный для агентов."""
    return Branch(
        id=f"vbr-{model.project_id}",
        project_id=model.project_id,
        system_model_id=model.id,
        title=f"{model.title} (base)",
        current_formulation=model.function or "(не сформулирована)",
        maturity=model.maturity,
    )


# ---------------------------------------------------------------------------
# Apply: применить approved ops
# ---------------------------------------------------------------------------


def apply_run(run_id: str, *, approved_op_ids: list[str]) -> dict[str, Any]:
    """Применить approved-ops к state. Мутирует БД."""
    run = get_run(run_id)
    if not run:
        raise ValueError(f"run '{run_id}' not found")

    artifacts = run.get("artifacts") or []
    if not artifacts:
        return {"run_id": run_id, "status": "no_ops"}

    approved = [op for op in artifacts if op["op_id"] in approved_op_ids]
    rejected = [op for op in artifacts if op["op_id"] not in approved_op_ids]

    conn = open_db()
    try:
        _set_run_status(conn, run_id, "applying")

        model = get_system_model(run["project_id"])
        applied: list[str] = []
        failures: list[dict] = []

        for op in approved:
            try:
                _apply_one(conn, run_id, op, model)
                op["decision"] = "approved"
                applied.append(op["op_id"])
                _log_event(conn, run_id, "user", None, "approve",
                           op["target_kind"], op["target_id"],
                           payload={"op_id": op["op_id"]})
                _log_event(conn, run_id, "user", None, "apply",
                           op["target_kind"], op["target_id"],
                           payload=op, result={"ok": True})
            except Exception as exc:
                op["decision"] = "failed"
                failures.append({"op_id": op["op_id"], "error": str(exc)[:300]})

        for op in rejected:
            op["decision"] = "rejected"
            _log_event(conn, run_id, "user", None, "reject",
                       op["target_kind"], op["target_id"],
                       payload={"op_id": op["op_id"]})

        # Persist обновлённый model если был мутирован
        if model:
            save_system_model(model)

        final_status = "applied" if not failures else "applied_with_failures"
        _set_run_status(conn, run_id, "applied", artifacts=artifacts)

        return {
            "run_id": run_id, "status": final_status,
            "applied_count": len(applied), "rejected_count": len(rejected),
            "failures": failures,
        }
    finally:
        conn.close()


def cancel_run(run_id: str) -> None:
    conn = open_db()
    try:
        _set_run_status(conn, run_id, "cancelled")
        _log_event(conn, run_id, "user", None, "reject",
                   "agent_run", run_id, payload={"reason": "cancelled by user"})
    finally:
        conn.close()


def _apply_one(conn: sqlite3.Connection, run_id: str, op: dict,
               model: EducationalSystemModel | None) -> None:
    """Применить один PreviewOp к state.

    Для каждого op_kind — мутация по семантике. В случае любой ошибки —
    пробрасываем наружу для логирования в failures.
    """
    op_kind = op["op_kind"]
    payload = op.get("payload") or {}

    # Все «system_model»-мутации применяются к Pydantic-модели,
    # потом одной save_system_model() в конце execute_run/apply_run.
    if op_kind == "propose_constraint_addition" and model:
        ek = payload.get("envelope_key")
        val = payload.get("value")
        if ek and val:
            cur = getattr(model.constraint_envelope, ek, [])
            if val not in cur:
                cur.append(val)
                setattr(model.constraint_envelope, ek, cur)
        return

    if op_kind == "propose_contradiction" and model:
        from .system_model import Contradiction
        c = Contradiction(
            requirement_a=payload.get("requirement_a", ""),
            requirement_b=payload.get("requirement_b", ""),
            kind=payload.get("kind", "pedagogical"),
            intensity=payload.get("intensity", 3),
        )
        if not any(x.requirement_a == c.requirement_a and
                   x.requirement_b == c.requirement_b for x in model.contradictions):
            model.contradictions.append(c)
        return

    if op_kind == "set_stabilization_risk" and model:
        val = payload.get("value")
        if val is not None:
            model.constraint_envelope.stabilization_risk = val
        return

    if op_kind == "add_adjacent_impact" and model:
        descr = payload.get("description")
        if descr:
            model.constraint_envelope.adjacent_system_impact.append(descr)
        return

    if op_kind == "refine_dolzhno" and model:
        model.dolzhno.update({k: v for k, v in payload.items() if v})
        return

    if op_kind == "add_verification_criterion" and model:
        from .system_model import VerificationCriterion
        v = VerificationCriterion(
            metric=payload.get("metric", ""),
            method=payload.get("method", "expert"),
            target=payload.get("target"),
        )
        model.verification.append(v)
        return

    if op_kind == "add_flow" and model:
        from .system_model import FlowSpec
        f = FlowSpec(
            kind=payload.get("kind", "content"),
            description=payload.get("description", ""),
            rhythm=payload.get("rhythm"),
        )
        model.flows.append(f)
        return

    if op_kind == "add_engineering_note":
        # Заметки идут как новые элементы в branch — для виртуального
        # branch'а нет персистенции. Логируем как event и всё.
        return

    if op_kind in {"propose_invert", "propose_split", "propose_mutate", "propose_merge"}:
        # Эти ops создают предложения; реальная мутация Branch'ей —
        # отдельная фаза (создание Branch в branches таблице). Пока — log.
        return

    if op_kind == "propose_risk_note":
        return  # log only

    if op_kind == "propose_ifr":
        # Создаём IdealImage запись
        from .system_model import IdealImage
        ifr = IdealImage(
            id=f"ifr-{uuid.uuid4().hex[:8]}",
            branch_id=op["target_id"],
            formulation=payload.get("formulation", ""),
            resources_used=payload.get("resources_to_zero") or [],
            cost=payload.get("cost"),
            harm=payload.get("harm"),
            direction=payload.get("direction"),
        )
        conn.execute(
            """INSERT INTO ideal_images (id, branch_id, formulation, full_json)
               VALUES (?, ?, ?, ?)""",
            (ifr.id, ifr.branch_id, ifr.formulation, ifr.model_dump_json()),
        )
        return

    if op_kind == "quality_verdict":
        return  # log only — verdict живёт в trace

    if op_kind == "set_maturity":
        # Если есть реальный branch в БД — апдейтим maturity
        new_mat = payload.get("verdict")
        if new_mat in ("advance", "test", "quarantine"):
            mat_map = {"advance": "selected", "test": "tested", "quarantine": "quarantined"}
            conn.execute(
                "UPDATE branches SET maturity = ?, updated_at = ? WHERE id = ?",
                (mat_map[new_mat], datetime.utcnow().isoformat(timespec="seconds"),
                 op["target_id"]),
            )
        return

    if op_kind == "generic_response":
        return  # log only

    # Если op_kind не известен — это не критично, логируем и идём дальше.
    return
