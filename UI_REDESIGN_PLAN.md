# Paideia · план пересборки интерфейса (UX v2)

Дата: 2026-06-13.
**Без переделки функционала.** Только структура навигации, иерархия страниц, шаблоны.

---

## 1. Что сломано в текущем UI

| Проблема | Симптом |
|---|---|
| **Плоская навигация** | 15 пунктов в шапке: catalog, map, match, import, waves, methods, foundry, эл.пространство, контр-сигналы, +проект, проекты, архив, аудит, теория. Не видно иерархии. |
| **Сервисное и пользовательское в одной шапке** | Foundry (98 candidates для разработчиков агентов) и +проект (главный action преподавателя) рядом. |
| **Нет ролевого landing** | Главная одинакова для преподавателя/исследователя/методиста/админа. |
| **Запуск агентов поверх проекта скрыт** | Чтобы запустить KOSMOS — нужно: проекты → проект → /runs → форма. Юзер не понимает что это вообще есть. |
| **Workflow проекта не виден** | 6 view (Dashboard/System/Vepol/Canvas/Lab/Runs/Export) — без stepper'а, в каком порядке проходить, что готово, что нет. |
| **Empty states слабые** | «нет данных», «пока пусто» без CTA. |
| **Нет command palette** | Все 24 профиля агентов, 40 ТРИЗ-приёмов, 118 кейсов — только через клик по дереву. |
| **Нет контекстной справки** | Что значит «pedagogical-contradiction-cutter»? Что писать в секцию «transit_to_life»? |
| **`/elective-space` не интерактивный** | Просто read-only список. Пользователь не понимает зачем заходить дважды. |
| **`/foundry` для пользователя выглядит как мусор** | 98 кандидатов, кнопки «📤 в регистр» — без объяснения зачем оно ему. |

---

## 2. Принципы пересборки (из research'а)

1. **Role × Task matrix**: роль определяет landing и видимость пунктов меню (Stripe Test/Live toggle).
2. **Task-first navigation**: главная — «что мне делать сегодня», не «какие модули есть» (Linear My Issues).
3. **Progressive disclosure**: показывать сначала 3 ключевых секции, остальное «Expand» (Figma Design panel).
4. **Seeded content вместо tour'а**: пустые экраны → demo-проекты + один-клик-templates (Notion, Linear).
5. **Workflow stepper**: «где ты в проекте» — pipeline сверху с % completeness (Stripe checkout, Typeform).
6. **Cmd+K**: единая точка действий и навигации опытному юзеру (Linear, Notion).
7. **Service mode toggle**: служебные функции прячутся за gear-icon (Stripe Developers).
8. **Info-popover вместо wiki**: hover/click → 2 строки + 1 пример (Linear, Figma).

---

## 3. Новая структура навигации

### 3.1 Top bar — 4 пункта вместо 15

```
[Paideia logo]   Корпус ▾   Мои проекты   + новый   |   🔍 Cmd+K   ⚙️
```

- **Корпус** (dropdown): Каталог · Карта · Методы (40 ТРИЗ) · Теория · Архив · Мониторинг волн
- **Мои проекты**: список с фильтром «активные / архив»
- **+ новый**: ведёт прямо в wizard
- **🔍** (или Cmd+K): command palette
- **⚙️**: service mode (Foundry, LLM-аудит, Контр-сигналы CRUD, Эл.пространство, Theory CRUD)

### 3.2 Главная — role-aware

**Если есть проекты:**
```
Здравствуй, [имя].
Продолжить: [последний проект] · Dashboard / Canvas / Запустить Run

Быстрые действия:
- ▶ Запустить KOSMOS на [проект]
- 📄 Экспорт РПД
- 🎭 Stakeholder Pressure
```

**Если проектов нет:**
```
3 demo-проекта (открыть, посмотреть, копировать)
+ большой CTA «Создать свой проект за 60 секунд»

Внизу — 4 ролевых входа:
🎓 Я преподаватель  → wizard
🔬 Я исследователь → /catalog
📋 Я методист     → /projects + export
⚙️ Я админ        → service mode
```

### 3.3 Project view — sticky stepper

Сверху каждой project-страницы:

```
[← Мои проекты]  [Project Name]                           [▶ Запустить агента ▾]
═══════════════════════════════════════════════════════════════════════════════
 ① Dashboard   ②  System   ③  Канвас   ④  Веполь   ⑤  Lab   ⑥  Runs   ⑦  Export
   ✓ готов      ✓ построена  12/18 заполнено  ✓ диагностика  3 runs  применено 1  готов
═══════════════════════════════════════════════════════════════════════════════
```

Stepper показывает порядок и completeness. Каждый шаг кликабелен. Текущий — выделен. Будущие — серые но доступны.

### 3.4 Cmd+K command palette

3 секции в одном поиске:
- **🤖 Запустить агента на проекте** (24 profile: KOSMOS, Stakeholder, Semester Sim, Anti-Washing, Time Machine...)
- **🔍 Найти в корпусе** (118 кейсов через RAG)
- **🧭 Перейти** (любой view, любой проект, любая сущность теории)

Шорткат `Cmd+K` / `Ctrl+K`. Открывается inline без перезагрузки.

### 3.5 Service mode (⚙️ toggle)

При активации появляется banner вверху + расширяется sidebar:

```
🛠 SERVICE MODE (admin/devops)               [выйти]

Sidebar:
- Agent Foundry (98 кандидатов из 16 PDF)
- LLM-аудит (токены, $, кеш)
- Регистр L1 агентов
- Контр-сигналы CRUD
- Эл.пространство (онтология)
- Теория CRUD (types/hypotheses/tensions/modes)
- Method Library (40 ТРИЗ для админа)
```

---

## 4. Пересборка отдельных страниц

### 4.1 Home (`/`)

| Сейчас | Должно стать |
|---|---|
| 5 одинаковых карточек юскейсов | Role detector → 4 разных landing'а |
| Нет рекомендаций «что дальше» | Топ-1 кнопка: «Продолжить [проект]» или «Создать проект» |
| Не видно последних действий | Recent activity (последний run, последняя секция, последний экспорт) |

### 4.2 Project view (`/project/{id}/*`)

| Сейчас | Должно стать |
|---|---|
| 6 кнопок переключения view в шапке | Stepper с % completeness каждого этапа |
| «▶ Run…» — кнопка на отдельной странице | Sticky-кнопка «▶ Запустить агента» в правом верхнем углу всех project-страниц + modal с 24 profile (как Linear «Create issue») |
| Канвас 18 секций — все открыты | Сначала 3 ключевые (signature_context / function / dolzhno), остальные за «развернуть остальные 15» |
| Каждая секция канваса — 4 кнопки (LLM-fill, ввести, история, переуточнить) | Главная кнопка по умолчанию (LLM-fill), остальные за `⋮` menu |
| Vepol-схема + Dashboard + System — 3 разные страницы | Объединить: Dashboard с веполь-миниатюрой и System Model collapsible |

### 4.3 Catalog (`/catalog`)

| Сейчас | Должно стать |
|---|---|
| 110+ карточек простым списком | Сразу map-view с фильтром (как Figma Community), список — переключатель |
| Карточка кейса — без preview | Hover → side-panel с превью (как Notion link preview) |

### 4.4 Empty states

| Где | Сейчас | Должно стать |
|---|---|---|
| Пустой канвас | «нет данных» | «KOSMOS заполнит 6 секций за минуту → [Запустить]» |
| Пустой Runs | «пока пусто» | «Попробуй на demo-electives» (one-click) |
| Пустой Export | «пока пусто» | 4 крупные кнопки шаблонов |

### 4.5 Info-popovers (контекстная справка)

- Каждая из 18 секций канваса → `?` icon с 2 строками + пример заполнения
- Каждый из 24 profile агентов → popover «что делает / что вернёт / когда использовать»
- Каждый из 40 ТРИЗ-приёмов → expand с примером из корпуса (уже есть, оставить)
- Каждый из 7 стейкхолдеров → popover с 1 типичным вопросом

### 4.6 Breadcrumbs

Везде кроме главной:
```
Главная > Мои проекты > demo-electives > Канвас > Секция: signature_context
```

---

## 5. Фазы реализации

Без переделки функционала. Каждая фаза — отдельный auto-deploy.

### U1 · Свернуть навигацию (1 вечер)

- `templates/base.html`: 15 пунктов → 4 + dropdown «Корпус» + gear icon для service mode
- Service mode — query-param `?mode=service`, в base.html условный показ доп-меню
- `templates/home.html`: role-detector (через cookie или query), 4 разных landing'а

### U2 · Project stepper (1 вечер)

- Новый partial `templates/_project_stepper.html` — 7 шагов с completeness-индикаторами
- Включается в начале каждой project-страницы (system_view, project, dashboard, vepol, runs, agent_run, agent_runs_list, export)
- Sticky-кнопка «▶ Запустить агента» в правом углу — открывает modal с 24 profile

### U3 · Cmd+K command palette (1 вечер)

- Новый JS-компонент `static/cmdk.js` (vanilla)
- Backend endpoints:
  - `GET /api/search/everything?q=...` — fuzzy search по: проектам, кейсам корпуса, view-страницам, profile агентов
  - `POST /api/cmd/run-agent?profile=...&project=...` — quick-action для запуска

### U4 · Empty states + info-popovers (1 вечер)

- Все шаблоны: пустые состояния — CTA-first
- `templates/_help_popover.html` partial — универсальный popover с lookup в `taxonomy/help/*.yaml`
- Заполнить `taxonomy/help/canvas_sections.yaml`, `help/agent_profiles.yaml`, `help/triz_methods.yaml`

### U5 · Project dashboard unification (1 вечер)

- Слить Dashboard + Vepol-thumbnail + System summary в одну страницу `/project/{id}` (default)
- Отдельные view (System / Vepol / Canvas / Lab / Runs / Export) остаются как deep-pages, доступны через stepper

### U6 · Catalog map-first (1 вечер)

- `/catalog` → map view по умолчанию, list — toggle
- Hover на точку карты → side-panel preview без перехода
- Поиск + фасеты в sidebar (как сейчас, но компактнее)

### U7 · Breadcrumbs + recent activity (0.5 вечера)

- `templates/_breadcrumbs.html` partial — universal
- Recent activity на главной — последние 5 событий из БД (агент-runs, секции, экспорты)

### U8 · Service-mode page (0.5 вечера)

- `/service` — отдельная landing для admin: 4 секции (Foundry / Регистр агентов / LLM-аудит / CRUD теории и контр-сигналов / Эл.пространство как онтология)
- Из обычного navigation эти пункты убираются

---

## 6. Что не трогаем

Функциональность — НЕ трогаем:
- ✅ Все 24 profile agentов работают как сейчас
- ✅ Wizard остаётся
- ✅ Все API endpoints остаются
- ✅ Все markdown-файлы в `content/` остаются
- ✅ База, индексы, кеши — как есть
- ✅ AgentRun preview/apply контракт — без изменений

Меняем только: шаблоны (templates/*.html), JS (Cmd+K), CSS (stepper, popovers).

---

## 7. Объём и приоритеты

| Фаза | Что | Дней | Приоритет |
|---|---|---|---|
| U1 | Свернуть navigation + service mode + role landing | 1 | **P1** (главная боль) |
| U2 | Project stepper + sticky Run-кнопка | 1 | **P1** (workflow visibility) |
| U3 | Cmd+K | 1 | **P2** (нужно опытному юзеру) |
| U4 | Empty states + info-popovers | 1 | **P1** (новичок без помощи теряется) |
| U5 | Dashboard unification | 1 | **P2** (3 страницы в одну) |
| U6 | Catalog map-first | 1 | **P3** (косметика) |
| U7 | Breadcrumbs + recent activity | 0.5 | **P2** |
| U8 | Service-mode landing | 0.5 | **P1** (юзер просил отдельно) |
| **Итого** | | **~7 вечеров** | |

Рекомендуемый порядок: **U1 → U8 → U2 → U4 → U7 → U5 → U3 → U6**.

Это даёт максимум эффекта в первые 3 фазы: после U1+U8 преподаватель видит чистую навигацию; после U2 — видит workflow и может запускать агенты прямо из проекта; после U4 — не теряется на пустых экранах.

---

## 8. Чек-лист готовности к v2

- [ ] Главная страница меняется в зависимости от роли
- [ ] Topbar содержит ≤ 5 пунктов
- [ ] Service-функции спрятаны за gear-icon
- [ ] На странице проекта виден workflow stepper с % completeness
- [ ] Кнопка «▶ Запустить агента» доступна с любой project-страницы
- [ ] Cmd+K работает (3 секции: агенты / корпус / навигация)
- [ ] Все empty states имеют CTA
- [ ] У каждой 18-секции канваса есть info-popover «что писать»
- [ ] У каждого из 24 profile есть info-popover «что делает»
- [ ] Breadcrumbs на всех страницах кроме главной
- [ ] Catalog по умолчанию открывается на карте

---

## 9. Ответ на твой вопрос про «где запуск агентов поверх контекста проекта»

Сейчас он есть, но скрыт:
1. `/project/{id}/system` → правая колонка → форма «Run profiles» → выбрать → запустить
2. `/project/{id}/runs` → форма вверху → выбрать profile → запустить
3. `/project/{id}/run/{id}` — страница конкретного run'а с preview/apply

**После U2** будет одна **sticky-кнопка «▶ Запустить агента»** в правом верхнем углу всех project-страниц — она откроет modal со списком 24 profile (fuzzy-search, описание каждого, ожидаемое время).

Это и есть «запуск промптов-агентов поверх контекста проекта».
