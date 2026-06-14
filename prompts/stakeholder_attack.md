# Stakeholder Attack — обстрел проекта от лица стейкхолдера

Получаешь:
- SystemModel проекта
- описание stakeholder (имя, kind, interests, fears, levers, attack_style)
- typical_questions из его каталога

Войди в позицию стейкхолдера и задай ему **5 самых неприятных вопросов
к проекту** + предложи ответы (если они есть) с пометкой выдерживает /
не выдерживает.

## Возврат: строгий JSON

```json
{
  "stakeholder_id": "...",
  "stakeholder_name": "...",
  "questions": [
    {
      "question": "<неприятный вопрос>",
      "kind_of_attack": "interest_threat | fear_amplification | lever_pull | tradition_breach",
      "intensity": 1-5,
      "current_answer_in_project": "<что проект может ответить — из SystemModel — или null>",
      "verdict": "withstands | partially | fails",
      "what_to_fix": "<что добавить в проект чтобы выдержать>"
    }
  ],
  "overall_resilience": 1-5,
  "weak_spots": ["..."]
}
```

Запреты:
- Не сглаживать вопросы («может быть стоит рассмотреть...»). Конкретные
  атаки в стиле стейкхолдера.
- Не отвечать дипломатично — отвечать **из проекта**. Если проект не
  отвечает — fails.
- Не более 5 вопросов — это spam.
