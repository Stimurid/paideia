---
id: ut-sage
name: UT Austin · UT Sage (Socratic tutorbot builder)
organization:
  name: The University of Texas at Austin
  type: U
  country: US
scenario:
  level:
  - undergraduate
  - graduate
  domains:
  - general
  context: lms-integrated
facets:
  orchestration: MOD
  pedagogy: ROLE
  control: HUMAN
  economy: BUD+EXT
ai:
  pattern: C
  agentivity: 2
  technologies:
  - gpt-4o
  - custom-prompting
  role: socratic tutorbot builder + canvas integration
orchestration_roles:
- faculty-designer
- students
- IT-team
- AI-tutor
roles:
  human:
  - faculty-designer
  - student-user
  machine:
  - tutorbot
  - syllabus-grounding
  interaction_scenario: 'Преподаватель проходит learning-design wizard, загружает
    материалы,

    задаёт Socratic-ограничения. Студенты получают доступ к tutorbot

    прямо из Canvas-меню курса.

    '
traces:
  logs: true
  prompts_versioned: true
  data_sources:
  - course-materials
  - syllabus
transformation_mode: campus-wide
axes:
  agentivity: 2
  ai_pattern: C
  orchestration: MOD
  control_locus: HUMAN
  provider_lock_in: 3
  rag_grounded: true
  has_persistent_state: false
  audit_trail_strength: 4
  domain_specificity: 3
  evaluation_evidence_strength: 2
  interaction_form: persona-roleplay
  pedagogy_transformation: ROLE
  transformation_mode: campus-wide
  scale_of_change: 3
  institutional_depth: 4
  radicalness: 3
  reversible: true
  governance_strength: 4
  portability: 4
  reflexivity: 3
  human_role_complexity: 3
  data_sensitivity: 2
  cost_intensity: 3
  lms_integration: true
  has_metrics: false
lifecycle:
  stage: rollout
  first_seen: wave-1
  history:
  - wave: wave-1
    stage: pilot
    note: пилоты Fall 2024 / Spring 2025
  - wave: wave-2
    stage: rollout
    note: общекампусный доступ Fall 2025 в рамках security/privacy политик
links:
- kind: type
  id: C
  relation: instantiates
  confidence: high
- kind: type
  id: B
  relation: instantiates
  confidence: high
- kind: hypothesis
  id: H2
  relation: supports
  confidence: medium
- kind: tension
  id: generation-vs-verification
  relation: weakens
  confidence: medium
metrics:
  hard: []
  soft:
  - canvas-integration
  - syllabus-grounded
  - socratic-constrained
sources:
- url: https://sage.utexas.edu/
  type: official
  accessed: 2026-02
verified: true
canvas:
  signature_context:
    text: 'UT Sage — конструктор Socratic tutorbots с интеграцией в Canvas.

      Преподаватель проходит learning-design wizard, загружает материалы и

      получает grounded-бота, который ведёт диалог по правилам курса. Эволюция

      от факультетских пилотов к общекампусной платформе.'
    status: draft
    source: imported
    updated_at: '2026-06-12'
  transferability:
    text: 'Эталон типа C (pedagogy-shaped dialogue): педагогический режим встроен
      в

      бота явно через wizard, а не оставлен на усмотрение пользователя.

      Connected to Canvas — естественный путь для студентов.'
    status: draft
    source: imported
    updated_at: '2026-06-12'
  ontology_status:
    text: UT Sage реализован как устойчивое кампусное решение, находящееся в стадии
      pilot с расширением к полноценному rollout-у на кампус. Это не просто прототип,
      а уже институционально закрепленная платформа с интеграцией в LMS (Canvas).
      По шкале Wave2 агентность зафиксирована на уровне 2/6, что предполагает функциональную
      роль без полного автономного цикла. Университет акцентирует контроль над данными
      и доступностью, следовательно UT Sage соответствует категории 'внедрение/кампусный
      rollout' с ограниченной автономностью AI-составляющей.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  problem_situation:
    text: До внедрения UT Sage возникали проблемы с качественной поддержкой Socratic-методики
      и персонализированного диалога в обучении, а также отсутствовала интеграция
      AI в привычные учебные системы (LMS). Без AI-помощника преподавателям было сложно
      создавать интерактивных tuteurbot-ов с поддержкой учебного материала курса,
      требовалось ручное сопровождение и ограниченное вовлечение студентов в глубокий
      диалог. Также существовал риск утечки или недостаточного контроля над учебными
      данными при использовании внешних AI-сервисов.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  effect_hypothesis:
    text: Внедрение UT Sage обещает обеспечить функциональную роль AI в качестве Socratic
      tutorbot, который ведет диалог, стимулирующий навыки критического мышления.
      AI встроен в Canvas, предоставляя удобный доступ студентам в контексте курса.
      Предполагается повышение вовлеченности студентов и улучшение интерактивности
      обучения без утраты контроля со стороны преподавателя. В частности, подчеркивается
      возможность ответов AI строго на основе загруженного силлабуса (course-specific
      content), а не как универсального чатбота.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  ai_architecture:
    text: 'Архитектура UT Sage включает несколько ключевых ролей: (1) преподаватель-дизайнер,
      который создает Socratic tutorbot, определяет цели обучения и загружает учебные
      материалы и силлабус; (2) студент-пользователь, взаимодействующий с ботом через
      Canvas; (3) AI-тьютор, реализующий функциональность Socratic диалога и интерпретирующий
      курс-специфическую информацию в диалоге; (4) LMS-контур (Canvas), обеспечивающий
      интеграцию и выдачу доступа пользователям. Технологически AI основан на GPT-4o
      с кастомными промптами и внутренними настройками под конкретные курсы без автономного
      самообучения или полноценных циклов оценки/интервенции. Агентность по Wave2
      — 2/6. Менеджмент данных сфокусирован на закрытых институциональных контурах.'
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  team_roles:
    text: 'В UT Sage выделены следующие человеческие роли: преподаватель-дизайнер,
      ответственный за создание и настройку Socratic tutorbots с учётом учебного плана;
      студент, получающий доступ к ботам через LMS и взаимодействующий с ними в диалоговой
      форме; команда поддержки обучения и ИТ-служба, обеспечивающие интеграцию с Canvas
      и сопровождение платформы; административные лица, занимающиеся политиками доступа
      и безопасностью данных. AI выступает как отдельный цифровой агент с функциональной
      ролью, при этом контроль и руководство осуществляет человек.'
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  ai_role:
    text: AI в UT Sage исполняет роль Socratic tutorbot — диалогового тьютора, который
      направляет обучение через вопросы, стимулирует мышление и взаимодействует по
      course-specific контенту. Он не заменяет преподавателя, а действует в рамках
      заданных сценариев и ограничений, интегрирован в систему LMS для удобного доступа.
      AI не обладает автономией полного цикла обучения, его агентность оценивается
      как 2/6, что соответствует функциональной и педагогически структурированной
      роли, а не как автономный агент или ассистент широкого спектра.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  interaction_scenario:
    text: 'Практика взаимодействия построена следующим образом: преподаватель-конструктор
      создаёт Socratic tutorbot, загружая учебный силлабус и материалы через специальный
      интерфейс. Студенты получают доступ к ботам непосредственно через меню курса
      в Canvas, начиная диалоги по темам курса. AI-тьютор ведёт последовательный Socratic-dialogue,
      зазывая студентов к размышлениям и ответам, основанным на материалах курса.
      В процессе преподаватель может обновлять и адаптировать содержание, обеспечивая
      постоянное соответствие учебным целям. Такая оркестрация включает чёткие роли
      и взаимодействия между преподавателем, студентом, AI и LMS.'
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  institutional_loop:
    text: UT Sage находится под управлением Office of Academic Technology Университета
      Техаса в Остине, что обеспечивает институциональную поддержку и нормативные
      рамки. В университетской политике подчеркивается безопасность, приватность и
      управление данными с акцентом на закрытую инфраструктуру. Governance модели
      включают контроль доступа через Canvas, а также регулирование рождается на уровне
      университетских правил по защите данных и ответственному использованию AI в
      образовании. Отметается автономия AI по управлению/оценке курсов, сохраняя роль
      преподавателя как главного контролера.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  transit_to_life:
    text: UT Sage прошёл пилоты в осеннем семестре 2024 и весеннем 2025, после чего
      планируется расширение доступности для широкой университетской аудитории в Fall
      2025. Rollout сопровождается уточнением правил безопасности и приватности, корректировками
      интеграции с Canvas и расширением функциональности tutorbot-ов. Отзывы и адаптации
      преподавателей учитываются для улучшения платформы, а также идет работа над
      оптимизацией пользовательского опыта студентов. Таким образом происходит постепенная
      институционализация и масштабирование решения.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  metrics_evidence:
    text: 'Публичных количественных метрик по эффектам обучения UT Sage не предоставляет.
      Есть свидетельства расширения пилотного охвата студентов и курсов, а также фиксация
      масштаба внедрения: Fall 2024/Spring 2025 пилоты; Fall 2025 — кампусный доступ
      ''для всех'' по campus governance. Отслеживаются usage-метрики интеграции (например,
      количество курсов c tutorbot-ами, активность студентов в диалогах). Однако данные
      об изменении learning gains, вовлеченности или успеваемости не опубликованы.
      Метрики сосредоточены на архитектурной верификации и масштабе применения.'
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  risks:
    text: Одним из рисков является злоупотребление AI как универсальным чатботом,
      что противоречит назначенной роли Socratic tutorbot и может снизить педагогическую
      ценность. Целесообразно отслеживать goal-substitution, когда преподаватели или
      студенты используют AI не по назначению. Также отмечается риск vendor lock-in,
      если платформа будет привязана к внешним GPT-4o сервисам без опций локального
      управления. Низкая автономия AI ограничивает риск слабой трассировки принятия
      решений, однако governance должен обеспечивать прозрачность и контроль со стороны
      преподавателя и ИТ.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  countersignals:
    text: Практика иногда расходится с заявленной строгой ролью tutorbot, если пользователи
      пытаются использовать AI для ответов вне рамок загруженного силлабуса или вне
      учебных целей. Это явное countersignal, сигнализирующий о необходимости дополнительного
      обучения пользователей или технических ограничений на генерацию вне контекста.
      Также возможно возникновение ситуаций, когда AI становится скорее пассивным
      источником информации, чем активным Socratic собеседником, что понижает уровень
      agentivity.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  theory_links:
    text: 'UT Sage является примером функциональной роли AI (Wave2: agentivity 2/6)
      в педагогическом моде ROLE и оркестрации MOD, с человеческим контролем (control:
      HUMAN) и экономикой, поддерживаемой бюджетом и внешними ресурсами (BUD+EXT).
      Он иллюстрирует тип C (edtech/корпоративные провайдеры обучающих сред) по классификации
      типов кейсов. В теоретических рамках связан с гипотезами об agentic AI в образовании,
      но подтверждает, что автономные многоагентные системы (3 и выше) пока не внедрены.
      UT Sage подтверждает эволюционный трек институционального контроля и повышенного
      human-in-loop управления [[H2-agentivity]], [[A-governed-access]], [[ROLE-pedagogy]].'
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  open_questions:
    text: Остаётся неясным, какие именно количественные показатели эффективности обучения
      UT Sage демонстрирует в долгосрочной перспективе и насколько Socratic tutorbot
      реально улучшает когнитивные навыки студентов. Неадекватное внимание к метрикам
      влияет на принятие решений по масштабированию. Также неизвестна степень адаптивности
      AI при разнообразных курсах и дисциплинах, а также как будут решаться потенциальные
      этические и privacy вызовы в развитии платформы. Будут ли интегрированы более
      автономные функции и как изменится роль преподавателя — важные вопросы для следующих
      фаз.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  next_wave_followup:
    text: В следующих волнах важно перепроверить реализуемость и качество Socratic
      диалогов, собирая user feedback преподавателей и студентов, а также внедрять
      и оценивать количественные метрики learning gains. Надо проследить динамику
      agentivity — нельзя ли повысить её с текущих 2/6 к уровню 3+ без потери контроля.
      Также стоит исследовать, как Governance механизмы масштабируются и как platform
      policies реагируют на расширение спектра бот-ролей. Важно наблюдать, как AI
      tutorbots вписываются в broader campus AI orchestration ecosystem.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  sources_verification:
    text: Данные о UT Sage подтверждены официальными источниками The University of
      Texas at Austin, включая Office of the Executive Vice President and Provost,
      учебные сайты и FAQ. Публикации и видеоматериалы фиксируют архитектуру, Canvas-интеграцию,
      временную шкалу пилотов и rollout. Информация о технологиях (GPT-4o, custom
      prompting) взята из официальных описаний, а agentivity и роли — из анализа waves
      1–4 и глобальной картографии образовательных AI-кейсов. Однако легкодоступных
      метрик обучения и результативности публично нет.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
---

## Описание

UT Sage — конструктор Socratic tutorbots с интеграцией в Canvas.
Преподаватель проходит learning-design wizard, загружает материалы и
получает grounded-бота, который ведёт диалог по правилам курса. Эволюция
от факультетских пилотов к общекампусной платформе.

## Что переиспользуемо

Эталон типа C (pedagogy-shaped dialogue): педагогический режим встроен в
бота явно через wizard, а не оставлен на усмотрение пользователя.
Connected to Canvas — естественный путь для студентов.
