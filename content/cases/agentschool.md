---
id: agentschool
name: AgentSchool · multi-agent educational simulation
organization:
  name: AgentSchool research group
  type: R
  country: INT
scenario:
  level:
  - research
  domains:
  - education-research
  context: research-prototype
facets:
  orchestration: SWARM
  pedagogy: SUBJ
  control: MACH
  economy: NONE
ai:
  pattern: B
  agentivity: 4
  technologies:
  - multiple-models
  role: student-agents + teacher-agents + classroom simulator
transformation_mode: greenfield
axes:
  agentivity: 4
  ai_pattern: B
  orchestration: SWARM
  control_locus: MACH
  interaction_form: multi-agent-simulation
  audit_trail_strength: 5
  has_persistent_state: true
  evaluation_evidence_strength: 2
lifecycle:
  stage: poc
  first_seen: diff-2026-06
  history:
  - wave: diff-2026-06
    stage: poc
    note: growable student-agents + adaptive teacher-agents + multi-scale classroom
      simulator с социальными эффектами
links:
- kind: type
  id: B
  relation: instantiates
  confidence: low
- kind: hypothesis
  id: H3
  relation: supports
  confidence: high
- kind: tension
  id: simulation-vs-engineering-power
  relation: illustrates
  confidence: high
sources:
- url: https://arxiv.org/
  type: academic
  accessed: 2026-06
verified: false
canvas:
  signature_context:
    text: 'AgentSchool — симулятор образовательной среды для до-внедренческого

      тестирования сценариев. Student-agents с weighted knowledge graphs,

      ZPD-adaptation, clique formation, peripheral participation. Эталон

      [[H3-text-to-agentic-environment]] на уровне исследовательского

      прототипа. Иллюстрирует [[simulation-vs-engineering-power]].'
    status: draft
    source: imported
    updated_at: '2026-06-12'
  ontology_status:
    text: 'AgentSchool позиционируется как *образовательный симулятор*, а не как тьютор
      или ассистент для реальных классов: многомодульная среда с агентами-«студентами»
      и агентами-«учителями», в которой исследуются сценарии оркестрации и групповой
      динамики в учебной аудитории. В пользовательском архиве кейс описан как «educational
      multi-agent simulation» и явно выделен в отдельную категорию «симуляционный
      кейс», отличную от реальных внедрений и teacher-facing систем.


      С онтологической точки зрения это *исследовательский прототип / proof-of-concept
      симулятора*, то есть контур моделирования, где и студенты, и преподаватели представлены
      агентами, а «класс» — вычислительной мультиагентной средой. Такой статус поддерживается
      описанием: growable student agents, adaptive teacher agents и multi-scale classroom
      simulator с формальными и неформальными «полями» обучения, причём кейс пока
      не применяется как операционная система поддержки реальных обучающихся, а служит
      инструментом для проектирования и тестирования архитектур оркестрации.


      Внутри общей онтологии Paideia AgentSchool относится к классу *multi-agent educational
      simulations* с уровнем агентности 3–4/6 и архитектурным паттерном B (no-code/MAS-агенты
      для образовательных задач), но функционирует именно как симуляционная инфраструктура,
      а не как производственная педагогическая платформа. Поэтому в текущей версии
      корпуса его статус фиксируется как: «research simulation / PoC, greenfield multi-agent
      classroom model», без признаков перехода в стадию реального внедрения в институциональную
      практику.

      '
    status: draft
    source: llm
    updated_at: '2026-06-13'
  ai_role:
    text: 'В AgentSchool искусственный интеллект выступает не как тьютор для реального
      класса, а как **симуляционное население образовательной среды**. Базовая роль
      AI — моделировать *student-agents* как растущие когнитивные сущности с взвешенными
      предметными графами знаний, пулами мыслительных workflow и явными заблуждениями,
      проходящими через траектории обучения в разных сценариях.


      Параллельно AI берёт на себя роль **teacher-agents** — адаптивных планировщиков,
      scaffolders и рефлексивных наблюдателей, которые проектируют задания, подстраиваются
      под зону ближайшего развития симулированных студентов и изменяют тактику в ответ
      на динамику класса. Эти «учительские» агенты не обучают человека, а управляют
      виртуальным классом из AI-студентов, проверяя разные стратегии оркестрации.


      Третья ключевая роль AI — **оркестратор многоагентной учебной экосистемы**:
      система моделирует classroom как мульти-масштабную симуляцию формальных и неформальных
      полей обучения, отслеживая социальные эффекты, групповую динамику и возникновение
      норм в популяции AI-студентов. Здесь AI выступает как инфраструктурный агентный
      контур, в котором разыгрываются гипотезы о дизайне курсов, групповой работе
      и управлении вниманием.


      Таким образом, функционально AI в AgentSchool совмещает роли *виртуальных учеников*,
      *виртуальных преподавателей* и *симулятора образовательной среды*, обеспечивая
      исследователям и дизайнерам возможность тестировать педагогические сценарии
      и схемы оркестрации без участия реальных обучающихся.'
    status: draft
    source: llm
    updated_at: '2026-06-13'
  problem_situation:
    text: Без AI образовательные процессы с мультиагентным взаимодействием остаются
      трудно формализуемыми, и симуляция classroom dynamics с учётом когнитивного
      развития student agents, адаптивного планирования teacher agents и социального
      взаимодействия группы была недоступна. Традиционные ITS или tutor systems не
      обеспечивали долгосрочное моделирование student profiles с social dynamics,
      weighted subject knowledge graphs и отражением педагогической нормы, что мешало
      полноценно исследовать комплексные образовательные сценарии, включая clique
      formation и opinion-leader emergence.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  effect_hypothesis:
    text: AgentSchool обещает ermöglichen multi-agent educational simulation с growable
      student agents и adaptive teacher agents, которые совместно симулируют multi-scale
      classroom environment. Система должна обеспечивать высокий уровень агентности
      3–4/6, представлять explicit misconceptions, ZPD-informed adaptation и социальные
      эффекты, тем самым давая возможность проверить и доработать образовательные
      сценарии до реальных внедрений. Это позволяет оценить, как меняются роли агентов,
      групповые эффекты и траектории освоения в условиях сложной педагогической оркестрации.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  ai_architecture:
    text: Архитектура AgentSchool включает multiple-models с LLM-powered student and
      teacher agents, построенных как growable cognitive entities с weighted subject
      knowledge graphs и thinking-workflow pools. teacher agents функционируют как
      adaptive planners, scaffolders и reflectors. Класссимулятор реализует multi-scale
      approach с учётом формального и неформального обучения. Агентность системы оценена
      в 3–4 по шкале агентности 0–6, что соответствует наличию долговременного когнитивного
      моделирования, социальной динамики и адаптивного педагогического планирования.
      Это симуляционный исследовательский прототип, не являющийся живым внедрением.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  team_roles:
    text: В системе задействованы роли student-agents, представляющих обучающихся
      с когнитивным ростом и модели misconceptions, и teacher-agents, выполняющих
      функции adaptive planner, scaffolders и reflectors, которые реагируют и корректируют
      образовательный процесс. Благодаря разделению ролей достигается распределение
      педагогических функций в симуляции, что способствует эмерджентным социальным
      эффектам и управлению когнитивными траекториями. От человекокомпонентов данных
      фрагментов явно не выделено, поскольку кейс находится в стадии симуляции и научной
      архитектуры.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  institutional_loop:
    text: AgentSchool — исследовательская симуляционная архитектура без текущей институционализации
      или нормативных требований. Проект не осуществляет живое внедрение, а служит
      платформой для моделирования и тестирования образовательных сценариев и педагогических
      стратегий до интеграции в реальные университетские процессы. В контексте институциональных
      циклов он скорее относится к этапу лабораторных исследований и прототипирования,
      предвосхищая дальнейшую институционализацию и внедрение.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  transit_to_life:
    text: На сегодня AgentSchool находится на стадии исследовательского прототипа
      и симуляционной модели. Реального перехода к внедрению или расширенному пилоту
      в учебных заведениях не зафиксировано. Система предназначена для предварительной
      проверки педагогических гипотез, ролей агентов и социальных эффектов в образовательных
      траекториях, что обеспечивает подготовку базы для последующего rollout. Коррекции
      и доработки связаны с оптимизацией моделей student и teacher agents и способов
      отражения социальной динамики.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  metrics_evidence:
    text: На данный момент отсутствуют количественные данные реального применения
      AgentSchool в живых классах. Оценка эффективности проводится на основе симуляций
      с моделями student profiles и classroom dynamics. Уровень агентности оценён
      как 3–4/6 по внутренней шкале, что отражает комплексность архитектуры и эмерджентность
      социального поведения агентов. Модель обеспечивает tracking weighted subject
      knowledge graphs, misconceptions и ZPD adaptation, но прямых метрик по образовательным
      результатам нет, что характерно для симуляционных prototyping систем.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  countersignals:
    text: Хотя AgentSchool представляет продвинутую симуляцию multi-agent образовательных
      процессов, он не является живым внедрением, что ограничивает возможность проверки
      его эффективности в реальных условиях. Система отстает от практик с настоящими
      course deployments, как ITAS/Old Dominion University с уровнем агентности 3/6,
      демонстрирующими работу в реальной академической среде. Это подчёркивает разрыв
      между исследовательской архитектурой и оперативной педагогической практикой,
      что требует дальнейшего перехода и интеграции.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  transferability:
    text: AgentSchool подходит для переноса в университетские исследовательские лаборатории,
      где нужны инструменты для предварительного тестирования и моделирования агентных
      образовательных сценариев. Его мультиагентная структура может быть адаптирована
      для разработки и оценки комплексных педагогических стратегий, а также для подготовки
      к внедрению multi-agent tutor систем и classroom orchestration architectures.
      Широкий потенциал также лежит в научных симуляционных экспериментах по изучению
      социальных эффектов и коллективных динамик в обучении.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  theory_links:
    text: AgentSchool задействует и иллюстрирует гипотезы H4 о hierarchical and multi-scale
      agent-based tutoring, а также гипотезы H2 и H3 о распределении педагогических
      функций между специализированными агентами (teacher agents как planner/scaffolders),
      опираясь на фасет SWARM, где обучение реализуется как orchestrated multi-agent
      interaction. Используется концепция агентности 3–4/6 с включением social effects,
      что коррелирует с теориями коллективной адаптивности и образования в зоне ближайшего
      развития (ZPD). Кейс пересекается с [[H4-agent-education]], [[SWARM-orchestration]]
      и [[agentic-pedagogy]] и отображает современную рамку agentic learning environments
      в исследованиях на 2025–2026.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  open_questions:
    text: Остаётся неясным, как AgentSchool может перейти от симуляционного прототипа
      к реальному внедрению с измеряемыми образовательными результатами. Требуется
      дополнительная проверка работоспособности adaptive teacher agents и growable
      student agents в реальных классных условиях. Также открытым остаётся вопрос
      устойчивости социальных эффектов (clique formation, opinion leader emergence)
      и их влияния на педагогическую норму и результаты обучения. Необходимо выяснить,
      каким образом институты смогут поддерживать и регулировать такую мультиагентную
      систему согласно governance frameworks.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  next_wave_followup:
    text: В следующей волне важно перепроверить возможность расширения AgentSchool
      в сторону интеграции с живыми курсами и участие человека-инструктора в адаптации
      и контроле. Следует сосредоточиться на метриках образовательного прогресса и
      оценке воздействия социальной динамики в мультиагентной среде. Особое внимание
      должно быть уделено оценке agentivity 4/6 и реализации meta-control layer, а
      также калибровке teacher agents к разным педагогическим парадигмам. Рекомендуется
      проверить взаимодействие AgentSchool с другими multi-agent tutor прототипами,
      такими как CogEvo-Edu и IntelliCode.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
---

## Описание

AgentSchool — симулятор образовательной среды для до-внедренческого
тестирования сценариев. Student-agents с weighted knowledge graphs,
ZPD-adaptation, clique formation, peripheral participation. Эталон
[[H3-text-to-agentic-environment]] на уровне исследовательского
прототипа. Иллюстрирует [[simulation-vs-engineering-power]].
