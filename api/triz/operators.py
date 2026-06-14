"""L0 Operators — примитивные детерминированные функции.

12 операторов из architecture/03_AGENT_LEVELS.md. Чистые функции,
без LLM, без сетевых вызовов. Работают над SystemModel или Branch
(копия + мутация → возврат). Никаких side effects, никаких записей в БД —
это делает AgentRun слой.

Все операторы возвращают `OperatorResult` с описанием действия и новым
объектом, чтобы их можно было класть в preview/apply поток.
"""

from __future__ import annotations

import copy
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Literal

from .system_model import (
    Branch, Contradiction, EducationalSystemModel, FlowSpec,
    IdealImage, Mutation, PedagogicalConstraintEnvelope, RoleSpec,
)

OperatorId = Literal[
    "split", "mutate", "invert", "ground", "select",
    "classify", "cluster", "gate", "merge", "idealize",
    "revive", "quarantine",
]


@dataclass
class OperatorResult:
    """Что вернул оператор. Подходит для preview/apply."""
    operator: OperatorId
    summary: str
    before: dict[str, Any]
    after: dict[str, Any]
    artifacts: list[dict[str, Any]] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    reversible: bool = True


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _clone_model(model: EducationalSystemModel) -> EducationalSystemModel:
    return EducationalSystemModel.model_validate(
        copy.deepcopy(model.model_dump())
    )


def _clone_branch(branch: Branch) -> Branch:
    return Branch.model_validate(copy.deepcopy(branch.model_dump()))


def _new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


# ---------------------------------------------------------------------------
# 01. split — разделить по оси
# ---------------------------------------------------------------------------


def split(branch: Branch, model: EducationalSystemModel, *,
          axis: str, parts: int = 2,
          axis_values: list[str] | None = None) -> OperatorResult:
    """Создать N дочерних Branch'ей, разделив исходный по оси.

    Пример: axis='duration', parts=2 → один Branch 'intensive 2w', другой 'spread 12w'.
    """
    if parts < 2:
        raise ValueError("split: parts must be >= 2")
    children: list[Branch] = []
    values = axis_values or [f"variant-{i+1}" for i in range(parts)]
    for i, val in enumerate(values[:parts]):
        ch = _clone_branch(branch)
        ch.id = _new_id("br")
        ch.parent_id = branch.id
        ch.title = f"{branch.title} · split[{axis}={val}]"
        ch.current_formulation = (
            f"{branch.current_formulation}\n[split по {axis}: {val}]"
        )
        ch.applied_operators = list(branch.applied_operators) + [f"split:{axis}"]
        children.append(ch)
    return OperatorResult(
        operator="split",
        summary=f"split по оси '{axis}' на {parts} вариантов",
        before={"branch_id": branch.id, "title": branch.title},
        after={"children": [c.id for c in children]},
        artifacts=[c.model_dump() for c in children],
        notes=[f"родитель {branch.id} остаётся, создаются {parts} дочерних"],
    )


# ---------------------------------------------------------------------------
# 02. mutate — модифицировать секцию модели
# ---------------------------------------------------------------------------


def mutate(branch: Branch, model: EducationalSystemModel, *,
           mutation_type: str, target_field: str,
           new_value: Any) -> OperatorResult:
    """Изменить конкретное поле SystemModel в новом Branch.

    Пример: mutation_type='replace', target_field='function',
            new_value='студент собирает прототип на реальной задаче'.
    """
    new_model = _clone_model(model)
    before_val = getattr(new_model, target_field, None) if hasattr(new_model, target_field) else None
    if hasattr(new_model, target_field):
        setattr(new_model, target_field, new_value)
    elif target_field in new_model.dano:
        before_val = new_model.dano.get(target_field)
        new_model.dano[target_field] = new_value
    elif target_field in new_model.dolzhno:
        before_val = new_model.dolzhno.get(target_field)
        new_model.dolzhno[target_field] = new_value
    else:
        raise ValueError(f"mutate: unknown target_field '{target_field}'")

    new_branch = _clone_branch(branch)
    new_branch.id = _new_id("br")
    new_branch.parent_id = branch.id
    new_branch.title = f"{branch.title} · mutate[{target_field}]"
    new_branch.applied_operators = list(branch.applied_operators) + [f"mutate:{mutation_type}:{target_field}"]
    new_branch.maturity = "mutated"

    return OperatorResult(
        operator="mutate",
        summary=f"mutate '{target_field}' ({mutation_type})",
        before={"field": target_field, "value": before_val},
        after={"field": target_field, "value": new_value, "branch_id": new_branch.id},
        artifacts=[new_branch.model_dump(), new_model.model_dump()],
    )


# ---------------------------------------------------------------------------
# 03. invert — инвертировать ключевое предположение
# ---------------------------------------------------------------------------


def invert(branch: Branch, model: EducationalSystemModel, *,
           assumption: str, inverted_form: str) -> OperatorResult:
    """Создать Branch, в котором ключевое предположение инвертировано.

    Пример: assumption='студенты замотивированы',
            inverted_form='студенты сопротивляются, нужно их вовлекать через провокацию'.
    """
    new_branch = _clone_branch(branch)
    new_branch.id = _new_id("br")
    new_branch.parent_id = branch.id
    new_branch.title = f"{branch.title} · INVERT"
    new_branch.current_formulation = (
        f"{branch.current_formulation}\n\n"
        f"[INVERTED] было предположение: «{assumption}»\n"
        f"стало: «{inverted_form}»"
    )
    new_branch.applied_operators = list(branch.applied_operators) + ["invert"]
    new_branch.maturity = "mutated"
    return OperatorResult(
        operator="invert",
        summary=f"инверсия предположения «{assumption[:60]}»",
        before={"assumption": assumption},
        after={"inverted_to": inverted_form, "branch_id": new_branch.id},
        artifacts=[new_branch.model_dump()],
    )


# ---------------------------------------------------------------------------
# 04. ground — добавить методические/инженерные заметки
# ---------------------------------------------------------------------------


def ground(branch: Branch, model: EducationalSystemModel, *,
           notes: list[str],
           note_kind: Literal["engineering", "market", "risk"] = "engineering") -> OperatorResult:
    """Привязать Branch к реальности через заметки методиста/инженера/маркетолога."""
    new_branch = _clone_branch(branch)
    if note_kind == "engineering":
        new_branch.notes_engineering = list(branch.notes_engineering) + notes
    elif note_kind == "market":
        new_branch.notes_market = list(branch.notes_market) + notes
    else:
        new_branch.notes_risk = list(branch.notes_risk) + notes
    new_branch.applied_operators = list(branch.applied_operators) + [f"ground:{note_kind}"]
    new_branch.maturity = "grounded" if new_branch.maturity == "seed" else new_branch.maturity
    return OperatorResult(
        operator="ground",
        summary=f"добавлено {len(notes)} {note_kind}-заметок",
        before={"branch_id": branch.id, "kind": note_kind},
        after={"notes_added": notes, "branch_id": new_branch.id},
        artifacts=[new_branch.model_dump()],
    )


# ---------------------------------------------------------------------------
# 05. select — изменить maturity по критериям
# ---------------------------------------------------------------------------


def select(branch: Branch, *, criteria: dict[str, Any],
           new_maturity: Literal["selected", "quarantined", "tested"]) -> OperatorResult:
    """Триаж Branch'а: продвинуть, протестировать, или отложить."""
    new_branch = _clone_branch(branch)
    new_branch.maturity = new_maturity
    new_branch.applied_operators = list(branch.applied_operators) + [f"select:{new_maturity}"]
    return OperatorResult(
        operator="select",
        summary=f"select → maturity={new_maturity}",
        before={"branch_id": branch.id, "maturity": branch.maturity},
        after={"branch_id": new_branch.id, "maturity": new_maturity, "criteria": criteria},
        artifacts=[new_branch.model_dump()],
    )


# ---------------------------------------------------------------------------
# 06. classify — назначить кластер
# ---------------------------------------------------------------------------


def classify(branch: Branch, *, cluster_id: str,
             rationale: str = "") -> OperatorResult:
    new_branch = _clone_branch(branch)
    new_branch.cluster = cluster_id
    new_branch.applied_operators = list(branch.applied_operators) + [f"classify:{cluster_id}"]
    return OperatorResult(
        operator="classify",
        summary=f"назначен кластер '{cluster_id}'",
        before={"branch_id": branch.id, "cluster": branch.cluster},
        after={"branch_id": new_branch.id, "cluster": cluster_id, "rationale": rationale},
        artifacts=[new_branch.model_dump()],
    )


# ---------------------------------------------------------------------------
# 07. cluster — сгруппировать список branches
# ---------------------------------------------------------------------------


def cluster(branches: list[Branch], *,
            grouping_fn: Callable[[Branch], str]) -> OperatorResult:
    """Сгруппировать список Branch'ей по функции группировки."""
    groups: dict[str, list[str]] = {}
    for b in branches:
        k = grouping_fn(b)
        groups.setdefault(k, []).append(b.id)
    return OperatorResult(
        operator="cluster",
        summary=f"кластеризовано {len(branches)} branches на {len(groups)} групп",
        before={"input_count": len(branches)},
        after={"clusters": {k: ids for k, ids in groups.items()}},
        artifacts=[],
    )


# ---------------------------------------------------------------------------
# 08. gate — проверка качества с блокировкой
# ---------------------------------------------------------------------------


def gate(branch: Branch, model: EducationalSystemModel, *,
         gate_id: str,
         conditions: list[Callable[[Branch, EducationalSystemModel], tuple[bool, str]]]
         ) -> OperatorResult:
    """Прогон Branch+SystemModel через список условий.
    Каждое условие возвращает (ok, reason).
    """
    failures: list[dict[str, str]] = []
    passes: list[dict[str, str]] = []
    for cond in conditions:
        ok, reason = cond(branch, model)
        (passes if ok else failures).append({"cond": cond.__name__, "reason": reason})
    severity = "block" if failures else "pass"
    return OperatorResult(
        operator="gate",
        summary=f"gate '{gate_id}': {len(passes)}/{len(conditions)} прошло",
        before={"branch_id": branch.id, "gate_id": gate_id},
        after={"severity": severity, "passes": passes, "failures": failures},
        artifacts=[],
        reversible=True,
    )


# ---------------------------------------------------------------------------
# 09. merge — скрестить два branch в chimera
# ---------------------------------------------------------------------------


def merge(branch_a: Branch, branch_b: Branch, model: EducationalSystemModel, *,
          take_from_a: list[str] | None = None,
          take_from_b: list[str] | None = None) -> OperatorResult:
    """Создать chimera-branch, объединив свойства двух."""
    chimera = _clone_branch(branch_a)
    chimera.id = _new_id("br")
    chimera.parent_id = branch_a.id
    chimera.title = f"chimera({branch_a.title} × {branch_b.title})"
    chimera.current_formulation = (
        f"chimera:\n"
        f"  взято из {branch_a.id}: {take_from_a or 'основа'}\n"
        f"  взято из {branch_b.id}: {take_from_b or 'дополнение'}\n"
        f"  base: {branch_a.current_formulation}\n"
        f"  +: {branch_b.current_formulation}"
    )
    chimera.applied_operators = (
        list(branch_a.applied_operators)
        + list(branch_b.applied_operators)
        + [f"merge:{branch_b.id}"]
    )
    chimera.maturity = "mutated"
    return OperatorResult(
        operator="merge",
        summary=f"merge {branch_a.id} × {branch_b.id}",
        before={"a": branch_a.id, "b": branch_b.id},
        after={"chimera_id": chimera.id, "take_from_a": take_from_a, "take_from_b": take_from_b},
        artifacts=[chimera.model_dump()],
    )


# ---------------------------------------------------------------------------
# 10. idealize — сформулировать ИКР (идеальный конечный результат)
# ---------------------------------------------------------------------------


def idealize(branch: Branch, model: EducationalSystemModel, *,
             formulation: str,
             resources_to_zero: list[str] | None = None,
             cost: str | None = None,
             harm: str | None = None,
             direction: str | None = None) -> OperatorResult:
    """Создать IdealImage для Branch.

    «Идеально: <функция> происходит, при этом <ресурс> = 0».
    """
    ideal = IdealImage(
        id=_new_id("ifr"),
        branch_id=branch.id,
        formulation=formulation,
        resources_used=resources_to_zero or [],
        cost=cost,
        harm=harm,
        direction=direction,
    )
    new_branch = _clone_branch(branch)
    new_branch.applied_operators = list(branch.applied_operators) + ["idealize"]
    return OperatorResult(
        operator="idealize",
        summary=f"IFR: «{formulation[:80]}»",
        before={"branch_id": branch.id},
        after={"ifr_id": ideal.id, "formulation": formulation},
        artifacts=[ideal.model_dump(), new_branch.model_dump()],
    )


# ---------------------------------------------------------------------------
# 11. revive — оживить quarantined branch
# ---------------------------------------------------------------------------


def revive(branch: Branch, *, reason: str = "") -> OperatorResult:
    if branch.maturity != "quarantined":
        raise ValueError(f"revive: branch '{branch.id}' не quarantined")
    new_branch = _clone_branch(branch)
    new_branch.maturity = "seed"
    new_branch.applied_operators = list(branch.applied_operators) + ["revive"]
    return OperatorResult(
        operator="revive",
        summary=f"оживлён quarantined branch ({reason or 'no reason'})",
        before={"branch_id": branch.id, "maturity": "quarantined"},
        after={"branch_id": new_branch.id, "maturity": "seed", "reason": reason},
        artifacts=[new_branch.model_dump()],
    )


# ---------------------------------------------------------------------------
# 12. quarantine — отправить branch в карантин
# ---------------------------------------------------------------------------


def quarantine(branch: Branch, *, reason: str = "") -> OperatorResult:
    new_branch = _clone_branch(branch)
    new_branch.maturity = "quarantined"
    new_branch.applied_operators = list(branch.applied_operators) + ["quarantine"]
    return OperatorResult(
        operator="quarantine",
        summary=f"карантин ({reason or 'no reason'})",
        before={"branch_id": branch.id, "maturity": branch.maturity},
        after={"branch_id": new_branch.id, "maturity": "quarantined", "reason": reason},
        artifacts=[new_branch.model_dump()],
    )


# ---------------------------------------------------------------------------
# Registry — для оркестратора
# ---------------------------------------------------------------------------


OPERATORS: dict[OperatorId, Callable] = {
    "split": split,
    "mutate": mutate,
    "invert": invert,
    "ground": ground,
    "select": select,
    "classify": classify,
    "cluster": cluster,
    "gate": gate,
    "merge": merge,
    "idealize": idealize,
    "revive": revive,
    "quarantine": quarantine,
}


def list_operators() -> list[dict[str, str]]:
    """Каталог операторов с описаниями (для UI Method Library)."""
    return [
        {"id": op_id, "doc": (fn.__doc__ or "").strip().split("\n")[0]}
        for op_id, fn in OPERATORS.items()
    ]
