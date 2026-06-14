---
id: genmentor
name: GenMentor · multi-agent goal-oriented learning framework
organization:
  name: GenMentor research group
  type: R
  country: INT
scenario:
  level:
  - professional
  - adult-learner
  domains:
  - skills
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
  - fine-tuned-llm
  role: goal-to-skill mapping + learning path scheduling
roles:
  human:
  - learner
  machine:
  - goal-to-skill mapper
  - gap analyzer
  - path planner
  - content generator
  interaction_scenario: 'Учащийся задаёт цель → fine-tuned LLM маппит цель в skills
    → анализ

    gap → evolving optimization строит learning path → exploration-drafting-

    integration генерирует контент.

    '
transformation_mode: greenfield
axes:
  agentivity: 3
  ai_pattern: B
  orchestration: NET
  control_locus: HYBR
  interaction_form: agent-workflow
  scale_of_change: 3
  institutional_depth: 1
  audit_trail_strength: 4
  evaluation_evidence_strength: 3
  has_persistent_state: true
  reflexivity: 3
lifecycle:
  stage: poc
  first_seen: diff-2026-06
  history:
  - wave: diff-2026-06
    stage: poc
    note: automated/human evaluation + practical deployment с professional learners
links:
- kind: type
  id: B
  relation: instantiates
  confidence: medium
- kind: hypothesis
  id: H2
  relation: supports
  confidence: high
- kind: hypothesis
  id: H3
  relation: supports
  confidence: medium
- kind: mode
  id: re-skilling
  relation: supports
  confidence: high
sources:
- url: https://arxiv.org/
  type: academic
  accessed: 2026-06
verified: false
canvas:
  signature_context:
    text: 'GenMentor — multi-agent framework, который переводит цель учащегося в

      skill map, строит learning path и генерирует адаптивный контент.

      AI действует как педагогический планировщик, диагност и генератор.

      Эталон агентности 3/6. Поддерживает [[H2-assistant-to-autonomy]] и

      моду [[re-skilling]].'
    status: draft
    source: imported
    updated_at: '2026-06-12'
  ontology_status:
    text: GenMentor представлен как deployed/application плюс исследование (study),
      то есть это не просто прототип или симуляция, а реальный кейс с внедрением и
      оценкой в живых условиях. Это подтверждает позицию кейса как практического решения
      в контексте multi-agent goal-oriented learning frameworks.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  problem_situation:
    text: В традиционном AI-образовании проблема заключалась не в одиночных ответах
      на запросы студента, а в отсутствии системного подхода, который связывают цели
      обучения с необходимыми навыками (goal-to-skill mapping), выявляет skill gaps
      и строит индивидуальные учебные траектории (learning path scheduling). В частности,
      отсутствие педагогического планировщика с диагностикой и генерацией маршрутов
      препятствовало персонализации и целенаправленному развитию компетенций.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  effect_hypothesis:
    text: GenMentor обещает повысить эффективность обучения за счёт автоматизации
      структурирования целей обучающегося в набор необходимых скиллов, выявления пробелов
      в знаниях, построения оптимального персонализированного учебного пути и динамической
      генерации учебного контента под конкретные дефициты. Такая orchestration управляется
      multi-agent framework с уровнем агентности 3/6, что означает автономную координацию
      нескольких функций AI для поддержки гибкого адаптивного обучения.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  ai_architecture:
    text: Архитектура GenMentor опирается на fine-tuned LLM, который выступает ключевым
      компонентом для goal-to-skill mapping. Для построения расписания траекторий
      используется evolving optimization approach, при этом профиль обучающегося является
      динамическим (dynamic learner profile). Контент создаётся через механизм exploration–drafting–integration,
      который адаптирует учебные материалы под выявленные skill gaps. Таким образом
      система функционирует как orchestration NET-тип с hybrid control, объединяя
      автоматический и управляемый AI-подходы.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  institutional_loop:
    text: В кейсе отмечен деплоймент и практика с профессиональными обучающимися,
      вместе с human study, что свидетельствует о наличии циклов обратной связи между
      разработчиками, пользователями и управляющими структурами. Однако конкретные
      governance-политики и нормативы в открытых данных подробно не освещены.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  transferability:
    text: Паттерн полного goal-to-skill mapping и learning path orchestration сильно
      релевантен для специализированных образовательных платформ, особенно тех, что
      ориентированы на adaptive learning и персонализированное образование. Это может
      быть полезно в корпоративном обучении, профессиональной подготовке и университетских
      образовательных траекториях, где требуется адаптация под конкретные карьерные
      цели ученика. В сравнении с кейсом ITAS Old Dominion University и CodeEdu, GenMentor
      выделяется как пример системного педагогического планировщика в многоагентной
      среде.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  theory_links:
    text: Кейс GenMentor затрагивает тип B из классификации AI-паттернов с агентностью
      уровня 3/6, что соответствует распределённой педагогической оркестрации в сетевом
      (NET) фасете. Его особенности включают goal-to-skill mapping и гибридный (HYBR)
      контроль образовательного процесса. В терминологии гипотез волны, кейс иллюстрирует
      переход от гипотезы H1 ('AI отвечает на вопросы') к H3/H4, где AI выступает
      как педагогический планировщик и диагностический игрок, создавая образовательные
      траектории. Это связано с [[H4-agentic-orchestration]] и [[autonomy-vs-control]],
      где AI балансирует между автономией и контролем со стороны пользователя и организатора
      обучения.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
---

## Описание

GenMentor — multi-agent framework, который переводит цель учащегося в
skill map, строит learning path и генерирует адаптивный контент.
AI действует как педагогический планировщик, диагност и генератор.
Эталон агентности 3/6. Поддерживает [[H2-assistant-to-autonomy]] и
моду [[re-skilling]].
