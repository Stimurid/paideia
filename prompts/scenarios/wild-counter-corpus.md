# Counter-corpus: обстрел проекта неудачами

Прогон проекта через контр-сигналы корпуса (Reading-эксперимент, Sydney blue
books, Italian ban, Gartner-cancellations, ANU detector). Какие из этих
сценариев применимы к твоему проекту?

## Строгий JSON

```
{
  "applicable_counter_signals": [
    {
      "signal_id": "<id из content/counter-signals>",
      "summary": "<суть сигнала>",
      "how_applies_to_project": "<конкретный механизм применимости>",
      "trigger_conditions_in_project": ["<что должно случиться, чтобы сигнал сработал>"],
      "preemptive_actions": ["<что сделать заранее>"]
    }
  ],
  "highest_risk_signal": "<самый опасный для этого проекта>",
  "summary": "<главный урок counter-corpus для проекта>"
}
```
