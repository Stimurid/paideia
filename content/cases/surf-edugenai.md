---
id: surf-edugenai
name: SURF (NL) · EduGenAI (AI-Hub + proxy + personae)
organization:
  name: SURF
  type: N
  country: NL
scenario:
  level:
  - undergraduate
  - graduate
  - faculty
  - staff
  domains:
  - general
  context: consortium-infra
facets:
  orchestration: META
  pedagogy: ROLE
  control: HYBR
  economy: BUD+EXT
ai:
  pattern: F
  agentivity: 3
  technologies:
  - multiple-models
  - rag
  role: web-app + LLM proxy + AI-Hub + Personae (mini-GPT) + dashboards
roles:
  human:
  - institution-CO
  - CO-line-1-support
  - EduGenAI-line-2
  - SURF-AI-Hub-line-3
  machine:
  - LLM-proxy
  - RAG
  - personae
  - dashboards
  interaction_scenario: 'Web-app + LLM proxy + AI-Hub + on-prem и cloud LLMs + RAG
    + Personae;

    мониторинг и логирование; трёхлинейная поддержка (CO → EduGenAI →

    SURF AI-Hub).

    '
transformation_mode: consortium-driven
axes:
  agentivity: 3
  ai_pattern: F
  orchestration: META
  control_locus: HYBR
  interaction_form: governed-portal
  scale_of_change: 5
  institutional_depth: 5
  governance_strength: 5
  audit_trail_strength: 5
  data_sensitivity: 4
  cost_intensity: 5
  has_metrics: true
lifecycle:
  stage: rollout
  first_seen: wave-2
  history:
  - wave: wave-2
    stage: rollout
    note: конcорциумная мета-инфраструктура для голландских университетов; DPIA-описана
links:
- kind: type
  id: F
  relation: instantiates
  confidence: high
- kind: type
  id: A
  relation: instantiates
  confidence: medium
- kind: hypothesis
  id: H1
  relation: supports
  confidence: high
- kind: hypothesis
  id: H3
  relation: supports
  confidence: medium
- kind: hypothesis
  id: H4
  relation: supports
  confidence: high
- kind: tension
  id: agentic-networks-vs-institutional-boundaries
  relation: illustrates
  confidence: high
sources:
- url: https://www.surf.nl/edugenai
  type: official
  accessed: 2026-02
verified: true
canvas:
  signature_context:
    text: 'EduGenAI (SURF) — мета-инфраструктура: web-app + LLM proxy + AI-Hub +

      RAG + Personae + dashboards для голландских университетов.

      Трёхлинейная поддержка. Близко к "операционной системе для

      институциональной GenAI". Эталон типа [[F-national-infrastructure]].

      Иллюстрирует [[agentic-networks-vs-institutional-boundaries]].'
    status: draft
    source: imported
    updated_at: '2026-06-12'
---

## Описание

EduGenAI (SURF) — мета-инфраструктура: web-app + LLM proxy + AI-Hub +
RAG + Personae + dashboards для голландских университетов.
Трёхлинейная поддержка. Близко к "операционной системе для
институциональной GenAI". Эталон типа [[F-national-infrastructure]].
Иллюстрирует [[agentic-networks-vs-institutional-boundaries]].
