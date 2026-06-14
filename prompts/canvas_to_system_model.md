# Канвас 18 секций → EducationalSystemModel

Получаешь 18-секционный канвас проекта (то что пользователь уже заполнил)
и должен извлечь из него **EducationalSystemModel** — центральную сущность
системы Paideia v3.

EducationalSystemModel описывает образовательную систему как «машину» с:
- функцией (что реально формирует у студента),
- работающим органом (кто/что выполняет функцию),
- потоками (студент/материал/время/оценивание/обратная связь),
- контролями (методист/ректор/регулятор/рынок),
- форматами трансмиссии (лекция/семинар/проект/игра/лаб),
- DANO (исходная ситуация) / DOLZHNO (целевое состояние),
- противоречиями (пары конфликтующих требований),
- мутациями (возможные ходы трансформации),
- эволюционным давлением,
- смежными системами,
- конвертом ограничений (preserved/sacred/hidden/violated/suspended/redefined).

## Правила извлечения

1. **Ничего не выдумывай.** Если по секции данных нет — оставляй пустое
   поле, не сочиняй.
2. **Используй формулировки пользователя** где возможно.
3. **`function` обязательна.** Если в канвасе её нет явно — попробуй
   синтезировать из effect_hypothesis + ai_role + interaction_scenario.
4. **Противоречия** ищи в секциях risks + countersignals + tensions +
   open_questions. Формулируй как пары «требование A vs требование B».
5. **DANO** = problem_situation + signature_context + institutional_loop
   (то что было до).
6. **DOLZHNO** = effect_hypothesis + metrics_evidence (то что должно быть).
7. **constraint_envelope** — preserved обычно из institutional_loop/sources;
   sacred — из ethics/normативки если упоминается; hidden — из ассумпций
   которые пользователь не сделал явными; violated — из transit_to_life.

## Возврат: строгий JSON по схеме EducationalSystemModel

```json
{
  "id": "system_<project_id>",
  "project_id": "<project_id>",
  "title": "<краткое имя системы>",
  "kind": "course|module|elective|programme|intensive|lab|studio|experiment|platform",
  "function": "<главная функция в формате 'студент получает способность X на материале Y'>",
  "secondary_functions": ["..."],
  "working_organ": [
    {"name": "...", "kind": "human|ai-persona|hybrid|infrastructure", "function": "...", "constraints": ["..."]}
  ],
  "flows": [
    {"kind": "student|content|time|assessment|feedback|energy", "description": "...", "rhythm": "..."}
  ],
  "controls": ["..."],
  "transmission": ["..."],
  "dano": {
    "student_arrives_with": "...",
    "institution_has": "...",
    "context": "...",
    "resources": "...",
    "constraints": "...",
    "available_technologies": "...",
    "current_practice": "..."
  },
  "dolzhno": {
    "student_can_do": "...",
    "measured_via": "...",
    "market_demand": "...",
    "success_criteria": "...",
    "protected_constraints": "...",
    "verification_conditions": "..."
  },
  "contradictions": [
    {
      "requirement_a": "...",
      "requirement_b": "...",
      "kind": "physical|technical|evolutionary|pedagogical|organizational|ethical",
      "intensity": 1-5
    }
  ],
  "mutations": [],
  "verification": [
    {"metric": "...", "method": "...", "target": "..."}
  ],
  "evolution_pressure": [
    {"source": "market|regulation|technology|demographics|culture|internal",
     "description": "...", "horizon": "6m|1y|3y|5y|10y+", "likelihood": 1-5}
  ],
  "adjacent_systems": ["..."],
  "constraint_envelope": {
    "preserved": ["..."],
    "sacred": ["..."],
    "hidden": ["..."],
    "violated": ["..."],
    "suspended": ["..."],
    "redefined": ["..."],
    "invention_level": 1-5,
    "stabilization_risk": 0-5,
    "adjacent_system_impact": ["..."]
  },
  "maturity": "seed|explored|mutated|grounded|tested|selected|quarantined",
  "source": "imported-from-canvas",
  "notes": null,
  "tags": []
}
```

Запреты:
- Не выдумывай противоречия — извлекай из текста.
- Не ставь invention_level > 3 без явных оснований (значительный отход от
  норматива в канвасе).
- Не пиши «продвинутая платформа», «современный подход», «инновационная
  методика» — это слоп. Конкретные глаголы и материалы.
