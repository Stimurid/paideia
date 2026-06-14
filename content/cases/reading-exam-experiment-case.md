---
id: reading-exam-experiment-case
name: University of Reading · скрытый AI-инфильтрационный эксперимент (исследование)
organization:
  name: University of Reading
  type: U
  country: UK
scenario:
  level:
  - research
  domains:
  - assessment-research
  context: research-experiment
facets:
  orchestration: LIN
  pedagogy: SUBJ
  control: HUMAN
  economy: BUD
ai:
  pattern: D
  agentivity: 1
  technologies:
  - gpt-4o
  role: hidden test participant
transformation_mode: bottom-up
axes:
  agentivity: 1
  ai_pattern: D
  orchestration: LIN
  control_locus: HUMAN
  interaction_form: chat
  audit_trail_strength: 5
  evaluation_evidence_strength: 5
lifecycle:
  stage: poc
  first_seen: meta-audit
  history:
  - wave: meta-audit
    stage: poc
    note: '2024: AI-сгенерированные работы через реальные аккаунты прошли оценивание
      с высокими оценками; флаг подозрения — единичный'
links:
- kind: hypothesis
  id: H4
  relation: contradicts
  confidence: high
- kind: tension
  id: generation-vs-verification
  relation: illustrates
  confidence: high
- kind: counter-signal
  id: reading-exam-experiment
  relation: supports
  confidence: high
sources:
- url: https://journals.plos.org/plosone/
  type: academic
  accessed: 2026-02
verified: true
canvas:
  signature_context:
    text: 'Reading — эмпирический стресс-тест системы оценивания: AI-ответы через

      реальные студенческие аккаунты, низкая детекция. Connected to

      counter-signal [[reading-exam-experiment]].'
    status: draft
    source: imported
    updated_at: '2026-06-12'
---

## Описание

Reading — эмпирический стресс-тест системы оценивания: AI-ответы через
реальные студенческие аккаунты, низкая детекция. Connected to
counter-signal [[reading-exam-experiment]].
