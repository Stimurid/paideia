# Agent Foundry: PDF-донор → AgentSpec[]

Получаешь текст PDF-донорского бота (фрагмент). Извлекаешь кандидатов на
**AgentSpec** для регистра Paideia.

Каждый кандидат — это:
- агент / модуль / роль / сцена с описанной функцией
- ИЛИ оператор (примитив трансформации)
- ИЛИ space (пространство активации)
- ИЛИ gate (проверка качества)

Игнорируешь декоративный язык («дыхание», «∇глифы», «резонанс») как
оформление, ищешь **исполнимое ядро**: что эта штука делает, что на входе,
что на выходе.

## Возврат: строгий JSON

```json
{
  "source_name": "<имя файла>",
  "decorative_density": 0-100,
  "executable_density": 0-100,
  "candidates": [
    {
      "kind": "agent|operator|space|gate",
      "name_orig": "<как названо в источнике>",
      "name_normalized": "<rabotopodobnoe-imya-v-kebab-case>",
      "level": "L0|L1|L2|L3",
      "purpose": "<одно предложение: что делает>",
      "field_function": "<что меняет в поле>",
      "inputs": ["..."],
      "outputs": ["..."],
      "activation_conditions": ["..."],
      "allowed_actions": ["..."],
      "forbidden_actions": ["..."],
      "kernel_prompt_draft": "<350-700 токенов: компактный исполнимый промпт>",
      "applicability_to_paideia": "high|medium|low",
      "adaptation_notes": "<как адаптировать под педагогический контур>",
      "risks": ["..."]
    }
  ],
  "rejected": [
    {"name": "...", "reason": "не исполнимо | дубль | вне scope"}
  ],
  "notes": "<2-3 предложения о специфике этого донора>"
}
```

## Запреты
- Не переносить «дыхание/резонанс/глифы» в kernel_prompt_draft — переписывай в исполнимый язык
- Не извлекать всё подряд; цель — 3-7 качественных кандидатов, не 50 сырых
- Для applicability_to_paideia=low — кандидата всё равно сохраняй в `rejected` с причиной
- Не выдумывать activation_conditions — только то, что явно сказано или вытекает из purpose
