---
id: openai-chatgpt-edu
name: OpenAI · ChatGPT Edu (университетский продукт)
organization:
  name: OpenAI
  type: C
  country: INT
scenario:
  level:
  - undergraduate
  - graduate
  - faculty
  - staff
  domains:
  - general
  context: vendor-product
facets:
  orchestration: LIN
  pedagogy: INST
  control: HYBR
  economy: MKT
ai:
  pattern: A
  agentivity: 1
  technologies:
  - gpt-4o
  role: enterprise-grade campus license
transformation_mode: vendor-pushed
axes:
  agentivity: 1
  ai_pattern: A
  orchestration: LIN
  control_locus: HYBR
  interaction_form: chat
  scale_of_change: 5
  institutional_depth: 3
  provider_lock_in: 5
  cost_intensity: 4
  has_metrics: false
lifecycle:
  stage: rollout
  first_seen: wave-1
  history:
  - wave: wave-1
    stage: rollout
    note: 'формат ChatGPT Edu для университетов: enterprise-grade с governance-механизмами'
  - wave: diff-2026-06
    stage: rollout
    note: массовое расширение через India, CSU, USC, UC Colorado, Hofstra
links:
- kind: type
  id: A
  relation: instantiates
  confidence: high
- kind: hypothesis
  id: H1
  relation: supports
  confidence: high
- kind: mode
  id: acceleration
  relation: supports
  confidence: high
sources:
- url: https://openai.com/chatgpt/education/
  type: official
  accessed: 2026-02
verified: true
canvas:
  signature_context:
    text: 'ChatGPT Edu — продуктовая форма OpenAI для университетов, основа для

      большинства кампусных rollouts типа [[A-governed-access]] в 2024–2026.

      Поддерживает [[H1-tool-to-infrastructure]] и моду [[acceleration]].'
    status: draft
    source: imported
    updated_at: '2026-06-12'
---

## Описание

ChatGPT Edu — продуктовая форма OpenAI для университетов, основа для
большинства кампусных rollouts типа [[A-governed-access]] в 2024–2026.
Поддерживает [[H1-tool-to-infrastructure]] и моду [[acceleration]].
