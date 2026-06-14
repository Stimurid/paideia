---
id: role-based-feedback-agents
name: Role-Based Feedback Agents · formative assessment MAS
organization:
  name: Role-Based Feedback research group
  type: R
  country: INT
scenario:
  level:
  - research
  domains:
  - assessment
  context: research-prototype
facets:
  orchestration: NET
  pedagogy: ROLE
  control: HYBR
  economy: NONE
ai:
  pattern: D
  agentivity: 3
  technologies:
  - multiple-models
  role: Evaluator + Equity Monitor + Coach + Aggregator + Reflexion Reviewer
transformation_mode: greenfield
axes:
  agentivity: 3
  ai_pattern: D
  orchestration: NET
  control_locus: HYBR
  interaction_form: multi-agent-simulation
  governance_strength: 4
  reflexivity: 5
  audit_trail_strength: 5
lifecycle:
  stage: poc
  first_seen: diff-2026-06
  history:
  - wave: diff-2026-06
    stage: poc
    note: '5 ролевых агентов формативного оценивания: Evaluator, Equity Monitor, Coach,
      Aggregator, Reflexion Reviewer'
links:
- kind: type
  id: D
  relation: instantiates
  confidence: medium
- kind: hypothesis
  id: H2
  relation: supports
  confidence: medium
- kind: tension
  id: generation-vs-verification
  relation: weakens
  confidence: medium
sources:
- url: https://arxiv.org/
  type: academic
  accessed: 2026-06
verified: false
canvas:
  signature_context:
    text: 'Role-Based Feedback — multi-agent система формативного оценивания с 5

      ролями: Evaluator, Equity Monitor, Coach, Aggregator, Reflexion Reviewer.

      Разделение функций оценщика снижает bias и даёт reflective контур.

      Ослабляет [[generation-vs-verification]].'
    status: draft
    source: imported
    updated_at: '2026-06-12'
---

## Описание

Role-Based Feedback — multi-agent система формативного оценивания с 5
ролями: Evaluator, Equity Monitor, Coach, Aggregator, Reflexion Reviewer.
Разделение функций оценщика снижает bias и даёт reflective контур.
Ослабляет [[generation-vs-verification]].
