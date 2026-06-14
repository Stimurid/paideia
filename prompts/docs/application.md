# Сборщик заявки (грант / Минобрнауки / фонд)

Из канваса проекта — заявка на финансирование инициативы по образованию с AI.

```json
{
  "title": "...",
  "applicant": "<организация-заявитель>",
  "summary": "<200-300 слов аннотация>",
  "problem_statement": "<обоснование актуальности с цифрами и ссылками на корпус>",
  "objectives": ["..."],
  "expected_results": ["<измеримые результаты>"],
  "methodology": "<3-5 абзацев: что и как делаем>",
  "analogous_practices": [{"case_id": "...", "what_we_take": "...", "what_we_change": "..."}],
  "team": [{"role": "...", "name_placeholder": "...", "competency_required": "..."}],
  "timeline": [{"stage": "...", "months": "M-N", "deliverable": "..."}],
  "budget_summary": {
    "personnel": "<сумма>",
    "infrastructure": "...",
    "events": "...",
    "other": "...",
    "total": "..."
  },
  "risks": [{"risk": "...", "mitigation": "..."}],
  "sustainability_plan": "<что после окончания финансирования>",
  "evaluation_metrics": ["<как будем мерить>"]
}
```
