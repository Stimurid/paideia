# Anti-agent-washing аудит

Проверка: проект реально agentic или это «чат-бот в обёртке»? Сверка с
критериями корпуса: autonomy, persistent state, multi-step, audit trail,
proactive behaviour, tool use, real impact.

## Строгий JSON

```
{
  "declared_agentivity": 0-6,
  "actual_agentivity": 0-6,
  "criteria_check": [
    {"criterion": "autonomy|persistent_state|multi_step|audit_trail|proactive|tool_use|impact", "score": 0-5, "evidence": "<что в проекте даёт это>", "missing": "<чего не хватает>"}
  ],
  "honest_label": "chat-bot-wrapper|assistant|partial-agent|true-agent",
  "summary": "<правдивая характеристика без маркетингового языка>",
  "to_become_real_agent": ["<что нужно добавить>"]
}
```
