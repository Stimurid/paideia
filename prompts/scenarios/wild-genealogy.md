# Генеалогия кейса: родители и дети

Для выбранного кейса корпуса — его «родители» (какие практики дали ему вырасти)
и «дети» (какие новые практики выросли из него).

## Строгий JSON

```
{
  "case_id": "...",
  "parents": [
    {"id": "<case_id или внешняя практика>", "what_gave": "<что унаследовано>", "year_approx": ...}
  ],
  "children": [
    {"id": "<case_id>", "what_inherited": "<что взяли>", "transformed_into": "<во что превратили>"}
  ],
  "siblings": [{"id": "...", "common_root": "..."}],
  "evolutionary_position": "early-adopter|stabilizer|mutator|dead-end|crystallization",
  "summary": "<генеалогическая характеристика>"
}
```
