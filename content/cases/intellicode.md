---
id: intellicode
name: IntelliCode · StateGraph orchestration for coding tutor
organization:
  name: IntelliCode research group
  type: R
  country: INT
scenario:
  level:
  - undergraduate
  domains:
  - programming
  context: research-prototype
facets:
  orchestration: META
  pedagogy: AUTO
  control: HYBR
  economy: NONE
ai:
  pattern: B
  agentivity: 3
  technologies:
  - stategraph
  - multiple-models
  role: 6 agents + centralized learner state
transformation_mode: greenfield
axes:
  agentivity: 3
  ai_pattern: B
  orchestration: META
  control_locus: HYBR
  interaction_form: agent-workflow
  domain_specificity: 5
  audit_trail_strength: 5
  has_persistent_state: true
  evaluation_evidence_strength: 2
lifecycle:
  stage: poc
  first_seen: diff-2026-06
  history:
  - wave: diff-2026-06
    stage: poc
    note: 'StateGraph Orchestrator + 6 агентов: skill assessment, learner profiling,
      hinting, curriculum, spaced repetition, engagement'
links:
- kind: type
  id: B
  relation: instantiates
  confidence: high
- kind: hypothesis
  id: H2
  relation: supports
  confidence: high
sources:
- url: https://arxiv.org/
  type: academic
  accessed: 2026-06
verified: false
canvas:
  signature_context:
    text: 'IntelliCode — агентная система с centralized versioned learner state и

      StateGraph Orchestrator, координирующим 6 агентов. Решает проблему

      single-turn assistants через persistent memory + spaced repetition.

      Образец «агентного семинариста с памятью».'
    status: draft
    source: imported
    updated_at: '2026-06-12'
  ontology_status:
    text: IntelliCode представлен исследовательским прототипом, а не реальным производственным
      внедрением. Validation происходит через симуляции обучающихся, что указывает
      на статус прототипа с низким уровнем зрелости для практического применения в
      классах. Несмотря на высокий инженерный уровень архитектуры, система ещё не
      прошла pilot-перетрансляцию в полноценный курс или institutional rollout.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  problem_situation:
    text: Без persistent learner representation современные single-turn ассистенты
      не могут вести долгосрочную педагогическую поддержку эффективно. Проблема в
      том, что без централизованного и версионированного состояния обучающегося невозможно
      аккумулировать и координировать знания о его мастерстве, некорректных концепциях,
      расписаниях повторений и мотивационных сигналах для адаптивного обучения.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  effect_hypothesis:
    text: IntelliCode обещает добиться многоагентной оркестрации с persistent learner
      state, которая позволит шести специализированным агентам (skill assessment,
      learner profiling, graduated hinting, curriculum selection, spaced repetition
      и engagement monitoring) совместно вести долгосрочную персонализацию обучения.
      Это должно обеспечить аудируемые обновления модели обучающегося с эффективным
      управлением памятью и интервалами повторений, что улучшит качество кодинг-обучения
      по сравнению с single-turn чат-ассистентами.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  ai_architecture:
    text: 'Архитектура построена вокруг централизованного и версионированного learner
      state, который содержит оценку мастерства, ошибки в знаниях, расписание повторений
      и сигналы вовлечённости. StateGraph Orchestrator обеспечивает координацию шести
      агентов: skill assessment, learner profiling, graduated hinting, curriculum
      selection, spaced repetition и engagement monitoring. Используется принцип single-writer
      policy для обновления состояния. Технологии включают надежное multi-model многопроцессное
      взаимодействие и persistent shared state для гарантий согласованности и аудируемости.'
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  team_roles:
    text: 'Команда состоит из шести AI-агентов, разделяющих педагогические функции:
      оценка навыков, профиль обучающегося, подсказки разного уровня, выбор учебной
      программы, интервальное повторение и мониторинг вовлечённости. Роли распределены
      по специализациям и скоординированы централизованным оркестратором StateGraph.
      Это пример мультиагентной архитектуры с разделением и специализацией ролей в
      образовании.'
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  ai_role:
    text: AI функционирует как multi-agent system, где шесть специализированных агентов
      совместно управляют долгосрочной моделью обучающегося и педагогическими стратегиями.
      Роль AI — не просто реакция на запросы, а активное оперирование глобальным состоянием
      learning journey, планирование занятий, контроль прогресса, поддержка мотивации
      и автоматический триггер повторений, обеспечивая более глубокую персонализацию.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  interaction_scenario:
    text: В процессе взаимодействия централизованный learner state обновляется агентами
      по мере прогресса студента. Агент оценки навыков анализирует новый ввод, агент
      профилирования обновляет модель обучающегося, агент подсказок формирует graduated
      hints, агент подбора учебного материала корректирует программу, агент интервального
      повторения рассчитывает оптимальные моменты для ревизии, а агент мониторинга
      вовлечённости подает сигналы для адаптации. Все взаимодействия управляются StateGraph
      Orchestrator, обеспечивая согласованность и аудируемость.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  institutional_loop:
    text: На текущем этапе отсутствует явно описанная институциональная практика governance
      или нормативно-правовая база. Система находится в исследовательском прототипе
      без интеграции в реальную образовательную политику или data governance. Таким
      образом, вопросы защиты данных обучающихся, управления обновлениями модели и
      прозрачности находятся в поле будущих разработок.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  transit_to_life:
    text: До сих пор внедрение ограничивается исследовательскими валидациями с симулированными
      обучающимися. Нет информации о завершенных пилотах или развертывании в реальных
      курсах. Предполагается, что будущие фазы включают контрольное тестирование на
      живых студентах с учетом норм и стандартов университета с возможными корректировками
      архитектуры и workflow.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  metrics_evidence:
    text: Поскольку реализация пока не внедрена в живые курсы, базовые метрики основаны
      на simulation-based validation и моделировании. Agenctность оценена на уровне
      3/6 в шкале агентности пользователя, что означает распределение ролей и persistent
      state, но отсутствует внешний показатель учебного успеха у реальных студентов.
      Verifiable data ограничены мастерством, ошибками, комплексностью расписаний
      повторений и взаимодействиями симулированных агентов.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  risks:
    text: Ключевой риск — goal-substitution, когда фокус системы смещается с реального
      улучшения учебных результатов к управлению internal state без внешней подтверждаемой
      эффективности. Отсутствует strong audit trail в реальных условиях, что может
      привести к слабому контролю качества. Vendor lock-in не упоминается, но прототиповый
      статус минимизирует рыночные риски. Есть риск завышенных ожиданий из-за сложной
      архитектуры без полевых тестов.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  countersignals:
    text: На сегодняшний день не выявлено явных противоречий в заявленной практике,
      однако model работает в симуляционном режиме, что противоречит ожиданиям реального
      classroom deployment. Это важный countersignal — пока технология осталась в
      прототипе, несмотря на техническую зрелость архитектуры.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  transferability:
    text: Паттерн IntelliCode — centralized persistent learner modeling + StateGraph
      multi-agent orchestration — может быть перенесён в любые контексты с длительными
      образовательными траекториями, где требуется координация множества педагогических
      ролей, например, инженерное образование, языковые курсы и профессиональная переподготовка.
      Модель соотносимая с другими multi-agent tutoring системами и многослойными
      педагогическими контроллерами [[CogEvo-Edu]], [[GraphMASAL]].
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  theory_links:
    text: IntelliCode относится к типу B agent pattern с агентностью уровня 3 из 6,
      опирается на фасеты META (orchestration), AUTO (pedagogy automatic), HYBR (control)
      и использует multi-model architectures с centralized persistent state. Включение
      StateGraph соответствует метамоделям многоагентной оркестрации, см. [[multi-agent
      tutoring]], [[persistent learner modeling]], а также подтверждает эволюционный
      тренд отхода от single-turn ассистентов к agentic systems с долгосрочной памятью
      и стратегическим планированием [[acceleration]], [[autonomy-vs-control]].
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  open_questions:
    text: Остаётся неясным, насколько схема масштабируема на реальные курсы с живыми
      студентами, каковы реальные эффекты качества обучения и вовлечённости. Нет данных
      по вопросам защиты персональных данных и аудита модели в живом использовании.
      Вопросы по переходу от симуляции к практике и требуемым организационным изменениям
      также остаются открытыми.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  next_wave_followup:
    text: В следующем цикле проверки необходимо уточнить результаты пилотного внедрения
      в учебных классах, получить реальные метрики эффективности и вовлечения, а также
      оценить институциональную готовность к масштабированию и governance framework.
      Следует проверить устойчивость агентной оркестрации в условиях шумных real-world
      данных и адаптации к разнообразным студентам.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  sources_verification:
    text: Данные кейса основаны на arXiv публикации исследовательской команды IntelliCode
      research group. Верификация сведений затруднена отсутствием публикаций из реальных
      внедрений и публикаций с независимой оценкой. Требуется доп. подтверждение от
      пилотных пользователей или из университетских отчетов.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
---

## Описание

IntelliCode — агентная система с centralized versioned learner state и
StateGraph Orchestrator, координирующим 6 агентов. Решает проблему
single-turn assistants через persistent memory + spaced repetition.
Образец «агентного семинариста с памятью».
