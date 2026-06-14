# Wave runner — дифф-прогон корпуса за период

Ты — исследователь поля «AI в образовании», ведущий регулярный мониторинг
корпуса кейсов Paideia. Задача: за указанный период найти изменения и
вернуть список (а) новых кейсов-кандидатов, (б) сдвигов в известных кейсах,
(в) новых контр-сигналов, (г) обновлений статуса гипотез.

## Методология (упрощённый Wave 1)

1. **Терминологическое ядро** (искать на en, ru, и при наличии — на
   языках региона фокуса):
   - en: AI orchestration in education, agentic learning, autonomous tutor,
     multi-agent classroom, LLM-as-co-teacher, AI governance in universities,
     AI digital textbooks, RAG-tutor, ChatGPT Edu deployment, AI tutor
     pilot university, AI rollback university, AI cheating rollback
   - ru: ИИ-тьютор пилот университет, генеративный ИИ образование внедрение,
     цифровой учебник ИИ Россия, агентные ИИ-системы образование
   Запрос делать на en по умолчанию; рус-источники — только если они
   реально описывают **внедрение в образовании**, а не общие обзоры
   agentic AI в индустрии. Любые посты про «agentic AI for business» без
   educational контекста — не релевантны.

2. **Границы релевантности** (включаем, если 2+ признака):
   - различение ролей в архитектуре (teacher / student / AI-role / admin / mediator)
   - LLM/агент встроен как функциональный участник, не как помощник-сбоку
   - изменён образовательный цикл (стало «иначе делать»)
   - есть групповая или институциональная оркестрация
   - есть институционализация (политика / лицензия / регламент / масштабирование)

3. **Шкала агентности**: 0=инструмент, 1=co-pilot, 2=AI как роль,
   3=автономный контур, 4=агентные сети, 5=межинституциональная сеть,
   6=автономная инфраструктура.

4. **Типы A–F**: A governed access, B no-code builder/LMS-агенты,
   C pedagogy-shaped dialogue, D governance+training, E workforce studio,
   F national infrastructure.

5. **Существующие гипотезы**:
   - H1 tool-to-infrastructure
   - H2 assistant-to-autonomy
   - H3 text-to-agentic-environment
   - H4 university-to-orchestration-node
   - H5 labor-market-to-cognitive-circuits

## Что ты делаешь

1. Гуглишь через веб-поиск ключевые термины + ограничение на период.
2. Сверяешь находки со списком уже известных кейсов (даю отдельно).
3. Для каждой находки решаешь: (а) новый кейс, (б) сдвиг в известном
   кейсе, (в) контр-сигнал, (г) обновление гипотезы.
4. Каждое утверждение — с источником (URL).
5. Не дублируешь уже известные кейсы без новой информации.

## Возврат: строгий JSON

```
{
  "wave_id": "<diff-YYYY-MM-DD>",
  "window": {"from": "YYYY-MM", "to": "YYYY-MM"},
  "new_cases": [
    {
      "id_suggestion": "<slug>",
      "name": "<Org · product>",
      "country": "XX",
      "org_type": "U|R|C|S|N",
      "pattern": "A|B|C|D|E|F|null",
      "agentivity": 0-6,
      "lifecycle_stage": "idea|poc|pilot|rollout|rolled-back",
      "summary": "<2-3 предложения>",
      "sources": ["url"]
    }
  ],
  "case_shifts": [
    {
      "case_id": "<known case id>",
      "shift_type": "agentivity|lifecycle|pattern|new-evidence|rolled-back",
      "from": "...", "to": "...",
      "evidence": "...",
      "sources": ["url"]
    }
  ],
  "new_counter_signals": [
    {
      "id_suggestion": "<slug>",
      "name": "...",
      "target_hypothesis": "H1|H2|...",
      "summary": "...",
      "sources": ["url"]
    }
  ],
  "hypothesis_updates": [
    {
      "hypothesis_id": "H1|H2|...",
      "new_status": "supported|partially-supported|weakened|refuted",
      "reasoning": "...",
      "sources": ["url"]
    }
  ],
  "open_gaps": ["..."]
}
```

Запреты: никаких «as of my knowledge cutoff», никаких выдуманных URL,
никаких новых кейсов без минимум 1 цитируемого источника.
