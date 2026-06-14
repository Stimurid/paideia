-- Paideia SQLite schema.
-- Source of truth — content/*.md с yaml-фронтматтером.
-- Эта БД пересобирается из content/ скриптом scripts/reindex.py.
-- Запросы из API идут только сюда; ничего не пишется напрямую в content/ через API.

PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

-- ---------------------------------------------------------------------------
-- Сущности корпуса
-- ---------------------------------------------------------------------------

-- Кейс — наблюдение организации × сценарий.
CREATE TABLE IF NOT EXISTS cases (
    id              TEXT PRIMARY KEY,           -- slug, например "asu-createai"
    name            TEXT NOT NULL,              -- человекочитаемое имя
    org_name        TEXT NOT NULL,
    org_type        TEXT NOT NULL,              -- U/R/C/S/N (несколько через "/")
    country         TEXT NOT NULL,              -- ISO alpha-2 или INT
    pattern         TEXT,                       -- A..F
    agentivity      INTEGER,                    -- 0..6
    orchestration   TEXT,                       -- LIN/MOD/NET/META/SWARM
    pedagogy        TEXT,                       -- AMP/ROLE/AUTO/INST/SUBJ
    control         TEXT,                       -- HUMAN/COOP/HYBR/MACH
    economy         TEXT,                       -- NONE/BUD/MKT/EXT (через "+")
    transformation_mode TEXT,                   -- см. taxonomy/transformation_modes.yaml
    lifecycle_stage TEXT NOT NULL,              -- idea/poc/pilot/rollout/rolled-back
    first_seen      TEXT NOT NULL,              -- wave id, в которой кейс появился
    verified        INTEGER NOT NULL DEFAULT 0, -- прошёл ли через верификатор (0/1)
    file_path       TEXT NOT NULL,              -- путь от корня репо к .md
    body_md         TEXT NOT NULL,              -- тело карточки (без фронтматтера)
    frontmatter_json TEXT NOT NULL,             -- сырой yaml как json (для отладки/восстановления)
    updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_cases_country     ON cases(country);
CREATE INDEX IF NOT EXISTS idx_cases_pattern     ON cases(pattern);
CREATE INDEX IF NOT EXISTS idx_cases_agentivity  ON cases(agentivity);
CREATE INDEX IF NOT EXISTS idx_cases_stage       ON cases(lifecycle_stage);
CREATE INDEX IF NOT EXISTS idx_cases_org_type    ON cases(org_type);
CREATE INDEX IF NOT EXISTS idx_cases_transform   ON cases(transformation_mode);

-- Проекты — собственные эксперименты пользователей в той же координатной сетке.
-- Те же поля контейнера, что у cases, но agentivity/pattern/lifecycle могут быть NULL
-- на ранних стадиях, есть author/status/portfolio_slot.
CREATE TABLE IF NOT EXISTS projects (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    author          TEXT,
    status          TEXT NOT NULL DEFAULT 'draft',  -- draft/review/approved/in-pilot/archived
    org_name        TEXT,
    org_type        TEXT,
    country         TEXT,
    pattern         TEXT,
    agentivity      INTEGER,
    orchestration   TEXT,
    pedagogy        TEXT,
    control         TEXT,
    economy         TEXT,
    transformation_mode TEXT,
    portfolio_slot  TEXT,
    file_path       TEXT NOT NULL,
    body_md         TEXT NOT NULL,
    frontmatter_json TEXT NOT NULL,
    created_at      TEXT,
    updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_projects_status    ON projects(status);
CREATE INDEX IF NOT EXISTS idx_projects_author    ON projects(author);
CREATE INDEX IF NOT EXISTS idx_projects_portfolio ON projects(portfolio_slot);
CREATE INDEX IF NOT EXISTS idx_projects_pattern   ON projects(pattern);

-- Аналоги проекта в корпусе (project → case).
CREATE TABLE IF NOT EXISTS project_analogues (
    project_id      TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    case_id         TEXT NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    confidence      TEXT NOT NULL DEFAULT 'medium',
    note            TEXT,
    PRIMARY KEY (project_id, case_id)
);

-- Архитектурные типы A–F (Wave 2).
CREATE TABLE IF NOT EXISTS types (
    id              TEXT PRIMARY KEY,           -- A..F
    name            TEXT NOT NULL,
    description     TEXT NOT NULL,
    markers_json    TEXT NOT NULL,              -- ["…","…"]
    file_path       TEXT NOT NULL,
    body_md         TEXT NOT NULL,
    updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Гипотезы фазовых переходов (Wave 3).
CREATE TABLE IF NOT EXISTS hypotheses (
    id              TEXT PRIMARY KEY,           -- H1..H5
    name            TEXT NOT NULL,
    wave_introduced TEXT NOT NULL,
    status_current  TEXT NOT NULL,              -- supported/partially-supported/weakened/refuted/proposed
    status_history_json TEXT NOT NULL,          -- [{wave,status,note}, …]
    markers_json    TEXT NOT NULL,
    file_path       TEXT NOT NULL,
    body_md         TEXT NOT NULL,
    updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Структурные противоречия (7 шт.).
CREATE TABLE IF NOT EXISTS tensions (
    id              TEXT PRIMARY KEY,           -- slug, например "autonomy-vs-control"
    name            TEXT NOT NULL,
    pole_a          TEXT NOT NULL,              -- одна сторона
    pole_b          TEXT NOT NULL,              -- другая сторона
    file_path       TEXT NOT NULL,
    body_md         TEXT NOT NULL,
    updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Стратегические моды (5 шт.).
CREATE TABLE IF NOT EXISTS modes (
    id              TEXT PRIMARY KEY,           -- slug
    name            TEXT NOT NULL,
    description     TEXT NOT NULL,
    file_path       TEXT NOT NULL,
    body_md         TEXT NOT NULL,
    updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Контр-сигналы — независимые наблюдения, опровергающие/ослабляющие гипотезы.
CREATE TABLE IF NOT EXISTS counter_signals (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    org_name        TEXT,                       -- если привязан к организации
    target_hypothesis TEXT,                     -- H1..H5 или NULL
    wave_introduced TEXT NOT NULL,
    file_path       TEXT NOT NULL,
    body_md         TEXT NOT NULL,
    frontmatter_json TEXT NOT NULL,
    updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Волны — снимки корпуса в определённый момент времени.
CREATE TABLE IF NOT EXISTS waves (
    id              TEXT PRIMARY KEY,           -- "wave-1", "diff-2026-06", …
    name            TEXT NOT NULL,
    run_at          TEXT NOT NULL,              -- ISO дата прогона
    description     TEXT,
    file_path       TEXT
);

-- Снапшоты сущностей в момент волны — для дифф-вьюера.
-- Каждая строка фиксирует, как кейс/гипотеза выглядел в этой волне.
CREATE TABLE IF NOT EXISTS wave_snapshots (
    wave_id         TEXT NOT NULL REFERENCES waves(id) ON DELETE CASCADE,
    entity_kind     TEXT NOT NULL,              -- case/hypothesis/type/tension/mode/counter-signal
    entity_id       TEXT NOT NULL,
    snapshot_json   TEXT NOT NULL,              -- фасеты на этот момент
    note            TEXT,
    PRIMARY KEY (wave_id, entity_kind, entity_id)
);

CREATE INDEX IF NOT EXISTS idx_snap_entity ON wave_snapshots(entity_kind, entity_id);

-- Эмпирический граф: связи между кейсом и теоретическими сущностями.
CREATE TABLE IF NOT EXISTS evidence_links (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id         TEXT NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    target_kind     TEXT NOT NULL,              -- type/hypothesis/tension/mode/counter-signal
    target_id       TEXT NOT NULL,
    relation        TEXT NOT NULL,              -- instantiates/supports/contradicts/weakens/illustrates
    confidence      TEXT NOT NULL DEFAULT 'medium', -- low/medium/high
    wave            TEXT,                       -- в какой волне связь зафиксирована
    note            TEXT,
    UNIQUE (case_id, target_kind, target_id, relation)
);

CREATE INDEX IF NOT EXISTS idx_links_case   ON evidence_links(case_id);
CREATE INDEX IF NOT EXISTS idx_links_target ON evidence_links(target_kind, target_id);

-- Источники по кейсам и контр-сигналам.
CREATE TABLE IF NOT EXISTS sources (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_kind      TEXT NOT NULL,              -- case/counter-signal
    owner_id        TEXT NOT NULL,
    url             TEXT,
    source_type     TEXT,                       -- official/press/academic/secondary
    accessed_at     TEXT
);

CREATE INDEX IF NOT EXISTS idx_sources_owner ON sources(owner_kind, owner_id);

-- Универсальная таблица значений по осям из taxonomy/axes.yaml.
-- Заполняется reindex'ом из фронтматтера для cases и projects.
-- value_num — для ordinal/bool (bool кодируется как 0/1).
-- value_text — для categorical/freeform.
-- Одна из двух колонок NOT NULL.
CREATE TABLE IF NOT EXISTS axis_values (
    entity_kind     TEXT NOT NULL,              -- case / project
    entity_id       TEXT NOT NULL,
    axis_id         TEXT NOT NULL,              -- ключ из taxonomy/axes.yaml
    value_num       REAL,
    value_text      TEXT,
    family          TEXT,                       -- ai_engineering / educational_transformation / synthesis
    PRIMARY KEY (entity_kind, entity_id, axis_id),
    CHECK (value_num IS NOT NULL OR value_text IS NOT NULL)
);

CREATE INDEX IF NOT EXISTS idx_axis_by_axis   ON axis_values(axis_id);
CREATE INDEX IF NOT EXISTS idx_axis_by_entity ON axis_values(entity_kind, entity_id);
CREATE INDEX IF NOT EXISTS idx_axis_by_family ON axis_values(family);

-- ---------------------------------------------------------------------------
-- FTS5 — полнотекст по кейсам и теоретическим сущностям.
-- ---------------------------------------------------------------------------

CREATE VIRTUAL TABLE IF NOT EXISTS cases_fts USING fts5(
    case_id UNINDEXED,
    name,
    org_name,
    body,
    tokenize = 'unicode61 remove_diacritics 2'
);

CREATE VIRTUAL TABLE IF NOT EXISTS projects_fts USING fts5(
    project_id UNINDEXED,
    name,
    author UNINDEXED,
    body,
    tokenize = 'unicode61 remove_diacritics 2'
);

CREATE VIRTUAL TABLE IF NOT EXISTS theory_fts USING fts5(
    entity_kind UNINDEXED,
    entity_id UNINDEXED,
    name,
    body,
    tokenize = 'unicode61 remove_diacritics 2'
);

-- ---------------------------------------------------------------------------
-- Векторные таблицы (sqlite-vec). Реальное создание делает scripts/reindex.py
-- после load_extension('vec0'). Тут только указатель в комментарии:
--
--   CREATE VIRTUAL TABLE cases_vec USING vec0(
--       case_id TEXT PRIMARY KEY,
--       embedding FLOAT[1536]
--   );
--   CREATE VIRTUAL TABLE theory_vec USING vec0(
--       entity_kind TEXT,
--       entity_id TEXT,
--       embedding FLOAT[1536]
--   );
-- ---------------------------------------------------------------------------

-- ---------------------------------------------------------------------------
-- Пользователи (минимальная схема под fastapi-users; полная — в alembic-миграции
-- при подключении SQLAlchemy. Здесь оставлена как ориентир.)
-- ---------------------------------------------------------------------------

-- Аудит-лог всех LLM-вызовов. Любой section-filler / wave-runner / url-importer
-- пишет сюда строку до и после вызова. Даёт прозрачность и возможность
-- отката draft-секций к предыдущему состоянию.
CREATE TABLE IF NOT EXISTS llm_runs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    purpose         TEXT NOT NULL,              -- section_filler / url_importer / wave_runner / hypothesis_recheck / match_explain
    model_role      TEXT NOT NULL,              -- fast / deep / search
    target_kind     TEXT,                       -- case / project / hypothesis / wave
    target_id       TEXT,
    section_id      TEXT,                       -- если purpose=section_filler
    input_json      TEXT,                       -- параметры запроса
    output_json     TEXT,                       -- ответ + citations
    citations_json  TEXT,                       -- список URL
    status          TEXT NOT NULL DEFAULT 'ok', -- ok / error
    error           TEXT,
    duration_ms     INTEGER,
    tokens_prompt   INTEGER,                    -- usage.prompt_tokens из ответа OpenAI-compatible
    tokens_completion INTEGER,                  -- usage.completion_tokens
    tokens_total    INTEGER,                    -- usage.total_tokens (если есть)
    provider_name   TEXT,                       -- 302.ai / mai-qwen
    model_name      TEXT,                       -- gpt-4.1-mini / gpt-5 / sonar-pro / qwen2.5-72b
    cached          INTEGER DEFAULT 0,          -- 1 если ответ из llm_cache
    cost_usd        REAL,                       -- расчёт по taxonomy/llm_pricing.yaml
    session_id      TEXT,                       -- F11: подсчёт токенов на сессию
    client_ip       TEXT,                       -- F11: для rate-limit
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_llm_runs_target ON llm_runs(target_kind, target_id);
CREATE INDEX IF NOT EXISTS idx_llm_runs_purpose ON llm_runs(purpose);
CREATE INDEX IF NOT EXISTS idx_llm_runs_session ON llm_runs(session_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_llm_runs_ip ON llm_runs(client_ip, created_at DESC);


-- ============================================================================
-- TRIZ-engine v3 (P1.1+) — EducationalSystemModel, Branch, AgentRun, EventLog
-- См. architecture/04_ORCHESTRATOR_MODEL.md и UI_ONTOLOGY_CONSTITUTION.md
-- из C:/projects/Claude/TRIZ/. Центральная сущность — EducationalSystemModel,
-- 18-секционный канвас остаётся как одна из projections (Card Desk view).
-- ============================================================================

-- EducationalSystemModel
CREATE TABLE IF NOT EXISTS system_models (
    id                  TEXT PRIMARY KEY,
    project_id          TEXT NOT NULL,
    title               TEXT NOT NULL,
    kind                TEXT,
    function            TEXT,
    maturity            TEXT NOT NULL DEFAULT 'seed',
    parent_variant_id   TEXT,
    source              TEXT NOT NULL DEFAULT 'manual',
    invention_level     INTEGER,
    full_json           TEXT NOT NULL,
    created_at          TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at          TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_system_models_project   ON system_models(project_id);
CREATE INDEX IF NOT EXISTS idx_system_models_maturity  ON system_models(maturity);

-- Branch — вариант / мутация SystemModel
CREATE TABLE IF NOT EXISTS branches (
    id                  TEXT PRIMARY KEY,
    project_id          TEXT NOT NULL,
    system_model_id     TEXT NOT NULL,
    parent_id           TEXT,
    title               TEXT NOT NULL,
    current_formulation TEXT,
    maturity            TEXT NOT NULL DEFAULT 'seed',
    cluster             TEXT,
    full_json           TEXT NOT NULL,
    created_at          TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at          TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (system_model_id) REFERENCES system_models(id)
);
CREATE INDEX IF NOT EXISTS idx_branches_project ON branches(project_id);
CREATE INDEX IF NOT EXISTS idx_branches_system  ON branches(system_model_id);
CREATE INDEX IF NOT EXISTS idx_branches_parent  ON branches(parent_id);

-- IdealImage (IFR)
CREATE TABLE IF NOT EXISTS ideal_images (
    id           TEXT PRIMARY KEY,
    branch_id    TEXT NOT NULL,
    formulation  TEXT NOT NULL,
    full_json    TEXT NOT NULL,
    created_at   TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (branch_id) REFERENCES branches(id)
);

-- AgentRun — process container (preview/apply/EventLog)
CREATE TABLE IF NOT EXISTS agent_runs (
    id                    TEXT PRIMARY KEY,
    project_id            TEXT NOT NULL,
    target_object_kind    TEXT NOT NULL,    -- system_model / branch / project / case
    target_object_id      TEXT NOT NULL,
    profile               TEXT NOT NULL,    -- kosmos / stakeholder_pressure / semester_sim / ...
    goal                  TEXT,
    space_id              TEXT,             -- L2 space active
    policy                TEXT,             -- preview-required / auto-apply / hybrid
    budget_json           TEXT,             -- {tokens, max_steps, time_limit_s}
    status                TEXT NOT NULL DEFAULT 'pending',
                                             -- pending/running/awaiting_approval/applied/failed/cancelled
    stop_criteria         TEXT,
    artifacts_json        TEXT,             -- hypotheses, mutations, reports
    trace_json            TEXT,             -- timeline шагов
    created_at            TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at            TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_agent_runs_project ON agent_runs(project_id);
CREATE INDEX IF NOT EXISTS idx_agent_runs_status  ON agent_runs(status);
CREATE INDEX IF NOT EXISTS idx_agent_runs_profile ON agent_runs(profile);

-- EventLog — append-only лог всех мутаций (контракт preview/apply)
CREATE TABLE IF NOT EXISTS triz_events (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_run_id    TEXT,
    actor_kind      TEXT NOT NULL,         -- user / agent / orchestrator / kosmos
    actor_id        TEXT,
    event_type      TEXT NOT NULL,         -- propose / preview / approve / apply / reject / mutate
    target_kind     TEXT NOT NULL,         -- system_model / branch / agent / space
    target_id       TEXT NOT NULL,
    operator_id     TEXT,                  -- L0 если применён
    payload_json    TEXT,
    result_json     TEXT,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_triz_events_run    ON triz_events(agent_run_id);
CREATE INDEX IF NOT EXISTS idx_triz_events_target ON triz_events(target_kind, target_id);

-- AgentSpec — регистр L1/L3 агентов (заполняется Agent Foundry)
CREATE TABLE IF NOT EXISTS agent_specs (
    agent_id                  TEXT PRIMARY KEY,
    name                      TEXT NOT NULL,
    level                     TEXT NOT NULL,   -- L0 / L1 / L2 / L3
    class                     TEXT,            -- working / meta / orchestrator
    purpose                   TEXT,
    field_function            TEXT,
    activation_conditions_json TEXT,
    inputs_json               TEXT,
    outputs_json              TEXT,
    allowed_actions_json      TEXT,
    forbidden_actions_json    TEXT,
    conflicts_with_json       TEXT,
    cooperates_with_json      TEXT,
    quality_gates_json        TEXT,
    kernel_prompt             TEXT,
    full_prompt_path          TEXT,
    tools_needed_json         TEXT,
    test_cases_json           TEXT,
    version                   TEXT NOT NULL DEFAULT '1.0.0',
    provenance                TEXT,
    status                    TEXT NOT NULL DEFAULT 'draft',
                                              -- draft / active / deprecated / needs_review
    created_at                TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at                TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_agent_specs_level  ON agent_specs(level);
CREATE INDEX IF NOT EXISTS idx_agent_specs_status ON agent_specs(status);

-- L1-агенты из content/agents/L1/ — индексированные для UI-списков и фильтров
CREATE TABLE IF NOT EXISTS content_agents (
    agent_id      TEXT PRIMARY KEY,
    name          TEXT NOT NULL,
    level         TEXT NOT NULL DEFAULT 'L1',
    purpose       TEXT,
    status        TEXT NOT NULL DEFAULT 'draft',
    cooperates_with_json TEXT,
    conflicts_with_json  TEXT,
    file_path     TEXT NOT NULL,
    body_md       TEXT NOT NULL,
    frontmatter_json TEXT NOT NULL,
    updated_at    TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_content_agents_status ON content_agents(status);
CREATE INDEX IF NOT EXISTS idx_content_agents_level  ON content_agents(level);

-- Стейкхолдеры из content/stakeholders/
CREATE TABLE IF NOT EXISTS stakeholders (
    stakeholder_id TEXT PRIMARY KEY,
    name          TEXT NOT NULL,
    kind          TEXT,                          -- internal/regulatory/external/...
    group_name    TEXT,                          -- students/administration/compliance/...
    attack_style  TEXT,
    typical_questions_json TEXT,
    interests_json  TEXT,
    fears_json      TEXT,
    levers_json     TEXT,
    file_path     TEXT NOT NULL,
    body_md       TEXT NOT NULL,
    frontmatter_json TEXT NOT NULL,
    updated_at    TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_stakeholders_kind  ON stakeholders(kind);
CREATE INDEX IF NOT EXISTS idx_stakeholders_group ON stakeholders(group_name);


-- ============================================================================
-- Library v1 — пользовательская библиотека (книги, статьи, концепты)
-- См. UI_REDESIGN_PLAN.md: 1000 страниц учебников должны не лежать пылью в
-- RAG, а быть первоклассными сущностями с summary + concepts + hierarchical
-- retrieval.
-- ============================================================================

CREATE TABLE IF NOT EXISTS library_books (
    id              TEXT PRIMARY KEY,            -- slug
    title           TEXT NOT NULL,
    authors         TEXT,                        -- "Дьюи; Эльконин" — через ";"
    year            INTEGER,
    source_kind     TEXT,                        -- pdf/docx/pptx/md/txt/epub/url
    source_path     TEXT,                        -- путь к оригиналу в content/library/<id>/
    source_url      TEXT,                        -- если из URL
    summary         TEXT,                        -- LLM-сгенерированное summary, 2-4 абзаца
    topics_json     TEXT,                        -- список тегов/тем
    page_count      INTEGER,
    chunk_count     INTEGER DEFAULT 0,
    concept_count   INTEGER DEFAULT 0,
    status          TEXT NOT NULL DEFAULT 'uploading',
                                                 -- uploading / text_extracted / chunks_embedded
                                                 -- summary_ready / concepts_ready / ready / failed
    error           TEXT,
    uploaded_at     TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_library_books_status ON library_books(status);
CREATE INDEX IF NOT EXISTS idx_library_books_year   ON library_books(year);

CREATE TABLE IF NOT EXISTS library_sections (
    id              TEXT PRIMARY KEY,
    book_id         TEXT NOT NULL,
    section_num     INTEGER,                     -- порядковый номер
    title           TEXT,                        -- если выделен заголовок
    char_start      INTEGER,                     -- offset в книге
    char_end        INTEGER,
    summary         TEXT,                        -- LLM-сгенерированное краткое
    chunk_count     INTEGER DEFAULT 0,
    FOREIGN KEY (book_id) REFERENCES library_books(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_library_sections_book ON library_sections(book_id);

CREATE TABLE IF NOT EXISTS library_concepts (
    id              TEXT PRIMARY KEY,
    book_id         TEXT NOT NULL,
    section_id      TEXT,                        -- может быть NULL если general для книги
    name            TEXT NOT NULL,               -- название концепта
    definition      TEXT,                        -- определение/раскрытие
    quote           TEXT,                        -- ключевая цитата (если есть)
    page_hint       INTEGER,                     -- примерный номер страницы
    links_json      TEXT,                        -- [{kind: type|hypothesis|tension|mode|case, id, relation}]
    importance      INTEGER DEFAULT 3,           -- 1-5
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (book_id) REFERENCES library_books(id) ON DELETE CASCADE,
    FOREIGN KEY (section_id) REFERENCES library_sections(id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_library_concepts_book ON library_concepts(book_id);
CREATE INDEX IF NOT EXISTS idx_library_concepts_name ON library_concepts(name);

CREATE TABLE IF NOT EXISTS library_chunks (
    id              TEXT PRIMARY KEY,
    book_id         TEXT NOT NULL,
    section_id      TEXT,                        -- к какой секции относится
    chunk_num       INTEGER,
    char_start      INTEGER,
    char_end        INTEGER,
    text            TEXT NOT NULL,
    FOREIGN KEY (book_id) REFERENCES library_books(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_library_chunks_book    ON library_chunks(book_id);
CREATE INDEX IF NOT EXISTS idx_library_chunks_section ON library_chunks(section_id);


CREATE TABLE IF NOT EXISTS users (
    id              TEXT PRIMARY KEY,
    email           TEXT NOT NULL UNIQUE,
    hashed_password TEXT NOT NULL,
    is_active       INTEGER NOT NULL DEFAULT 1,
    is_superuser    INTEGER NOT NULL DEFAULT 0,
    is_verified     INTEGER NOT NULL DEFAULT 0,
    role            TEXT NOT NULL DEFAULT 'editor',
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ============================================================
-- F9-F12: sessions, rate limits, supporters, courses (scaffold)
-- ============================================================

-- Анонимные сессии для подсчёта токенов/стоимости в навбаре.
CREATE TABLE IF NOT EXISTS user_sessions (
    id              TEXT PRIMARY KEY,
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    last_seen_at    TEXT NOT NULL DEFAULT (datetime('now')),
    role            TEXT,                              -- F9: teacher/methodologist/admin/student
    course_id       TEXT,                              -- F3: активный курс
    is_supporter    INTEGER NOT NULL DEFAULT 0        -- F12: задонатил → no rate limit
);
CREATE INDEX IF NOT EXISTS idx_user_sessions_seen ON user_sessions(last_seen_at DESC);

-- F12: журнал пожертвований (заполняется вручную или через webhook).
CREATE TABLE IF NOT EXISTS supporters (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id      TEXT,
    nickname        TEXT,
    amount_rub      REAL,
    amount_usd      REAL,
    channel         TEXT,                              -- yoomoney/tinkoff/boosty/patreon/manual
    note            TEXT,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

-- F3 scaffold: Course = курс как первоклассная сущность.
CREATE TABLE IF NOT EXISTS courses (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    description     TEXT,
    period_start    TEXT,                              -- ISO date
    period_end      TEXT,
    authors         TEXT,
    target_audience TEXT,
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS course_events (
    id              TEXT PRIMARY KEY,
    course_id       TEXT NOT NULL,
    kind            TEXT NOT NULL,                     -- lecture/seminar/homework_release/homework_submission/chat_burst/reading/exam/reflection
    title           TEXT,
    happened_at     TEXT,                              -- timestamp
    duration_min    INTEGER,
    artifact_path   TEXT,                              -- путь к транскрипту/слайдам
    body_md         TEXT,                              -- текст / расшифровка
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_course_events_time ON course_events(course_id, happened_at);

-- Артефакты события курса: два пакета (author / student) с разными типами.
CREATE TABLE IF NOT EXISTS course_event_artifacts (
    id              TEXT PRIMARY KEY,
    event_id        TEXT NOT NULL,
    package         TEXT NOT NULL,                     -- author / student / course_meta
    kind            TEXT NOT NULL,                     -- slides/transcript/reading/homework_brief/homework_submission/chat_export/student_question/notes
    title           TEXT,
    body_md         TEXT,
    file_path       TEXT,                              -- если файл
    author_nickname TEXT,                              -- для student-package
    author_session_id TEXT,                            -- для трекинга кто загрузил
    in_response_to  TEXT,                              -- FK на homework_release artifact (для цепочки д/з)
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (event_id) REFERENCES course_events(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_event_artifacts ON course_event_artifacts(event_id, package, kind);
CREATE INDEX IF NOT EXISTS idx_event_artifacts_response ON course_event_artifacts(in_response_to);

-- Структурные сообщения чата (для kind=chat_burst события)
CREATE TABLE IF NOT EXISTS course_chat_messages (
    id              TEXT PRIMARY KEY,
    event_id        TEXT NOT NULL,
    speaker         TEXT,                              -- ник/имя
    role_at_time    TEXT,                              -- lecturer/student/ta/...
    content         TEXT NOT NULL,
    sent_at         TEXT,                              -- timestamp в чате
    sequence        INTEGER NOT NULL,                  -- порядок в треде
    FOREIGN KEY (event_id) REFERENCES course_events(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_chat_msgs ON course_chat_messages(event_id, sequence);

-- G3 · Litops-извлечения из артефакта события (транскрипта/чата/домашки).
CREATE TABLE IF NOT EXISTS litops_extracts (
    id              TEXT PRIMARY KEY,
    event_id        TEXT NOT NULL,
    kind            TEXT NOT NULL,                     -- question / model / difficulty / open_loop / insight
    content         TEXT NOT NULL,                     -- сам текст экстракта
    speaker         TEXT,                              -- "аудитория"/"лектор"/имя/null
    quote           TEXT,                              -- цитата-якорь
    position_hint   TEXT,                              -- "начало"/"середина"/"конец"/timestamp
    related_concepts_json TEXT,                        -- [{name, book_id}] — ссылки на library_concepts
    confidence      INTEGER DEFAULT 3,                 -- 1-5
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (event_id) REFERENCES course_events(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_litops_event ON litops_extracts(event_id, kind);

-- F1 · Конфликты концептов библиотеки (для consistent-selector в RAG).
CREATE TABLE IF NOT EXISTS concept_conflicts (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    concept_a_id    TEXT NOT NULL,
    concept_b_id    TEXT NOT NULL,
    relation        TEXT NOT NULL,                     -- conflicts / complements / equivalent / unrelated
    similarity      REAL,                              -- embedding cosine similarity
    rationale       TEXT,                              -- LLM-объяснение в 1-2 предложения
    school_a        TEXT,                              -- ярлык школы/позиции А
    school_b        TEXT,
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(concept_a_id, concept_b_id)
);
CREATE INDEX IF NOT EXISTS idx_concept_conflicts_a ON concept_conflicts(concept_a_id);
CREATE INDEX IF NOT EXISTS idx_concept_conflicts_b ON concept_conflicts(concept_b_id);
CREATE INDEX IF NOT EXISTS idx_concept_conflicts_rel ON concept_conflicts(relation);

CREATE TABLE IF NOT EXISTS course_role_bindings (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id       TEXT NOT NULL,
    session_id      TEXT NOT NULL,
    role            TEXT NOT NULL,                     -- author/lecturer/seminarist/student/ta/observer
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    UNIQUE(course_id, session_id, role)
);

-- Feedback acceptor: пользовательские соображения / критика / идеи.
CREATE TABLE IF NOT EXISTS feedback_threads (
    id              TEXT PRIMARY KEY,
    session_id      TEXT,
    user_role       TEXT,
    page_path       TEXT,                              -- откуда пришло
    page_context    TEXT,                              -- title/h1 страницы для контекста
    status          TEXT NOT NULL DEFAULT 'open',      -- open / clarifying / saved / dismissed
    category        TEXT,                              -- идея / критика / баг / похвала / вопрос / прочее
    severity        TEXT,                              -- low / medium / high / blocker
    summary         TEXT,                              -- LLM-сводка одной фразой
    tags_json       TEXT,                              -- ["ui","library","concierge",...]
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_feedback_status ON feedback_threads(status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_feedback_session ON feedback_threads(session_id, created_at DESC);

CREATE TABLE IF NOT EXISTS feedback_messages (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    thread_id       TEXT NOT NULL,
    sender          TEXT NOT NULL,                     -- user / llm
    content         TEXT NOT NULL,
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (thread_id) REFERENCES feedback_threads(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_feedback_messages ON feedback_messages(thread_id, id);

-- Discuss-агент: дискуссия с агентом по проекту / курсу с QMO-слайдерами.
CREATE TABLE IF NOT EXISTS discuss_sessions (
    id              TEXT PRIMARY KEY,
    session_id      TEXT,                              -- cookie session
    project_id      TEXT,                              -- если в проекте
    course_id       TEXT,                              -- если в курсе
    title           TEXT,                              -- автогенерация из первого вопроса
    config_json     TEXT NOT NULL,                     -- QMO-настройки + goal + critique_level
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_discuss_session ON discuss_sessions(session_id, updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_discuss_project ON discuss_sessions(project_id);
CREATE INDEX IF NOT EXISTS idx_discuss_course ON discuss_sessions(course_id);

CREATE TABLE IF NOT EXISTS discuss_messages (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    discuss_id      TEXT NOT NULL,
    sender          TEXT NOT NULL,                     -- user / kaiyona / system
    content         TEXT NOT NULL,
    config_snapshot TEXT,                              -- какая конфигурация QMO была активна
    duration_ms     INTEGER,
    tokens          INTEGER,
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (discuss_id) REFERENCES discuss_sessions(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_discuss_msgs ON discuss_messages(discuss_id, id);

CREATE TABLE IF NOT EXISTS discuss_presets (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    description     TEXT,
    config_json     TEXT NOT NULL,
    is_builtin      INTEGER NOT NULL DEFAULT 0,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ============================================================
-- vec0 virtual tables (sqlite-vec). Расширение загружается в open_db().
-- ============================================================

CREATE VIRTUAL TABLE IF NOT EXISTS library_vec USING vec0(
    chunk_id TEXT PRIMARY KEY,
    embedding FLOAT[1536]
);
