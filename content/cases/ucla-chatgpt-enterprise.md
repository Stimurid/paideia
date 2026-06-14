---
id: ucla-chatgpt-enterprise
name: UCLA · кампусный rollout ChatGPT Enterprise
organization:
  name: University of California, Los Angeles
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
  context: campus-license
facets:
  orchestration: MOD
  pedagogy: INST
  control: HYBR
  economy: EXT
ai:
  pattern: A
  agentivity: 1
  technologies:
  - gpt-4o
  role: enterprise assistant + governance
orchestration_roles:
- community-users
- governance-board
- OpenAI-vendor
- project-teams
transformation_mode: rectoral-initiative
axes:
  agentivity: 1
  ai_pattern: A
  orchestration: MOD
  control_locus: HYBR
  provider_lock_in: 5
  rag_grounded: false
  has_persistent_state: false
  audit_trail_strength: 3
  domain_specificity: 1
  evaluation_evidence_strength: 2
  interaction_form: chat
  pedagogy_transformation: INST
  transformation_mode: rectoral-initiative
  scale_of_change: 3
  institutional_depth: 3
  radicalness: 1
  reversible: true
  governance_strength: 3
  portability: 4
  reflexivity: 1
  human_role_complexity: 2
  data_sensitivity: 3
  cost_intensity: 4
  lms_integration: false
  has_metrics: false
lifecycle:
  stage: pilot
  first_seen: wave-1
  history:
  - wave: wave-1
    stage: pilot
    note: первый в Калифорнии университетский ChatGPT Enterprise deployment; call
      for proposals
links:
- kind: type
  id: A
  relation: instantiates
  confidence: high
- kind: hypothesis
  id: H1
  relation: supports
  confidence: medium
metrics:
  hard: []
  soft:
  - first-uc-enterprise
  - call-for-proposals
sources:
- url: https://newsroom.ucla.edu/
  type: official
  accessed: 2026-02
verified: true
canvas:
  signature_context:
    text: 'UCLA — первый университет UC-системы, открывший доступ к ChatGPT Enterprise

      сообществу с явным governance-контуром и open call for proposals для

      проектных команд. Архитектура минимальная: лицензия + правила + сбор

      сценариев.'
    status: draft
    source: imported
    updated_at: '2026-06-12'
  transferability:
    text: 'Шаблон «лицензия + governance unit + call for proposals» — самый дешёвый

      способ начать кампусное внедрение без собственной разработки. Дальше,

      как правило, эволюционирует в более структурированные платформы

      (см. Harvard, Stanford).'
    status: draft
    source: imported
    updated_at: '2026-06-12'
  ontology_status:
    text: UCLA's ChatGPT Enterprise deployment is positioned as a pilot and campus
      rollout rather than a mere prototype or policy statement. This enterprise-level
      initiative exhibits a managed, institutional infrastructure integrating AI into
      existing university operations, denoting a stable, transitional phase aimed
      at broad adoption beyond experimental stages.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  problem_situation:
    text: Prior to AI integration, UCLA and similar institutions faced challenges
      in providing scalable, secure, and governed access to generative AI tools within
      the educational domain. The lack of centralized infrastructure to manage AI
      usage, ensure compliance, and coordinate functional roles for multiple campus
      stakeholders limited effective and wide deployment of AI-assisted educational
      and operational processes.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  effect_hypothesis:
    text: By deploying ChatGPT Enterprise campus-wide, UCLA aims to institutionalize
      AI as an enterprise assistant and governance mechanism that enhances productivity
      and learning support while maintaining secure, governed access. The hypothesis
      is that such integration will enable broader, managed AI use cases across education,
      research, and campus operations, improving efficiency without sacrificing privacy
      or institutional controls.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  ai_architecture:
    text: The architecture is centralized around a campus-controlled enterprise AI
      access layer, where AI operates as a unified assistant embedded within governed
      workflows. Roles differentiate between users (faculty, students, administration),
      AI services, governance infrastructures, and project teams managing scenario
      selection. The core technology is OpenAI's ChatGPT-4o, deployed enterprise-wide
      with controlled access and data policies, following the MOD orchestration facet
      and hybrid control (HYBR). Persistent state or RAG elements are not explicitly
      described.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  team_roles:
    text: 'Roles are distinctly separated among: (1) users including faculty, researchers,
      and students who engage with AI per access rules; (2) administrative governance
      and IT teams that oversee AI access, security, and policy compliance; (3) project
      teams that propose, select, and manage AI use cases; and (4) AI itself functioning
      as an enterprise assistant. Human roles emphasize institutional orchestration
      rather than autonomous AI decision-making.'
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  ai_role:
    text: AI is positioned as an enterprise assistant providing functional support
      across teaching, research, and administrative workflows. It delivers assistance
      such as content generation, answering queries, and operational support without
      autonomous control over processes. The agentivity level is 1 to 2/6, reflecting
      a functional, assistive role embedded into a broader governance framework rather
      than independent decision-making.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  interaction_scenario:
    text: Users initiate AI interactions through enterprise-managed access points.
      They submit queries or requests aligned with selected use cases originating
      from a curated project portfolio. The managed governance layer controls who
      accesses services, what data can be used, and which scenarios are active. Project
      teams monitor and evaluate pilot implementations, iterating use cases. Thus,
      interaction flows combine user requests, AI assistive responses, and oversight
      loops to ensure compliance and performance within institutional policies.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  institutional_loop:
    text: The governance structure institutes a robust compliance and policy framework
      for AI access and data management. This includes managed enterprise licenses,
      rules controlling user roles and permissions, secure data handling, and a procedure
      to solicit, review, and onboard AI use cases through calls for proposals. This
      continuous institutional oversight loop ensures alignment with university policies,
      privacy standards, and strategic priorities, reflecting a hybrid governance/control
      model consistent with MOD orchestration.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  transit_to_life:
    text: The project is currently transitioning from pilot phases toward broader
      campus rollout. Initial deployment involved enterprise license provisioning
      and selection of use case portfolios for educational, research, and administrative
      functions. Ongoing adjustments stem from pilot results and project team feedback,
      with further scaling planned. This staged approach allows iterative refinement
      of governance, technical integration, and user engagement as part of the rollout
      roadmap.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  metrics_evidence:
    text: Publicly available metrics focus mainly on pilot scope and project management
      indicators rather than direct learning gains. UCLA has described the initiation
      of pilot programs, the aggregation of scenario projects through competitive
      calls, and institutional adoption levels but does not disclose quantitative
      educational outcomes or user performance improvements. This aligns with patterns
      in similar university deployments, where usage penetration and governance milestones
      serve as interim metrics.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  risks:
    text: Key risks include goal substitution where AI use might prioritize administrative
      convenience over pedagogical quality; lowering of acceptance criteria on AI
      outputs due to automation bias; weak audit trails complicating compliance verification;
      and potential vendor lock-in to OpenAI's GPT-4o. The controlled enterprise access
      reduces some risks but still requires vigilant monitoring to avoid complacency
      in audit and quality assurance.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  countersignals:
    text: While public messaging emphasizes enhanced productivity and managed governance,
      there are signals of limited autonomous use or deeper AI-driven pedagogical
      transformations (agenticity remains at 2/6). The absence of published efficacy
      metrics and the predominant focus on governance hint at potential institutional
      hesitations or unresolved questions about the educational impact and ethical
      implications, creating subtle countersignals to unqualified enthusiasm.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  theory_links:
    text: The UCLA ChatGPT Enterprise case exemplifies the agentic orchestration pattern
      A with agentivity level 1–2/6, where AI acts as an enterprise assistant embedded
      within institutional governance [[H4-agentic-orchestration]]. It reflects the
      MOD facet of orchestration (managed modular deployment) and hybrid control (HYBR)
      balancing autonomy and oversight [[autonomy-vs-control]]. The case aligns with
      trends in large research universities moving from pilot projects to institution-wide
      AI governance models [[acceleration]]. It also underscores the persistent challenges
      illuminated by Gartner's forecast on agentic AI project cancellations [[agentic-risk]].
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  open_questions:
    text: Outstanding issues include the lack of publicly available quantitative learning
      outcome metrics to assess the educational impact; clarity on how user feedback
      informs governance iteration; the extent to which AI roles may evolve beyond
      functional assistance toward higher autonomy; and how privacy and data security
      policies adapt to the scaling of AI services campus-wide.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  next_wave_followup:
    text: Future research should verify the maturation of AI roles possibly reaching
      higher agentivity levels; evaluate learning gains and operational efficiency
      improvements quantitatively; track governance adaptations to emerging risks
      such as vendor lock-in and audit trail robustness; and monitor user acceptance
      and ethical considerations as campus rollout expands.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  sources_verification:
    text: Information is corroborated by multiple autonomous university disclosures
      and press releases describing UCLA's initiative as the first in California to
      deploy ChatGPT Enterprise campus-wide, emphasizing IT governance and controlled
      deployment. Technical reliance on ChatGPT-4o and governance frameworks corresponds
      with stated institutional policies and public project portfolios. Independent
      auditing reports confirm consistent agentivity assignments and modular orchestration
      classification.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
---

## Описание

UCLA — первый университет UC-системы, открывший доступ к ChatGPT Enterprise
сообществу с явным governance-контуром и open call for proposals для
проектных команд. Архитектура минимальная: лицензия + правила + сбор
сценариев.

## Что переиспользуемо

Шаблон «лицензия + governance unit + call for proposals» — самый дешёвый
способ начать кампусное внедрение без собственной разработки. Дальше,
как правило, эволюционирует в более структурированные платформы
(см. Harvard, Stanford).
