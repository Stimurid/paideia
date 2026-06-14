# Paideia Agent Commands

These are docs-level command families. They are not executable shell commands unless implemented later.

## preflight

Identify branch, status, working surface, target files, risk level, allowed tests, and rollback.

## inspect-llm-calls

Map LLM call families, provider roles, prompt sources, cost risk, and trace surfaces without calling live APIs.

## inspect-prompts

Inventory prompt families and proposed overlay points without rewriting prompt bodies.

## inspect-triz

Map AgentRun, scenario, Foundry, system-model, Kairon/Kaiyona, and L1-agent boundaries.

## inspect-kairon

Inspect Kairon routes/prompts/docs as local publication/article-model layer. No rewrite by default.

## inspect-secrets-topology

List secret variable names and config paths without reading or printing secret values.

## safe-docs-change

Docs-only change. Must not touch runtime, prompts, templates, deploy, raw, schema, or `.env`.

## protected-runtime-change-request

Runtime change proposal requiring plan, files, expected behavior, tests, rollback, and explicit human approval before edit.
