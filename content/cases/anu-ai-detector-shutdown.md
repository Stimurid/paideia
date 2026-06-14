---
id: anu-ai-detector-shutdown
name: Australian National University · отключение Turnitin AI detector
organization:
  name: Australian National University
  type: U
  country: AU
scenario:
  level:
  - undergraduate
  - graduate
  domains:
  - general
  context: detector-shutdown
facets:
  orchestration: MOD
  pedagogy: INST
  control: HUMAN
  economy: BUD
ai:
  pattern: D
  agentivity: 1
  technologies:
  - turnitin-ai-detection
  role: shut down detector
transformation_mode: rectoral-initiative
axes:
  agentivity: 1
  ai_pattern: D
  orchestration: MOD
  control_locus: HUMAN
  interaction_form: chat
  governance_strength: 5
  reversible: true
  evaluation_evidence_strength: 4
lifecycle:
  stage: rolled-back
  first_seen: meta-audit
  history:
  - wave: meta-audit
    stage: rolled-back
    note: отключение AI-writing detection в Turnitin с 01.01.2024 из-за ненадёжности
      и bias против non-native English
links:
- kind: type
  id: D
  relation: instantiates
  confidence: low
- kind: hypothesis
  id: H2
  relation: contradicts
  confidence: high
- kind: tension
  id: generation-vs-verification
  relation: illustrates
  confidence: high
- kind: counter-signal
  id: anu-detector-shutdown
  relation: supports
  confidence: high
sources:
- url: https://www.anu.edu.au/
  type: official
  accessed: 2026-02
verified: true
canvas:
  signature_context:
    text: 'ANU — публичный отказ от AI-detection в Turnitin (январь 2024) после

      данных о ненадёжности и bias против non-native English speakers. Первый

      крупный публичный пример институционального отката. Связан с

      counter-signal [[anu-detector-shutdown]].'
    status: draft
    source: imported
    updated_at: '2026-06-12'
---

## Описание

ANU — публичный отказ от AI-detection в Turnitin (январь 2024) после
данных о ненадёжности и bias против non-native English speakers. Первый
крупный публичный пример институционального отката. Связан с
counter-signal [[anu-detector-shutdown]].
