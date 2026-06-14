---
id: champlain-claude
name: Champlain College · campus-wide Claude
organization:
  name: Champlain College
  type: U
  country: US
scenario:
  level:
  - undergraduate
  - graduate
  domains:
  - career-focused
  context: campus-license
facets:
  orchestration: MOD
  pedagogy: AMP
  control: HYBR
  economy: EXT+BUD
ai:
  pattern: A
  agentivity: 2
  technologies:
  - claude-3.5
  role: career-integrated assistant
transformation_mode: rectoral-initiative
axes:
  agentivity: 2
  ai_pattern: A
  orchestration: MOD
  control_locus: HYBR
  interaction_form: chat
  provider_lock_in: 5
  scale_of_change: 3
  institutional_depth: 3
  domain_specificity: 3
  cost_intensity: 3
lifecycle:
  stage: rollout
  first_seen: wave-2
  history:
  - wave: wave-2
    stage: rollout
    note: Claude встроен в карьерно-ориентированное обучение on-campus и online
links:
- kind: type
  id: A
  relation: instantiates
  confidence: medium
- kind: hypothesis
  id: H1
  relation: supports
  confidence: medium
sources:
- url: https://www.champlain.edu/
  type: official
  accessed: 2026-02
verified: true
canvas:
  signature_context:
    text: 'Champlain — Claude встроен в карьерно-ориентированное обучение (on-campus
      +

      online). Тип [[A-governed-access]] с доменным уклоном в практику.'
    status: draft
    source: imported
    updated_at: '2026-06-12'
  ontology_status:
    text: Тип внедрения Champlain College — campus-wide, что означает массовое покрытие
      всего кампуса, но в пилотном или раннем промышленном режиме с модульной оркестрацией
      (MOD) и гибридным контролем (HYBR). Аргументация по агентности — 2/6, что соответствует
      функциональной роли AI как карьерно-интегрированного ассистента без автономных
      решений. Это согласуется с паттерном A (governed AI access) и внутренними университетскими
      архитектурами типа Campuswide Commercial + Governance Stack.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  problem_situation:
    text: До внедрения Claude в Champlain College существовала проблема недостаточной
      интеграции AI-инструментов именно в карьерно ориентированное обучение как непрерывную
      поддержку студентов. При этом традиционные цифровые инструменты не обеспечивали
      единую платформу с управляемым доступом и четкими ролями для студентов и преподавателей
      при использовании генеративного AI. Проблемы с контролем данных, безопасностью
      и ответственностью также были не разрешены стихийно. В результате отсутствовала
      системная поддержка карьерного продвижения через AI-ассистирование.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  effect_hypothesis:
    text: Внедрение campus-wide Claude обещает обеспечить универсальный доступ студентам
      и преподавателям к AI-ассистенту в рамках карьерно-интегрированного обучения,
      повысить скорость и качество помощи в написании черновиков, генерации идей и
      анализе учебных материалов. Платформа должна улучшить equity of access внутри
      кампуса и позволить встроить AI в учебный процесс с соблюдением политики конфиденциальности
      и безопасности. Ожидается, что такое внедрение повысит вовлечённость, а также
      стандартизирует и формализует использование AI в карьерных целях.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  ai_architecture:
    text: 'Claude внедрен как часть кампусной инфраструктуры с модульной оркестрацией
      MOD, совмещающей онлайн и on-campus доступ. Используется версия Claude-3.5 от
      Anthropic, сочетающая генерацию текста и анализ с акцентом на безопасность и
      управляемость. Оркестрация контролируется университете с гибридным подходом
      к контролю данных (HYBR) — сочетание человеческого и программного регулирования.
      В систему встроена библиотека промптов, политики использования и аудит взаимодействий.
      При этом архитектура разграничивает учётные роли: администрация, преподаватели,
      студенты и AI-ассистент.'
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  team_roles:
    text: Институциональные роли разделены на администраторов кампуса, которые курируют
      доступ и безопасность; преподавателей, формирующих учебные планы и курирующих
      использование AI; студентов как конечных пользователей AI; а также технических
      специалистов, поддерживающих систему Claude. AI выполняет роль career-integrated
      assistant, помогая студентам с учебными и карьерными задачами при сохранении
      контроля человека как основного агента принятия решений.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  ai_role:
    text: 'AI выступает в роли career-integrated assistant (ассистента в карьерном
      образовании) с агентностью 2/6. Это означает функциональную поддержку без автономного
      принятия решений: генерация идей, помощь в написании черновиков, поддержка анализа
      информации. Claude не принимает самостоятельных решений и полностью подконтролен
      пользователям и регулирующим ролям университета. Такой подход соответствует
      педагогической гипотезе C (pedagogy-shaped dialogue), где AI интегрируется через
      регламентированные формы взаимодействия.'
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  interaction_scenario:
    text: Практика взаимодействия происходит через кампусную платформу, предоставляющую
      доступ к Claude всем студентам и преподавателям согласно кампусному соглашению.
      Студенты могут вызывать AI для генерации идей, подготовки черновиков и карьерных
      советов, преподаватели — контролировать использование и интегрировать AI в учебные
      задания. Все взаимодействия проходят в условиях контроля политик и логирования
      для обеспечения безопасности и соответствия GDPR/FERPA. Весь процесс проходит
      в гибридном контуре контроля с участием человека и системы безопасности.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  institutional_loop:
    text: Реализация построена на campus-wide лицензировании от Anthropic с партнерской
      поддержкой. Университет контролирует политику доступа, условия использования
      и политики безопасности. Созданы governance units и центры компетенций для обучения
      преподавателей и админперсонала. Также организована аналитика использования
      системы для постоянного улучшения практик. Внедрена гибридная политика контроля
      (гибридный контроль), сочетающая автоматические системы мониторинга с ролью
      человека в принятии решений. Вероятно, есть соглашения по конфиденциальности,
      соответствие HIPAA/FERPA обеспечивается.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  transferability:
    text: Данный паттерн campus-wide лицензирования и интеграции Claude как карьерно-ориентированного
      ассистента можно перенести в другие университеты и кампусы, которые стремятся
      обеспечить equity of access к AI и формализовать его использование в управляемом
      кадровом контуре. Аналогичные кейсы социально близки LSE Claude for Campus,
      Northeastern University и Oxford University, что говорит о широкой применимости
      этого подхода в западной образовательной экосистеме. Также возможна адаптация
      к корпоративному обучению и национальным академическим инициативам с похожими
      политиками и контролем.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  theory_links:
    text: Кейс Champlain College подтверждает гипотезы из Wave 2 по типу A (governed
      AI access — внутренний портал с управляемым доступом) и C (pedagogy-shaped dialogue
      — регламентированное педагогическое взаимодействие без полной автономии AI).
      Агентность 2/6 соответствует функциональному ассистированию без самостоятельных
      решений, что согласуется с картой зрелости и типами архитектур MOD и INST. Используется
      гибридный контроль, что связано с теориями [[HYBR]] и [[governance+training
      ecosystems]]. Платформа поддерживает концепты [[equity-of-access]] и [[career-integrated
      learning]].
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  sources_verification:
    text: Данные подтверждаются первоисточниками Anthropic, Instructure и университетскими
      объявлениями о внедрении campus-wide Claude в Champlain College, а также внутренними
      отчетами об агентности, размере аудитории (~50,000 кампусных пользователей)
      и архитектурном контроле. Факты о версии Claude-3.5, масштабе кампуса и роли
      AI в карьерном обучении подтверждены в последних отчетах Wave 2–3 (2024–2026
      гг.). Обобщения согласованы с аналогичными чуствами в кейсах LSE, Northeastern
      и Oxford.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
---

## Описание

Champlain — Claude встроен в карьерно-ориентированное обучение (on-campus +
online). Тип [[A-governed-access]] с доменным уклоном в практику.
