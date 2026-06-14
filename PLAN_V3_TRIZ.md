# Paideia v3 — TRIZ-engine как ядро

Дата: 2026-06-13.
Заменяет: PLAN_V2.md (P1 «5 ТРИЗ-промптов с yaml» отменяется).

---

## Что я нашёл (анализ донорских материалов)

### В `C:/projects/Claude/TRIZ/` — готовая архитектура, не реализованная в коде

| Файл | Что там |
|---|---|
| `architecture/00_BIG_PICTURE.md` | Inventive Memory Bench как «метастабильное творческое поле» (не чат-бот, не Trello) |
| `architecture/02_CORE_ONTOLOGY.md` | Сущности: Branch, ConstraintEnvelope, AgentAttractor, AgentSpec, Operator, Gate, Space, RuntimeEvent, KOSMOSRun, PromptSource, AgentKernel, IdealImage |
| `architecture/03_AGENT_LEVELS.md` | L0 примитивы / L1 рабочие агенты (9 штук) / L2 пространства (6) / L3 мета-агенты |
| `architecture/04_ORCHESTRATOR_MODEL.md` | Оркестратор-регулятор — observables → decisions, KOSMOS режим, manual co-individuation |
| `architecture/05_AGENT_FOUNDRY.md` | Импорт raw промптов → candidates → AgentSpec → kernel → тесты → activate |
| `architecture/08_SELF_RECONFIGURATION.md` | Правила: что агент может предлагать, что forbidden, review gates |
| `architecture/10_ROADMAP.md` | 10 фаз, текущая Bench v0 на TypeScript+Vite |
| `inventive-memory-bench-mvp/knowledge/11_UI_ONTOLOGY_CONSTITUTION.md` | **Конституция UI FifthConstraint/quint** — нормативная памятка про то, как НЕ делать |
| `inventive-memory-bench-mvp/knowledge/00_PROJECT_INTENT.md` | Product name **FifthConstraint** / **quint**, не чат-бот, не доска идей, а System Workbench |
| `inventive-memory-bench-mvp/knowledge/01-10` | CORE_ONTOLOGY, AGENT_RUN_MODEL, LLM_ACTION_CONTRACT, USER_TYPES, DECISIONS, NEXT_LAYERS, ALIEN_CONCEPT, и т.д. |
| `prompt_sources/agent_specs/`, `kernels/`, `full_prompts/` | **ПУСТЫЕ** — задумано, но не реализовано |

**Ключевое:** L0-L3 модель, KOSMOS, AgentRun, ConstraintEnvelope, EventLog, preview/apply — всё спроектировано детально. **Не доделан Phase 5: LLM Agent Runtime.** Сейчас в MVP — deterministic функции.

### В `C:/projects/Claude/TRIZ/ТРИЗовец/` — 14 PDF-донорских ботов

Это сырьё для Agent Foundry, ещё не разобранное:
- `TRIZ NEW HCORE.pdf` (32 стр)
- `TRIZ MOD ARCH 3.pdf` (16 стр)
- `TRIZ_META_APEX_CORE.txt` (1100 строк — это я прочитал, там агенты G_Contradix, G_Wepol, G_Pivot, G_Assamblix, G_IdealTrace, G_SceneLoop, G_ContradixSentinel, G_PrescanCascadeBreaks, и режимы входа ::Технический/Психотехнический/Гиперинженерный/Игровой/Архитектурный)
- `триз кодекс 2.pdf`, `триз мета оригинал 2.pdf`
- `triz mod game 2.pdf` — игровой вход
- `Quality-of-Mind Operator 2.pdf`, `INDUSTY MAPPER.pdf`, `MODULE GUIDE CORE 41/42.pdf`, `TECH_ENTREPRENEURSHIP_CORE.pdf`
- 5 МТМ-ботов: ProjBot, TECH BOT, meTAPHORBOT, Оркестратор Тело, концепт бот 6
- `бот концептуализатор 14.pdf`

---

## Что меняется в плане

### Что отменяется из PLAN_V2

| Старый P1 (отменяется) | Почему |
|---|---|
| «5 ТРИЗ-промптов как короткие JSON-сценарии» | Подход неправильный. Это method, не agent, не run. |
| «`taxonomy/triz_methods_edu.yaml` с 40 приёмами» | Войдёт, но как `Method/Operator Library`, не как корень |
| «Веполь как одна SVG-визуализация» | Веполь — это онтологическая сцепка системы, должен быть частью EducationalSystemModel |
| «ИКР как итеративный диалог по URL» | IdealImage = поле на EducationalSystemModel, генерируется L1-агентом IdealizeAgent |

### Что остаётся, но переоформляется

| PLAN_V2 | PLAN_V3 |
|---|---|
| 24 «сценария лаборатории» как промпты | становятся **AgentRun profiles** + методы из Method Library |
| Стейкхолдер-обстрел (4 сценария) | становится одним `AgentRun: StakeholderPressure` с L1-агентами-стейкхолдерами |
| Симулятор семестра, what-if, anti-washing | становятся `AgentRun: Simulator` с разными profiles |
| Метакогнитив (slop-минёр, ассумпции, blind-spots) | становятся **L1 Quality Gate + Prompt Adversary** агенты |
| Дикие идеи (time-machine, genealogy, counter-corpus) | становятся `Space` (Counter-Corpus Space) и `AgentRun` profiles |
| Документы РФ (РПД, силлабус, заявка, бизнес-план) | становятся `Export AgentRun profiles` |
| Канвас 18 секций | становится **проекция** на `EducationalSystemModel`, не source of truth |

### Что добавляется фундаментально

1. **`EducationalSystemModel`** — центральная сущность вместо «канваса». Поля: function, working organ, students-as-flow, content-flow, controls, transmission, constraints, contradictions, adjacent systems, DANO (исходная ситуация курса), DOLZHNO (целевой эффект), evolution pressure, mutations, verification.
2. **`PedagogicalConstraintEnvelope`** — preserved (ФГОС-минимум), sacred (то что не нарушать), hidden, violated, suspended, redefined, invention_level (1–5).
3. **L0 Operators** — детерминированные функции на Python: split, mutate, invert, ground, select, classify, cluster, gate, merge, idealize, revive, quarantine.
4. **L1 Agents** — 9 + педагогических расширений:
   - **Pedagogical Reconstructor** (выявить скрытые педассумпции)
   - **Frame Breaker** (нарушить рамку: что если не курс, а игра?)
   - **Pedagogical Contradiction Cutter** (найти триадные противоречия)
   - **Stabilizer** (совместимость с нормативкой / контекстом вуза)
   - **Methodological Grounder** (привязка к реальной аудитории)
   - **Outcome Inverter** (от ожидаемой компетенции → к программе)
   - **Curriculum Chimerizer** (скрестить два кейса/проекта корпуса)
   - **Selector** (triage альтернатив)
   - **Quality Gate** (блокировать преждевременные решения, slop-минёр сюда)
5. **L2 Spaces** — 6 пространств:
   - Pedagogical Engineering Field (по умолчанию)
   - Curriculum Concept Field (поиск формы программы)
   - Educational Game Field (нелинейные форматы)
   - Stakeholder Pressure Field (обстрел)
   - Counter-Corpus Field (стресс-тест провалами)
   - Document Output Field (сборка артефактов)
6. **L3 Meta-Agents** — для Agent Foundry:
   - Prompt Refactor Agent, Prompt Adversary, Integration Agent, Orchestrator Critic, Agent Splitter, Agent Deprecator
7. **Orchestrator** — регулятор метастабильности с observable метриками (количество вариантов, contradiction density, agent activity log, и т.д.) и решениями (activate/deactivate/amplify/suppress/launch KOSMOS/stop).
8. **KOSMOS as AgentRun profile** — не глобальная магическая кнопка. Профиль «авто-сборка 6 альтернатив программы».
9. **AgentRun** — process-контейнер. Все мутации идут через preview → user approval → apply → EventLog → updated ContextPack.
10. **Method/Operator Library** — searchable каталог методов (включая 40 ТРИЗ-приёмов в педагогической интерпретации) с привязкой к агентам.
11. **Agent Foundry** — парсер 14 PDF-донорских ботов → AgentSpec → kernel → активный регистр.

### UI-конституция FifthConstraint применяется к Paideia

- Header: project/session/view; **Run...** кнопка (не «KOSMOS Generate 6»)
- Selected Object Bar: текущий выбранный объект + 3–5 контекстных действий
- Main Workspace: одна из view (System / Machine / Spindle DANO↔DOLZHNO / Card Desk / Trajectory / Narrative / Metrics / Effects / R&D)
- Right Dock: resizable shutter с Inspector / Copilot / Agents / Runs / Debug
- Left Rail: nav / сценарии / Method Library / help (collapsed по умолчанию)
- Action Palette: 3–5 top actions + More
- Card Desk: tabletop mode (опционально), не source of truth

**Главное: текущий 18-секционный канвас остаётся как одна из view (Card Desk), но EducationalSystemModel становится default view после открытия проекта.**

---

## Новый план реализации

### P1-new · TRIZ-engine ядро (~12 дней)

| # | Что | Дней |
|---|---|---|
| P1.1 | `EducationalSystemModel` Pydantic-схема (function / organ / flows / controls / constraints / contradictions / DANO / DOLZHNO) + миграция текущего канваса 18 секций в неё как одна из projections | 2 |
| P1.2 | `PedagogicalConstraintEnvelope` (preserved/sacred/hidden/violated/suspended/redefined + invention_level) | 0.5 |
| P1.3 | L0 операторы (12 функций) как `api/triz/operators.py` | 1 |
| P1.4 | 9 L1 агентов: kernel-промпты + activation conditions + io contract + quality_gates | 3 |
| P1.5 | 6 L2 Spaces — конфиги активных агентов + дефолтных gates | 0.5 |
| P1.6 | Orchestrator-регулятор: observables → decisions (Python class, не LLM) | 1 |
| P1.7 | `AgentRun` + EventLog + preview/apply поток | 1.5 |
| P1.8 | KOSMOS как AgentRun profile (6 стратегий генерации альтернатив программы) | 1 |
| P1.9 | UI Workbench layout: Header/Object Bar/Workspace (System view)/Right Dock/Card Desk | 1.5 |

### P2-new · Agent Foundry (~3 дня) — критично, иначе не накопить агентов

| # | Что | Дней |
|---|---|---|
| P2.1 | Парсер PDF-донорских ботов (extract: candidates, decorative density, executable density, risks) | 1 |
| P2.2 | UI Foundry: review candidates → AgentSpec draft → kernel extraction | 1 |
| P2.3 | Compatibility check + scenario testing + activate workflow | 1 |

### P3-new · 40 ТРИЗ-приёмов в педдизайне + Method Library (~2 дня)

| # | Что | Дней |
|---|---|---|
| P3.1 | `taxonomy/triz_methods_edu.yaml` с 40 приёмами (педагогическая адаптация: дробление → split-курс, динамизация → адаптивная траектория, посредник → AI-роль, и т.д.) | 1 |
| P3.2 | Method Library UI — searchable, grouped, applicability, default agents | 1 |

### P4-new · Стейкхолдер-обстрел как AgentRun + сущность Stakeholders (~3 дня)

| # | Что | Дней |
|---|---|---|
| P4.1 | `content/stakeholders/*.md` каталог (студент, ректор, министр, методист, юрист, и т.д.) | 1 |
| P4.2 | L1-агенты-стейкхолдеры с kernel-промптами и ролями | 1 |
| P4.3 | `AgentRun: StakeholderPressure` — авто-карта → атака от каждого → синтез слабостей | 1 |

### P5-new · Симулятор / What-If / Anti-washing как AgentRun profiles (~3 дня)

| # | Что | Дней |
|---|---|---|
| P5.1 | `AgentRun: SemesterSimulator` с UI таймлайна по неделям | 1 |
| P5.2 | `AgentRun: WhatIfMatrix` с UI матрицы | 1 |
| P5.3 | `AgentRun: AntiAgentWashing` с радар-скорингом по 6 критериям | 1 |

### P6-new · Проектный визард + ролевая модель ТюмГУ + AI-персоны (~3 дня)

| # | Что | Дней |
|---|---|---|
| P6.1 | Типология преподавателей → разные entry routes (Impossible dream / Local contradiction / Existing system evolution / Market backward / Cost optimization / Corpus entry) | 0.5 |
| P6.2 | Wizard `/project/new/wizard` — пошаговое заполнение EducationalSystemModel через вопросы | 1.5 |
| P6.3 | Ролевая модель команды (картограф/организатор/медиатор/хранитель мотивации) как раздел System Model | 0.5 |
| P6.4 | AI-персона как самостоятельная сущность с собственным канвасом (роль, функции, ограничения, точки интеграции) | 0.5 |

### P7-new · Дикие идеи как Space + AgentRun (~3 дня)

| # | Что | Дней |
|---|---|---|
| P7.1 | Time-machine = L1 «Evolution Predictor» на основе 8 эволюционных линий | 1 |
| P7.2 | Genealogy = L0 операторы + граф в БД + UI | 1 |
| P7.3 | Counter-corpus = Space «Counter-Corpus Field» + AgentRun «Failure Pressure» | 0.5 |
| P7.4 | Hypothesis forge = AgentRun «New Hypothesis Crafting» с накоплением свидетельств | 0.5 |

### P8-new · Документы РФ как Export AgentRun (~2 дня)

| # | Что | Дней |
|---|---|---|
| P8.1 | Каталог `taxonomy/fgos_competencies.yaml` (УК/ОПК/ПК коды) | 0.5 |
| P8.2 | `AgentRun: ExportRPD` с привязкой к ФГОС | 0.5 |
| P8.3 | `AgentRun: ExportSyllabus` / `ExportApplication` / `ExportBusinessPlan` | 1 |

### P9-new · Инфраструктура (~2 дня)

| # | Что | Дней |
|---|---|---|
| P9.1 | UI git-история секций + откат через preview/apply | 0.5 |
| P9.2 | Кеши всех LLM-вызовов (по hash promt+context) | 0.5 |
| P9.3 | LLM-аудит с токенами и стоимостью | 0.5 |
| P9.4 | Версии моделей в аудите + reproducible runs | 0.5 |

---

## Сводка

| Блок | Дней | Что даёт |
|---|---|---|
| **P1** TRIZ-engine ядро | 12 | EducationalSystemModel + L0-L3 + Orchestrator + AgentRun + KOSMOS |
| **P2** Agent Foundry | 3 | Импорт 14 PDF-доноров → агенты в регистре |
| **P3** ТРИЗ-приёмы + Method Library | 2 | 40 приёмов педдизайна как методы |
| **P4** Stakeholders | 3 | Стейкхолдер-обстрел как AgentRun |
| **P5** Симулятор/What-If/Anti-washing | 3 | 3 AgentRun profiles |
| **P6** Wizard + роли + AI-персоны | 3 | Пользовательский workflow |
| **P7** Дикие идеи | 3 | 4 фичи |
| **P8** Документы РФ | 2 | 4 export profiles |
| **P9** Инфра | 2 | Производственные качества |
| **Итого до v3** | **~33 дня** | |

### Рекомендуемый порядок

**P1 → P2 → P3 → P6 → P5 → P4 → P7 → P8 → P9**

Объяснение:
- **P1 первый** — без EducationalSystemModel + AgentRun ничего больше не строится правильно
- **P2 сразу за P1** — иначе агентов будет только 9 базовых, не покрывают реальные кейсы (твои PDF — main source)
- **P3** — Method Library нужна для всех остальных AgentRun
- **P6 раньше P4/P5** — без wizard у юзера нет проекта чтобы прогонять обстрел/симулятор
- **P5/P4/P7** в любом порядке (они независимые AgentRun)
- **P8/P9** — последние, прикладные

---

## Что мне нужно от тебя для старта

1. **Принимаешь архитектурный сдвиг?** Да = иду по P1-new. Нет = откатываю на старый P1 «5 промптов + yaml», но это ниже потолок продукта.
2. **Имя продукта**: оставляем «Paideia», или это становится «Paideia/FifthConstraint» (можно совместить — FifthConstraint как название движка, Paideia как образовательная инстанция)? Я бы оставил «Paideia» снаружи и «paideia-engine» внутри.
3. **Старый MVP на TypeScript в `inventive-memory-bench-mvp/`** — переиспользовать UI-компоненты или писать UI с нуля в Jinja2 (как сейчас в Paideia)? Я бы шёл по второму: Jinja2-проще, всё уже в paideia-app, никаких bridge'ей.
4. **14 PDF-доноров** — все парсить через Agent Foundry, или сначала выбрать 3–5 самых релевантных? Я бы шёл по второму: TRIZ NEW HCORE → triz mod game → концептуализатор → meTAPHOR → ProjBot — 5 штук, ~3 дня.
5. **Можно делать в фоне постепенно** или нужен «релиз вместе»? Я бы шёл фичу-за-фичей с auto-deploy после каждой (bootstrap.ps1 уже идемпотентен).

После твоих ответов берусь за P1.1 (`EducationalSystemModel` схема + миграция канваса как одна из projections).
