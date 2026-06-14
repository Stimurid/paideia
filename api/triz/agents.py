"""L1 agent runtime — загрузка AgentSpec, запуск через LLM, propose-операции.

Каждый L1 агент:
1. Загружается из content/agents/L1/<agent_id>.md (yaml-фронтматтер + kernel).
2. При запуске получает context (Branch + SystemModel + опц. archive RAG).
3. Через LLM возвращает структурированный JSON-ответ.
4. Ответ не мутирует state напрямую — превращается в список PreviewOp,
   которые AgentRun обрабатывает через preview/apply.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import frontmatter
import yaml

from ..agent import _extract_json
from ..llm import get_llm
from .system_model import Branch, EducationalSystemModel

ROOT = Path(__file__).resolve().parent.parent.parent
AGENTS_DIR = ROOT / "content" / "agents" / "L1"
SPACES_PATH = ROOT / "taxonomy" / "spaces.yaml"


@dataclass
class AgentSpec:
    agent_id: str
    name: str
    level: str
    purpose: str
    activation_conditions: list[str]
    allowed_actions: list[str]
    forbidden_actions: list[str]
    cooperates_with: list[str]
    conflicts_with: list[str]
    quality_gates: list[str]
    kernel_prompt: str
    version: str
    status: str
    full: dict[str, Any] = field(default_factory=dict)


@dataclass
class PreviewOp:
    """Предложенная операция от агента. Применяется через AgentRun.apply()."""
    agent_id: str
    op_kind: str
    """кратко: propose_constraint_addition / propose_invert / set_stabilization_risk / ..."""
    target_kind: str
    """branch | system_model | ideal_image | agent_spec"""
    target_id: str
    payload: dict[str, Any]
    rationale: str = ""
    confidence: str = "medium"


def load_agent_spec(agent_id: str) -> AgentSpec:
    """Загрузка AgentSpec из md-файла content/agents/L1/<id>.md."""
    path = AGENTS_DIR / f"{agent_id}.md"
    if not path.exists():
        raise FileNotFoundError(f"agent '{agent_id}' not found at {path}")
    post = frontmatter.load(path)
    fm = post.metadata
    return AgentSpec(
        agent_id=fm["agent_id"],
        name=fm["name"],
        level=fm["level"],
        purpose=fm.get("purpose", ""),
        activation_conditions=fm.get("activation_conditions", []) or [],
        allowed_actions=fm.get("allowed_actions", []) or [],
        forbidden_actions=fm.get("forbidden_actions", []) or [],
        cooperates_with=fm.get("cooperates_with", []) or [],
        conflicts_with=fm.get("conflicts_with", []) or [],
        quality_gates=fm.get("quality_gates", []) or [],
        kernel_prompt=post.content.strip(),
        version=fm.get("version", "1.0.0"),
        status=fm.get("status", "draft"),
        full=fm,
    )


def list_agent_specs(status: str | None = "active") -> list[AgentSpec]:
    specs: list[AgentSpec] = []
    if not AGENTS_DIR.exists():
        return specs
    for p in sorted(AGENTS_DIR.glob("*.md")):
        try:
            spec = load_agent_spec(p.stem)
            if status is None or spec.status == status:
                specs.append(spec)
        except Exception:
            continue
    return specs


def load_spaces() -> list[dict[str, Any]]:
    if not SPACES_PATH.exists():
        return []
    with SPACES_PATH.open(encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data.get("spaces") or []


def get_space(space_id: str) -> dict[str, Any] | None:
    for s in load_spaces():
        if s["id"] == space_id:
            return s
    return None


def default_space() -> dict[str, Any]:
    for s in load_spaces():
        if s.get("is_default"):
            return s
    spaces = load_spaces()
    if not spaces:
        raise RuntimeError("no spaces defined in taxonomy/spaces.yaml")
    return spaces[0]


def active_agents_in_space(space_id: str | None = None) -> list[str]:
    space = get_space(space_id) if space_id else default_space()
    return space.get("active_agents", []) if space else []


# ---------------------------------------------------------------------------
# Run an L1 agent
# ---------------------------------------------------------------------------


def run_agent(agent_id: str, branch: Branch, model: EducationalSystemModel,
              *, archive_chunks: list[dict[str, Any]] | None = None
              ) -> tuple[list[PreviewOp], dict[str, Any]]:
    """Запустить L1 агента над Branch+SystemModel. Возвращает (preview_ops, meta).

    Не мутирует БД и не пишет в content/. Только LLM-вызов и формирование
    PreviewOp'ов для AgentRun.apply().
    """
    spec = load_agent_spec(agent_id)
    if spec.status != "active":
        raise ValueError(f"agent '{agent_id}' status={spec.status}, must be 'active'")

    # Контекст для LLM: компактная сводка
    ctx = {
        "branch": {
            "id": branch.id,
            "title": branch.title,
            "current_formulation": branch.current_formulation,
            "maturity": branch.maturity,
            "applied_operators": branch.applied_operators,
            "notes_engineering": branch.notes_engineering[-5:],
            "notes_risk": branch.notes_risk[-5:],
        },
        "system_model": {
            "title": model.title,
            "kind": model.kind,
            "function": model.function,
            "dano": model.dano,
            "dolzhno": model.dolzhno,
            "contradictions": [c.model_dump() for c in model.contradictions],
            "constraint_envelope": model.constraint_envelope.model_dump(),
            "working_organ": [r.model_dump() for r in model.working_organ],
            "flows": [f.model_dump() for f in model.flows],
            "transmission": model.transmission,
        },
    }
    if archive_chunks:
        ctx["archive_excerpts"] = archive_chunks[:5]

    user_prompt = (
        f"Контекст:\n```json\n{json.dumps(ctx, ensure_ascii=False, indent=2)}\n```\n\n"
        f"Выполни свою функцию согласно kernel-промпту. Верни строго JSON."
    )

    llm = get_llm()
    started = time.time()
    raw = llm.chat_fast([
        {"role": "system", "content": spec.kernel_prompt + "\n\nВыведи только JSON, без markdown-обёртки."},
        {"role": "user", "content": user_prompt},
    ])
    duration_ms = int((time.time() - started) * 1000)
    parsed = _extract_json(raw)
    if not parsed:
        return [], {
            "agent_id": agent_id, "status": "parse-fail",
            "duration_ms": duration_ms, "raw_preview": (raw or "")[:300],
        }

    ops = _build_preview_ops(spec, parsed, branch, model)
    return ops, {
        "agent_id": agent_id, "status": "ok",
        "duration_ms": duration_ms,
        "ops_count": len(ops),
        "raw_response": parsed,
    }


def _build_preview_ops(spec: AgentSpec, parsed: dict[str, Any],
                       branch: Branch, model: EducationalSystemModel
                       ) -> list[PreviewOp]:
    """Конвертация ответа агента в PreviewOp-ы по семантике.

    Для каждого типа агента — свой mapper, потому что JSON-схемы у них
    разные.
    """
    ops: list[PreviewOp] = []
    aid = spec.agent_id

    if aid == "pedagogical-reconstructor":
        for ass in parsed.get("new_hidden_assumptions") or []:
            ops.append(PreviewOp(
                agent_id=aid, op_kind="propose_constraint_addition",
                target_kind="system_model", target_id=model.id,
                payload={"envelope_key": "hidden", "value": ass},
                rationale="hidden assumption surfaced",
                confidence=parsed.get("confidence", "medium"),
            ))
        for note in parsed.get("risk_notes") or []:
            ops.append(PreviewOp(
                agent_id=aid, op_kind="propose_risk_note",
                target_kind="branch", target_id=branch.id,
                payload={"note": note},
                rationale="risk surfaced from hidden assumption",
            ))

    elif aid == "frame-breaker":
        for alt in parsed.get("alternatives") or []:
            ops.append(PreviewOp(
                agent_id=aid, op_kind=f"propose_{alt.get('kind', 'mutate')}",
                target_kind="branch", target_id=branch.id,
                payload=alt,
                rationale=alt.get("what_we_violate", ""),
            ))

    elif aid == "pedagogical-contradiction-cutter":
        for c in parsed.get("contradictions") or []:
            ops.append(PreviewOp(
                agent_id=aid, op_kind="propose_contradiction",
                target_kind="system_model", target_id=model.id,
                payload=c, rationale=c.get("where_it_lives", ""),
            ))

    elif aid == "stabilizer":
        ops.append(PreviewOp(
            agent_id=aid, op_kind="set_stabilization_risk",
            target_kind="system_model", target_id=model.id,
            payload={"value": parsed.get("stabilization_risk"),
                     "verdict": parsed.get("verdict"),
                     "block_reason": parsed.get("block_reason")},
            rationale=str(parsed.get("compliance_check", {})),
        ))
        for impact in parsed.get("adjacent_system_impact") or []:
            ops.append(PreviewOp(
                agent_id=aid, op_kind="add_adjacent_impact",
                target_kind="system_model", target_id=model.id,
                payload=impact,
            ))

    elif aid == "methodological-grounder":
        for note in parsed.get("engineering_notes") or []:
            ops.append(PreviewOp(
                agent_id=aid, op_kind="add_engineering_note",
                target_kind="branch", target_id=branch.id,
                payload=note,
            ))
        for f in parsed.get("flows_to_add") or []:
            ops.append(PreviewOp(
                agent_id=aid, op_kind="add_flow",
                target_kind="system_model", target_id=model.id,
                payload=f,
            ))

    elif aid == "outcome-inverter":
        if parsed.get("refined_dolzhno"):
            ops.append(PreviewOp(
                agent_id=aid, op_kind="refine_dolzhno",
                target_kind="system_model", target_id=model.id,
                payload=parsed["refined_dolzhno"],
            ))
        for crit in parsed.get("verification_criteria") or []:
            ops.append(PreviewOp(
                agent_id=aid, op_kind="add_verification_criterion",
                target_kind="system_model", target_id=model.id,
                payload=crit,
            ))

    elif aid == "curriculum-chimerizer":
        ops.append(PreviewOp(
            agent_id=aid, op_kind="propose_merge",
            target_kind="branch", target_id=branch.id,
            payload=parsed,
            rationale=parsed.get("synergy_check", ""),
        ))

    elif aid == "selector":
        for v in parsed.get("verdicts") or []:
            ops.append(PreviewOp(
                agent_id=aid, op_kind="set_maturity",
                target_kind="branch", target_id=v.get("branch_id"),
                payload=v,
                rationale=v.get("rationale", ""),
            ))

    elif aid == "quality-gate":
        ops.append(PreviewOp(
            agent_id=aid, op_kind="quality_verdict",
            target_kind="branch", target_id=branch.id,
            payload={
                "severity": parsed.get("severity"),
                "mines": parsed.get("mines"),
                "checklist": parsed.get("checklist"),
                "overall": parsed.get("overall_verdict"),
            },
        ))

    elif aid == "ideal-tracer":
        for ifr in parsed.get("ifrs") or []:
            ops.append(PreviewOp(
                agent_id=aid, op_kind="propose_ifr",
                target_kind="branch", target_id=branch.id,
                payload=ifr,
            ))

    else:
        # generic fallback
        ops.append(PreviewOp(
            agent_id=aid, op_kind="generic_response",
            target_kind="branch", target_id=branch.id,
            payload=parsed,
        ))

    return ops
