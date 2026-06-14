---
id: tutor-copilot-rct
name: Tutor CoPilot · RCT-based human-AI tutor augmentation
organization:
  name: Tutor CoPilot research group
  type: R
  country: US
scenario:
  level:
  - k12
  domains:
  - math
  context: research-trial
facets:
  orchestration: MOD
  pedagogy: ROLE
  control: HUMAN
  economy: BUD
ai:
  pattern: C
  agentivity: 2
  technologies:
  - llm
  role: real-time AI suggestions for human tutors
transformation_mode: bottom-up
axes:
  agentivity: 2
  ai_pattern: C
  orchestration: MOD
  control_locus: HUMAN
  interaction_form: agent-workflow
  evaluation_evidence_strength: 5
  audit_trail_strength: 4
  domain_specificity: 3
  reflexivity: 3
lifecycle:
  stage: pilot
  first_seen: wave-2
  history:
  - wave: wave-2
    stage: pilot
    note: RCT с human tutors + real-time AI suggestions; учимая прибавка по математике
links:
- kind: type
  id: C
  relation: instantiates
  confidence: medium
- kind: hypothesis
  id: H2
  relation: supports
  confidence: high
- kind: tension
  id: generation-vs-verification
  relation: weakens
  confidence: high
sources:
- url: https://arxiv.org/
  type: academic
  accessed: 2026-02
verified: true
canvas:
  signature_context:
    text: 'Tutor CoPilot — один из немногих кейсов с RCT-доказательной базой: real-time

      AI suggestions для human tutors дают значимую прибавку в математике. Один

      из главных эмпирических аргументов в пользу [[H2-assistant-to-autonomy]].

      Ослабляет [[generation-vs-verification]].'
    status: draft
    source: imported
    updated_at: '2026-06-12'
---

## Описание

Tutor CoPilot — один из немногих кейсов с RCT-доказательной базой: real-time
AI suggestions для human tutors дают значимую прибавку в математике. Один
из главных эмпирических аргументов в пользу [[H2-assistant-to-autonomy]].
Ослабляет [[generation-vs-verification]].
