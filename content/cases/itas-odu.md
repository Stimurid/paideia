---
id: itas-odu
name: Old Dominion University · ITAS (Intelligent Teaching Assistant System)
organization:
  name: Old Dominion University
  type: U
  country: US
scenario:
  level:
  - graduate
  domains:
  - quantum-computing
  context: course-deployment
facets:
  orchestration: NET
  pedagogy: ROLE
  control: HYBR
  economy: BUD
ai:
  pattern: B
  agentivity: 3
  technologies:
  - multiple-models
  - cloud-run
  - bigquery
  role: multi-agent tutor (Video/Code/Guidance + Synthesizer + autograder)
orchestration_roles:
- instructor
- students
- specialist-agents
- synthesizer
- autograder
roles:
  human:
  - instructor
  - student
  machine:
  - video-agent
  - code-agent
  - guidance-agent
  - synthesizer
  - autograder
  interaction_scenario: 'Студент идёт по teaching layer (specialist-agents + synthesizer
    +

    autograder), operational layer ведёт логи и события, feedback layer

    даёт инструктору conversational analytics по псевдонимизированным

    событиям.

    '
traces:
  logs: true
  prompts_versioned: true
  data_sources:
  - course-materials
  - syllabus
transformation_mode: experimental-cell
axes:
  agentivity: 3
  ai_pattern: B
  orchestration: NET
  control_locus: HYBR
  interaction_form: multi-agent-simulation
  scale_of_change: 2
  institutional_depth: 2
  domain_specificity: 5
  audit_trail_strength: 5
  evaluation_evidence_strength: 4
  has_persistent_state: true
  rag_grounded: true
  reflexivity: 3
  has_metrics: true
lifecycle:
  stage: pilot
  first_seen: diff-2026-06
  history:
  - wave: diff-2026-06
    stage: pilot
    note: семестровый деплой в graduate quantum computing; 5 студентов; 334 chat turns;
      10628 events; 2 instructor-actionable findings
links:
- kind: type
  id: B
  relation: instantiates
  confidence: high
- kind: hypothesis
  id: H2
  relation: supports
  confidence: high
- kind: tension
  id: simulation-vs-engineering-power
  relation: weakens
  confidence: medium
metrics:
  hard:
  - students-5
  - chat-turns-334
  - events-10628
  soft:
  - event-memory
  - autograder-approach-eval
sources:
- url: https://arxiv.org/abs/
  type: academic
  accessed: 2026-06
verified: true
canvas:
  signature_context:
    text: 'ITAS — production-like multi-agent tutor, реально работавший семестр в

      graduate quantum computing курсе ODU. Spoke-and-wheel композиция

      specialist agents + Synthesizer + autograder, Cloud Run microservices,

      BigQuery-логи, instructor analytics. Это редкий пример агентности 3/6 с

      эмпирической базой. Поддерживает [[H2-assistant-to-autonomy]]; ослабляет

      противоречие [[simulation-vs-engineering-power]] (есть реальный деплой).'
    status: draft
    source: imported
    updated_at: '2026-06-12'
  ontology_status:
    text: 'ITAS на Old Dominion University — реальный развернутый прототип multi-agent
      tutoring system с использованием нескольких специализированных агентов и продвинутой
      инфраструктуры, развернутый в production-like режиме на курсе graduate quantum
      computing. Статус — прототип с успешным внедрением в учебный процесс, а не просто
      экспериментальная модель.


      Используется cloud-run микросервисы, BigQuery для хранения и анализа событий,
      что показывает зрелый уровень реализации и прототипирования, приближенный к
      промышленным решениям.'
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  problem_situation:
    text: До внедрения ITAS в Old Dominion University отсутствовал инструмент, способный
      распределять педагогические функции между несколькими агентыми с учётом событийной
      памяти, автоматизированной проверки не только правильности сдачи заданий, но
      и подхода к решению, и предоставлять инструктору аналитический слой на базе
      псевдонимизированных данных общения. Аналогичные системы либо были единоагентными,
      либо не интегрировались напрямую в учебные курсы, что ограничивало возможности
      поддержки студентов и преподавателей в сложных предметах, таких как квантовые
      вычисления.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  effect_hypothesis:
    text: 'ITAS обещает обеспечить multi-agent tutoring на уровне агентности 3/6,
      где специализированные агенты (Video, Code, Guidance) взаимодействуют в комплексе
      с Synthesizer и autograder, предоставляя глубокую поддержку обучения. Система
      направлена на повышение эффективности обучения через автоматическую проверку
      подходов к задачам и анализ поведения студентов для инструкторов, расширяя возможности
      персонализации и обратной связи в реальном учебном процессе.


      Ожидается, что такой подход позволит усилить роль AI как реального партнёра
      в обучении, способного распределять педагогические роли и обеспечивать учебную
      аналитику в реальном времени.'
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  ai_architecture:
    text: 'Архитектура ITAS представлена трёхслойной системой: teaching layer с spoke-and-wheel
      композицией специализированных агентов — Video, Code, Guidance; Synthesizer,
      который агрегирует информацию; и autograder, оценивающий как правильность, так
      и подход к решению.


      Operational layer построен на облачных микросервисах Cloud Run, хранилище данных
      Cloud SQL, асинхронной коммуникации Pub/Sub и аналитической платформе BigQuery.


      Feedback layer обеспечивает инструктору conversational analytics на основе 10
      628 событий и 334 диалоговых ходов, что даёт инструмент для глубокого понимания
      учебной динамики.


      Таким образом, архитектура сочетает передовые облачные технологии с многоагентной
      педагогикой по шаблону multi-agent tutor с agentivity 3/6, реализуя роль распределённого
      и координированного AI-партнёра.'
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  team_roles:
    text: 'Типичные человеческие роли в ITAS включают преподавателя, который получает
      расширенные аналитические данные и взаимодействует с AI-агентами; студентов,
      участвующих в курсе; и разработчиков/операторов, обеспечивающих поддержку и
      развитие multi-agent системы.


      Распределение ответственности: AI-агенты принимают на себя роли декомпозированных
      педагогических функций — видеообъяснителя, кода-ассистента, наставника по учебному
      процессу и оценщика (autograder); преподаватель работает как руководитель процесса
      с доступом к аналитике и обратной связи. Таким образом, командный подход поддерживает
      гибридную модель контроля и агентности (facets: HYBR).'
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  ai_role:
    text: 'ИИ в ITAS выполняет функции multi-agent tutor: специализированные агенты
      отвечают за видеообъяснения, сопровождение написания кода, навигацию по учебному
      материалу (Guidance), а Synthesizer агрегирует знания и вызывает autograder
      для оценки результатов.


      Роль AI выходит за пределы простого помощника — агенты совместно распределяют
      педагогические задачи, создавая взаимодействующую сеть поддержки, и сопровождают
      обучение, обеспечивая обратную связь как студентам, так и преподавателю.


      Уровень агентности — 3/6, что соответствует стадии, когда AI реализует распределённое
      выполнение ролей с частичной автономией.'
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  interaction_scenario:
    text: 'В ходе семестра пяти студентов курса graduate quantum computing использовали
      ITAS как multi-agent tutor с последовательностью из 334 чат-ходов и более 10
      000 событий учебных взаимодействий. Студенты обращались к разным агентам для
      видеообъяснений, помощи с кодом и учебным руководством.


      Autograder автоматически проверял их решения не только на правильность, но и
      на адекватность подхода, повышая качество обратной связи. Преподаватель получал
      аналитику по активности и прогрессу студентов через feedback layer, что позволяло
      адаптировать преподавание и вмешиваться при необходимости.


      Таким образом взаимодействие представляет собой связанный multi-agent workflow,
      интегрированный в учебный процесс с реальным применением в классе.'
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  institutional_loop:
    text: 'Old Dominion University выступает как институциональный оператор, задающий
      инфраструктуру и политику использования ITAS в учебном процессе. Это university-managed
      AI hub, где governance нацелена на интеграцию AI в design coursework и research
      activities.


      Политика управления включает контроль над сохранностью псевдонимизированных
      данных студентов (10 628 событий) и прозрачную аналитику для инструкторов, обеспечивая
      баланс между эффективностью AI и этическими нормами обработки учебной информации.


      Таким образом реализован hybrid control (HYBR) с нормативным управлением на
      уровне кампуса и сохранением гибкости AI-оркестрации.'
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  transit_to_life:
    text: 'ITAS уже прошёл этап pilotdeployment на одном курсе с пятью студентами
      и одним семестром. Полученные данные и аналитика позволяют рассматривать кейс
      как production-like развертывание, с перспективой масштабирования на другие
      курсы и факультеты при адаптации архитектуры и политики.


      Последующие итерации предполагают расширение числа студентов, интеграцию новых
      агентных функций и возможное повышение агентности выше 3/6 за счёт более продвинутых
      orchestrative и meta-control слоёв.


      В начале 2026 года кейс позиционируется как рабочий прототип с подтверждённой
      практической ценностью.'
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  metrics_evidence:
    text: 'В течение семестра ITAS зафиксировал 334 chat turns (хода общения) с пятью
      студентами по курсу graduate quantum computing. Всего зарегистрировано 10 628
      событий across five modules, что представлено в аналитике преподавателю.


      Зафиксированы два instructor-actionable findings, то есть выявленные факты,
      на которые преподаватель смог оперативно отреагировать для улучшения учебного
      процесса.


      Эти количественные показатели демонстрируют реальное применение multi-agent
      tutoring с измеримыми эффектами и аналитической обратной связью для педагогов.'
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  risks:
    text: 'Внедрение ITAS на стадии прототипа с малым числом студентов несёт риски
      goal-substitution — возможного сосредоточения на оптимизации chat-turns и событий
      в ущерб глубине понимания. Наличие autograder повышает риск lowered bar, если
      автоматическая проверка предпочтёт формальные критерии над креативностью.


      Также необходима прозрачная audit trail для подтверждения корректного применения
      AI-оценки и сохранения академической честности, что требует постоянного мониторинга.


      Vendor lock-in минимален, поскольку платформа построена на облачных сервисах
      Google и собственных разработках, но требует внимания по контролю над данными
      и политикой их использования.'
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  countersignals:
    text: 'На данном этапе не выявлено явных countersignals или противоречий в практическом
      использовании ITAS: вся зафиксированная информация подтверждает заявленные функции
      и эффективность multi-agent tutoring.


      Отсутствие негативных отзывов или протестов в рамках данного курса свидетельствует
      о согласованности системы с учебными потребностями и политикой университета.


      Тем не менее, необходимы дальнейшие оценки в более масштабных аудиториях для
      выявления возможных системных рисков и сопротивлений.'
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  transferability:
    text: 'ITAS демонстрирует примечательный паттерн multi-agent tutoring с agentivity
      3/6 и cloud-based architecture, который может быть перенесён в другие вузовские
      курсы с высокой сложностью и требованиями персонализации, особенно STEM-дисциплины
      с объёмным практическим кодингом и сложным учебным материалом.


      Университетская среда с подобным уровнем governance (HYBR) и концепцией campus-managed
      AI hubs (NET, BUD) подходит для масштабирования этого паттерна в институтах
      с новыми образовательными технологиями.


      Переносимость также возможна в смежные образовательные проекты, которые фокусируются
      на multi-agent orchestration и распределении ролей tutoring для увеличения агентности
      AI.'
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  theory_links:
    text: 'ITAS отражает гипотезу H2–H3 о multi-agent распределении педагогических
      функций с уровнем агентности 3/6 и фасетами ORCHESTRATION=NET, PEDAGOGY=ROLE,
      CONTROL=HYBR, ECONOMY=BUD. Система воплощает концепцию spoke-and-wheel multi-agent
      tutoring, что соответствует [[wikilink|multi-agent tutoring frameworks]] и [[H4-agent-distribution]]
      для образовательных технологий.


      Видна связь с теорией hybrid governance для campus-made AI-сред (см. [[A-governed-access]])
      и противоречиями между автономией AI и контролем преподавателей ([[autonomy-vs-control]]).


      ITAS служит мостом между идеями разворачивания AI как педагогического ассистента
      и превращением его в комплексную среду с продвинутой обратной связью и аналитикой.'
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  open_questions:
    text: 'Остаётся неясным, насколько возможно масштабирование ITAS beyond один курс
      и семестр, и какие архитектурные изменения понадобятся для повышения агентности
      выше 3/6.


      Интересно оценить, как система справится с более разнообразным студентским контингентом,
      и будет ли достаточной текущая политика обработки данных с точки зрения privacy
      и этики.


      Нужно понять, какие корректировки interface и пользовательского опыта потребуются
      для интеграции ITAS в массовое образование и какое влияние окажут новые типы
      заданий и форматов коммуникации.'
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  next_wave_followup:
    text: 'В следующем дифф-прогоне обязательно нужно перепроверить:

      - динамику agentivity: появятся ли более автономные orchestrator агенты или
      meta-control слои;

      - расширение статистики метрик использования и влияние на учебные результаты;

      - мнение преподавателей и студентов о качестве и полезности обратной связи;

      - варианты интеграции ITAS с другими campus-managed AI hubs в экосистеме Old
      Dominion University.


      Также важно проверить юридические аспекты и adherence к governance policy в
      расширенных условиях.'
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  sources_verification:
    text: 'Основные источники по ITAS — архитектурная статья ITAS architecture paper
      и companion paper “From Prototype to Classroom”, подтверждающие факты развертывания
      и использования.


      Дополнительно использованы публичные сводки и аналитика, предоставляющие достоверные
      цифры по chat turns и событиям, а также описание компонентов архитектуры.


      Пока отсутствуют противоположные или непроверяемые данные, что повышает доверие
      к правдивости представленной информации.'
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
---

## Описание

ITAS — production-like multi-agent tutor, реально работавший семестр в
graduate quantum computing курсе ODU. Spoke-and-wheel композиция
specialist agents + Synthesizer + autograder, Cloud Run microservices,
BigQuery-логи, instructor analytics. Это редкий пример агентности 3/6 с
эмпирической базой. Поддерживает [[H2-assistant-to-autonomy]]; ослабляет
противоречие [[simulation-vs-engineering-power]] (есть реальный деплой).
