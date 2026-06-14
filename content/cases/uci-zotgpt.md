---
id: uci-zotgpt
name: UC Irvine · ZotGPT (Chat + Creator + ClassChat)
organization:
  name: University of California, Irvine
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
  pedagogy: ROLE
  control: HYBR
  economy: BUD+EXT
ai:
  pattern: B
  agentivity: 2
  technologies:
  - gpt-4o
  - azure-ai
  - aws
  role: chat + creator + class-bots
orchestration_roles:
- users
- bot-authors
- IT-team
- AI-modules
transformation_mode: rectoral-initiative
axes:
  agentivity: 2
  ai_pattern: B
  orchestration: MOD
  control_locus: HYBR
  provider_lock_in: 2
  rag_grounded: true
  has_persistent_state: false
  audit_trail_strength: 3
  domain_specificity: 2
  evaluation_evidence_strength: 2
  interaction_form: lms-microrole
  pedagogy_transformation: ROLE
  transformation_mode: rectoral-initiative
  scale_of_change: 3
  institutional_depth: 4
  radicalness: 2
  reversible: true
  governance_strength: 3
  portability: 3
  reflexivity: 1
  human_role_complexity: 3
  data_sensitivity: 3
  cost_intensity: 3
  lms_integration: true
  has_metrics: true
lifecycle:
  stage: rollout
  first_seen: wave-1
  history:
  - wave: wave-1
    stage: rollout
    note: ZotGPT Chat + Creator (no-code builder) + ClassChat (per-course)
links:
- kind: type
  id: B
  relation: instantiates
  confidence: high
- kind: type
  id: A
  relation: instantiates
  confidence: medium
- kind: hypothesis
  id: H1
  relation: supports
  confidence: medium
metrics:
  hard: []
  soft:
  - free-access
  - multi-product-suite
sources:
- url: https://zotgpt.uci.edu/
  type: official
  accessed: 2026-02
verified: true
canvas:
  signature_context:
    text: 'ZotGPT — зонтичная платформа UCI: чат, Creator (no-code builder локальных

      ботов) и ClassChat (боты, привязанные к материалам курса). Поддерживается

      центральным IT, доступна сообществу бесплатно. Гибрид типа A (доступ) и

      типа B (конструктор).'
    status: draft
    source: imported
    updated_at: '2026-06-12'
  transferability:
    text: 'Триада «чат + конструктор + classroom-bot» хорошо ложится на структуру

      университетского сервиса, который должен закрывать и базовый запрос

      (простой ассистент), и продвинутый (per-course тьютор).'
    status: draft
    source: imported
    updated_at: '2026-06-12'
---

## Описание

ZotGPT — зонтичная платформа UCI: чат, Creator (no-code builder локальных
ботов) и ClassChat (боты, привязанные к материалам курса). Поддерживается
центральным IT, доступна сообществу бесплатно. Гибрид типа A (доступ) и
типа B (конструктор).

## Что переиспользуемо

Триада «чат + конструктор + classroom-bot» хорошо ложится на структуру
университетского сервиса, который должен закрывать и базовый запрос
(простой ассистент), и продвинутый (per-course тьютор).
