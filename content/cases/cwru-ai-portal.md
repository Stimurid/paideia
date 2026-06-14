---
id: cwru-ai-portal
name: Case Western Reserve · CWRU AI портал
organization:
  name: Case Western Reserve University
  type: U
  country: US
scenario:
  level:
  - undergraduate
  - graduate
  - faculty
  - staff
  - researcher
  domains:
  - general
  - medicine
  context: campus-platform
facets:
  orchestration: META
  pedagogy: ROLE
  control: HYBR
  economy: BUD+EXT
ai:
  pattern: A
  agentivity: 3
  technologies:
  - gpt-4o
  - claude-3.5
  role: portal + prompt library + departmental bots on demand
transformation_mode: rectoral-initiative
axes:
  agentivity: 3
  ai_pattern: A
  orchestration: META
  control_locus: HYBR
  interaction_form: governed-portal
  provider_lock_in: 2
  scale_of_change: 4
  institutional_depth: 4
  governance_strength: 4
  audit_trail_strength: 4
  data_sensitivity: 4
  cost_intensity: 4
  rag_grounded: true
lifecycle:
  stage: rollout
  first_seen: wave-2
  history:
  - wave: wave-2
    stage: rollout
    note: выбор модели, файлы и поиск по файлам, prompt library; departmental чатботы
      по запросу с HIPAA-ограничениями
links:
- kind: type
  id: A
  relation: instantiates
  confidence: high
- kind: type
  id: B
  relation: instantiates
  confidence: medium
- kind: hypothesis
  id: H1
  relation: supports
  confidence: high
sources:
- url: https://case.edu/
  type: official
  accessed: 2026-02
verified: true
canvas:
  signature_context:
    text: 'CWRU AI портал — secure портал с выбором модели, file-search, prompt library

      и возможностью разворачивать department/group чатботы по запросу с

      HIPAA-ограничениями. Шаблон оркестрации «общий портал →

      специализированные боты по подразделениям». Гибрид

      [[A-governed-access]] и [[B-no-code-builder]].'
    status: draft
    source: imported
    updated_at: '2026-06-12'
---

## Описание

CWRU AI портал — secure портал с выбором модели, file-search, prompt library
и возможностью разворачивать department/group чатботы по запросу с
HIPAA-ограничениями. Шаблон оркестрации «общий портал →
специализированные боты по подразделениям». Гибрид
[[A-governed-access]] и [[B-no-code-builder]].
