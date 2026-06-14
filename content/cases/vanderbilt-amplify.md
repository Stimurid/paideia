---
id: vanderbilt-amplify
name: Vanderbilt University · Amplify (secure GenAI sandbox)
organization:
  name: Vanderbilt University
  type: U
  country: US
scenario:
  level:
  - faculty
  - staff
  domains:
  - general
  context: campus-sandbox
facets:
  orchestration: MOD
  pedagogy: AMP
  control: HYBR
  economy: BUD+EXT
ai:
  pattern: A
  agentivity: 1
  technologies:
  - gpt-4o
  - claude-3.5
  - llama-3
  role: secure multi-LLM sandbox with custom instructions
orchestration_roles:
- faculty
- staff
- IT-team
transformation_mode: rectoral-initiative
axes:
  agentivity: 1
  ai_pattern: A
  orchestration: MOD
  control_locus: HYBR
  provider_lock_in: 1
  rag_grounded: false
  has_persistent_state: false
  audit_trail_strength: 3
  domain_specificity: 1
  evaluation_evidence_strength: 1
  interaction_form: governed-portal
  pedagogy_transformation: AMP
  transformation_mode: rectoral-initiative
  scale_of_change: 2
  institutional_depth: 3
  radicalness: 1
  reversible: true
  governance_strength: 3
  portability: 4
  reflexivity: 1
  human_role_complexity: 2
  data_sensitivity: 4
  cost_intensity: 3
  lms_integration: false
  has_metrics: false
lifecycle:
  stage: pilot
  first_seen: wave-1
  history:
  - wave: wave-1
    stage: pilot
    note: waitlist; защищённая среда с custom instructions для faculty/staff
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
  hard: []
  soft:
  - secure-sandbox
  - custom-instructions
sources:
- url: https://www.vanderbilt.edu/
  type: official
  accessed: 2026-02
verified: true
canvas:
  signature_context:
    text: 'Amplify — защищённая чат-среда Vanderbilt для faculty/staff. Поддержка

      custom instructions, multi-LLM выбор. На момент описания — пилот с

      waitlist; не открыт для студентов.'
    status: draft
    source: imported
    updated_at: '2026-06-12'
  transferability:
    text: 'Если нужно начать с малых рисков: faculty-only sandbox даёт время

      выработать политику до того, как сервис придёт к студентам.'
    status: draft
    source: imported
    updated_at: '2026-06-12'
  ontology_status:
    text: Amplify реализуется как внутренний защищённый sandbox для Generative AI
      внутри Vanderbilt University, что соответствует уровню prototyping от кампусного
      пилота к устойчивому инфраструктурному ресурсу. AI-среда — это не consumer-grade
      chat-инструмент, а кастомизированная open-source платформа, управляемая инфраструктурной
      командой университета, с акцентом на безопасность и контроль в образовательной
      среде.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  problem_situation:
    text: До внедрения Amplify использовались внешние публичные AI-инструменты, которые
      не обеспечивали адекватный контроль безопасности, приватности университетских
      данных и кастомизации поведения моделей для специфических образовательных нужд.
      Пользователи не имели возможности задавать персонализированные инструкции, а
      интеграция с университетской средой отсутствовала, что порождало риски и низкую
      институциональную поддержку AI.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  effect_hypothesis:
    text: Amplify как защищённая песочница обещает перевести Generative AI из разрозненного
      внешнего инструмента в управляемый и проверенный университетский ресурс. Обещан
      доступ к нескольким LLM с возможностью задать кастомизированные инструкции,
      безопасность данных и поддержку экспериментирования в безопасной институциональной
      среде. Предполагается использование AI в роли ассистента для учебы и работы,
      что должно повысить продуктивность и обеспечить устойчивый кампусный доступ.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  ai_architecture:
    text: 'Архитектура Amplify включает четыре ключевых слоя: (1) пользователи - faculty,
      staff, students; (2) контур безопасности и условия использования, обеспечивающие
      приватность и compliant доступ; (3) LLM-слой с мультивендорным подключением
      к моделям GPT-4o, Claude-3.5, LLaMA-3, которые принимают кастомные инструкции;
      (4) институциональная управляющая платформа — open-source sandbox, обеспечивающий
      устойчивый кампусный сервис. Amplify функционирует как «multi-LLM secure sandbox»
      с гибкой кастомизацией на стороне пользователя под контролем института.'
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  team_roles:
    text: 'В роли сервиса задействованы: (1) конечные пользователи — преподаватели,
      сотрудники и студенты, (2) команда поддержки и управления платформой Amplify,
      которая курирует безопасность, правила использования и эксплуатацию, (3) LLM-слой,
      который по сути является набором AI-ассистентов, получающих кастомные инструкции,
      (4) ИТ-отдел Vanderbilt University, обеспечивающий инфраструктурную поддержку
      и governance. Разделение ролей подчёркивает институциональный контроль над AI.'
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  ai_role:
    text: AI в Amplify выполняет функциональную роль ассистента и среды для продуктивной
      работы с Generative AI. Модель не автономна в полном смысле (агентность 2/6),
      отсутствие циклов самоуправления и автономных интервенций, AI выступает как
      инструмент, подчинённый пользовательским кастомным инструкциям и административному
      контролю в защищённом кампусном контуре.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  interaction_scenario:
    text: Пользователь (faculty/staff/student) инициирует доступ к Amplify в кампусной
      среде, выбирает из набора LLM и передаёт им кастомизированные инструкции. Запросы
      обрабатываются в изолированной песочнице с обеспечением безопасности данных.
      Институциональная команда следит за соблюдением правил, модерацией и поддержкой.
      Таким образом, пользователи получают защищённый и конфиденциальный канал работы
      с AI, интегрированной с университетскими сервисами.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  institutional_loop:
    text: Amplify управляется через внутренние политики Vanderbilt University, предусматривающие
      secure access, соблюдение условий использования и контроль над персональными
      и учебными данными. Платформа строится как open-source решение, что позволяет
      университету вести governance, снизить риски vendor lock-in и обеспечить прозрачность.
      Политика направлена на интеграцию AI в образовательный процесс с учётом нормативных
      и этических стандартов.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  metrics_evidence:
    text: 'Публично задокументирован масштаб внедрения: Amplify доступна всему контингенту
      faculty, staff и студентов campus-wide, что представляет собой кампусный rollout.
      Отдельные количественные метрики по повышению успеваемости, навыков или эффективности
      обучения не опубликованы. Официальные метрики — количество пользователей с free-access
      в рамках пилотной программы и уровень институционального закрепления платформы.'
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
---

## Описание

Amplify — защищённая чат-среда Vanderbilt для faculty/staff. Поддержка
custom instructions, multi-LLM выбор. На момент описания — пилот с
waitlist; не открыт для студентов.

## Что переиспользуемо

Если нужно начать с малых рисков: faculty-only sandbox даёт время
выработать политику до того, как сервис придёт к студентам.
