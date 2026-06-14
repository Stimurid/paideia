---
id: H2
name: От ассистента к контурной автономии
wave_introduced: wave-3
status:
  current: weakened
  history:
    - { wave: wave-3, status: proposed, note: "сформулирована как фазовый переход: AI берёт цикл диагностика → план → выполнение → оценка" }
    - { wave: meta-audit, status: weakened, note: "Gartner: 40% agentic-проектов отменятся к 2027; широкое распространение 'agent washing'; локально подтверждается (IgniteAI Agent, Scientific Reports RCT 2025), но как общеполевой переход — нет" }
markers:
  - multi-step agentic workflows внутри LMS
  - AI ведёт цикл diagnose → intervene → assess
  - feedback loops без человеческого вмешательства
  - системы с persistent learner state и долговременной памятью
related_hypotheses: [H1]
related_tensions: [autonomy-vs-control, generation-vs-verification]
---

## Тезис

AI переходит от роли ассистента к роли автономного контура, который берёт на
себя полный цикл педагогической задачи: диагностика уровня → план
интервенции → выполнение → оценка результата. Маркеры — multi-step agentic
workflows, persistent learner state, многоагентные педагогические
архитектуры (ITAS, GenMentor, GraphMASAL, CogEvo-Edu, IntelliCode).

## Условия ложности

Гипотеза опровергается, если:

- значимая доля заявленных «agentic» решений на проверке оказывается
  ребрендингом обычных чатботов (agent washing);
- институции систематически откатывают автономные функции в критических
  точках (assessment, дисциплинарные кейсы);
- многоагентные системы остаются исследовательскими прототипами без
  устойчивого деплоя в реальных курсах.

## Текущая база поддержки

_(автогенерируется reindex'ом)_

## Контрсигналы и опровержители

_(автогенерируется reindex'ом)_

Известные контр-сигналы:
- Gartner: 40% agentic AI проектов будут отменены к 2027 (agent washing);
- ANU отключил Turnitin AI detector (01/2024) — институциональный откат от
  автономных инструментов контроля;
- Stanford HAI: AI-детекторы демонстрируют bias против non-native English.
