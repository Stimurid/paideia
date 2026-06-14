---
id: harvard-ai-sandbox
name: Harvard University · AI Sandbox 2.0
organization:
  name: Harvard University
  type: U
  country: US
scenario:
  level:
  - undergraduate
  - graduate
  - faculty
  domains:
  - general
  context: campus-portal
facets:
  orchestration: META
  pedagogy: INST
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
  role: multi-LLM portal + custom assistants roadmap
orchestration_roles:
- community-users
- IT-operations
- governance-board
- model-vendors
roles:
  human:
  - community-user
  - IT-operator
  - governance-officer
  machine:
  - LLM-router
  - custom-assistant
  - usage-analytics
  interaction_scenario: 'Сообщество приходит через единый интерфейс LibreChat-стиля;
    выбирает

    модель; данные не уходят на тренировку вендора; IT держит роадмап

    custom assistants и security-review.

    '
traces:
  logs: true
  prompts_versioned: true
  data_sources:
  - community-uploads
transformation_mode: rectoral-initiative
axes:
  agentivity: 3
  ai_pattern: A
  orchestration: META
  control_locus: HYBR
  provider_lock_in: 1
  rag_grounded: false
  has_persistent_state: true
  audit_trail_strength: 4
  domain_specificity: 1
  evaluation_evidence_strength: 3
  interaction_form: governed-portal
  pedagogy_transformation: INST
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
  cost_intensity: 4
  lms_integration: false
  has_metrics: true
lifecycle:
  stage: rollout
  first_seen: wave-1
  history:
  - wave: wave-1
    stage: pilot
    note: Harvard AI Sandbox 1.0 как secure environment для community
  - wave: wave-2
    stage: rollout
    note: 'AI Sandbox 2.0: multi-LLM access, usage analytics, roadmap custom assistants'
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
  confidence: medium
- kind: tension
  id: speed-vs-responsibility
  relation: weakens
  confidence: medium
metrics:
  hard:
  - users-25k
  - active-users-7k
  soft:
  - secure-multi-model-access
  - data-not-used-for-training
sources:
- url: https://www.harvard.edu/ai-sandbox/
  type: official
  accessed: 2026-02
verified: true
canvas:
  signature_context:
    text: 'Harvard AI Sandbox 2.0 — институциональная среда доступа сообщества Harvard

      к нескольким коммерческим LLM (OpenAI, Anthropic, Google, open-source)

      через единый интерфейс с приватностью данных, usage-аналитикой и

      дорожной картой custom assistants. С Fall 2023 эволюционирует как

      постоянный кампусный сервис, не как разовый пилот.'
    status: draft
    source: imported
    updated_at: '2026-06-12'
  transferability:
    text: 'Паттерн «multi-vendor governed portal + privacy-by-default + аналитика
      +

      дорожная карта custom assistants» — образец инфраструктуры типа A,

      применим для крупных университетов с собственным IT и security review.'
    status: draft
    source: imported
    updated_at: '2026-06-12'
  countersignals:
    text: 'Метрики обучения (learning gains) не публикуются; usage-метрики

      демонстрируют масштаб, но не педагогический эффект. В META-AUDIT

      рассматривается как пример «инфраструктуризации без обязательной

      педагогической верификации».'
    status: draft
    source: imported
    updated_at: '2026-06-12'
  ontology_status:
    text: 'Harvard AI Sandbox выступает как институциональный кампусный сервис с устойчивой
      платформой GenAI, работающей в режиме sandbox с контролируемым доступом и защитой
      приватности. Это не эксперимент или прототип, а действующая инфраструктура,
      применяемая с Fall 2023 и развивающаяся (AI Sandbox 1.0/2.0). Такая организация
      указывает на текущий статус внедрения (rollout), где AI интегрирован как инфраструктурный
      ресурс для сообщества университета.


      Кроме того, платформа сохраняет высокую степень безопасности данных — отдельная
      политика не позволяет использовать данные пользователей для дообучения внешних
      моделей, что подчёркивает GOVERNED-NATURE решения. Подобное позиционирование
      соответствует паттерну «governed AI access» из гипотезы типа A по Wave2.


      Таким образом, по статусу Harvard AI Sandbox можно отнести к категории институциональных
      rollout решений с инфраструктурной зрелостью и ориентированностью на безопасность
      и управление.'
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  problem_situation:
    text: 'До запуска Harvard AI Sandbox университет сталкивался с вызовами безопасности
      использования моделей LLM в образовательном и исследовательском процессе: отсутствие
      контролируемой среды и рисков утечки данных, а также недостаток платформенного
      доступа к многообразию моделей от разных провайдеров.


      Традиционно преподаватели и студенты пользовались внешними, зачастую коммерческими
      чатботами без гарантии соблюдения академической честности или приватности. Кроме
      того, в отсутствии целенаправленной оркестрации AI ролей внутри кампуса не было
      инфраструктуры для массового, безопасного и регулируемого использования генеративных
      моделей.


      Данные ограничения сказывались на вовлечённости университетских сообществ и
      сдерживали развитие новых педагогических форматов с AI-партнёрством.'
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  effect_hypothesis:
    text: 'Harvard AI Sandbox обещает обеспечить кампусный безопасный доступ к нескольким
      LLM-моделям через единый интерфейс, что стимулирует экспериментирование с AI
      в обучении и исследованиях при минимизации рисков приватности и соответствия
      нормативным требованиям.


      Применение AI в роли ассистента и аналитического партнёра в ряде курсов должно
      способствовать росту интереса к новым образовательным форматам, а также формированию
      новых норм академической честности и использования AI.


      Кроме того, архитектура sandbox с политиками по защите данных обещает вывести
      AI из камерной эксплуатации в открытый, но при этом контролируемый кампусный
      сервис, что позволит масштабировать использование без снижения доверия и качества.'
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  ai_architecture:
    text: 'Архитектурно Harvard AI Sandbox представляет собой много-модельную платформу
      с единым интерфейсом, предоставляющим доступ одновременно к LLM от разных провайдеров
      — GPT-4o, Claude 3.5, Gemini 1.5, Llama 3 и др.


      Важным элементом является контур политики и контроля, который гарантирует, что
      пользовательские данные не используются для тренировки внешних моделей, тем
      самым обеспечивается privacy-first подход. Платформа поддерживает расширенную
      работу с документами и сохранение сессий, что облегчает продуктивность и эксперименты.


      Стек реализован как secure generative AI sandbox с институциональным управлением
      и мультивендорным шлюзом, что соответствует паттерну governed AI access и META-оркестрации
      согласно фасетам кейса.'
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  team_roles:
    text: 'Роли в Harvard AI Sandbox распределены между:


      (1) студентами, преподавателями и другими пользователями сообщества университета,
      которые взаимодействуют с AI как с инструментом продуктивности и аналитики;


      (2) центральной IT-командой, управляющей инфраструктурой и обеспечивающей нормы
      безопасности и compliance;


      (3) исследовательскими группами, внедряющими AI в образовательные пилоты и оценивающими
      его применение;


      (4) преподавателями, устанавливающими педагогические правила использования AI,
      контролирующими границы разрешённых сценариев.


      Такое разделение обеспечивает сочетание user-driven и governance-driven подходов
      к оркестрации.'
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  ai_role:
    text: 'AI в Harvard AI Sandbox играет роль много-модельного ассистента и аналитического
      партнёра, поддерживающего учебные кейсы, генерацию альтернативных интерпретаций
      текстов и помощью в лабораторных вычислениях.


      При этом AI не автономен — отсутствует развитый цикл самостоятельного планирования,
      оценки и интервенций, скорее AI выступает как инструмент с функциональной агентностью
      2/6 в классификации Wave2, встроенный в учебный и исследовательский процесс
      под контролем человека.


      Таким образом, AI роль — функциональный ассистент и академический партнёр с
      высоким уровнем институционального управления.'
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  institutional_loop:
    text: 'Институциональный контур Harvard AI Sandbox выстроен на основе политики
      безопасности и управления данными, включая запрет использовать пользовательские
      данные для тренировки внешних моделей поставщиков.


      Оркестрация построена в режиме разрешительного доступа, где преподаватели и
      IT-службы определяют правила и границы допустимого использования AI.


      Также есть архитектура governance units, поддерживающая нормы академической
      честности и регулирующая экспериментальное использование AI в рамках кампуса,
      что соответствует схеме с гибридным контролем (HYBR) и институциональному уровню
      (INST) по фасетам.'
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
---

## Описание

Harvard AI Sandbox 2.0 — институциональная среда доступа сообщества Harvard
к нескольким коммерческим LLM (OpenAI, Anthropic, Google, open-source)
через единый интерфейс с приватностью данных, usage-аналитикой и
дорожной картой custom assistants. С Fall 2023 эволюционирует как
постоянный кампусный сервис, не как разовый пилот.

## Что переиспользуемо

Паттерн «multi-vendor governed portal + privacy-by-default + аналитика +
дорожная карта custom assistants» — образец инфраструктуры типа A,
применим для крупных университетов с собственным IT и security review.

## Риски / контрсигналы

Метрики обучения (learning gains) не публикуются; usage-метрики
демонстрируют масштаб, но не педагогический эффект. В META-AUDIT
рассматривается как пример «инфраструктуризации без обязательной
педагогической верификации».
