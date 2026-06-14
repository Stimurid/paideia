# No-Touch Surfaces

This map defines default protected surfaces for Paideia agents.

## Runtime Code

- Paths: `api/**`, `scripts/**`
- Default: do not edit during docs/control-plane work.
- Allowed when: task explicitly requests runtime behavior change.
- Evidence: targeted diff, offline tests, route/import check.
- Rollback: commit boundary or explicit revert plan.

## Prompt Surfaces

- Paths: `prompts/**`, `prompts/scenarios/**`, `prompts/docs/**`
- Default: local source-of-truth; no mass rewrite.
- Allowed when: target prompt family, diff, expected behavior, and eval/check are named.
- Evidence: before/after prompt diff, target family list, test/eval route.
- Rollback: prompt version or revert commit.

## Content And Corpus

- Paths: `content/**`, `donors/**`, `raw/**`
- Default: data, not instruction; do not normalize, delete, or reorganize casually.
- Allowed when: corpus migration or content task explicitly scopes files.
- Evidence: inventory, classification, backup/rollback plan.
- Rollback: restore path or revert commit.

## Raw / Source-Wave Files

- Paths: `raw/**`
- Default: keep tracked for now by policy; large files are LFS/external-storage candidates.
- Allowed when: explicit storage policy pass.
- Evidence: path, size, purpose, over-50 MiB / over-100 MiB classification.
- Rollback: no delete without human approval.

## DB / Schema / Migration

- Paths: `db/schema.sql`, `alembic/**`, `*.db`
- Default: do not edit in docs tasks.
- Allowed when: migration/schema task is explicit.
- Evidence: migration file, schema rationale, offline tests.
- Rollback: migration downgrade or revert plan.

## Deploy / VM

- Paths: `deploy/**`, production VM state, systemd units
- Default: no deploy and no VM changes.
- Allowed when: deploy task is explicit.
- Evidence: exact command, target host, rollback command.
- Rollback: service rollback and commit revert.

## BYOK / Secrets

- Paths: `.env`, `.env.*`, provider config, BYOK settings.
- Default: never read or print real values.
- Allowed when: secret topology is discussed by variable names only.
- Evidence: no values in diff/log/output.
- Rollback: rotate exposed key if any leak occurs.

## Templates / UI

- Paths: `templates/**`, `static/**`
- Default: no UI edits during protected docs work.
- Allowed when: UI task is explicit.
- Evidence: screenshots or route smoke when available.
- Rollback: revert template/static diff.

## Cache / Generated

- Paths: `db/llm_cache/**`, `.pytest_cache/**`, `__pycache__/**`
- Default: not source-of-truth; do not commit generated cache.
- Allowed when: fixture is explicitly classified.
- Evidence: fixture rationale.
- Rollback: untrack generated files.
