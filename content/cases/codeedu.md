---
id: codeedu
name: CodeEdu · multi-agent coding education platform
organization:
  name: CodeEdu research group
  type: R
  country: INT
scenario:
  level:
  - undergraduate
  - professional
  domains:
  - programming
  context: research-prototype
facets:
  orchestration: NET
  pedagogy: AUTO
  control: HYBR
  economy: NONE
ai:
  pattern: B
  agentivity: 3
  technologies:
  - multiple-models
  role: task planner + tutor + code executor + debugger + report generator
transformation_mode: greenfield
axes:
  agentivity: 3
  ai_pattern: B
  orchestration: NET
  control_locus: HYBR
  interaction_form: agent-workflow
  domain_specificity: 5
  audit_trail_strength: 4
  evaluation_evidence_strength: 2
  has_persistent_state: true
lifecycle:
  stage: poc
  first_seen: diff-2026-06
  history:
  - wave: diff-2026-06
    stage: poc
    note: 'multi-agent: task planning, personalized material gen, real-time QA, step-by-step
      tutoring, code exec, debug, learning report'
links:
- kind: type
  id: B
  relation: instantiates
  confidence: high
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
    text: 'CodeEdu — multi-agent платформа для персонализированного обучения

      программированию: task planning, code execution, debugging, learning

      report generation. Без реального course deployment. Тип [[B-no-code-builder]]

      в research-форме.'
    status: draft
    source: imported
    updated_at: '2026-06-12'
  ontology_status:
    text: CodeEdu представляет собой исследовательскую архитектуру — multi-agent collaborative
      platform для персонализированного обучения программированию. Это не полноценное
      развернутое решение («в продакшне»), а prototype/architectural case с уровнем
      агентности 3/6, где AI-агенты распределяют педагогические и инженерные функции,
      но нет данных о реальном институциональном внедрении. Рассматривается как исследовательская
      разработка, показывающая возможности мультиагентной организации в coding education.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  problem_situation:
    text: До появления CodeEdu не было решения, которое системно распределяло бы задачи
      персонализированного обучения программированию между несколькими агентами с
      функционалами от планирования задач до выполнения и проверки кода и генерации
      обучающих отчетов. Существующие ChatGPT-помощники или монолитные модели не обеспечивали
      органическую координацию ролей tutor, debugger и report generator в единой платформе
      и не подстраивались динамически под индивидуальные потребности студента.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  effect_hypothesis:
    text: 'CodeEdu обещает повысить качество персонализации обучения программированию
      за счет multi-agent collaboration, где каждый агент отвечает за отдельный этап:
      планирование задач, предоставление обучающих материалов, пошаговое сопровождение,
      выполнение и отладку кода, формирование отчетов о прогрессе. Такой дистрибутивный
      подход ориентирован на улучшение coding performance и оптимизацию учебного процесса
      с помощью динамического распределения ресурсов и автоматических оценок.'
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  ai_architecture:
    text: 'В платформе CodeEdu применяется мультиагентная архитектура с интеграцией
      нескольких моделей и инструментов. Роли агрегированы по функционалу: task planner,
      tutor, code executor, debugger и report generator. Эта система мультиагентов
      строится на стеке, включающем динамическое назначение задач и использование
      нескольких моделей ИИ для решения конкретных подзадач. Хотя нет подробностей
      по провайдерам или версиям, архитектура предполагает orchestration NET вместе
      с AUTO педагогикой и гибридным контролем (HYBR).'
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  team_roles:
    text: В архитектуре кодирования специфичные роли людей ещё мало детализированы,
      так как кейс исследовательский. Однако предполагается наличие разработчиков
      платформы, педагогов-дизайнеров курсов и конечных пользователей-студентов. От
      человеческой команды требуется координация с AI-моделями, в частности в вопросах
      создания учебных траекторий, оценки результатов и анализа.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  ai_role:
    text: 'ИИ выступает как распределённый multi-agent tutor, выполняющий задачи planner
      + tutor + code executor + debugger + report generator. То есть ИИ интегрирован
      и в педагогические, и в технические процессы: планирует учебные задачи, сопровождает
      студента, интерпретирует и выполняет код, выявляет ошибки, выдает рекомендации
      и генерирует отчёты. Это даёт агентность 3 из 6, свидетельствующую о средней
      степени автономии и распределённости функций между агентами.'
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  interaction_scenario:
    text: В типичном сценарии пользователь запускает сессию обучения, после чего агенты
      CodeEdu распределяют образовательные задачи. Планировщик формирует учебный план,
      tutor ведёт обучение шаг за шагом, code executor проверяет и запускает код,
      debugger анализирует ошибки, а report generator формирует отчет о прогрессе.
      Эти агенты динамически координируются под конкретного студента, обеспечивая
      адаптацию контента и помощи в реальном времени.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
---

## Описание

CodeEdu — multi-agent платформа для персонализированного обучения
программированию: task planning, code execution, debugging, learning
report generation. Без реального course deployment. Тип [[B-no-code-builder]]
в research-форме.
