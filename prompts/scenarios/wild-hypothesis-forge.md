# Кузница новой гипотезы H6

Пользователь хочет сформулировать собственную гипотезу о ИИ в образовании,
выросшую из его проекта. Помоги её отковать: уточни формулировку, найди
supports/contradicts в корпусе, предложи условия фальсификации.

## Строгий JSON

```
{
  "proposed_hypothesis": {
    "id": "H6",
    "name": "<рабочее имя>",
    "thesis": "<2-3 предложения формулировки>",
    "scope": "<границы применимости>",
    "falsification_conditions": ["<когда гипотеза опровергается>"]
  },
  "supports_in_corpus": [{"case_id": "...", "how_supports": "..."}],
  "contradicts_in_corpus": [{"case_id": "...", "how_contradicts": "..."}],
  "relation_to_existing_hypotheses": [{"existing_id": "H1|H2...", "relation": "extends|narrows|opposes|orthogonal", "how": "..."}],
  "ready_for_corpus": true|false,
  "improvements_needed": ["<что доработать до публикации>"]
}
```
