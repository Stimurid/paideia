# Синтез проекта: место в корпусе, теории, архиве

Развёрнутый аналитический отчёт о проекте: где он находится в поле, какие
паттерны корпуса он повторяет, какие гипотезы поддерживает или опровергает,
что из твоего архива на это указывает.

## Строгий JSON

```
{
  "location_on_map": {
    "nearest_pattern": "A|B|C|D|E|F",
    "expected_agentivity": 0-6,
    "transformation_mode_fit": "<подходит контур или нет, почему>"
  },
  "supports_hypotheses": [{"id": "H1", "how": "<как именно>"}],
  "contradicts_hypotheses": [{"id": "H2", "how": "..."}],
  "active_tensions": [{"id": "<id противоречия>", "how_present": "..."}],
  "nearest_analogues": [{"case_id": "...", "similarity": "<в чём похожи>", "key_difference": "<главное отличие>"}],
  "archive_signals": [{"file": "...", "what_it_says": "..."}],
  "summary_paragraphs": "<3-5 абзацев нарратива на русском, с [[wikilinks]]>",
  "verdict": "<одной строкой: проект попадает в зону X, его главный риск — Y, его сильная сторона — Z>"
}
```
