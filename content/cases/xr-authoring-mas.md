---
id: xr-authoring-mas
name: Multi-Agent XR Authoring Framework · classroom authoring MAS
organization:
  name: XR Authoring research group
  type: R
  country: INT
scenario:
  level:
  - primary
  - secondary
  domains:
  - k12
  - xr
  context: research-prototype
facets:
  orchestration: NET
  pedagogy: ROLE
  control: HYBR
  economy: NONE
ai:
  pattern: B
  agentivity: 3
  technologies:
  - multiple-models
  - xr
  role: Pedagogical + Execution + Safeguard + Tutor agents
transformation_mode: greenfield
axes:
  agentivity: 3
  ai_pattern: B
  orchestration: NET
  control_locus: HYBR
  interaction_form: multi-agent-simulation
  domain_specificity: 4
  audit_trail_strength: 4
  evaluation_evidence_strength: 1
lifecycle:
  stage: poc
  first_seen: diff-2026-06
  history:
  - wave: diff-2026-06
    stage: poc
    note: Pedagogical/Execution/Safeguard/Tutor agents для авторинга XR-контента в
      классе
links:
- kind: type
  id: B
  relation: instantiates
  confidence: low
- kind: hypothesis
  id: H2
  relation: supports
  confidence: low
sources:
- url: https://arxiv.org/
  type: academic
  accessed: 2026-06
verified: false
canvas:
  signature_context:
    text: 'Multi-Agent XR Authoring — multi-agent система для авторинга

      XR-контента в школьном классе. Pedagogical agent / Execution agent /

      Safeguard agent / Tutor agent.'
    status: draft
    source: imported
    updated_at: '2026-06-12'
  ontology_status:
    text: Multi-Agent XR Authoring Framework находится на стадии прототипа, предназначенного
      для classroom authoring use в K–12 контексте. Это не коммерческое решение и
      не policy, а исследовательский пример архитектуры, демонстрирующий организацию
      разнофункциональных агентов в XR-среде. Исходя из описания, система еще не прошла
      полноценный rollout и масштабное внедрение, сохраняя экспериментальный статус.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  problem_situation:
    text: До внедрения Multi-Agent XR Authoring Framework в K–12 классы существовали
      ограничения в координации создания и контроля XR образовательного контента на
      уровне агентного распределения ролей. Традиционные системы либо концентрировались
      на отдельных ERP/authoring инструментах без интеграции safety агентности, либо
      не обеспечивали явную специализированную роль педагогики, исполнения и безопасности.
      Контроль качества XR контента и его педагогические параметры оставались разрозненными,
      что усложняло системную подготовку учебной среды учителем. В частности, отсутствие
      отдельного Safeguard Agent в существующих решениях создаёт риски безопасности
      и несоответствия нормам, а отсутствие явного Tutor Agent снижало качество образовательной
      поддержки.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  effect_hypothesis:
    text: 'Система обещает повысить качество и безопасность авторинга XR-контента
      через распределение функций между специализированными агентами: Pedagogical
      Agent формирует учебные цели и спецификации, Execution Agent осуществляет сбор
      3D ассетов и контента, Safeguard Agent проверяет безопасность по нескольким
      критериям, а Tutor Agent добавляет образовательные комментарии и вопросы для
      проверки знаний. Такая архитектура направлена на orchestration учебной среды
      на уровне NET-фасеты с промежуточным agentivity 3/6, что означает значительную,
      но не полную автономность, где ИИ-агенты координируются в совместном workflow,
      служа для поддержки учителя и улучшения школьного образовательного процесса.'
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  ai_architecture:
    text: 'Архитектура Multi-Agent XR Authoring Framework опирается на распределённый
      multi-agent подход с 4 основными ролями: Pedagogical Agent, который управляет
      спецификациями контента и образовательными целями в соответствии с grade-appropriate
      требованиями; Execution Agent, отвечающий за сбор и интеграцию 3D ассетов и
      XR материалов; Safeguard Agent, встроенный для проверки безопасности по пяти
      критериям, обеспечивая соответствие XR среды нормам и предотвращая риски; и
      Tutor Agent, который добавляет учебно-педагогический контент — образовательные
      заметки и quiz questions. Используется многомодельная технология (multiple-models)
      с акцентом на XR, что поддерживает NET-оркестрацию и гибридный режим контроля
      (HYBR), ориентированный на teacher-facing использование.'
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  team_roles:
    text: 'В рамках кейса выделяются четко распределённые роли AI-агентов, помимо
      человеческих участников. Среди AI: Pedagogical Agent, Execution Agent, Safeguard
      Agent и Tutor Agent, которые отвечают за разные этапы производства и контроля
      XR образовательного контента. Роль teachera, скорее всего, сосредоточена на
      координации, проверке и использовании сгенерированного контента в классе, при
      этом AI-агенты направлены не на замену учителя, а на поддержку и автоматизацию
      частей workflow. От человека ожидается управление и принятие финальных решений,
      особенно в контексте безопасности и педагогического администрирования.'
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  ai_role:
    text: ИИ-агенты выполняют функции pedagogical design (Pedagogical Agent), исполнения
      и сбора материалов (Execution Agent), обеспечения безопасности контента (Safeguard
      Agent) и формирования учебной поддержки (Tutor Agent). В этом кейсе AI выступает
      не как автономный учитель, а как комплексный исполнитель и оркестратор учебной
      среды, выступая в роли multi-agent system с промежуточным уровнем agentivity
      (3/6), обеспечивая баланс между автономностью и контролем человека. Таким образом,
      AI играет ключевую роль в создании, проверке и поддержке XR контента для образовательных
      целей.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  interaction_scenario:
    text: Процесс авторинга начинается с того, что Pedagogical Agent формирует требования
      к XR контенту согласно учебным целям и возрастной категории. Далее Execution
      Agent собирает необходимые 3D объекты и компилирует XR-среду. Safeguard Agent
      проверяет весь создаваемый контент и среду по пяти критериям безопасности, исключает
      потенциально опасные элементы и гарантирует соответствие стандартам. Завершает
      цикл Tutor Agent, который добавляет образовательные заметки, пояснения и вопросы
      для оценки усвоения материала. Учитель использует полученный XR материал, направляя
      и контролируя учебный процесс с гибридным контролем, где AI-agent workflow тесно
      встроен в teacher-facing интерфейс.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
---

## Описание

Multi-Agent XR Authoring — multi-agent система для авторинга
XR-контента в школьном классе. Pedagogical agent / Execution agent /
Safeguard agent / Tutor agent.
