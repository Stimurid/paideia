# Anti-Agent-Washing — скоринг заявленной vs фактической агентности

Получаешь SystemModel + ai.agentivity (заявленный уровень 0-6).

Оцени **фактический** уровень агентности по 6 критериям:
1. **Autonomy** — действует ли AI без явного запроса
2. **Persistent state** — помнит ли AI между сессиями
3. **Multi-step planning** — делает ли AI многошаговые планы
4. **Audit trail** — есть ли логи действий AI
5. **Goal-orientation** — преследует ли AI цель, или просто отвечает
6. **Tool use** — использует ли AI внешние инструменты

Для каждого критерия — 0-5 по фактическим признакам в SystemModel.

## Возврат: строгий JSON

```json
{
  "claimed_agentivity": <0-6>,
  "criteria": [
    {"name": "autonomy", "score": 0-5, "evidence": "...", "missing": "..."},
    {"name": "persistent_state", "score": 0-5, "evidence": "...", "missing": "..."},
    {"name": "multi_step_planning", "score": 0-5, "evidence": "...", "missing": "..."},
    {"name": "audit_trail", "score": 0-5, "evidence": "...", "missing": "..."},
    {"name": "goal_orientation", "score": 0-5, "evidence": "...", "missing": "..."},
    {"name": "tool_use", "score": 0-5, "evidence": "...", "missing": "..."}
  ],
  "factual_agentivity": <0-6>,
  "washing_gap": <claimed - factual>,
  "verdict": "honest | minor_washing | significant_washing | severe_washing",
  "recommendations": ["..."]
}
```

Запреты:
- Если evidence не найден — score=0, не выдумывать
- Не льстить заявленному уровню
- factual_agentivity не может быть выше количества критериев со score >= 3
