---
id: educationq
name: EducationQ · multi-agent teaching evaluation framework
organization:
  name: EducationQ research group
  type: R
  country: INT
scenario:
  level:
  - research
  domains:
  - evaluation
  context: research-prototype
facets:
  orchestration: NET
  pedagogy: AUTO
  control: MACH
  economy: NONE
ai:
  pattern: D
  agentivity: 3
  technologies:
  - multiple-models
  role: teaching + learning + evaluation agents для оценки LLM-педагогики
transformation_mode: greenfield
axes:
  agentivity: 3
  ai_pattern: D
  orchestration: NET
  control_locus: MACH
  interaction_form: multi-agent-simulation
  evaluation_evidence_strength: 4
  audit_trail_strength: 4
lifecycle:
  stage: poc
  first_seen: diff-2026-06
  history:
  - wave: diff-2026-06
    stage: poc
    note: agents оценивают педагогические способности LLM через teach/learn/evaluate
      цикл
links:
- kind: type
  id: D
  relation: instantiates
  confidence: low
- kind: hypothesis
  id: H2
  relation: supports
  confidence: medium
sources:
- url: https://arxiv.org/
  type: academic
  accessed: 2026-06
verified: false
canvas:
  signature_context:
    text: 'EducationQ — multi-agent dialogue framework для оценки педагогических

      способностей LLM: teaching-agent / learning-agent / evaluation-agent

      ведут полный цикл. Прикладной слой к [[H2-assistant-to-autonomy]].'
    status: draft
    source: imported
    updated_at: '2026-06-12'
  ontology_status:
    text: EducationQ представлен как исследовательская multi-agent evaluation framework,
      не являющаяся production deployment. Это prototypical исследовательский кейс
      по оценке учебных способностей LLM посредством многоголосного диалога агентов
      в условиях controlled experimental setting, что помещает его в статус прототипа
      с академическим уклоном.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  problem_situation:
    text: Без AI framework для оценки педагогических способностей LLM существовали
      лишь общие benchmarking-метрики, не учитывающие сложную педагогическую коммуникацию
      и multi-role teaching interactions. Ограничения прежних подходов заключались
      в отсутствии инструментов для системной оценки teaching effectiveness с учётом
      diverse teaching/learning/evaluation ролей и множественных дисциплин.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  effect_hypothesis:
    text: EducationQ обещает обеспечить multi-agent mediated, role-divided evaluation,
      адекватно моделирующую педагогический процесс и выявляющую teaching effectiveness
      LLM. Гипотеза в том, что распределённая multi-agent система даёт более надёжную
      и комплексную диагностику педагогических навыков моделей, чем традиционные uni-agent
      benchmarks. Также выявлено, что эффективность преподавания коррелирует не прямо
      с масштабом модели, а зависит от специфических teaching capabilities, что важно
      для выбора LLM в образовательных применениях.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  ai_architecture:
    text: 'Архитектура EducationQ основана на multi-agent dialogue framework с тремя
      группами агентов: teaching agents, learning agents и evaluation agents. Для
      тестирования используются 14 LLM от ведущих AI организаций, охватывающих 13
      предметных областей и 10 уровней сложности вопросов. Агентность находится в
      диапазоне 2–3/6 — агентов много, они распределяют педагогическую функцию, но
      система пока не является образовательным deployment. Используется orchestration
      по NET-фасете с AUTO-педагогикой и MACH-контролем. Подробности про стек и модели
      неизвестны из представленных фрагментов.'
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  team_roles:
    text: Роли внутри системы распределены на teaching agents, которые моделируют
      аспекты преподавания; learning agents, представляющие учеников в диалогах; и
      evaluation agents, анализирующие поведение LLM как педагогов. Такой разделённый
      multi-agent состав обеспечивает раздельную оценку и симуляцию различных педагогических
      функций в диалоге, что формирует репрезентативную экосистему для instructional
      benchmarking.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  ai_role:
    text: AI выступает в роли распределённого эмулятора и оценщика teaching behaviour
      LLM. Он не заменяет учителя, а генерирует и координирует многоголосные диалоги,
      моделирующие педагога, ученика и оценщика, что даёт возможность объективно измерять
      способность LLM к педагогической коммуникации и адаптации. Таким образом AI
      — evaluation и teaching partner в целевом эксперименте, но не диспетчер образовательного
      процесса непосредственно.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  interaction_scenario:
    text: Сценарии базируются на multi-agent dialogue sessions с участием teaching,
      learning и evaluation агентов, взаимодействующих через серии вопросов и ответов
      (1 498 вопросов по 13 дисциплинам). Каждый LLM проходит эти сессии, где агенты
      моделируют учебное взаимодействие и педагогическую оценку. Сценарий позволяет
      выявить способности и ограничения модели в teaching context, с учётом разных
      сложностей и направлений дисциплин.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  metrics_evidence:
    text: Проведено тестирование 14 LLM из разных AI организаций на 1 498 вопросах,
      охватывающих 13 дисциплин и 10 уровней сложности. Выявлено, что teaching effectiveness
      не коррелирует прямо с масштабом модели или общим reasoning capacity. Некоторые
      меньшие open-source модели превзошли крупные коммерческие аналоги в педагогическом
      контексте, что является важным empirical evidence. Это подчёркивает необходимость
      специализированной оценки pedagogical функций LLM, выходящей за рамки традиционных
      general benchmarks.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  theory_links:
    text: Кейс затрагивает гипотезу agentivity уровней 2–3/6 в multi-agent evaluation
      и демонстрирует значение orchestration по NET фасете с AUTO pedagogy и MACH
      control. Работы перекликаются с [[H4-teaching-effectiveness]], [[A-multi-agent-orchestration]],
      а также указывают на важность теории role-based agent specificity в обучении
      и оценке. Кейс дополняет линии исследований multi-agent AI for education, инаугурируя
      переход к комплексным педагогическим evaluation frameworks и поднимает вопросы
      о сложностях benchmarking teaching abilities в LLM-педагогиках.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
---

## Описание

EducationQ — multi-agent dialogue framework для оценки педагогических
способностей LLM: teaching-agent / learning-agent / evaluation-agent
ведут полный цикл. Прикладной слой к [[H2-assistant-to-autonomy]].
