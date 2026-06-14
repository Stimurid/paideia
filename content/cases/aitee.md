---
id: aitee
name: AITEE · agentic tutor for electrical engineering
organization:
  name: AITEE research group
  type: R
  country: INT
scenario:
  level:
  - undergraduate
  - graduate
  domains:
  - engineering
  context: research-prototype
facets:
  orchestration: MOD
  pedagogy: ROLE
  control: HYBR
  economy: NONE
ai:
  pattern: B
  agentivity: 3
  technologies:
  - llm
  - rag
  - spice-sim
  role: domain tutor with circuit reconstruction + simulation
transformation_mode: greenfield
axes:
  agentivity: 3
  ai_pattern: B
  orchestration: MOD
  control_locus: HYBR
  interaction_form: agent-workflow
  domain_specificity: 5
  audit_trail_strength: 4
  rag_grounded: true
  evaluation_evidence_strength: 3
lifecycle:
  stage: poc
  first_seen: diff-2026-06
  history:
  - wave: diff-2026-06
    stage: poc
    note: circuit reconstruction + RAG по лекциям + parallel SPICE-симуляция + Socratic
      dialogue
links:
- kind: type
  id: B
  relation: instantiates
  confidence: medium
- kind: type
  id: C
  relation: instantiates
  confidence: medium
- kind: hypothesis
  id: H2
  relation: supports
  confidence: medium
- kind: tension
  id: domain-cognition-vs-interpretation
  relation: illustrates
  confidence: high
sources:
- url: https://arxiv.org/
  type: academic
  accessed: 2026-06
verified: false
canvas:
  signature_context:
    text: 'AITEE — domain-specific agentic tutor для electrical engineering: circuit

      reconstruction, RAG по лекциям, parallel SPICE-симуляция, Socratic dialogue

      mode. Агентность возникает из связи LLM + предметный объект + симулятор.

      Иллюстрирует [[domain-cognition-vs-interpretation]].'
    status: draft
    source: imported
    updated_at: '2026-06-12'
  ontology_status:
    text: AITEE представлен как новый архитектурный кейс с агентным тьютором для electrical
      engineering, находящийся на уровне прототипа с уровнем агентности 2–3 из 6.
      Это означает, что система уже более развита, чем просто симуляция, но еще не
      достигла полноценного реального развертывания в университете. Согласно рамке
      оценки волн, кейс рассматривается как архитектурное решение с агентным подходом,
      пока без полного институционального внедрения, что соответствует статусу прототипа.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
---

## Описание

AITEE — domain-specific agentic tutor для electrical engineering: circuit
reconstruction, RAG по лекциям, parallel SPICE-симуляция, Socratic dialogue
mode. Агентность возникает из связи LLM + предметный объект + симулятор.
Иллюстрирует [[domain-cognition-vs-interpretation]].
