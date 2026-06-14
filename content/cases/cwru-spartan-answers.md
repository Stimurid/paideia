---
id: cwru-spartan-answers
name: Case Western Reserve · Spartan Answers (студсервис-бот)
organization:
  name: Case Western Reserve University
  type: U
  country: US
scenario:
  level:
  - undergraduate
  - graduate
  - prospective
  domains:
  - general
  context: student-services
facets:
  orchestration: LIN
  pedagogy: AMP
  control: HUMAN
  economy: BUD+EXT
ai:
  pattern: B
  agentivity: 2
  technologies:
  - gpt-4o
  role: Q&A info-broker with footnotes
transformation_mode: rectoral-initiative
axes:
  agentivity: 2
  ai_pattern: B
  orchestration: LIN
  control_locus: HUMAN
  interaction_form: chat
  scale_of_change: 2
  institutional_depth: 3
  audit_trail_strength: 3
  rag_grounded: true
  has_persistent_state: false
lifecycle:
  stage: rollout
  first_seen: wave-2
  history:
  - wave: wave-2
    stage: rollout
    note: front-door Q&A бот с подтягиванием контента с сайтов и сносками-ссылками
links:
- kind: type
  id: B
  relation: instantiates
  confidence: medium
- kind: hypothesis
  id: H1
  relation: supports
  confidence: low
sources:
- url: https://case.edu/
  type: official
  accessed: 2026-02
verified: true
canvas:
  signature_context:
    text: 'Spartan Answers — front-door Q&A бот CWRU с подтягиванием контента с сайтов

      университета и сносками-ссылками на источники. Тип

      [[B-no-code-builder]] в роли info-broker.'
    status: draft
    source: imported
    updated_at: '2026-06-12'
---

## Описание

Spartan Answers — front-door Q&A бот CWRU с подтягиванием контента с сайтов
университета и сносками-ссылками на источники. Тип
[[B-no-code-builder]] в роли info-broker.
