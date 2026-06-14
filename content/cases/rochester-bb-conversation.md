---
id: rochester-bb-conversation
name: University of Rochester · AI Conversations (Blackboard)
organization:
  name: University of Rochester
  type: U
  country: US
scenario:
  level:
  - undergraduate
  - graduate
  domains:
  - general
  context: lms-integrated
facets:
  orchestration: MOD
  pedagogy: ROLE
  control: HUMAN
  economy: EXT+MKT
ai:
  pattern: C
  agentivity: 2
  technologies:
  - multiple-models
  role: graded persona dialogue with log
transformation_mode: bottom-up
axes:
  agentivity: 2
  ai_pattern: C
  orchestration: MOD
  control_locus: HUMAN
  interaction_form: persona-roleplay
  reflexivity: 5
  audit_trail_strength: 5
  scale_of_change: 2
  institutional_depth: 2
  lms_integration: true
lifecycle:
  stage: pilot
  first_seen: wave-2
  history:
  - wave: wave-2
    stage: pilot
    note: 'AI Conversation как graded activity: сценарий и persona от преподавателя;
      log виден; сравнение с внешними чатами'
links:
- kind: type
  id: C
  relation: instantiates
  confidence: high
- kind: hypothesis
  id: H2
  relation: supports
  confidence: low
sources:
- url: https://www.rochester.edu/
  type: official
  accessed: 2026-02
verified: true
canvas:
  signature_context:
    text: 'Rochester — AI Conversation как graded activity: persona фиксируется

      преподавателем, лог виден, есть сравнение с внешними чатами. Применение

      кейса [[anthology-bb-conversation]] на стороне университета.'
    status: draft
    source: imported
    updated_at: '2026-06-12'
  ontology_status:
    text: Кейс Университета Рочестера с Blackboard AI Conversations относят к типу
      C по архитектуре, где AI выступает как педагогически формализованная роль (persona
      в учебном диалоге), что соответствует agentivity 2, то есть функциональной роли
      ассистента в рамках педагогически регламентированного диалога. Развернутая в
      LMS модульная архитектура (MOD) подчеркивает, что это не автономный агент, а
      компонент с ограниченной самостоятельностью и строгим человеческим контролем.
      Это соответствует Wave 2 и отражает тренд на обучение с AI как ролью, а не автономизацией
      учебного процесса.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  problem_situation:
    text: До внедрения Blackboard AI Conversations в Университете Рочестера существовали
      ограничения традиционных LMS-инструментов в том, что они не позволяли интегрировать
      AI как полноценную персону в учебный диалог с регламентированными ролями и логированием,
      что нужно для оценивания и рефлексии. Также отсутствовали собственные средства
      для педагогически контролируемого диалога со студентами, где AI служил бы не
      просто источником ответов, а активным участником учебного процесса с прозрачной
      оценкой.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  effect_hypothesis:
    text: Заявленная цель AI Conversations — включить искусственный интеллект как
      роль (персону) для проведения упорядоченного учебного диалога с возможностью
      задания преподавателем параметров (persona, тема, сложность) и сопровождения
      процесса с обязательной рефлексией и доступом к логам. Это должно повысить качество
      вовлечения студентов в учебное взаимодействие, облегчить оценивание работы посредством
      логов, а также создать более глубинный педагогический опыт, нежели простые чаты
      или генераторы контента.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  ai_architecture:
    text: 'Архитектура Blackboard AI Conversations реализует модульный (MOD) паттерн
      с интеграцией в LMS Blackboard. AI представлен в виде роли в учебном цикле:
      преподаватель формирует сценарий, определяет persona и другие параметры, студент
      ведет диалог с AI, а затем происходит рефлексия. Лог взаимодействий сохраняется
      и доступен инструктору для оценивания. Агентность 2/6 — AI не автономен, а выполняет
      роль диалогового ассистента с фиксированной персоной. Используется мульти-модельный
      стек, вероятно, с облачными языковыми моделями и механизмами логирования и метрик.
      Контроль человеческий (HUMAN).'
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  team_roles:
    text: 'В кейсе четко разграничены роли: преподаватель создает и настраивает сценарии
      и персонажи AI, студент взаимодействует непосредственно с AI как с собеседником,
      а AI выступает как роль, поддерживающая диалог. Техническая поддержка осуществляет
      интеграцию AI в LMS и обеспечивает логирование. Контроль и оценивание остаются
      полностью за преподавателем. Это проявление модели ROLE с human-in-the-loop
      контролем.'
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  ai_role:
    text: AI в Blackboard Conversations играет функциональную роль диалогового партнера
      с заданной персоной в формате Socratic questioning и role-play, помогая студентам
      вести учебный диалог, при этом действует под контролем человека и не генерирует
      автономно учебные материалы. Это AI как среда для активной учебной роли, а не
      просто генератор контента. AI обеспечивает контур рефлексии, доступный для оценки
      преподавателю. Агентность 2 — AI действует как ассистент и роль, а не автономный
      агент.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  interaction_scenario:
    text: Преподаватель определяет persona ИИ, тему и уровень сложности диалога. Студент
      взаимодействует с AI через интерфейс LMS, ведет диалог в рамках заданного сценария.
      Весь процесс фиксируется в логах, доступных преподавателю для последующего анализа
      и оценивания. После диалога студент проходит рефлексию (reflection), что структурирует
      опыт и способствует глубокому усвоению материала. Таким образом практика задействует
      педагогически формализованную ролевую активность с human-in-the-loop контролем.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  institutional_loop:
    text: Внедрение Blackboard AI Conversations предусматривает административный opt-in
      (опциональное включение инструмента), строгий контроль доступа и централизованное
      управление в LMS. Нормативка включает политику data governance с необходимостью
      прозрачности логов и защиты персональных данных, что соответствует требованиям
      university-wide политики. Преподаватели и IT службы участвуют в поддержании
      качества и соблюдении правил, что соответствует модели HYBR контроли с human-in-the-loop.
      Такой подход обеспечивает баланс между инновациями и ответственностью.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  metrics_evidence:
    text: 'Заявлено, что Blackboard AI Conversations используется как graded activity,
      где логи диалогов доступны для оценивания преподавателям. Агентность — 2 (функциональная
      роль с ограничениями). Хотя конкретные числовые метрики по количеству пользователей
      или действий не указаны, отмечены следующие качественные индикаторы: persona
      фиксирована, логи доступны, активна рефлексия как часть процесса оценки. Отсутствуют
      данные о объёмах использования или влиянии на учебные результаты, что характерно
      для Wave 2 на стадии пилота/прототипа.'
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  transferability:
    text: Паттерн Blackboard AI Conversations — педагогически формализованный диалог
      с ролью AI, встроенный в LMS и ориентированный на graded activities — потенциально
      применим в университетах с развитой LMS-инфраструктурой, где важен human-in-the-loop
      контроль и оценка активности студентов. Хорошо переносится в образовательные
      форматы, требующие обучающего диалога и рефлексии. Зрелые LMS платформы с возможностью
      расширения через плагины и API могут адаптировать этот подход в своих системах.
      Это часть тренда по типу C (pedagogy-shaped dialogue) в [[Agentic orchestration]]
      и [[Wave 2 onderwijs AI]].
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  theory_links:
    text: Кейс находится в плоскости Hypothesis C (pedagogy-shaped dialogue) — регламентированная
      педагогическая форма диалога с AI как ролью в учебном процессе, без автономизации.
      Это проявление фасеты ROLE и контроль HUMAN, соответствует agentivity 2 уровню.
      Система отражает эволюционный тренд перехода от функциональной ассистентности
      к интегрированной роли AI внутри учебного цикла, в LMS с модульной архитектурой
      (MOD). Связи с [[H4-pedagogy-role]], [[A-governed-access]] и [[autonomy-vs-control]]
      очевидны.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
---

## Описание

Rochester — AI Conversation как graded activity: persona фиксируется
преподавателем, лог виден, есть сравнение с внешними чатами. Применение
кейса [[anthology-bb-conversation]] на стороне университета.
