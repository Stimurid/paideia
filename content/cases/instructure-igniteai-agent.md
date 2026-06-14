---
id: instructure-igniteai-agent
name: Instructure · IgniteAI Agent (workflow agent)
organization:
  name: Instructure
  type: C
  country: US
scenario:
  level:
  - faculty
  domains:
  - general
  context: lms-product
facets:
  orchestration: META
  pedagogy: ROLE
  control: HYBR
  economy: MKT
ai:
  pattern: B
  agentivity: 3
  technologies:
  - multiple-models
  role: NL→workflow agent in Canvas
transformation_mode: vendor-pushed
axes:
  agentivity: 3
  ai_pattern: B
  orchestration: META
  control_locus: HYBR
  interaction_form: agent-workflow
  scale_of_change: 5
  institutional_depth: 4
  audit_trail_strength: 4
  lms_integration: true
  has_metrics: true
lifecycle:
  stage: rollout
  first_seen: wave-2
  history:
  - wave: wave-2
    stage: rollout
    note: NL-запрос → Canvas workflows; >30k educators по релизу; заявка на 'agentic
      phase'
links:
- kind: type
  id: B
  relation: instantiates
  confidence: high
- kind: hypothesis
  id: H2
  relation: supports
  confidence: medium
- kind: tension
  id: autonomy-vs-control
  relation: illustrates
  confidence: high
- kind: counter-signal
  id: gartner-agentic-cancellations
  relation: weakens
  confidence: low
  note: agent washing-риск частично применим
metrics:
  hard:
  - educators-30k
sources:
- url: https://www.instructure.com/
  type: official
  accessed: 2026-02
verified: true
canvas:
  signature_context:
    text: 'IgniteAI Agent — чат-агент преподавателя, переводящий NL-запросы в

      Canvas workflows под контролем human-confirm. Заявлено >30k educators. Это

      сдвиг AI от инструмента-рядом к оркестратору действий внутри LMS.

      Поддерживает [[H2-assistant-to-autonomy]] локально, но иллюстрирует

      противоречие [[autonomy-vs-control]].'
    status: draft
    source: imported
    updated_at: '2026-06-12'
---

## Описание

IgniteAI Agent — чат-агент преподавателя, переводящий NL-запросы в
Canvas workflows под контролем human-confirm. Заявлено >30k educators. Это
сдвиг AI от инструмента-рядом к оркестратору действий внутри LMS.
Поддерживает [[H2-assistant-to-autonomy]] локально, но иллюстрирует
противоречие [[autonomy-vs-control]].
