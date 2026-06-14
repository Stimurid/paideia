---
id: stanford-ai-playground
name: Stanford University · AI Playground + AI API Gateway
organization:
  name: Stanford University
  type: U
  country: US
scenario:
  level:
  - undergraduate
  - graduate
  - faculty
  - staff
  - postdoc
  domains:
  - general
  context: campus-portal
facets:
  orchestration: META
  pedagogy: ROLE
  control: HYBR
  economy: BUD+EXT
ai:
  pattern: A
  agentivity: 3
  technologies:
  - gpt-4o
  - claude-3.5
  - gemini-1.5
  - llama-3
  - librechat
  role: multi-LLM portal + Stanford-specific agents + API gateway
orchestration_roles:
- community-users
- University-IT
- model-vendors
- agent-authors
roles:
  human:
  - community-user
  - IT-operator
  - agent-author
  machine:
  - LLM-router
  - Stanford-handbook-agent
  - API-gateway
  interaction_scenario: 'Пользователь заходит в Playground, выбирает модель или встроенного

    "Stanford-specific agent" (обновляется ежемесячно — handbooks); для

    собственных инструментов есть AI API Gateway.

    '
traces:
  logs: true
  prompts_versioned: true
  data_sources:
  - stanford-handbooks
transformation_mode: rectoral-initiative
axes:
  agentivity: 3
  ai_pattern: A
  orchestration: META
  control_locus: HYBR
  provider_lock_in: 1
  rag_grounded: true
  has_persistent_state: true
  audit_trail_strength: 5
  domain_specificity: 2
  evaluation_evidence_strength: 3
  interaction_form: governed-portal
  pedagogy_transformation: ROLE
  transformation_mode: rectoral-initiative
  scale_of_change: 4
  institutional_depth: 5
  radicalness: 2
  reversible: true
  governance_strength: 4
  portability: 3
  reflexivity: 2
  human_role_complexity: 3
  data_sensitivity: 4
  cost_intensity: 5
  lms_integration: false
  has_metrics: true
lifecycle:
  stage: rollout
  first_seen: wave-2
  history:
  - wave: wave-2
    stage: rollout
    note: Playground запущен Fall 2024 на LibreChat + AI API Gateway
  - wave: diff-2026-06
    stage: rollout
    note: 6,900+ users, 1.4M+ messages, 35B+ tokens с момента запуска
links:
- kind: type
  id: A
  relation: instantiates
  confidence: high
- kind: hypothesis
  id: H1
  relation: supports
  confidence: high
- kind: hypothesis
  id: H4
  relation: supports
  confidence: high
- kind: tension
  id: autonomy-vs-control
  relation: illustrates
  confidence: medium
metrics:
  hard:
  - users-6900
  - messages-1.4M
  - tokens-35B
  soft:
  - multi-vendor-portal
  - monthly-agent-updates
sources:
- url: https://uit.stanford.edu/service/ai-playground
  type: official
  accessed: 2026-02
verified: true
canvas:
  signature_context:
    text: 'Stanford AI Playground — кампусный мульти-вендорный шлюз на LibreChat с

      дополнительным AI API Gateway для разработчиков. Поддерживает выбор

      моделей, встроенные Stanford-specific agents (handbooks-боты,

      обновляемые ежемесячно), single sign-on. Метрики публично заявлены и

      делают кейс одним из самых верифицируемых в корпусе.'
    status: draft
    source: imported
    updated_at: '2026-06-12'
  transferability:
    text: 'Паттерн «портал + специализированные агенты + API gateway» позволяет

      дать пользователям и готовый интерфейс, и площадку для собственных

      инструментов. Воспроизводимо в любом крупном вузе с собственным IT.'
    status: draft
    source: imported
    updated_at: '2026-06-12'
  countersignals:
    text: 'Те же ограничения, что у Harvard AI Sandbox: масштаб usage не равен

      педагогическому эффекту. AI Playground работает как инфраструктура

      доступа, а не как педагогический контур (см. отдельные курсовые

      проекты, использующие Gateway).'
    status: draft
    source: imported
    updated_at: '2026-06-12'
  ontology_status:
    text: Stanford AI Playground представляет собой устойчивое институциональное внедрение
      в разрезе внутренней кампусной инфраструктуры университета, что выносит его
      за статус прототипа и фиксирует как платформу с мета-ролью оркестрации (META).
      Это не разовый пилот, а полноценный campus-wide сервис с hybrid-режимом контроля
      и бюджетным + внешним финансированием, ориентированный на долгосрочное использование
      и развитие.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  problem_situation:
    text: До внедрения AI Playground университет сталкивался с фрагментированным доступом
      к внешним AI-инструментам без единой платформы или контроля, что ограничивало
      возможности для безопасного, масштабного и организованного использования LLM
      разными ролями сообщества (faculty, staff, students). Отсутствие институциональной
      инфраструктуры затрудняло мониторинг, управление данными и экспериментирование
      с моделями в академическом контексте.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  effect_hypothesis:
    text: Предполагается, что создание единой универсальной песочницы и AI API Gateway
      позволит централизовать доступ к многообразию моделей (gpt-4o, claude-3.5, gemini-1.5,
      llama-3, librechat), обеспечивая governance, обновления и кастомизацию. Это
      повысит эффективность рабочих процессов, расширит возможности для разработки
      собственных AI-инструментов, а также усилит безопасность и управляемость использования
      AI в учебной и исследовательской деятельности.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  ai_architecture:
    text: Архитектура построена на базе LibreChat как песочницы с поддержкой нескольких
      LLM и постоянных обновлений. Внутри платформы реализуются «Stanford-specific
      agents» с ручным обновлением handbooks ежемесячно. Параллельно функционирует
      AI API Gateway, служащий для сборки специализированных инструментов и кастомных
      агентов. Система поддерживает SSO, логирование, библиотеку промптов и безопасный
      multi-model доступ с модульной организацией компонентов. Это отражает паттерн
      «Governed GenAI Portal» с высокой степенью инфраструктурной зрелости и гибридным
      контролем.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  team_roles:
    text: 'В архитектуре задействованы: широкая роль пользователей кампуса (faculty,
      staff, students, postdocs, affiliates) как конечных пользователей; IT-отдел
      университета выполняет функцию управляющего контура, отвечающего за эксплуатацию
      и поддержку платформы; внешние поставщики AI-моделей обеспечивают интеграцию
      и обновления моделей; разработчики Stanford-specific agents и кастомных инструментов
      формируют дополнительный слой агентов внутри платформы. Такой распределённый
      состав ролей подчёркивает гибридный характер управления и поддержания экосистемы.'
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  ai_role:
    text: AI выполняет роль ассистентов и инфраструктурных агентов, предоставляя доступ
      к разнообразным моделям и формируя workflow-контуры с частичной автономией (агентность
      3 из 6). AI не просто инструмент, а модульный участник процессов, который помогает
      пользователям строить кастомные контуры, обеспечивать поддержку и интеграцию
      в учебные и исследовательские сценарии. Это подтверждает позицию AI как платформенного
      множества ассистентов с заданными ролями, поддерживаемых институциональной оркестрацией.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  institutional_loop:
    text: Внедрена система governance и контроля данных — университет управляет доступом
      к AI через IT, реализован гибридный режим контроля над использованием моделей
      и данными, поддерживаются политики безопасности и обновлений. Платформа открывает
      возможности для анализа usage, ведётся логирование и поддержка политик приватности,
      что согласуется с выявленными в исследовании тенденциями построения «governed
      AI access» (тип А). Роль governance unit и поддержки обучающих программ не освещена
      подробно в фрагментах, но отмечена как часть кампусной инфраструктуры.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  metrics_evidence:
    text: 'Публично были заявлены следующие метрики с момента запуска осенью 2024
      года: более 6,900 пользователей, свыше 1.4 миллиона сообщений и более 35 миллиардов
      токенов. Эти данные указывают на значительный масштаб использования и позволяют
      оценивать активность и нагрузку на платформу. Показатели охвата пользователей
      и объёма взаимодействий превосходят многие другие кампусные внедрения AI, что
      свидетельствует о зрелости и зрелом institutional adoption.'
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  theory_links:
    text: Кейс подтверждает гипотезу типа А (governed AI access), демонстрируя практическую
      реализацию институционального портала с управляемым доступом и контролем. Архитектура
      и роль AI укладываются в рамки фасеты META оркестрации и подтверждают стратегию
      смешанного контроля (HYBR) с использованием внутреннего бюджета и внешних платформ
      (BUD+EXT). По агентности — 3 из 6, что соответствует workflow с частичной автономией,
      а не полной сети агентов с автономным циклом. С точки зрения педагогики AI выступает
      как ролевая платформа ассистентов, а не автономный учитель, что соотносится
      с концепциями педагогического контроля и распределения ролей в AI-средах [[H1-governed-access]],
      [[autonomy-vs-control]], [[acceleration]].
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  sources_verification:
    text: Информация о кейсе и метрики подтверждены публикациями Университета Стэнфорда
      и вторичными источниками исследовательского аудита Wave 1 и 2 по 2024–2026 годам.
      Упоминаются официальные release notes, описание архитектуры и публичные отчёты
      usage. Тем не менее отсутствует независимый аудит педагогической эффективности
      и методическая оценка интеграции AI в образовательный процесс.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
---

## Описание

Stanford AI Playground — кампусный мульти-вендорный шлюз на LibreChat с
дополнительным AI API Gateway для разработчиков. Поддерживает выбор
моделей, встроенные Stanford-specific agents (handbooks-боты,
обновляемые ежемесячно), single sign-on. Метрики публично заявлены и
делают кейс одним из самых верифицируемых в корпусе.

## Что переиспользуемо

Паттерн «портал + специализированные агенты + API gateway» позволяет
дать пользователям и готовый интерфейс, и площадку для собственных
инструментов. Воспроизводимо в любом крупном вузе с собственным IT.

## Риски / контрсигналы

Те же ограничения, что у Harvard AI Sandbox: масштаб usage не равен
педагогическому эффекту. AI Playground работает как инфраструктура
доступа, а не как педагогический контур (см. отдельные курсовые
проекты, использующие Gateway).
