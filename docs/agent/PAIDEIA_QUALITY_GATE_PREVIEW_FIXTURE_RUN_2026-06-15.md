# PAIDEIA_QUALITY_GATE_PREVIEW_FIXTURE_RUN_2026-06-15

Status: `preview_only_real_fixture_run`

This pass runs real offline Paideia fixtures through ORGAN-007 in advisory preview mode.

No runtime auto-blocking was enabled.
No prompts were rewritten.
No live LLM/API provider was called.
No raw corpus, database, upload, export artifact, deployed VM, or production state was mutated.

## Selected Fixtures

| Fixture ID | Scene Family | Source Files | Why It Is Representative |
|---|---|---|---|
| `demo_electives_synthesis_stub` | `project-synthesis` | `content/projects/demo-electives.md` | Minimal project stub that tempts synthesis overreach. |
| `seminar_cards_anti_washing` | `anti_washing` | `content/projects/example-seminar-cards.md` | Real project with bounded agentivity claim, audit hints, and explicit AI roles. |
| `seminar_cards_stakeholder_attack_rector` | `stakeholder_attack` | `content/projects/example-seminar-cards.md`, `content/stakeholders/rector.md` | Real project plus an actual high-leverage stakeholder pressure surface. |
| `seminar_cards_export_rpd_gap` | `export_rpd` | `content/projects/example-seminar-cards.md`, `content/stakeholders/fgos-expert.md`, `prompts/docs/rpd.md` | Real project tested against export-grade methodist expectations. |
| `seminar_cards_rough_valid_control` | `rough_valid_control` | `content/projects/example-seminar-cards.md` | Control case: rough draft that is still operational and should not be blocked. |

## Preview Results

| Fixture ID | Scene Family | Input Summary | Expected Concern | Preview-Only Recommendation | Severity | Action | Evidence Phrase | False-Positive Risk | Mutation |
|---|---|---|---|---|---|---|---|---|---|
| `demo_electives_synthesis_stub` | `project-synthesis` | Minimal project stub with signature context and a one-line intent only. | thin project stub should not be promoted into synthesis narrative | Do not synthesize beyond stub level; request missing problem, mechanism, risks, and evaluation fields first. | `high` | `request_revision` | Only signature context and one-line intent are present; operational project sections are missing. | `low` | `none` |
| `seminar_cards_anti_washing` | `anti_washing` | Richer seminar project with bounded agentivity, logs, prompt versioning, and explicit AI roles. | bounded agentivity claim still needs stronger outcome evidence | Keep the agentivity claim modest and add stronger outcome evidence before any stronger branding. | `low` | `advise` | The project already declares low agentivity and keeps audit hints, but outcome evidence is still thin. | `medium` | `none` |
| `seminar_cards_stakeholder_attack_rector` | `stakeholder_attack` | Seminar project reviewed against rector-level pressure around budget, brand, strategy, and accountability. | strategic, budget, and accountability answers are only partial | Escalate to human review before positioning this as an institution-level initiative. | `medium` | `escalate_review` | Methodical approval is mentioned, but budget, institutional strategy, and named accountability remain only partial. | `medium` | `none` |
| `seminar_cards_export_rpd_gap` | `export_rpd` | Seminar project checked against RPD/FGOS export expectations and the methodist pressure surface. | export readiness is weaker than the narrative suggests | Keep export in preview-only mode until competency mapping, learning outcomes, and responsibility are explicit. | `medium` | `request_revision` | The project names institutional intent, but the project draft does not yet expose an explicit competency map or export-grade responsibility chain. | `low` | `none` |
| `seminar_cards_rough_valid_control` | `rough_valid_control` | Rough but operational seminar draft with problem, hypothesis, roles, metrics, and explicit risks. | rough draft should receive advice without being blocked | Allow the draft to proceed with advice; do not block a living draft that already names risks and evidence targets. | `low` | `allow` | The draft is incomplete, but it is operational: problem, hypothesis, roles, metrics, and risks are visible. | `high` | `none` |

## Where Quality Gate Helped

- It stopped synthesis inflation on a stub project that does not yet justify a field-level narrative.
- It kept the anti-washing pass honest by rewarding bounded claims instead of demanding fake maturity.
- It exposed a real rector-level governance gap: strategic and accountability framing is weaker than the local project draft suggests.
- It showed that export-readiness should stay preview-only until competency and responsibility surfaces become explicit.

## Where It Overreached Or Could Overreach

- The rough-valid control confirms the main danger: Quality Gate can become a premature blocker if it treats productive draftness as slop.
- Stakeholder pressure can easily push the gate toward institutional theater if it mistakes missing bureaucracy for missing pedagogical substance.

## False-Positive Control

Result: the rough but valid seminar draft should not be blocked.

The gate should advise, not punish, when a draft already shows:

- explicit problem statement;
- explicit hypothesis;
- named roles;
- some evidence target;
- visible risks.

## Activation Readiness

Recommendation: `ALLOW_PREVIEW_ONLY_FOR_SELECTED_SCENES`

Safe first preview-only scene families:

- `anti_washing`
- `project-synthesis`

Conditionally safe with human review:

- `stakeholder_attack`
- `export_rpd`

Unsafe to treat as hard blocking:

- any scene where a rough but operational draft could be mistaken for slop

## Boundary Statement

This fixture run does not prove hard enforcement.
It proves bounded usefulness of ORGAN-007 in preview-only advisory mode over real Paideia fixtures.

Explicitly: no runtime auto-blocking was enabled, and mutation = none for every fixture.
