# Counter-Corpus — обстрел провалами корпуса

Получаешь SystemModel и список counter-signals корпуса (Reading
infiltration, Sydney assessment reform, Italian ChatGPT ban, Gartner 40%
cancellations, ANU detector off, blue books backlash).

Для каждого counter-signal оцени:
- **может ли наш проект провалиться по тому же сценарию**
- **что общего** между нашим проектом и провалившимся кейсом
- **что у нас лучше** (если что-то лучше)
- **что у нас хуже** (если что-то хуже)
- **митигация** конкретно для нашего случая

## Возврат

```json
{
  "applicable_counter_signals": [
    {
      "counter_signal_id": "...",
      "applicability": "high | medium | low | not_applicable",
      "shared_traits": ["..."],
      "we_are_better_in": ["..."],
      "we_are_worse_in": ["..."],
      "mitigation": "<конкретное действие>",
      "probability_of_repeat": 1-5
    }
  ],
  "highest_risk_signal": "...",
  "overall_fragility": 1-5
}
```
