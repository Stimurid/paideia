---
id: graphmasal
name: GraphMASAL · graph-based multi-agent adaptive learning
organization:
  name: GraphMASAL research group
  type: R
  country: INT
scenario:
  level:
  - adult-learner
  domains:
  - general
  context: research-prototype
facets:
  orchestration: NET
  pedagogy: AUTO
  control: HYBR
  economy: NONE
ai:
  pattern: B
  agentivity: 3
  technologies:
  - langgraph
  - neural-ir
  role: Diagnostician + Planner + Tutor on dynamic knowledge graph
transformation_mode: greenfield
axes:
  agentivity: 3
  ai_pattern: B
  orchestration: NET
  control_locus: HYBR
  interaction_form: knowledge-graph-tutor
  audit_trail_strength: 4
  evaluation_evidence_strength: 3
  has_persistent_state: true
  rag_grounded: true
lifecycle:
  stage: poc
  first_seen: diff-2026-06
  history:
  - wave: diff-2026-06
    stage: poc
    note: 'Diagnostician/Planner/Tutor по dynamic knowledge graph; metrics: structural
      alignment, coverage, lower cost'
links:
- kind: type
  id: B
  relation: instantiates
  confidence: high
- kind: hypothesis
  id: H2
  relation: supports
  confidence: high
- kind: hypothesis
  id: H3
  relation: supports
  confidence: medium
sources:
- url: https://arxiv.org/
  type: academic
  accessed: 2026-06
verified: false
canvas:
  signature_context:
    text: 'GraphMASAL — multi-agent система с явным разделением Diagnostician /

      Planner / Tutor поверх dynamic knowledge graph и optimization-based

      planning. Метрики ориентированы на инженерную верификацию оркестрации

      (structural alignment, coverage of weak concepts, lower learning cost),

      а не на маркетинговый engagement. Поддерживает [[H2-assistant-to-autonomy]]

      и [[H3-text-to-agentic-environment]].'
    status: draft
    source: imported
    updated_at: '2026-06-12'
  ontology_status:
    text: GraphMASAL представлен как исследовательский прототип, а не зрелое промышленное
      внедрение. Система находится на стадии разработки и апробации концепции multi-agent
      adaptive learning с уровнем агентности 3/6, отражающим распределённые роли агентов
      и persistent learner modeling, но без реального classroom deployment. Это соответствует
      стадии прототипа, демонстрирующего потенциал архитектуры для будущих приложений.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  problem_situation:
    text: До применения GraphMASAL педагогический процесс не был структурирован как
      граф состояний с динамическим планированием маршрутов обучения. Отсутствовала
      чёткая сегментация педагогических функций на диагностику, планирование обучения
      и интерактивное обучение, что снижало эффективность персонализации и адаптивности.
      Также не было надёжных методов когнитивной диагностики и оптимального построения
      траекторий обучения на основе реального состояния знаний студента.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  effect_hypothesis:
    text: GraphMASAL обещает повысить качество адаптивного обучения за счёт разделения
      педагогических ролей на Diagnostician, Planner и Tutor, координируемых через
      dynamic knowledge graph и нейронный информационный поиск (neural IR). Система
      направлена на улучшение structural/sequence alignment, coverage of weak concepts,
      снижение стоимости обучения и повышение точности когнитивной диагностики, что
      ведёт к более эффективной и персонализированной образовательной траектории.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  ai_architecture:
    text: 'Архитектура GraphMASAL построена на основе dynamic knowledge graph, используемого
      для представления и обработки учебного материала и знаний студента. Оркестрация
      агентов реализуется с помощью LangGraph, которая управляет тремя ключевыми агентами:
      Diagnostician (когнитивная диагностика), Planner (планирование персонализированных
      траекторий обучения) и Tutor (обучающее взаимодействие). В архитектуру также
      интегрирован neural IR для релевантного извлечения информации. Уровень агентности
      оценивается на 3/6, что отражает наличие распределённых ролей и persistent learner
      modeling. В настоящий момент это исследовательский прототип без развертывания
      в живом классе.'
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  team_roles:
    text: В исходных материалах нет конкретных данных о составе и ролях команды разработчиков
      или педагогов, работающих с системой GraphMASAL, поэтому эта секция остается
      неполной.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  ai_role:
    text: AI в GraphMASAL функционирует как Diagnostician, который анализирует текущее
      состояние знаний студента; Planner, который формирует оптимальные образовательные
      маршруты на базе диагностических данных; и Tutor, который непосредственно взаимодействует
      с учащимся, помогая усваивать материал и корректировать ошибки. Таким образом,
      AI выполняет диагностическую, планировочную и обучающую функции и обеспечивает
      адаптивность обучения через динамическое управление знаниями и задачами.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  interaction_scenario:
    text: 'Динамика взаимодействия строится вокруг цикла: Diagnostician проводит когнитивную
      диагностику текущих знаний студента, передаёт результаты Planner, который генерирует
      индивидуальный learning path, затем Tutor реализует обучающие сессии по заданному
      маршруту. Весь процесс базируется на обновляющемся dynamic knowledge graph,
      что позволяет адаптировать планы в зависимости от прогресса учащегося. Такая
      оркестрация поддерживает постоянный feedback loop между агентами и учащимся
      для максимально эффективного персонализированного обучения.'
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  institutional_loop:
    text: Информация о governance, нормативных актах или политике данных для GraphMASAL
      отсутствует, поскольку система пока не внедрена в институциональную среду и
      находится на стадии прототипа. Вопросы регулирования и этики использования AI
      в данном кейсе не раскрыты.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  transit_to_life:
    text: GraphMASAL пока не перешёл от прототипа к полноценному развертыванию в учебных
      учреждениях. На данный момент реализована исследовательская версия с оценкой
      на уровне лабораторного прототипа и экспериментальными результатами, без данных
      о пилотировании или масштабировании. Следующий шаг — тестирование в реальных
      классах и сбор широкого фидбека для корректировки архитектуры и алгоритмов.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  metrics_evidence:
    text: Авторы GraphMASAL оценивают эффективность системы с точки зрения structural/sequence
      alignment между планами обучения и знаниями студентов, покрытия слабых концепций,
      снижения стоимости обучения и точности когнитивной диагностики. Данные метрики
      ориентированы на инженерную верификацию оркестрации, а не на субъективные показатели
      удовлетворённости. Конкретных численных значений, проведённых в классе измерений
      или статистики по количеству пользователей в материалах нет, поскольку система
      остаётся прототипом.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  risks:
    text: В материалах отсутствует детальный разбор рисков, однако можно предположить
      потенциальные проблемы goal-substitution (смещение целей с реального обучения
      на оптимизацию механистических метрик), сниженный порог качества обучения из-за
      автоматизации и возможные сложности с аудиторским контролем работы сложной multi-agent
      архитектуры. Также отсутствуют данные об интеграции с внешними институтами и
      рисках вендорного захвата.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  countersignals:
    text: Нет заметных кейсов или практик, которые шли бы вразрез с заявленной ролью
      или архитектурой GraphMASAL. Кейс подчёркивает экспериментальный характер и
      отсутствие реального внедрения, что служит сдерживающим фактором для переоценки
      его действительной эффективности.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  transferability:
    text: Концепция представления образовательного процесса как графа состояний с
      ролями Diagnostician, Planner и Tutor, оркестрируемыми через dynamic knowledge
      graph и neural IR, может быть перенесена в разные образовательные контексты,
      где важна гибкая и адаптивная персонализация обучения. Particularly релевантен
      для дисциплин с чёткой иерархией знаний и необходимых последовательностей освоения,
      а также для разработки multi-agent образовательных платформ с разделением педагогических
      функций. Подобные паттерны рассматриваются в рамках [[B-pattern]], [[agentic
      tutor]] и [[adaptive multi-agent systems]].
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  theory_links:
    text: GraphMASAL затрагивает гипотезу H3 (раскладка педагогической функции на
      агенты Diagnostician, Planner и Tutor), демонстрирует тип B паттерна в multi-agent
      adaptive learning, причём фасеты оркестрации относят его к NET, педагогику —
      к AUTO, а контроль — к HYBR. Это соответствует идеям распределённой агентной
      интеллигенции с hybrid control и persistent learner modeling. Кейс имеет связи
      с теоретическими концепциями эволюционных противоречий между автономией агента
      и необходимостью институционального контроля ([[autonomy-vs-control]]), а также
      иллюстрирует тренды на разложение педагогической роли на отдельные контролируемые
      компоненты в AI-образовании [[H4-agent-ecosystems]].
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  open_questions:
    text: Остаётся неясным, как система будет внедряться в реальные учебные процессы
      и какие вызовы встретит при масштабировании. В частности, неизвестна оценка
      реакции педагогов и студентов, вопросы нормативного регулирования, интеграции
      с образовательными стандартами и управление данными пользователей. Также нет
      однозначной проверки устойчивости и эффективности оркестрации агентов в разнообразных
      предметных областях и группах учащихся.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  next_wave_followup:
    text: Следует перепроверить реальные classroom deployment-сценарии с оценкой влияния
      multi-agent orchestration на результаты обучения и удовлетворённость. Необходима
      более подробная валидация persistent learner modelling и plan adaptation в живой
      среде. Важно проверить возможность расширения сети агентов и устойчивость к
      ошибкам или конфликтам между ролями.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  sources_verification:
    text: Основные данные подтверждаются публикациями из arXiv и другими исследовательскими
      источниками, где описаны архитектурные особенности и экспериментальные результаты
      по GraphMASAL. Однако прямых независимых исследований внедрения и эффектов пока
      нет, что ограничивает уровень подтверждения заявленных эффектов до прототипных
      исследований. Источники являются высококачественными, но ограничены академической
      стадией развития системы.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
---

## Описание

GraphMASAL — multi-agent система с явным разделением Diagnostician /
Planner / Tutor поверх dynamic knowledge graph и optimization-based
planning. Метрики ориентированы на инженерную верификацию оркестрации
(structural alignment, coverage of weak concepts, lower learning cost),
а не на маркетинговый engagement. Поддерживает [[H2-assistant-to-autonomy]]
и [[H3-text-to-agentic-environment]].
