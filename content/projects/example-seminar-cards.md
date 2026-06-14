---
id: example-seminar-cards
name: AI-конструктор карточек для семинара по педагогическим текстам
kind: project
author: example-author
status: draft
organization:
  name: ТюмГУ · SAS
  type: U
  country: RU
scenario:
  level:
  - undergraduate
  domains:
  - pedagogy
  - humanities
  context: seminar-augmentation
facets:
  orchestration: MOD
  pedagogy: ROLE
  control: HUMAN
  economy: BUD
ai:
  pattern: B
  agentivity: 2
  technologies:
  - gpt-4o
  role: card-assembler + critic
roles:
  human:
  - семинарист
  - картограф предметной области
  - медиатор
  machine:
  - сборщик карточек
  - критик
  - генератор контр-аргументов
  interaction_scenario: 'Семинарист готовит набор педагогических текстов, AI собирает
    по ним

    карточки концептов и контр-аргументов; на семинаре студенты

    взаимодействуют с карточками через медиатора.

    '
traces:
  logs: true
  prompts_versioned: true
  data_sources:
  - course-readings
  - syllabus
risks:
  goal_substitution: 'Риск, что студенты будут спорить с AI-карточками, а не с самими
    текстами.

    '
  lowered_bar: 'Если carды слишком готовые — снижение требований к самостоятельному

    прочтению первоисточников.

    '
  weak_audit_trail: null
transformation_mode: experimental-cell
axes:
  agentivity: 2
  ai_pattern: B
  orchestration: MOD
  control_locus: HUMAN
  rag_grounded: true
  has_persistent_state: false
  audit_trail_strength: 4
  domain_specificity: 4
  evaluation_evidence_strength: 1
  interaction_form: persona-roleplay
  pedagogy_transformation: ROLE
  transformation_mode: experimental-cell
  scale_of_change: 2
  institutional_depth: 2
  radicalness: 3
  reversible: true
  governance_strength: 2
  portability: 4
  reflexivity: 4
  human_role_complexity: 4
  data_sensitivity: 2
  cost_intensity: 1
  lms_integration: false
  has_metrics: false
  risk_of_goal_substitution: 3
  risk_of_lowered_bar: 3
analogues:
- asu-createai
radical_version:
  summary: 'Каждая карточка превращается в персону-агента, ведущего сократический

    диалог по своему фрагменту; студент проходит «совет советников».

    '
  axes:
    agentivity: 3
    interaction_form: multi-agent-simulation
    radicalness: 4
    human_role_complexity: 5
  notes: 'Требует адаптации канваса под persona-roleplay и явный логирующий контур.

    '
portfolio_slot: tyumgu-experimental-cell
links:
- kind: type
  id: B
  relation: instantiates
  confidence: medium
- kind: hypothesis
  id: H2
  relation: supports
  confidence: low
created_at: '2026-06-12'
updated_at: '2026-06-12'
canvas:
  signature_context:
    text: Электив 'Семинар-карточки для метакогнитивной рефлексии'. Магистратура по
      педагогике, 8 недель, 24 студента. ИТМО, 2026-фall.
    status: draft
    source: manual
    updated_at: '2026-06-13'
  problem_situation:
    text: Студенты-магистранты в педагогике освоили теорию (Дьюи, Выготский, Дэвидов),
      но не умеют переносить её в собственную практику. Курсы превращаются в пересказ
      источников без операционального применения.
    status: draft
    source: manual
    updated_at: '2026-06-13'
  effect_hypothesis:
    text: Если ввести 18-секционный канвас как обязательную форму описания собственного
      учебного эксперимента, и заставить студентов прогонять свой замысел через систему
      контр-вопросов от 5 разных стейкхолдеров — то они начнут отличать декларации
      от операций.
    status: draft
    source: manual
    updated_at: '2026-06-13'
  ai_architecture:
    text: AI-агенты квалифицируют каждую секцию канваса (Pedagogical Reconstructor,
      Quality Gate), стейкхолдер-обстрел — отдельный модуль. Базовая LLM — gpt-4.1-mini,
      для глубокой работы — gpt-5.
    status: draft
    source: manual
    updated_at: '2026-06-13'
  team_roles:
    text: '- Преподаватель-картограф (1 чел): структура курса, методология

      - AI-медиатор: surface ассумпций, slop-минёр

      - AI-критик от лица стейкхолдеров: 7 типажей из каталога'
    status: draft
    source: manual
    updated_at: '2026-06-13'
  ai_role:
    text: AI как Quality Gate — блокирует продвижение секции канваса если есть мины
      (общие фразы без операции, моральное сглаживание, ложные мосты). AI как стейкхолдер
      — атакует от 5 разных позиций.
    status: draft
    source: manual
    updated_at: '2026-06-13'
  interaction_scenario:
    text: 'Неделя 1: студенты формулируют замысел. Неделя 2: заполняют канвас. Неделя
      3: AI-критик от 3 стейкхолдеров атакует. Неделя 4: переработка. Недели 5-6:
      проектная сессия. Неделя 7: защита. Неделя 8: рефлексия.'
    status: draft
    source: manual
    updated_at: '2026-06-13'
  institutional_loop:
    text: Согласовано с методическим управлением. РПД оформлен как 'спецсеминар' (4
      з.е.). Использование AI задекларировано в политике курса. Сданные канвасы хранятся
      в LMS Moodle.
    status: draft
    source: manual
    updated_at: '2026-06-13'
  metrics_evidence:
    text: 'Заявлено: студент способен различить декларативную фразу от операциональной
      (slop-test). Метрика: на pre-test 30% корректных различений; цель — 75% на post-test.'
    status: draft
    source: manual
    updated_at: '2026-06-13'
  risks:
    text: 1. Студенты-гуманитарии могут отвергнуть формализованную форму канваса как
      'технократическую'. 2. AI-критик может оказаться слишком жёстким, парализовать
      инициативу. 3. Зависимость от gpt-API (риск отключения).
    status: draft
    source: manual
    updated_at: '2026-06-13'
  transferability:
    text: 'Паттерн (канвас + стейкхолдер-обстрел) переносим в любую программу где
      студенты проектируют собственные эксперименты: PhD-программы, MBA, IDEO-style
      design schools.'
    status: draft
    source: manual
    updated_at: '2026-06-13'
  theory_links:
    text: Поддерживает [[H2-assistant-to-autonomy]]. Иллюстрирует тип [[C-pedagogy-shaped-dialogue]].
      Применяет приёмы [[01-segmentation]] (разделение работы на роли) и [[24-intermediary]]
      (AI как медиатор).
    status: draft
    source: manual
    updated_at: '2026-06-13'
---

## Проблема

В семинаре по педагогическим текстам у студентов слабо развивается навык
критики и сопоставления авторских позиций — обсуждение часто скатывается
в пересказ.

## Гипотеза эффекта

Если AI-собранные карточки концептов и контр-аргументов будут на столе как
«третий собеседник», студенты быстрее научатся занимать позицию по
отношению к авторскому тезису.

## Минимальная версия (для критики на семинарской доработке)

- Семинарист загружает 3–5 текстов недели.
- AI собирает 10–15 карточек: концепт / тезис / контр-аргумент / ссылка
  на фрагмент.
- На семинаре: 30 минут на обсуждение карточек, 30 минут — на работу с
  текстами напрямую, 30 минут — на рефлексию.

## Радикальная версия

См. блок `radical_version` во фронтматтере: персона-агенты по каждой
карточке + совет советников.

## Открытые вопросы

- Как избежать подмены чтения первоисточников взаимодействием с
  карточками? (см. risks.goal_substitution)
- Нужен ли явный лог взаимодействия с AI, чтобы преподаватель видел, на
  каких карточках студент «застрял»?
