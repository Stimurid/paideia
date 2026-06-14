---
id: colorado-chatgpt-edu-delay
name: University of Colorado · ChatGPT Edu rollout delay (faculty governance)
organization:
  name: University of Colorado System
  type: U
  country: US
scenario:
  level:
  - undergraduate
  - graduate
  - faculty
  - staff
  domains:
  - general
  context: governance-pause
facets:
  orchestration: MOD
  pedagogy: INST
  control: HUMAN
  economy: EXT
ai:
  pattern: A
  agentivity: 1
  technologies:
  - gpt-4o
  role: ChatGPT Edu (faculty access only)
transformation_mode: faculty-governed
axes:
  agentivity: 1
  ai_pattern: A
  orchestration: MOD
  control_locus: HUMAN
  interaction_form: chat
  provider_lock_in: 5
  scale_of_change: 3
  institutional_depth: 3
  governance_strength: 5
  reversible: true
lifecycle:
  stage: pilot
  first_seen: diff-2026-06
  history:
  - wave: diff-2026-06
    stage: pilot
    note: faculty/staff доступ с 31.03.2026; студенческий слой отложен по запросу
      Faculty Council из-за рисков
links:
- kind: type
  id: A
  relation: instantiates
  confidence: medium
- kind: hypothesis
  id: H4
  relation: weakens
  confidence: medium
- kind: counter-signal
  id: colorado-rollout-delay
  relation: supports
  confidence: high
- kind: tension
  id: autonomy-vs-control
  relation: illustrates
  confidence: high
sources:
- url: https://www.cu.edu/
  type: official
  accessed: 2026-06
verified: false
canvas:
  signature_context:
    text: 'University of Colorado — ранний пример faculty-governance паузы.

      Архитектурно тип [[A-governed-access]] на лицензии ChatGPT Edu, но

      заглохший на студенческом слое. Иллюстрирует [[autonomy-vs-control]].

      Связан с counter-signal [[colorado-rollout-delay]].'
    status: draft
    source: imported
    updated_at: '2026-06-12'
---

## Описание

University of Colorado — ранний пример faculty-governance паузы.
Архитектурно тип [[A-governed-access]] на лицензии ChatGPT Edu, но
заглохший на студенческом слое. Иллюстрирует [[autonomy-vs-control]].
Связан с counter-signal [[colorado-rollout-delay]].
