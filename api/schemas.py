"""Pydantic-схемы для валидации yaml-фронтматтера content/*.md.

Грузим taxonomy один раз, проверяем им фасеты. Любой кейс/тип/гипотеза
из content/ должен парситься в одну из этих схем без ошибок.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, Field, field_validator, model_validator

TAXONOMY_DIR = Path(__file__).resolve().parent.parent / "taxonomy"


def _load_yaml(name: str) -> dict[str, Any]:
    with (TAXONOMY_DIR / name).open(encoding="utf-8") as f:
        return yaml.safe_load(f)


_FACETS = _load_yaml("facets.yaml")
_AGENTIVITY = _load_yaml("agentivity_scale.yaml")
_INSTITUTIONS = _load_yaml("institution_types.yaml")
_PATTERNS = _load_yaml("patterns.yaml")
_COUNTRIES = _load_yaml("countries.yaml")
_LIFECYCLE = _load_yaml("lifecycle.yaml")
_RELATIONS = _load_yaml("relations.yaml")
_AXES = _load_yaml("axes.yaml")
_TRANSFORM_MODES = _load_yaml("transformation_modes.yaml")

_ORCHESTRATION_VALUES = set(_FACETS["orchestration"]["values"].keys())
_PEDAGOGY_VALUES = set(_FACETS["pedagogy"]["values"].keys())
_CONTROL_VALUES = set(_FACETS["control"]["values"].keys())
_ECONOMY_VALUES = set(_FACETS["economy"]["values"].keys())
_AGENTIVITY_LEVELS = set(_AGENTIVITY["scale"].keys())
_INSTITUTION_TYPES = set(_INSTITUTIONS["types"].keys())
_PATTERN_IDS = set(_PATTERNS["types"].keys())
_COUNTRY_CODES = set(_COUNTRIES["countries"].keys())
_LIFECYCLE_STAGES = set(_LIFECYCLE["stages"].keys())
_RELATION_NAMES = set(_RELATIONS["relations"].keys())
_CONFIDENCE_LEVELS = set(_RELATIONS["confidence_levels"])
_AXIS_DEFS: dict[str, dict[str, Any]] = _AXES["axes"]
_TRANSFORM_MODE_IDS = set(_TRANSFORM_MODES["modes"].keys())


def _resolve_axis_enum(axis_def: dict[str, Any]) -> set[str]:
    """Если у оси указан enum_source, подтянуть значения из соответствующего yaml."""
    if "enum" in axis_def:
        return set(axis_def["enum"])
    src = axis_def.get("enum_source")
    if src == "patterns.yaml":
        return _PATTERN_IDS
    if src == "transformation_modes.yaml":
        return _TRANSFORM_MODE_IDS
    raise ValueError(f"axis enum_source '{src}' not wired up in schemas.py")


def _validate_axes(values: dict[str, Any] | None) -> dict[str, Any]:
    """Проверить, что все ключи известны и значения подходят по типу/диапазону."""
    if not values:
        return values or {}
    for key, value in values.items():
        if key not in _AXIS_DEFS:
            raise ValueError(f"unknown axis '{key}' (add to taxonomy/axes.yaml)")
        spec = _AXIS_DEFS[key]
        kind = spec["kind"]
        if kind == "ordinal":
            lo, hi = spec["scale"]
            if not isinstance(value, int) or not (lo <= value <= hi):
                raise ValueError(f"axis '{key}' expects int in [{lo}, {hi}], got {value!r}")
        elif kind == "categorical":
            allowed = _resolve_axis_enum(spec)
            if value not in allowed:
                raise ValueError(f"axis '{key}'={value!r} not in {sorted(allowed)}")
        elif kind == "bool":
            if not isinstance(value, bool):
                raise ValueError(f"axis '{key}' expects bool, got {value!r}")
        elif kind == "freeform":
            if not isinstance(value, str):
                raise ValueError(f"axis '{key}' expects str, got {value!r}")
        else:
            raise ValueError(f"axis '{key}': unsupported kind '{kind}'")
    return values


def _validate_economy(value: str) -> str:
    """economy может быть комбинацией через '+': 'BUD+EXT'."""
    if value is None:
        return value
    parts = [p.strip() for p in value.split("+")]
    for p in parts:
        if p not in _ECONOMY_VALUES:
            raise ValueError(f"economy '{p}' not in {sorted(_ECONOMY_VALUES)}")
    return value


def _validate_org_type(value: str) -> str:
    """org_type может быть комбинацией через '/': 'U/N'."""
    parts = [p.strip() for p in value.split("/")]
    for p in parts:
        if p not in _INSTITUTION_TYPES:
            raise ValueError(f"org_type '{p}' not in {sorted(_INSTITUTION_TYPES)}")
    return value


# ---------------------------------------------------------------------------
# Кейс
# ---------------------------------------------------------------------------


class Organization(BaseModel):
    name: str
    type: str
    country: str

    @field_validator("type")
    @classmethod
    def _check_type(cls, v: str) -> str:
        return _validate_org_type(v)

    @field_validator("country")
    @classmethod
    def _check_country(cls, v: str) -> str:
        if v not in _COUNTRY_CODES:
            raise ValueError(f"country '{v}' not in {sorted(_COUNTRY_CODES)}")
        return v


class Scenario(BaseModel):
    level: list[str] = Field(default_factory=list)
    domains: list[str] = Field(default_factory=list)
    context: str | None = None


class Facets(BaseModel):
    orchestration: str | None = None
    pedagogy: str | None = None
    control: str | None = None
    economy: str | None = None

    @field_validator("orchestration")
    @classmethod
    def _check_orch(cls, v: str | None) -> str | None:
        if v is not None and v not in _ORCHESTRATION_VALUES:
            raise ValueError(f"orchestration '{v}' not in {sorted(_ORCHESTRATION_VALUES)}")
        return v

    @field_validator("pedagogy")
    @classmethod
    def _check_ped(cls, v: str | None) -> str | None:
        if v is not None and v not in _PEDAGOGY_VALUES:
            raise ValueError(f"pedagogy '{v}' not in {sorted(_PEDAGOGY_VALUES)}")
        return v

    @field_validator("control")
    @classmethod
    def _check_ctl(cls, v: str | None) -> str | None:
        if v is not None and v not in _CONTROL_VALUES:
            raise ValueError(f"control '{v}' not in {sorted(_CONTROL_VALUES)}")
        return v

    @field_validator("economy")
    @classmethod
    def _check_econ(cls, v: str | None) -> str | None:
        return _validate_economy(v) if v is not None else v


class AiConfig(BaseModel):
    pattern: str | None = None
    agentivity: int
    technologies: list[str] = Field(default_factory=list)
    role: str | None = None

    @field_validator("pattern")
    @classmethod
    def _check_pattern(cls, v: str | None) -> str | None:
        if v is not None and v not in _PATTERN_IDS:
            raise ValueError(f"pattern '{v}' not in {sorted(_PATTERN_IDS)}")
        return v

    @field_validator("agentivity")
    @classmethod
    def _check_agentivity(cls, v: int) -> int:
        if v not in _AGENTIVITY_LEVELS:
            raise ValueError(f"agentivity {v} not in {sorted(_AGENTIVITY_LEVELS)}")
        return v


class LifecycleHistoryEntry(BaseModel):
    wave: str
    stage: str | None = None
    facets: dict[str, Any] = Field(default_factory=dict)
    note: str | None = None

    @field_validator("stage")
    @classmethod
    def _check_stage(cls, v: str | None) -> str | None:
        if v is not None and v not in _LIFECYCLE_STAGES:
            raise ValueError(f"stage '{v}' not in {sorted(_LIFECYCLE_STAGES)}")
        return v


class Lifecycle(BaseModel):
    stage: str
    first_seen: str
    history: list[LifecycleHistoryEntry] = Field(default_factory=list)

    @field_validator("stage")
    @classmethod
    def _check_stage(cls, v: str) -> str:
        if v not in _LIFECYCLE_STAGES:
            raise ValueError(f"stage '{v}' not in {sorted(_LIFECYCLE_STAGES)}")
        return v


class EvidenceLink(BaseModel):
    kind: Literal["type", "hypothesis", "tension", "mode", "counter-signal"]
    id: str
    relation: str
    confidence: str = "medium"
    note: str | None = None

    @field_validator("relation")
    @classmethod
    def _check_relation(cls, v: str) -> str:
        if v not in _RELATION_NAMES:
            raise ValueError(f"relation '{v}' not in {sorted(_RELATION_NAMES)}")
        return v

    @field_validator("confidence")
    @classmethod
    def _check_confidence(cls, v: str) -> str:
        if v not in _CONFIDENCE_LEVELS:
            raise ValueError(f"confidence '{v}' not in {sorted(_CONFIDENCE_LEVELS)}")
        return v


class Source(BaseModel):
    url: str | None = None
    type: str | None = None
    accessed: str | None = None


class Metrics(BaseModel):
    hard: list[str] = Field(default_factory=list)
    soft: list[str] = Field(default_factory=list)


class RoleSplit(BaseModel):
    """Разделение ролей между людьми и машинами по канвасу ТюмГУ (slide 34-35)."""
    human: list[str] = Field(default_factory=list)
    machine: list[str] = Field(default_factory=list)
    interaction_scenario: str | None = None


# ---------------------------------------------------------------------------
# Канвас описания (18 секций)
# Каждая секция — отдельный markdown-абзац (или пустой). Пустые отображаются в
# UI как «нет данных» с кнопками «уточнить через LLM» / «добавить вручную».
# Источник структуры: «генетическая карточка психотехнической LLM-игры» +
# slide 34 ТюмГУ + промпт поиска кейсов Wave 1.
# ---------------------------------------------------------------------------


CANVAS_SECTIONS: list[tuple[str, str]] = [
    ("ontology_status",       "Онтологический статус"),
    ("signature_context",     "Сигнатура и контекст"),
    ("problem_situation",     "Проблема и исходная ситуация"),
    ("effect_hypothesis",     "Гипотеза эффекта"),
    ("ai_architecture",       "Архитектура AI"),
    ("team_roles",            "Ролевая модель команды"),
    ("ai_role",               "Роль AI"),
    ("interaction_scenario",  "Сценарий взаимодействия"),
    ("institutional_loop",    "Институциональный контур"),
    ("transit_to_life",       "Транзит к жизни (pilot → rollout)"),
    ("metrics_evidence",      "Метрики и доказательная база"),
    ("risks",                 "Риски"),
    ("countersignals",        "Контр-сигналы и откаты"),
    ("transferability",       "Что переносимо"),
    ("theory_links",          "Связи с теорией"),
    ("open_questions",        "Открытые вопросы"),
    ("next_wave_followup",    "След для следующей волны"),
    ("sources_verification",  "Источники и верификация"),
]

CANVAS_KEYS = {k for k, _ in CANVAS_SECTIONS}


class CanvasSection(BaseModel):
    text: str = ""
    status: Literal["empty", "draft", "verified", "stale"] = "empty"
    source: Literal["manual", "llm", "imported", "enriched-from-waves"] | None = None
    updated_at: str | None = None


class CanvasBlock(BaseModel):
    """Содержит до 18 секций. Любая секция может отсутствовать."""
    model_config = {"extra": "allow"}

    @model_validator(mode="after")
    def _validate_keys(self) -> "CanvasBlock":
        unknown = set(self.model_dump(exclude_unset=False).keys()) - CANVAS_KEYS - {"model_config"}
        if unknown:
            raise ValueError(f"unknown canvas sections: {sorted(unknown)} (allowed: {sorted(CANVAS_KEYS)})")
        return self


class TracesBlock(BaseModel):
    """Что фиксируется как след эксперимента (audit trail)."""
    logs: bool = False
    prompts_versioned: bool = False
    data_sources: list[str] = Field(default_factory=list)
    notes: str | None = None


class RisksBlock(BaseModel):
    """Качественные риски из канваса; численные оценки идут через axes."""
    goal_substitution: str | None = None
    lowered_bar: str | None = None
    weak_audit_trail: str | None = None
    other: list[str] = Field(default_factory=list)


class CaseFrontmatter(BaseModel):
    id: str
    name: str
    organization: Organization
    scenario: Scenario = Field(default_factory=Scenario)
    facets: Facets = Field(default_factory=Facets)
    ai: AiConfig
    orchestration_roles: list[str] = Field(default_factory=list)
    roles: RoleSplit = Field(default_factory=RoleSplit)
    traces: TracesBlock = Field(default_factory=TracesBlock)
    risks: RisksBlock = Field(default_factory=RisksBlock)
    transformation_mode: str | None = None
    axes: dict[str, Any] = Field(default_factory=dict)
    canvas: dict[str, CanvasSection] = Field(default_factory=dict)
    lifecycle: Lifecycle
    links: list[EvidenceLink] = Field(default_factory=list)
    metrics: Metrics = Field(default_factory=Metrics)
    sources: list[Source] = Field(default_factory=list)
    verified: bool = False

    @field_validator("canvas")
    @classmethod
    def _check_canvas_keys(cls, v: dict[str, Any]) -> dict[str, Any]:
        bad = set(v.keys()) - CANVAS_KEYS
        if bad:
            raise ValueError(f"unknown canvas sections: {sorted(bad)}")
        return v

    @field_validator("transformation_mode")
    @classmethod
    def _check_mode(cls, v: str | None) -> str | None:
        if v is not None and v not in _TRANSFORM_MODE_IDS:
            raise ValueError(f"transformation_mode '{v}' not in {sorted(_TRANSFORM_MODE_IDS)}")
        return v

    @field_validator("axes")
    @classmethod
    def _check_axes(cls, v: dict[str, Any]) -> dict[str, Any]:
        return _validate_axes(v)

    @model_validator(mode="after")
    def _id_is_slug(self) -> "CaseFrontmatter":
        if not all(c.isalnum() or c in "-_" for c in self.id):
            raise ValueError(f"id '{self.id}' must be a slug (alnum + '-' + '_')")
        return self


# ---------------------------------------------------------------------------
# Проект — собственный эксперимент пользователя в той же координатной сетке.
# Те же поля контейнера, что у Case, но мягче: agentivity и lifecycle могут
# быть пустыми на ранних стадиях (idea → draft), source-link не обязателен,
# зато появляются author/status/portfolio_slot и блок radical_version.
# ---------------------------------------------------------------------------


ProjectStatus = Literal["draft", "review", "approved", "in-pilot", "archived"]


class ProjectVersion(BaseModel):
    """Минимальная / продвинутая версия по slide 36."""
    summary: str | None = None
    axes: dict[str, Any] = Field(default_factory=dict)
    notes: str | None = None

    @field_validator("axes")
    @classmethod
    def _check_axes(cls, v: dict[str, Any]) -> dict[str, Any]:
        return _validate_axes(v)


class ProjectFrontmatter(BaseModel):
    id: str
    name: str
    kind: Literal["project"] = "project"
    author: str | None = None
    status: ProjectStatus = "draft"
    organization: Organization | None = None
    scenario: Scenario = Field(default_factory=Scenario)
    facets: Facets = Field(default_factory=Facets)
    ai: AiConfig | None = None
    roles: RoleSplit = Field(default_factory=RoleSplit)
    traces: TracesBlock = Field(default_factory=TracesBlock)
    risks: RisksBlock = Field(default_factory=RisksBlock)
    transformation_mode: str | None = None
    axes: dict[str, Any] = Field(default_factory=dict)
    canvas: dict[str, CanvasSection] = Field(default_factory=dict)
    analogues: list[str] = Field(default_factory=list)  # case_id'ы из корпуса
    radical_version: ProjectVersion | None = None
    portfolio_slot: str | None = None  # например, "tyumgu-basic-track" / "tyumgu-radical-track"
    links: list[EvidenceLink] = Field(default_factory=list)
    created_at: str | None = None
    updated_at: str | None = None

    @field_validator("transformation_mode")
    @classmethod
    def _check_mode(cls, v: str | None) -> str | None:
        if v is not None and v not in _TRANSFORM_MODE_IDS:
            raise ValueError(f"transformation_mode '{v}' not in {sorted(_TRANSFORM_MODE_IDS)}")
        return v

    @field_validator("axes")
    @classmethod
    def _check_axes(cls, v: dict[str, Any]) -> dict[str, Any]:
        return _validate_axes(v)

    @field_validator("canvas")
    @classmethod
    def _check_canvas_keys(cls, v: dict[str, Any]) -> dict[str, Any]:
        bad = set(v.keys()) - CANVAS_KEYS
        if bad:
            raise ValueError(f"unknown canvas sections: {sorted(bad)}")
        return v

    @model_validator(mode="after")
    def _id_is_slug(self) -> "ProjectFrontmatter":
        if not all(c.isalnum() or c in "-_" for c in self.id):
            raise ValueError(f"id '{self.id}' must be a slug (alnum + '-' + '_')")
        return self


# ---------------------------------------------------------------------------
# Тип A–F
# ---------------------------------------------------------------------------


class TypeFrontmatter(BaseModel):
    id: str
    name: str
    full_name: str | None = None
    wave_introduced: str
    markers: list[str] = Field(default_factory=list)
    related_types: list[str] = Field(default_factory=list)

    @field_validator("id")
    @classmethod
    def _check_id(cls, v: str) -> str:
        if v not in _PATTERN_IDS:
            raise ValueError(f"type id '{v}' not in {sorted(_PATTERN_IDS)}")
        return v


# ---------------------------------------------------------------------------
# Гипотеза H1–H5
# ---------------------------------------------------------------------------


HypothesisStatus = Literal[
    "proposed", "supported", "partially-supported", "weakened", "refuted"
]


class HypothesisStatusEntry(BaseModel):
    wave: str
    status: HypothesisStatus
    note: str | None = None


class HypothesisStatusBlock(BaseModel):
    current: HypothesisStatus
    history: list[HypothesisStatusEntry] = Field(default_factory=list)


class HypothesisFrontmatter(BaseModel):
    id: str
    name: str
    wave_introduced: str
    status: HypothesisStatusBlock
    markers: list[str] = Field(default_factory=list)
    related_hypotheses: list[str] = Field(default_factory=list)
    related_tensions: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Противоречие
# ---------------------------------------------------------------------------


class TensionFrontmatter(BaseModel):
    id: str
    name: str
    pole_a: str
    pole_b: str
    wave_introduced: str
    related_hypotheses: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Мода
# ---------------------------------------------------------------------------


class ModeFrontmatter(BaseModel):
    id: str
    name: str
    wave_introduced: str
    intensifiers: list[str] = Field(default_factory=list)
    dampeners: list[str] = Field(default_factory=list)
    interferes_with: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Контр-сигнал
# ---------------------------------------------------------------------------


class CounterSignalFrontmatter(BaseModel):
    id: str
    name: str
    org_name: str | None = None
    target_hypothesis: str | None = None
    wave_introduced: str
    sources: list[Source] = Field(default_factory=list)
