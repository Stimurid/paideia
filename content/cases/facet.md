---
id: facet
name: FACET · teacher-centred MAS for personalized worksheets
organization:
  name: FACET research group
  type: R
  country: INT
scenario:
  level:
  - primary
  - secondary
  domains:
  - k12
  context: research-prototype
facets:
  orchestration: NET
  pedagogy: AMP
  control: HUMAN
  economy: NONE
ai:
  pattern: B
  agentivity: 2
  technologies:
  - multiple-models
  role: learner-agents + teacher-agent + evaluator-agent
transformation_mode: greenfield
axes:
  agentivity: 2
  ai_pattern: B
  orchestration: NET
  control_locus: HUMAN
  interaction_form: agent-workflow
  audit_trail_strength: 4
  evaluation_evidence_strength: 2
lifecycle:
  stage: poc
  first_seen: diff-2026-06
  history:
  - wave: diff-2026-06
    stage: poc
    note: 'teacher-facing: learner-agents с profile, teacher-agent для дизайна, evaluator-agent
      для QA; exploratory feedback от K-12 учителей'
links:
- kind: type
  id: B
  relation: instantiates
  confidence: medium
- kind: hypothesis
  id: H2
  relation: supports
  confidence: low
sources:
- url: https://arxiv.org/
  type: academic
  accessed: 2026-06
verified: false
canvas:
  signature_context:
    text: 'FACET — teacher-centred multi-agent система: помогает учителю собирать

      индивидуальные материалы для гетерогенного класса. AI вокруг

      преподавателя, а не вместо. В отличие от [[itas-odu]] и [[genmentor]],

      оптимизирует teacher-design loop.'
    status: draft
    source: imported
    updated_at: '2026-06-12'
---

## Описание

FACET — teacher-centred multi-agent система: помогает учителю собирать
индивидуальные материалы для гетерогенного класса. AI вокруг
преподавателя, а не вместо. В отличие от [[itas-odu]] и [[genmentor]],
оптимизирует teacher-design loop.
