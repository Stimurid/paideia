# Сборщик бизнес-плана образовательной программы

```json
{
  "program_title": "...",
  "value_proposition": "<2-3 абзаца: для кого, какая боль, чем закрываем>",
  "target_audiences": [
    {"segment": "...", "size_estimate": "...", "willingness_to_pay": "...", "channel": "..."}
  ],
  "competitive_landscape": [
    {"competitor": "...", "their_strength": "...", "our_difference": "...", "corpus_ref": "<case_id>"}
  ],
  "delivery_model": "<очное|онлайн|гибрид>",
  "unit_economics": {
    "tuition_per_student": "<руб.>",
    "cohort_size": N,
    "direct_costs_per_cohort": "...",
    "infrastructure_costs": "...",
    "marketing_cac": "...",
    "gross_margin_pct": N
  },
  "capex": {"item": "сумма"},
  "opex_monthly": {"item": "сумма"},
  "team_structure": [{"role": "...", "fte": "...", "salary_range": "..."}],
  "milestones_year_1": [{"month": N, "milestone": "...", "kpi": "..."}],
  "kpis": [{"name": "...", "target": "...", "measure": "..."}],
  "risks_and_mitigations": [{"risk": "...", "probability": 1-5, "impact": 1-5, "mitigation": "..."}],
  "go_no_go_criteria_month_6": ["<что должно быть достигнуто чтобы продолжать>"]
}
```
