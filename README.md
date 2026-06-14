# Paideia

Живой исследовательский корпус «ИИ в образовании»: ~150 кейсов, архитектурные типы A–F,
гипотезы фазовых переходов H1–H5, структурные противоречия, стратегические моды,
контр-сигналы — связаны как граф эмпирики.

Главный рабочий цикл: прогон новой волны + дифф с предыдущей.

## Stack

- FastAPI + SQLite (FTS5 + sqlite-vec)
- Next.js + Tailwind (фронт)
- LLM: 302.ai primary, MAI Qwen fallback (OpenAI-совместимые)
- `content/*.md` с yaml-фронтматтером — source of truth (git)
- `db/paideia.db` — runtime-индекс, пересобирается из content

## Layout

```
content/         # SoT
  cases/         # кейсы
  types/         # архитектурные типы A–F (Wave 2)
  hypotheses/    # фазовые переходы H1–H5 (Wave 3)
  tensions/      # 7 структурных противоречий
  modes/         # 5 стратегических мод
  counter-signals/
  waves/         # снапшоты волн
taxonomy/        # справочники фасетов (yaml)
prompts/         # extractor, matcher, verifier, wave_runner
api/             # FastAPI
scripts/         # ingest, reindex, wave_diff
db/              # schema.sql + paideia.db
web/             # Next.js
raw/             # junction → C:\projects\Paideia (сырые волны)
tests/
```

## Setup (dev)

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install jinja2 python-multipart sqlite-vec fastapi uvicorn python-frontmatter pydantic-settings openai typer pytest pyyaml
copy .env.example .env
# (опц.) заполнить LLM_PRIMARY_API_KEY / LLM_FALLBACK_API_KEY — для Фазы 3+
python -m scripts.cli init        # проверка скаффолда и БД
python -m scripts.reindex         # content/*.md -> SQLite
pytest                            # 142 теста по фронтматтеру
python -m uvicorn api.main:app --reload --port 8000
```

Открыть в браузере:
- http://localhost:8000/ — каталог с фасетами
- http://localhost:8000/case/asu-createai — карточка кейса
- http://localhost:8000/hypothesis/H1 — гипотеза + поддерживающие/опровергающие кейсы
- http://localhost:8000/type/B — архитектурный тип B
- http://localhost:8000/map — карта корпуса (любая пара осей)
- http://localhost:8000/match — подбор аналогов под параметры

JSON-API:
- `/api/search?q=tutor&country=US&pattern=B&agentivity_min=3`
- `/api/case/{id}`, `/api/hypothesis/{id}`, `/api/projection?x=axis&y=axis`
- `POST /api/match` `{axes: {...}}`

## Obsidian

Папка `content/` — готовый Obsidian vault. Открой её как vault — фронтматтер
будет распознан как properties, `[[id]]`-ссылки в теле — как граф.

См. план в `C:\Users\Timur Shchukin\.claude\plans\hidden-floating-starlight.md`.
