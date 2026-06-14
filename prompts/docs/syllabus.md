# Сборщик силлабуса

Из канваса проекта — силлабус по неделям, ориентированный на студента.

```json
{
  "course_title": "...",
  "instructor": "...",
  "term": "осень 2026|весна 2027|...",
  "course_overview": "<2-3 абзаца>",
  "learning_objectives": ["<glagol-formula 'студент сможет X'>"],
  "weekly_schedule": [
    {
      "week": 1,
      "theme": "...",
      "before_class": ["<что прочитать/сделать>"],
      "in_class": ["<активности>"],
      "after_class": ["<задание>"],
      "ai_use_guidelines": "<что разрешено/обязательно/запрещено на этой неделе>",
      "deliverables": ["<что сдать>"]
    }
  ],
  "grading": [{"component": "...", "weight_pct": N, "rubric_summary": "..."}],
  "policies": {
    "ai_use": "...",
    "academic_integrity": "...",
    "attendance": "...",
    "late_work": "...",
    "accessibility": "..."
  },
  "support_resources": ["..."]
}
```
