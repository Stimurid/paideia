# Secret And Provider Topology

Agentum did not read or print Paideia secret values.

Known surfaces by name only:

- `.env` and `.env.*` are secret/no-touch paths;
- `.env.example` documents provider variable names;
- BYOK/settings exists as Paideia runtime feature;
- `api/config.py` maps runtime config;
- `api/llm.py` provides fast/deep/search/embed methods;
- `taxonomy/llm_pricing.yaml` records pricing posture.

Rules:

- never paste secret values into prompts, docs, logs, or reports;
- do not switch providers during guard install;
- do not call live LLM APIs during verification unless explicitly requested;
- provider or BYOK behavior changes require a separate reviewed runtime pass.
