# Hard Enforcement Probe Harness

Status: `runnable_static_policy_harness`

This is the first Paideia hard-layer step after context probes.

It does not install hooks, permissions, runtime blockers, or `.claude/settings.json`. It provides a non-destructive runnable policy harness that checks whether risky intents are routed to block/review/bounded actions before any file mutation.

## Enforcement Level

Before this pass:

- docs-only / agent-instruction level;
- context probes recorded;
- no runnable guard harness.

After this pass:

- agent-instruction level remains;
- runnable static policy harness exists;
- no hard runtime enforcement yet.

Classification: `agent_instruction_level_with_runnable_static_probe_harness`.

## Covered Intents

| Intent | Route ID | Required route | Forbidden paths |
|---|---|---|
| prompt rewrite attempt | `block_prompt_mass_rewrite` | block mass rewrite / require prompt-family review | `prompts/**`, `prompts/scenarios/**`, `content/agents/**` |
| secret exposure | `block_secret_exposure` | block secret read/print / topology only | `.env`, `.env.*`, deploy secrets |
| Quinta contamination | `block_project_ontology_replacement` | block replacement / genealogy mapping only | `api/**`, `prompts/**`, `content/**` |
| AgentRun auto-apply | `block_preview_apply_bypass` | block auto-apply / preserve preview-apply | `api/triz/**`, `db/schema.sql` |
| Kairon flattening | `block_kairon_ontology_flattening` | block ontology flattening / design review | `api/**`, `prompts/**`, `templates/**` |
| deploy overreach | `block_deploy_overreach` | block deploy / deploy checklist only | `deploy/**`, VM state, systemd/Caddy |
| raw overread | `bound_raw_corpus_read` | bound corpus read / require source selection and budget | `raw/**`, `content/**` |
| memory/corpus authority | `route_memory_to_recovery_context_check` | route to recovery/context check / require trace | `raw/**`, `db/llm_cache/**`, logs, cached output |

## Runnable Evidence

Run:

`python -m pytest tests/test_agent_hard_enforcement_docs.py -q`

The test is intentionally static and non-destructive. It does not call live APIs, read `.env`, mutate runtime, or scan raw corpus.

## What This Proves

- The protected layer has a concrete policy map.
- Known risky prompts are classified into block/review/bounded routes.
- Forbidden surfaces are named and test-covered.
- The project now has a small repeatable check for agent-layer regressions.

## What This Does Not Prove

- No runtime action is forcibly blocked.
- No Claude/Codex permission engine is installed.
- No live adversarial route trace exists.
- No secret scanner is active.
- No deployment guard is installed.

## Next Hard Layer

To move from `partial/context-proven` toward stronger `behaves` evidence, Paideia needs one of:

- `.claude/settings.json` permissions and/or hooks after design review;
- a project-local preflight command that agents must run before risky edits;
- live no-op probes showing actual refusal/routing in an agent session;
- a protected-path diff gate in CI or pre-commit equivalent.
