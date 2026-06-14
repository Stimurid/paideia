---
id: queens-librechat
name: Queen's University · LibreChat campus deployment
organization:
  name: Queen's University
  type: U
  country: CA
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
  - librechat
  - gpt-4o
  - claude-3.5
  role: open-source LibreChat + data privacy
transformation_mode: rectoral-initiative
axes:
  agentivity: 2
  ai_pattern: A
  orchestration: MOD
  control_locus: HYBR
  interaction_form: governed-portal
  provider_lock_in: 1
  scale_of_change: 3
  institutional_depth: 4
  governance_strength: 4
  audit_trail_strength: 4
  data_sensitivity: 4
  cost_intensity: 3
lifecycle:
  stage: rollout
  first_seen: wave-2
  history:
  - wave: wave-2
    stage: rollout
    note: LibreChat для faculty/staff/students с акцентом 'data remains within the
      Queen's domain'
links:
- kind: type
  id: A
  relation: instantiates
  confidence: high
- kind: hypothesis
  id: H1
  relation: supports
  confidence: high
sources:
- url: https://www.queensu.ca/
  type: official
  accessed: 2026-02
verified: true
canvas:
  signature_context:
    text: 'Queen''s University (Canada) — LibreChat-based кампусный сервис с

      приватностью данных «within the Queen''s domain». Тип

      [[A-governed-access]] на open-source основе.'
    status: draft
    source: imported
    updated_at: '2026-06-12'
---

## Описание

Queen's University (Canada) — LibreChat-based кампусный сервис с
приватностью данных «within the Queen's domain». Тип
[[A-governed-access]] на open-source основе.
