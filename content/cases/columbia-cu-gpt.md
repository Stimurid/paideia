---
id: columbia-cu-gpt
name: Columbia University · CU-GPT
organization:
  name: Columbia University
  type: U
  country: US
scenario:
  level:
  - undergraduate
  - graduate
  - faculty
  - staff
  domains:
  - general
  context: campus-platform
facets:
  orchestration: MOD
  pedagogy: INST
  control: HYBR
  economy: BUD+EXT
ai:
  pattern: A
  agentivity: 2
  technologies:
  - gpt-4o
  role: university multi-tenant chat platform
orchestration_roles:
- departments
- users
- IT-team
transformation_mode: rectoral-initiative
axes:
  agentivity: 2
  ai_pattern: A
  orchestration: MOD
  control_locus: HYBR
  provider_lock_in: 4
  rag_grounded: false
  has_persistent_state: true
  audit_trail_strength: 4
  domain_specificity: 1
  evaluation_evidence_strength: 2
  interaction_form: governed-portal
  pedagogy_transformation: INST
  transformation_mode: rectoral-initiative
  scale_of_change: 3
  institutional_depth: 4
  radicalness: 2
  reversible: true
  governance_strength: 4
  portability: 3
  reflexivity: 1
  human_role_complexity: 2
  data_sensitivity: 4
  cost_intensity: 4
  lms_integration: false
  has_metrics: false
lifecycle:
  stage: pilot
  first_seen: wave-1
  history:
  - wave: wave-1
    stage: pilot
    note: pay-as-you-go, departmental quotas, role-aware access, file uploads; pilot
      ~1000 users
links:
- kind: type
  id: A
  relation: instantiates
  confidence: high
- kind: hypothesis
  id: H1
  relation: supports
  confidence: medium
metrics:
  hard:
  - users-1000-pilot
  soft:
  - departmental-quotas
  - role-aware-access
sources:
- url: https://www.columbia.edu/
  type: official
  accessed: 2026-02
verified: true
canvas:
  signature_context:
    text: 'CU-GPT — внутренняя ChatGPT-подобная платформа Columbia на собственной

      инфраструктуре: pay-as-you-go биллинг, лимиты департаментов, role-aware

      доступ, file uploads. Альтернатива ChatGPT Enterprise с большей

      автономией.'
    status: draft
    source: imported
    updated_at: '2026-06-12'
  transferability:
    text: 'Подход «своя multi-tenant платформа вместо vendor-Enterprise» хорош для

      университетов с сильным IT и желанием контролировать стоимость по

      департаментам.'
    status: draft
    source: imported
    updated_at: '2026-06-12'
  ontology_status:
    text: CU-GPT позиционируется как университетский многоарендный AI-сервис, предлагающий
      контролируемую и управляющую архитектуру доступа к LLM в кампусе Columbia University.
      По шкале Wave2, агентность AI оценивается как 2/6 — функциональный ассистент
      без полной автономизации циклов. Это скорее внедрение с институциональным охватом,
      чем прототип или симуляция, где AI интегрирован в управляемый контур с ограничениями
      и учётом затрат.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  problem_situation:
    text: До внедрения CU-GPT университет сталкивался с проблемами приватности и управлением
      рисками при использовании публичных AI-сервисов, таких как открытый ChatGPT.
      Не было контролируемого, безопасного корпоративного ассистента для всех категорий
      пользователей кампуса, а также механизма учёта затрат и управления доступом
      на уровне департаментов и пользователей. Это создавало сложности в обеспечении
      согласованного, регулируемого AI-сервиса для преподавателей, студентов и сотрудников.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  effect_hypothesis:
    text: CU-GPT обещает предложить безопасную университетскую альтернативу публичному
      ChatGPT с интеграцией в внутренние системы, что позволит снизить риски приватности,
      усилить контроль за расходами и обеспечить институциональное сопровождение AI-сервиса.
      AI выступает как функциональный ассистент, который повышает эффективность и
      безопасность использования LLM в учебных и административных задачах кампуса,
      при этом поддерживая прозрачный мониторинг затрат и историю сообщений.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  ai_architecture:
    text: 'Архитектура CU-GPT строится как многоарендная (multi-tenant) университетская
      платформа с ролями: департамент IT (развёртывание и управление лимитами/бюджетами),
      пользователи (faculty, staff, студенты), AI-интерфейс ChatGPT-подобного типа
      с функциями загрузки файлов, архивирования сообщений и мониторинга использования,
      а также встроенная система учёта API-затрат (OpenAI API). Вся платформа ориентирована
      на pay-as-you-go модель с контролем расходов, role-aware доступом и отслеживанием
      активности. Агентность AI составляет 2/6, что соответствует функциональному
      ассистенту в устойчивом институциональном контуре.'
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  team_roles:
    text: В реализации CU-GPT задействован департамент информационных технологий Columbia
      University, который отвечает за разработку, развёртывание и поддержку платформы.
      Пользователи включают преподавателей, сотрудников и студентов, у которых регламентирован
      доступ к сервису по ролевым политикам и лимитам. Нет заявления о выделенных
      ролях для AI-разработчиков или педагогических координировщиков в публичных описаниях;
      основная роль команды — техническая поддержка и управление инфраструктурой.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  ai_role:
    text: AI в CU-GPT выступает как многоарендный университетский ассистент, предоставляющий
      функциональный чат-интерфейс для широкого круга задач учебного и административного
      характера. Он не автономен, действует в рамках управляющего институционального
      контура, обеспечивает поддержку пользователей с возможностями загрузки файлов,
      ведения истории диалогов и мониторинга расхода ресурсов. AI — сервисный ассистент
      c агентностью 2/6 по шкале Wave2.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  interaction_scenario:
    text: Пользователи (faculty, staff, студенты) получают доступ к CU-GPT через университетский
      интерфейс, где могут задавать запросы AI, загружать файлы и получать помощь
      по разным задачам. Департаменты устанавливают лимиты использования и бюджеты,
      которые мониторятся через встроенную систему отслеживания расхода API. Вся активность
      записывается с архивацией сообщений, что формирует прозрачный контроль использования.
      Контур использования AI построен вокруг функциональных взаимодействий без автономного
      самоуправления.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  institutional_loop:
    text: CU-GPT встроен в университетскую управленческую систему с жёстким контролем
      приватности и расходования средств. Департаменты задают лимиты по бюджетам и
      доступу, а сервис ведёт мониторинг использования в реальном времени. Институциональные
      политики данных подчёркивают безопасность и легитимность использования AI, превращая
      публичный чат в регулируемый внутренний ресурс. Обеспечивается роль контроля
      и учёта, что соответствует гибридной модели контроля (HYBR).
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  metrics_evidence:
    text: Публичные метрики образовательных эффектов отсутствуют. В качестве операционных
      метрик используется мониторинг объёмов использования, история сообщений и встроенный
      дисплей счетчиков затрат в режиме реального времени. В пилотной фазе заявлено
      участие около 1000 пользователей, что фиксирует масштабы внедрения. Это показывает
      институциональную зрелость и эффективность учёта, но не доказывает педагогический
      прирост знания.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  countersignals:
    text: Отсутствует публичный отчёт о конкретных образовательных результатах или
      обучающих метриках, что может указывать на фокус платформы скорее на инфраструктурном
      и организационном уровне, чем на педагогическом эффекте. Это может свидетельствовать
      о возможном goal-substitution, когда акцент смещается на безопасность и учет
      затрат, а не на улучшение учебных результатов.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  theory_links:
    text: "CU-GPT соответствует паттерну оркестрации с агентностью 2/6 согласно Wave2
      шкале, где AI выполняет функциональную роль ассистента внутри контролируемого
      институционального контура. Система отражает фасеты MOD (модерируемая оркестрация),
      INST (институциональная педагогика), HYBR (гибридный контроль) и экономику BUD+EXT
      (бюджетный и внешний контроль). Платформа подтверждает теорию о необходимости
      role-aware multi-tenant AI-сервисов в университетской среде и позиционируется
      как противовес частным, непубличным AI \r[[A-governed-access]] [[autonomy-vs-control]]."
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  open_questions:
    text: Остаётся неясным, есть ли внутри CU-GPT интеграция более продвинутых педагогических
      функций, выхода за рамки ассистентской роли, а также какие планы по масштабированию
      и добавлению образовательных метрик в будущем. Также отсутствуют публичные сведения
      о внутренней оценке влияния на учебные результаты или вовлечённость пользователей.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  next_wave_followup:
    text: В следующем дифф-прогоне важно перепроверить наличие и эффективность метрик
      learning gains, а также прогресс институционализации практик с учётом обратной
      связи пользователей. Следует проверить, как расширяется функционал AI и происходит
      ли интеграция с учебными LMS или образовательными сервисами шире, чем только
      как чат-ассистент.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
---

## Описание

CU-GPT — внутренняя ChatGPT-подобная платформа Columbia на собственной
инфраструктуре: pay-as-you-go биллинг, лимиты департаментов, role-aware
доступ, file uploads. Альтернатива ChatGPT Enterprise с большей
автономией.

## Что переиспользуемо

Подход «своя multi-tenant платформа вместо vendor-Enterprise» хорош для
университетов с сильным IT и желанием контролировать стоимость по
департаментам.
