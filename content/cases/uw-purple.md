---
id: uw-purple
name: University of Washington · Purple (GenAI tool)
organization:
  name: University of Washington
  type: U
  country: US
scenario:
  level:
  - undergraduate
  - graduate
  - faculty
  - staff
  - researcher
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
  - multiple-models
  role: trusted campus AI tool with role-aware scenarios
transformation_mode: rectoral-initiative
axes:
  agentivity: 2
  ai_pattern: A
  orchestration: MOD
  control_locus: HYBR
  interaction_form: governed-portal
  provider_lock_in: 2
  scale_of_change: 3
  institutional_depth: 4
  governance_strength: 4
  audit_trail_strength: 4
  cost_intensity: 4
lifecycle:
  stage: pilot
  first_seen: wave-2
  history:
  - wave: wave-2
    stage: pilot
    note: rolling early access; разграничение сценариев по ролям (студент/преподаватель/исследователь)
links:
- kind: type
  id: A
  relation: instantiates
  confidence: high
- kind: hypothesis
  id: H1
  relation: supports
  confidence: medium
sources:
- url: https://www.washington.edu/
  type: official
  accessed: 2026-02
verified: true
canvas:
  signature_context:
    text: 'Purple — единая платформа GenAI Вашингтонского университета с разделением

      сценариев по ролям (студент/преподаватель/сотрудник/исследователь).

      Тип [[A-governed-access]].'
    status: draft
    source: imported
    updated_at: '2026-06-12'
  ontology_status:
    text: 'Кейс University of Washington · Purple описан как реализованный прототип
      или пилот с rolling early access, который на момент данных января 2026 года
      не доступен для всех, а по сути работает в режиме расширенного доступа с отчетами
      об использовании. Это соответствует переходной стадии внедрения, где технология
      уже технически интегрирована в кампус, но с ограничениями по охвату пользователей.


      Таким образом, статус ontology находится между прототипом и ранним rollout с
      контролируемым расширением и мониторингом, характерным для моделей уровня 2
      агентности с hybrid control и бюджетно-внешним экономконтуром.'
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  problem_situation:
    text: 'До внедрения Purple в Университете Вашингтона существовал недостаток единых
      платформ с интегрированным доступом для разных ролей (студенты, преподаватели,
      сотрудники, исследователи) к современным LLM-сервисам. Отсутствовала централизованная,
      роль-ориентированная среда с разграничением сценариев использования AI, а также
      обучающей и сообществной инфраструктурой.


      Ранее решения часто представляли собой лишь единообразный доступ без функционального
      встраивания в процессы обучения и управления, с ограниченной мониторингом метрик
      и отсутствием продуманной роли AI в образовательном цикле. Это снижало эффективность
      и безопасность использования AI в кампусных условиях.'
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  effect_hypothesis:
    text: "University of Washington поставил цель создать единую платформу GenAI,
      доверенный AI-ассистент кампуса, который поддерживает разные сценарии в зависимости
      от ролей пользователей: студентов, преподавателей, сотрудников и исследователей.
      \n\nОбещается функциональная интеграция AI как интерактивного помощника, который
      отвечает на вопросы, генерирует тексты, содействует обучению и поддерживает
      сообщество. Значимым эффектом является обеспечение управляемого, гибридного
      контроля и детального мониторинга usage-метрик для прозрачного и ответственного
      внедрения в образовательную среду."
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  ai_architecture:
    text: 'Архитектура Purple строится как единая модульная платформа (MOD) с multi-model
      доступом к современным LLM-провайдерам, включая OpenAI GPT-4. Платформа реализует
      role-aware сценарии с разграничением доступа для разных ролей (студенты, преподаватели,
      staff, исследователи).


      Оркестрация включает в себя единый шлюз доступа (SSO через университетский аккаунт),
      систему обучения пользователей и сообщество. AI функционирует как интерактивный
      ассистент. Контроль гибридный (HYBR), экономический контур смешанный — бюджетный
      университетский и внешние платформы (BUD+EXT).'
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  metrics_evidence:
    text: 'По данным на середину 2024 года, сервис Purple использовали тысячи пользователей
      в неделю, фиксируя их активность через метрики интенсивности использования:
      числа сообщений в неделю (messages per week) и динамику регистрируемых пользователей.


      Однако пока не публикуются учебные результаты или прямые образовательные метрики
      вроде оценок или скоростей обучения. В отчетах упоминаются внутренняя аналитика
      и rolling early access с регулярными отчетами. Это позволяет различать реальные
      внедрения от PR-поверхностных запусков.'
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  theory_links:
    text: "Кейс University of Washington · Purple демонстрирует тип «Governed GenAI
      Portal» с функцией единого институционального портала, включающего multi-model
      LLM, prompt-library и role-aware access.\n\nОн подтверждает идеи типологии Wave
      2 о доминировании модульной архитектуры (MOD) с гибридным контролем (HYBR),
      а также модель агентности 2/6, где AI работает как функциональный ассистент
      без автономии. \n\nПрисутствуют признаки институционального сдвига (INST) и
      управления на основе governance units, что связывает кейс с [[H2-agentivity-levels]],
      [[A-governed-access]], [[MOD-architecture]] и [[institutional-shift]]."
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
---

## Описание

Purple — единая платформа GenAI Вашингтонского университета с разделением
сценариев по ролям (студент/преподаватель/сотрудник/исследователь).
Тип [[A-governed-access]].
