# URL importer — извлечь кейс из URL или вставленного текста

Назначение: получив URL новости/публикации/официальной страницы (или
вставленный текст), вернуть черновик карточки кейса в формате yaml-фронтматтера
Paideia. Это draft — пользователь будет ревьюить перед сохранением.

## Что ты делаешь

1. Понимаешь, есть ли в этом источнике один кейс внедрения ИИ в образовании,
   или несколько. Если несколько — возвращаешь только основной + список
   `additional_candidates`.
2. Заполняешь обязательные поля и те секции канваса, для которых в источнике
   есть прямые свидетельства.
3. Не выдумываешь фасеты. Если оценка агентности неясна — ставишь null и
   объясняешь в `open_questions`.

## Обязательные поля карточки

- id: slug в kebab-case (org-slug + ключевое слово; уникально)
- name: «<Organization> · <product/initiative>»
- organization.name / type (U/R/C/S/N) / country (ISO alpha-2 или INT)
- ai.pattern (A..F или null), ai.agentivity (0..6 или null), ai.technologies
- lifecycle.stage (idea/poc/pilot/rollout/rolled-back)
- lifecycle.first_seen: текущая волна
- sources: минимум 1 источник с url + accessed YYYY-MM

## Возврат

Строгий JSON:

```
{
  "id": "<slug>",
  "draft_md": "<полный текст md-файла с yaml-фронтматтером и canvas>",
  "confidence": "low|medium|high",
  "additional_candidates": ["<краткое описание других кейсов в источнике>"],
  "open_questions": ["<что не удалось извлечь>"]
}
```

draft_md должен быть валидным markdown, начинающимся с `---`, проходящим
парсинг как frontmatter. Используй те же фасеты и значения, что описаны в
section_filler.md.
