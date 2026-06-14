---
id: advisory-governance-layer
name: Advisory Governance Layer · multi-stakeholder MAS for ITS
organization:
  name: AGL research group
  type: R
  country: INT
scenario:
  level:
  - research
  domains:
  - governance
  context: research-prototype
facets:
  orchestration: NET
  pedagogy: INST
  control: HYBR
  economy: NONE
ai:
  pattern: D
  agentivity: 3
  technologies:
  - multiple-models
  role: stakeholder-agents (students/parents/teachers/institutions) для policy advice
transformation_mode: greenfield
axes:
  agentivity: 3
  ai_pattern: D
  orchestration: NET
  control_locus: HYBR
  interaction_form: multi-agent-simulation
  governance_strength: 5
  audit_trail_strength: 5
  evaluation_evidence_strength: 1
lifecycle:
  stage: poc
  first_seen: diff-2026-06
  history:
  - wave: diff-2026-06
    stage: poc
    note: 'reference architecture: stakeholder-agents оценивают педагогические действия
      с разных policy-perspectives'
links:
- kind: type
  id: D
  relation: instantiates
  confidence: medium
- kind: hypothesis
  id: H4
  relation: supports
  confidence: medium
- kind: tension
  id: agentic-networks-vs-institutional-boundaries
  relation: illustrates
  confidence: high
sources:
- url: https://arxiv.org/
  type: academic
  accessed: 2026-06
verified: false
canvas:
  signature_context:
    text: 'Advisory Governance Layer — не tutor, а слой governance вокруг tutor-системы.

      Stakeholder-agents (students / parents / teachers / institutions) оценивают

      педагогические действия с разных policy-перспектив. Редкая формализация

      того, что в университетских внедрениях обычно остаётся неявным.

      Иллюстрирует [[agentic-networks-vs-institutional-boundaries]].'
    status: draft
    source: imported
    updated_at: '2026-06-12'
---

## Описание

Advisory Governance Layer — не tutor, а слой governance вокруг tutor-системы.
Stakeholder-agents (students / parents / teachers / institutions) оценивают
педагогические действия с разных policy-перспектив. Редкая формализация
того, что в университетских внедрениях обычно остаётся неявным.
Иллюстрирует [[agentic-networks-vs-institutional-boundaries]].
