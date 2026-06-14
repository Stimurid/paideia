"""EducationalSystemModel — центральная сущность Paideia v3.

Заменяет «канвас 18 секций как source of truth». 18-секционный канвас
остаётся как одна из projections (Card Desk view), но primary view —
SystemModel.

Адаптация TechnicalSystemModel из FifthConstraint к образовательному контуру:
- function: что курс/программа реально формирует у студента
- working_organ: кто/что выполняет функцию (преподаватель, AI-роль, среда)
- flows: потоки студента, материала, времени, оценивания, обратной связи
- controls: кто принимает решения (методист, ректор, регулятор, рынок)
- transmission: форматы (лекция, семинар, проектная работа, игра, лаб)
- adjacent_systems: другие курсы, программа в целом, рынок труда
- DANO: исходная ситуация (с чем приходит студент, что есть у вуза)
- DOLZHNO: целевое состояние (выпускник может делать X на материале Y)
- evolution_pressure: тренды (компетенции, технологии, демография)
- mutations: возможные ходы трансформации программы
- verification: как проверить что программа работает
- contradictions: пары конфликтующих требований
- constraints: PedagogicalConstraintEnvelope (см. ниже)
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


# ---------------------------------------------------------------------------
# PedagogicalConstraintEnvelope — конверт ограничений программы
# ---------------------------------------------------------------------------


InventionLevel = Literal[1, 2, 3, 4, 5]
"""1 — рутинная модификация. 5 — открытие нового образовательного класса."""


class PedagogicalConstraintEnvelope(BaseModel):
    """Конверт допустимости для варианта программы.

    Адаптация ConstraintEnvelope из FifthConstraint:
    - preserved: то, что надо сохранить (ФГОС-минимум, договорные обязательства)
    - sacred: то, что нельзя нарушать ни при каких условиях (этика, безопасность,
      нормативные пороги, репутационные риски)
    - hidden: скрытые предположения, которые надо surface (например «преподаватель
      умеет вести Socratic-диалог», «студенты замотивированы»)
    - violated: то, что мы сознательно нарушаем (например, отказываемся от
      лекционного формата вообще)
    - suspended: временно отложенные (например, «вернёмся к этому ограничению
      когда выйдем на 100+ студентов»)
    - redefined: переопределённые (например, «оценка» переопределена из
      «контрольная» в «защита проекта в реальной команде»)
    """

    preserved: list[str] = Field(default_factory=list)
    sacred: list[str] = Field(default_factory=list)
    hidden: list[str] = Field(default_factory=list)
    violated: list[str] = Field(default_factory=list)
    suspended: list[str] = Field(default_factory=list)
    redefined: list[str] = Field(default_factory=list)

    invention_level: InventionLevel | None = None
    """1–5: радикальность отхода от существующей практики."""

    stabilization_risk: int | None = Field(default=None, ge=0, le=5)
    """0–5: риск дестабилизации смежных систем (других курсов, программы)."""

    adjacent_system_impact: list[str] = Field(default_factory=list)
    """Какие смежные системы затронуты: «изменение РПД соседнего курса»,
    «нагрузка на методическое управление», «конфликт с балансом часов»."""


# ---------------------------------------------------------------------------
# Подсхемы EducationalSystemModel
# ---------------------------------------------------------------------------


class FlowSpec(BaseModel):
    """Поток в образовательной системе: что движется, через что, в каком ритме."""

    kind: Literal["student", "content", "time", "assessment", "feedback", "energy"]
    description: str
    rhythm: str | None = None
    """ритм: «4 пары в неделю», «асинхронно с дедлайнами»."""


class RoleSpec(BaseModel):
    """Роль в работающем органе образовательной системы.

    По модели ТюмГУ: картограф / организатор деятельности / медиатор /
    хранитель мотивации + ИИ-персоны. Но также годится для классической
    «преподаватель + ассистент».
    """

    name: str
    kind: Literal["human", "ai-persona", "hybrid", "infrastructure"]
    function: str
    """Что делает в системе."""
    constraints: list[str] = Field(default_factory=list)
    """Ограничения роли (что нельзя)."""


class Contradiction(BaseModel):
    """Пара конфликтующих требований."""

    requirement_a: str
    requirement_b: str
    kind: Literal[
        "physical", "technical", "evolutionary",
        "pedagogical", "organizational", "ethical",
    ]
    """physical/technical/evolutionary — классические ТРИЗ-виды.
    pedagogical — конфликт педагогических ценностей (глубина vs массовость).
    organizational — конфликт оргструктур (автономия vs контроль).
    ethical — нормативно-этический конфликт."""
    intensity: int = Field(ge=1, le=5)


class Mutation(BaseModel):
    """Возможный ход трансформации программы."""

    title: str
    operator: str
    """Какой L0 оператор применён (split/mutate/invert/...)."""
    rationale: str
    expected_effect: str
    risk: str | None = None


class VerificationCriterion(BaseModel):
    """Как проверить, что программа работает."""

    metric: str
    method: str
    """RCT / pre-post / лонгитюд / экспертиза / сравнение с control."""
    target: str | None = None
    """Целевое значение или условие успеха."""


class EvolutionPressure(BaseModel):
    """Эволюционное давление: что заставляет программу меняться."""

    source: Literal["market", "regulation", "technology", "demographics", "culture", "internal"]
    description: str
    horizon: Literal["6m", "1y", "3y", "5y", "10y+"]
    likelihood: int = Field(ge=1, le=5)


# ---------------------------------------------------------------------------
# EducationalSystemModel — главное
# ---------------------------------------------------------------------------


class EducationalSystemModel(BaseModel):
    """Центральная сущность Paideia v3.

    После открытия проекта пользователь сразу видит EducationalSystemModel,
    не «канвас 18 секций» (тот доступен как Card Desk view).
    """

    # --- идентификация ---
    id: str
    project_id: str
    title: str
    """Краткое имя системы (что мы проектируем)."""
    kind: Literal[
        "course", "module", "elective", "programme",
        "intensive", "lab", "studio", "experiment", "platform",
    ] = "course"

    # --- функция: что система реально делает ---
    function: str = ""
    """Главная функция: «студент получает способность X на материале Y».
    Для maturity != 'seed' обязательна (проверяется validator'ом)."""

    secondary_functions: list[str] = Field(default_factory=list)
    """Побочные функции: «формируется коммьюнити», «выпускается портфолио»."""

    # --- working organ: кто/что выполняет функцию ---
    working_organ: list[RoleSpec] = Field(default_factory=list)

    # --- потоки ---
    flows: list[FlowSpec] = Field(default_factory=list)

    # --- управление и трансмиссия ---
    controls: list[str] = Field(default_factory=list)
    """Контуры контроля: методист, ректор, регулятор, рынок, оценочная комиссия."""

    transmission: list[str] = Field(default_factory=list)
    """Форматы передачи: лекция, семинар, проект, симуляция, игра, лаб, поле."""

    # --- DANO / DOLZHNO двухполюсная сцепка ---
    dano: dict[str, Any] = Field(default_factory=dict)
    """Исходная ситуация: студент_входит_с / у_вуза_есть / контекст / ресурсы /
    ограничения / технологии_доступны / текущая_практика."""

    dolzhno: dict[str, Any] = Field(default_factory=dict)
    """Целевое: студент_сможет / измеряется_через / market_demand /
    success_criteria / protected_constraints / verification_conditions."""

    # --- противоречия, мутации, верификация ---
    contradictions: list[Contradiction] = Field(default_factory=list)
    mutations: list[Mutation] = Field(default_factory=list)
    verification: list[VerificationCriterion] = Field(default_factory=list)

    # --- эволюционное давление ---
    evolution_pressure: list[EvolutionPressure] = Field(default_factory=list)

    # --- adjacent systems и constraints ---
    adjacent_systems: list[str] = Field(default_factory=list)
    """Соседние курсы, программа в целом, рынок труда, регулятор."""

    constraint_envelope: PedagogicalConstraintEnvelope = Field(
        default_factory=PedagogicalConstraintEnvelope
    )

    # --- метаданные ---
    maturity: Literal[
        "seed", "explored", "mutated", "grounded",
        "tested", "selected", "quarantined",
    ] = "seed"
    """Зрелость варианта (по модели Branch в FifthConstraint)."""

    parent_variant_id: str | None = None
    """Если это мутация другого варианта — id родителя."""

    source: Literal["wizard", "imported-from-canvas", "kosmos", "manual", "agent-run"] = "manual"

    created_at: str | None = None
    updated_at: str | None = None

    # --- расширения для будущего ---
    notes: str | None = None
    tags: list[str] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def _coerce_none_strings(cls, data: Any) -> Any:
        """Нормализация: None для string-полей превращаем в пустую строку."""
        if isinstance(data, dict):
            for k in ("function", "title", "notes"):
                if data.get(k) is None:
                    data[k] = ""
        return data

    @model_validator(mode="after")
    def _check_completeness(self) -> "EducationalSystemModel":
        """Не валим валидацию на пустых полях — это нормально для seed-варианта.
        Но фиксируем что без function модель не считается зрелой."""
        if self.maturity != "seed" and not self.function.strip():
            raise ValueError(
                f"function обязательна для maturity '{self.maturity}'"
            )
        return self


# ---------------------------------------------------------------------------
# Branch — вариант / мутация SystemModel
# ---------------------------------------------------------------------------


class Branch(BaseModel):
    """Вариант / мутация EducationalSystemModel.

    По модели FifthConstraint: Branch это unit of becoming — траектория
    решения с полным состоянием. Mutable — агенты трансформируют branches.

    В Paideia: каждый проект может иметь множество Branches —
    альтернативных вариантов программы. Базовый Branch создаётся из wizard,
    дополнительные — через KOSMOS или ручную мутацию.
    """

    id: str
    project_id: str
    parent_id: str | None = None
    children_ids: list[str] = Field(default_factory=list)

    system_model_id: str
    """Branch — это projection над SystemModel. Хранится отдельно потому что
    SystemModel может быть один (base), а Branches — много."""

    title: str
    current_formulation: str
    """Краткое описание текущего состояния варианта."""

    maturity: Literal[
        "seed", "explored", "mutated", "grounded",
        "tested", "selected", "quarantined",
    ] = "seed"

    applied_operators: list[str] = Field(default_factory=list)
    """История применённых L0 операторов."""

    applied_agents: list[str] = Field(default_factory=list)
    """История применённых L1 агентов."""

    contradictions_found: list[str] = Field(default_factory=list)
    resources_identified: list[str] = Field(default_factory=list)

    cluster: str | None = None
    """Если кластеризован — id кластера."""

    notes_engineering: list[str] = Field(default_factory=list)
    notes_market: list[str] = Field(default_factory=list)
    notes_risk: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# IdealImage (Ideal Final Result) — отдельная сущность
# ---------------------------------------------------------------------------


class IdealImage(BaseModel):
    """Идеальный конечный результат — теневая сцепка любой инженерной сцены.

    По FifthConstraint: «выгода/издержки → максимум функции при минимуме
    вреда/веса/затрат». В педдизайне: «студент получает способность X
    без затрат преподавательского времени / без падения качества /
    без расхода бюджета».

    IFR не достигается — он различается как притяжение.
    """

    id: str
    branch_id: str
    formulation: str
    """«Идеально: <функция> происходит, при этом <ресурс> = 0»."""

    resources_used: list[str] = Field(default_factory=list)
    """Какие ресурсы должны исчезнуть."""

    cost: str | None = None
    """Идеальная стоимость: 0 или близко."""

    harm: str | None = None
    """Идеальный вред: 0."""

    direction: str | None = None
    """Куда идти от текущего варианта к идеалу."""
