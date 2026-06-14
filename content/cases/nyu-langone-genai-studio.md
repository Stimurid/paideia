---
id: nyu-langone-genai-studio
name: NYU Langone Health · GenAI Studio + Prompt-a-thon
organization:
  name: NYU Langone Health
  type: C
  country: US
scenario:
  level:
  - professional
  - clinical
  - research
  domains:
  - medicine
  context: workforce-studio
facets:
  orchestration: META
  pedagogy: INST
  control: HYBR
  economy: BUD+EXT
ai:
  pattern: E
  agentivity: 3
  technologies:
  - azure-openai
  - custom-ui
  role: private GenAI studio + mentor command center + scored projects
roles:
  human:
  - mentors
  - participants
  - command-center
  machine:
  - GenAI studio
  - scoring system
  - usage analytics
  interaction_scenario: 'Внутренний portal на private Azure OpenAI; "playground" UI;
    mentor

    command center курирует prompt-a-thon заявки; команды оцениваются на

    результаты, метрики использования и стоимости.

    '
transformation_mode: rectoral-initiative
axes:
  agentivity: 3
  ai_pattern: E
  orchestration: META
  control_locus: HYBR
  interaction_form: governed-portal
  scale_of_change: 4
  institutional_depth: 5
  governance_strength: 5
  audit_trail_strength: 5
  data_sensitivity: 5
  evaluation_evidence_strength: 4
  cost_intensity: 5
  domain_specificity: 4
  has_metrics: true
lifecycle:
  stage: rollout
  first_seen: wave-2
  history:
  - wave: wave-2
    stage: rollout
    note: 1007 заявок за 6 мес.; 560 участников вводного вебинара; метрики токенов/стоимости
links:
- kind: type
  id: E
  relation: instantiates
  confidence: high
- kind: type
  id: D
  relation: instantiates
  confidence: high
- kind: hypothesis
  id: H1
  relation: supports
  confidence: high
- kind: hypothesis
  id: H4
  relation: supports
  confidence: medium
metrics:
  hard:
  - applications-1007
  - webinar-560
  soft:
  - token-metrics
  - cost-tracking
sources:
- url: https://nyulangone.org/
  type: official
  accessed: 2026-02
verified: true
canvas:
  signature_context:
    text: 'NYU Langone GenAI Studio — эталон типа [[E-workforce-studio]]: private

      Azure OpenAI с собственным UI, mentor command center, prompt-a-thon

      формат с оценкой проектов. Один из немногих кейсов с публичными hard-

      метриками воронки внедрения.'
    status: draft
    source: imported
    updated_at: '2026-06-12'
---

## Описание

NYU Langone GenAI Studio — эталон типа [[E-workforce-studio]]: private
Azure OpenAI с собственным UI, mentor command center, prompt-a-thon
формат с оценкой проектов. Один из немногих кейсов с публичными hard-
метриками воронки внедрения.
