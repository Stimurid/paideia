---
id: utah-chatgpt-edu
name: University of Utah · ChatGPT Edu (managed)
organization:
  name: University of Utah
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
  context: campus-platform
facets:
  orchestration: MOD
  pedagogy: INST
  control: HYBR
  economy: BUD+EXT
ai:
  pattern: A
  agentivity: 2
  technologies:
  - gpt-4o
  role: managed campus ChatGPT Edu
transformation_mode: rectoral-initiative
axes:
  agentivity: 2
  ai_pattern: A
  orchestration: MOD
  control_locus: HYBR
  interaction_form: governed-portal
  provider_lock_in: 5
  scale_of_change: 3
  institutional_depth: 4
  governance_strength: 4
  audit_trail_strength: 4
  has_metrics: true
  cost_intensity: 4
lifecycle:
  stage: rollout
  first_seen: wave-2
  history:
  - wave: wave-2
    stage: rollout
    note: SSO + сервис-каталог + обучение + usage-аналитика
links:
- kind: type
  id: A
  relation: instantiates
  confidence: high
- kind: type
  id: D
  relation: instantiates
  confidence: medium
- kind: hypothesis
  id: H1
  relation: supports
  confidence: high
sources:
- url: https://www.utah.edu/
  type: official
  accessed: 2026-02
verified: true
canvas:
  signature_context:
    text: 'University of Utah — managed ChatGPT Edu с SSO, сервис-каталогом, обучением

      и анализом usage-данных для долгосрочной модели сервиса. Тип

      [[A-governed-access]] + начатки [[D-governance-training-ecosystem]].'
    status: draft
    source: imported
    updated_at: '2026-06-12'
  ontology_status:
    text: University of Utah's ChatGPT Edu is a managed campus-level deployment following
      pattern A, where AI assumes a functional assistant role with agentivity level
      2/6. It is positioned as an institutional platform integrated into the existing
      educational governance and infrastructure, exemplifying a prototype-to-policy
      transition stage rather than an experimental pilot or mere simulation. This
      aligns with observed replication patterns in U.S. universities where AI services
      are centrally managed with explicit governance and controlled access, without
      autonomous full-cycle learning management.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  problem_situation:
    text: Before AI integration, educational workflows at University of Utah relied
      heavily on manual instructional design and limited scalability in providing
      personalized or context-aware support to students at scale across diverse faculties.
      Traditional LMS and educational resources did not facilitate interactive AI-powered
      dialogue or adaptive tutoring specific to course content. Furthermore, universities
      faced challenges in centrally managing AI usage while maintaining privacy, compliance,
      and equitable access, which without AI tools remained labor- and resource-intensive.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  effect_hypothesis:
    text: The deployment of ChatGPT Edu by University of Utah promises to enhance
      instructional support by providing an integrated, managed AI assistant embedded
      within the campus infrastructure. Expected effects include increased efficiency
      in content generation, student engagement through interactive tutoring aligned
      with syllabus materials, and a stable, secure environment for AI use governed
      by university policies. The AI's role is to functionally assist educators and
      students without full autonomy, supporting institutional orchestration with
      moderate agentivity (2/6).
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  ai_architecture:
    text: The architecture leverages GPT-4o model technology, deployed as a managed
      campus ChatGPT Edu service. The system provides centralized access controlled
      via university governance layers, ensuring compliance with data privacy and
      security norms. It integrates functional AI assistants embedded in LMS platforms,
      facilitating course-specific dialogue and tutoring. This architecture follows
      the MOD facet of orchestration, combining managed infrastructure and hybrid
      control between institutional oversight and user roles. Persistent state and
      RAG (Retrieval-Augmented Generation) features are not explicitly detailed but
      inferred through context-specific tutoring and syllabus integration.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  team_roles:
    text: Roles are distributed among campus IT administration, faculty as course
      content designers and AI role creators, and students as end-users interacting
      with AI tutors. The IT unit manages governance, security, and infrastructure
      orchestration, while faculty configure AI functionalities aligned with pedagogical
      goals. Human orchestration ensures that AI remains an assistive tool rather
      than autonomous decision-maker, consistent with agentivity 2/6. The team structure
      reflects a hybrid model blending pedagogy-driven design and infrastructure-led
      governance.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  ai_role:
    text: AI functions primarily as a managed campus assistant embedded into educational
      workflows, enabling Socratic dialogic tutoring and contextual help based on
      course materials. The AI does not assume autonomous management of learning cycles
      but rather supports instructional activities with fixed constraints, fitting
      agentivity level 2/6. This managed AI assistant role emphasizes functionality
      over autonomy, aiding faculty and students in knowledge exploration and task
      completion within institutional guardrails.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  interaction_scenario:
    text: Educational interactions proceed with faculty designing AI tutors integrated
      into courses via the LMS interface. Students engage directly with these AI tutors,
      which provide answers, generate ideas, and support learning through Socratic
      questioning grounded in course syllabi and materials. All AI interactions are
      managed via institutional infrastructure, ensuring controlled, secure access.
      This stepwise scenario moves from course design incorporating AI roles, through
      student-AI interactive sessions, to institutional monitoring and iterative platform
      enhancement.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  institutional_loop:
    text: The University of Utah implements governance frameworks to manage AI deployment,
      including policies for data privacy, access control, usage monitoring, and compliance
      with educational standards. Institutional loops involve faculty committees,
      IT governance units, and administrative oversight collaborating to maintain
      safe, ethical, and pedagogically sound AI use. These governance mechanisms ensure
      hybrid control, balancing innovation with risk management and consistent with
      campus-wide managed access patterns.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  transit_to_life:
    text: The ChatGPT Edu deployment transitioned from pilot phases involving select
      courses and faculties to a wider institutional rollout, expanding access campus-wide
      with iterative improvements to integration and governance. Adjustments included
      scaling infrastructure to support the entire student body and refining AI tutor
      functionalities to better align with diverse curricula. University communications
      highlighted milestones such as pilot start dates and expanding user base, mirroring
      the typical Wave 1–4 evolution from pilot to institutional embedding.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  metrics_evidence:
    text: While explicit learning gains or educational outcome metrics are not publicly
      released, operational metrics include campus-wide availability, number of users
      accessing ChatGPT Edu, and volume of interactions logged within the LMS integration.
      Consistent with similar US university deployments, these usage data reflect
      initial adoption scale and infrastructural stability rather than direct measurement
      of knowledge improvement or skill acquisition.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  risks:
    text: Key risks include goal substitution where AI assistance might encourage
      surface-level learning or dependency rather than deep understanding, potential
      lowered bar for academic integrity, and vendor lock-in concerns due to reliance
      on ChatGPT-4o proprietary models. Further, audit trails might be weak if institutional
      monitoring pipelines are immature, raising challenges for accountability. These
      risks align with known pitfalls highlighted in Gartner's forecast of agentic
      AI projects and broader educational AI governance critiques.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  countersignals:
    text: Contrary to promises of AI fully autonomously remaking educational processes
      (agentivity 4+), the University of Utah model exemplifies a cautious, hybrid
      approach with controlled AI functionality at agentivity 2/6. The practice emphasizes
      managed access and human orchestration over autonomous multi-agent systems,
      signaling a countertrend to narratives of agentic AI deployment ramping rapidly.
      This careful institutional stance serves as a calibrating counter-signal to
      overly ambitious AI-inflected educational transformations.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  transferability:
    text: The managed campus ChatGPT Edu pattern with moderate agentivity and hybrid
      control is transferable to other large universities seeking to centralize AI
      services within governed infrastructure. It is especially relevant for institutions
      prioritizing institutional risk management, privacy, and pedagogical integration
      over experimental autonomous AI learning systems. Similar US and international
      research universities with digital infrastructures and compliance requirements
      can replicate this approach with appropriate local adaptations.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  theory_links:
    text: The University of Utah case reflects pattern A of AI functional integration
      and agentivity level 2/6 as characterized in the Prompt 4 taxonomy. It illustrates
      the MOD facet of orchestration balancing managed infrastructure and pedagogical
      control (INST). The hybrid control (HYBR) model reconciles autonomy and governance
      tensions seen across educational AI cases. The scaling from pilot to campus-wide
      service resonates with [[acceleration]] and [[autonomy-vs-control]] trade-offs,
      while governance frameworks link to [[A-governed-access]] theory nodes.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  open_questions:
    text: Open questions remain regarding the detailed pedagogical impacts on learning
      gains and skill acquisition, which are not yet publicly quantified for this
      case. Further inquiry is needed into how ongoing governance adapts to evolving
      AI capabilities, and whether increasing agentivity levels might be introduced
      in future iterations. The extent to which student and faculty experiences shape
      iterative AI role evolution also requires longitudinal study.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  next_wave_followup:
    text: Future evaluation cycles should verify actual usage statistics against educational
      outcomes to validate initial promises. They should also track governance effectiveness
      and risk mitigation in practice, and monitor potential agentivity escalation
      or expansion of AI functions beyond the current scope. Rechecking the sustainability
      of institutional orchestration amid emerging multi-agent AI trends will be crucial.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  sources_verification:
    text: Primary sources confirming the deployment include institutional releases,
      campus announcements, and related case documentation in Waves 1–4 compilations.
      Cross-referencing with similar US university cases (e.g., UCLA, Duke, University
      of Michigan) validates the identified architecture and governance patterns.
      However, educational outcome measurements are not publicly auditable at present,
      and reliance on vendor-supplied GPT-4o models warrants ongoing scrutiny for
      data privacy compliance.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
---

## Описание

University of Utah — managed ChatGPT Edu с SSO, сервис-каталогом, обучением
и анализом usage-данных для долгосрочной модели сервиса. Тип
[[A-governed-access]] + начатки [[D-governance-training-ecosystem]].
