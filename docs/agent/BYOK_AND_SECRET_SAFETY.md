# BYOK And Secret Safety

BYOK is Paideia runtime behavior. It is not Agentum payload.

## Rules

- Do not commit real API keys.
- Do not read or print `.env` values.
- Do not log full keys.
- Do not render full keys back to the browser.
- Do not paste secrets into prompts, reports, tests, screenshots, or issue text.
- Test keys must be placeholders.
- Deploy secrets are no-touch unless the task is an explicit deploy/secret-rotation pass.

## Safe Discussion

Allowed:

- variable names;
- config topology;
- placeholder examples;
- masked display behavior;
- risk notes.

Forbidden:

- actual key values;
- full tokens;
- private provider credentials;
- production secret dumps.

## Blocker Rule

Any suspected secret exposure is a blocker.

Stop, report the path/output where exposure may have occurred, and do not continue until the key is rotated or the human owner clears the risk.
