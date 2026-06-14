"""KOSMOS — AgentRun profile для автономной генерации 6 альтернатив программы.

По architecture/04_ORCHESTRATOR_MODEL.md: KOSMOS не глобальная кнопка,
а profile AgentRun. Запускает 6 стратегий генерации, потом прогоняет
результаты через L1-агенты, кластеризует, применяет quality gate.

Стратегии (для педдизайна):
1. invert-assumption — инверсия ключевого предположения проекта
2. split-by-format — разделение по формату (lecture/seminar/project/game)
3. mutate-function — переформулировка function на радикальный лад
4. merge-with-corpus-case — скрестить с релевантным кейсом корпуса
5. idealize — построить от IFR обратно
6. outcome-invert — backward design от целевой компетенции

Каждая стратегия — это PreviewOp для будущего Branch.
"""

from __future__ import annotations

KOSMOS_DEFAULT_AGENTS = [
    "pedagogical-reconstructor",
    "pedagogical-contradiction-cutter",
    "frame-breaker",
    "outcome-inverter",
    "ideal-tracer",
    "methodological-grounder",
    "selector",
    "quality-gate",
]
"""KOSMOS прогоняет проект через эту цепочку агентов в этом порядке."""


KOSMOS_STRATEGIES = [
    {
        "id": "invert-assumption",
        "name": "Инверсия ключевого предположения",
        "description": "Найти одну сильную ассумпцию проекта и сгенерировать вариант, в котором она ложна",
        "via_agent": "frame-breaker",
        "via_operator": "invert",
    },
    {
        "id": "split-by-format",
        "name": "Разделение по формату трансмиссии",
        "description": "Разбить программу на варианты по формату: lecture / seminar / project / game / lab",
        "via_agent": "frame-breaker",
        "via_operator": "split",
    },
    {
        "id": "mutate-function",
        "name": "Радикальная переформулировка функции",
        "description": "Переписать главную функцию системы в другом регистре (от content к experience, от skill к community и т.д.)",
        "via_agent": "frame-breaker",
        "via_operator": "mutate",
    },
    {
        "id": "merge-with-corpus-case",
        "name": "Скрещивание с кейсом корпуса",
        "description": "Найти релевантный кейс корпуса и собрать chimera-вариант",
        "via_agent": "curriculum-chimerizer",
        "via_operator": "merge",
    },
    {
        "id": "idealize",
        "name": "От Идеального Конечного Результата",
        "description": "Сформулировать IFR и спроектировать вариант, который движется в его направлении",
        "via_agent": "ideal-tracer",
        "via_operator": "idealize",
    },
    {
        "id": "outcome-invert",
        "name": "Backward design от компетенции выпускника",
        "description": "Развернуть программу от поведенческой компетенции на выходе обратно к проекту",
        "via_agent": "outcome-inverter",
        "via_operator": "invert",
    },
]


def kosmos_summary() -> dict:
    """Для UI: что делает KOSMOS."""
    return {
        "name": "KOSMOS",
        "description": "Автономная генерация 6 альтернативных вариантов программы через 6 стратегий с прогонкой через L1-агенты, кластеризацию и quality gate.",
        "agents": KOSMOS_DEFAULT_AGENTS,
        "strategies": KOSMOS_STRATEGIES,
        "expected_duration_s": 90,
        "default_policy": "preview-required",
    }
