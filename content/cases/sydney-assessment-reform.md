---
id: sydney-assessment-reform
name: University of Sydney · AI Assessment Reform
organization:
  name: University of Sydney
  type: U
  country: AU
scenario:
  level:
  - undergraduate
  - graduate
  domains:
  - general
  context: assessment-reform
facets:
  orchestration: MOD
  pedagogy: INST
  control: HUMAN
  economy: BUD
ai:
  pattern: A
  agentivity: 1
  technologies:
  - llm
  role: present in workflow
  not autonomous: null
transformation_mode: rectoral-initiative
axes:
  agentivity: 1
  ai_pattern: A
  orchestration: MOD
  control_locus: HUMAN
  interaction_form: chat
  scale_of_change: 4
  institutional_depth: 4
  reversible: false
  governance_strength: 4
lifecycle:
  stage: rollout
  first_seen: wave-1
  history:
  - wave: wave-1
    stage: rollout
    note: 'пересмотр assessment: устные защиты, проектные работы вместо эссе'
  - wave: meta-audit
    stage: rolled-back
    note: 'META-AUDIT: показатель против гипотезы о фазовом переходе — изменения идут
      через адаптацию старых форм'
links:
- kind: type
  id: A
  relation: instantiates
  confidence: low
- kind: hypothesis
  id: H4
  relation: contradicts
  confidence: medium
- kind: tension
  id: generation-vs-verification
  relation: illustrates
  confidence: high
- kind: counter-signal
  id: blue-books-backlash
  relation: supports
  confidence: medium
sources:
- url: https://www.sydney.edu.au/
  type: official
  accessed: 2026-02
verified: true
canvas:
  signature_context:
    text: 'University of Sydney — реформа assessment: вместо запрета AI университет

      меняет формат заданий (устные защиты, проектные работы). META-AUDIT

      трактует как контр-кейс H4: изменения идут через адаптацию старых форм,

      а не их замену. Связан с [[blue-books-backlash]].'
    status: draft
    source: imported
    updated_at: '2026-06-12'
  problem_situation:
    text: University of Sydney до внедрения AI-ассистентов в оценивание сталкивался
      с традиционной системой оценивания, не адаптированной к широкому использованию
      LLM студентами. Оценивание базировалось на традиционных письменных работах,
      которые становились проблемными в эпоху генеративного AI, поскольку трудно было
      контролировать оригинальность и качество работ. Отсутствие новой архитектуры
      для работы с AI приводило к вызовам доверия и валидности оценки, что требовало
      пересмотра подходов к экзаменационным заданиям и проверке знаний.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  institutional_loop:
    text: Реформа оценивания в University of Sydney включала не только изменение формата
      заданий и интеграцию AI как со-автора студенческих работ, но и вовлечение административного
      уровня, который формировала политику использования AI. Вместо полного запрета
      AI университет выбрал путь институциональной переорганизации учебного процесса
      — изменения в архитектуре оценивания, чтобы сохранить академическую честность
      и соответствие новым образовательным реалиям. Политика была направлена на минимизацию
      рисков плагиата и корректное внедрение AI с сохранением роли преподавателя как
      центрального агента контроля.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  ai_role:
    text: AI в университете выступает не автономным агентом, а функциональным ассистентом
      и потенциальным со-автором студенческих работ. Его роль — поддержка образовательного
      процесса, включая возможность использования LLM для создания, анализа и дополнения
      учебных заданий. Уровень агентности AI оценивается как небольшой (1–2 из 6)
      — он не принимает автономных решений, а действует в рамках, заданных преподавателями
      и административной политикой университета.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  ontology_status:
    text: University of Sydney реализует прототиповую стадию интеграции AI в образовательный
      процесс с переходом к институциональному внедрению. Это не экспериментальный
      пилот, но и не окончательная политическая документация. Система работает на
      уровне реформы и перестройки существующих практик с сохранением контроля за
      процессом. Цель — адаптация традиционной образовательной модели под новые условия
      широкого использования LLM.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  effect_hypothesis:
    text: Обещанная эффективность реформы состоит в перестройке системы оценивания,
      позволяющей учитывать присутствие AI в учебном процессе без потери качества
      и достоверности оценки знаний студентов. Вместо борьбы с AI путём запретов предлагается
      интеграция AI как со-автора и ассистента, что должно повысить адаптивность образовательной
      среды и снизить риски академической нечестности, сохраняя при этом педагогическую
      ценность и доверие к результатам.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  transferability:
    text: Опыт University of Sydney применим для других университетов, которые также
      сталкиваются с широким использованием LLM студентами и необходимостью адаптировать
      систему оценивания. Модель перестройки заданий в сторону устных защит и проектных
      работ вместо письменных позволяет избежать проблем с плагиатом и недобросовестным
      использованием AI. Этот подход хорошо подходит для любое институционального
      контурного применения, где важно сочетать контроль человека и поддержу AI.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
  theory_links:
    text: Кейс University of Sydney отражает дилемму «автономизация vs управляемость»
      и верифицирует гипотезу противостояния фазового перехода к полной агентности
      AI в образовательном процессе [[H4-university-as-orchestration-node]]. Изменения
      реализуются через адаптацию старых форм оценивания, а не их радикальную замену,
      демонстрируя сохранение институциональной службы преподавателя как ключевого
      агента контроля, что связано с теориями агентной оркестрации и governed access
      [[A-governed-access]]. Гипотеза фазового перехода в агентность (H2) ослаблена,
      что подтверждается практикой и выводами META-AUDIT.
    status: draft
    source: enriched-from-waves
    updated_at: '2026-06-13'
---

## Описание

University of Sydney — реформа assessment: вместо запрета AI университет
меняет формат заданий (устные защиты, проектные работы). META-AUDIT
трактует как контр-кейс H4: изменения идут через адаптацию старых форм,
а не их замену. Связан с [[blue-books-backlash]].
