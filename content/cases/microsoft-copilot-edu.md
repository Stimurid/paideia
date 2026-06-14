---
id: microsoft-copilot-edu
name: Microsoft · Copilot for Education
organization:
  name: Microsoft
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
  pedagogy: AMP
  control: HUMAN
  economy: MKT
ai:
  pattern: A
  agentivity: 1
  technologies:
  - gpt-4o
  - copilot
  role: in-app assistant (Word/PPT/Teams)
transformation_mode: vendor-pushed
axes:
  agentivity: 1
  ai_pattern: A
  orchestration: LIN
  control_locus: HUMAN
  interaction_form: chat
  scale_of_change: 5
  institutional_depth: 2
  provider_lock_in: 5
  cost_intensity: 4
lifecycle:
  stage: rollout
  first_seen: wave-1
  history:
  - wave: wave-1
    stage: rollout
    note: 'Copilot встроен в Microsoft 365: Word, PowerPoint, Teams'
links:
- kind: type
  id: A
  relation: instantiates
  confidence: low
- kind: hypothesis
  id: H1
  relation: supports
  confidence: low
sources:
- url: https://www.microsoft.com/education
  type: official
  accessed: 2026-02
verified: true
canvas:
  signature_context:
    text: 'Microsoft Copilot for Education — встроен в Microsoft 365. Глобальный

      масштаб, но архитектурно — простой in-app assistant.'
    status: draft
    source: imported
    updated_at: '2026-06-12'
---

## Описание

Microsoft Copilot for Education — встроен в Microsoft 365. Глобальный
масштаб, но архитектурно — простой in-app assistant.
