# План: адаптация второго этапа после AUTOPILOT

**Дата:** 2026-06-17
**Автор:** Codex
**Статус:** черновик

## Цель

Превратить `converted.md` в короткий Codex-native второй этап после `AUTOPILOT.md`, без Claude-специфики и без лишней библиотеки, которую агент не будет читать.

## Принцип работы

- Не переносить `converted.md` целиком.
- Работать маленькими спринтами.
- Каждый спринт сверять с официальной документацией Codex.
- После каждого спринта проверять, что новая структура читается, обновляется и не дублирует уже существующие папки.
- Если официальная документация по нужной поверхности недоступна, спринт не начинать.

## Официальные опоры

- `AGENTS.md`: https://developers.openai.com/codex/guides/agents-md
- Config: https://developers.openai.com/codex/config-basic
- Advanced config и hooks: https://developers.openai.com/codex/config-advanced
- Skills: https://developers.openai.com/codex/skills
- MCP: https://developers.openai.com/codex/mcp
- Subagents: https://developers.openai.com/codex/subagents
- Automations: https://developers.openai.com/codex/app/automations
- Chrome extension: https://developers.openai.com/codex/app/chrome-extension
- IDE slash commands: https://developers.openai.com/codex/ide/slash-commands
- CLI slash commands: https://developers.openai.com/codex/cli/slash-commands

## Карта соответствий Claude -> Codex

| В `converted.md` | В Codex-версии | Решение |
|---|---|---|
| `CLAUDE.md` | `AGENTS.md` | Заменить везде. Codex читает `AGENTS.md` как durable-инструкции проекта. |
| `.claude/settings.json` | `.codex/config.toml` или `.codex/hooks.json` | Не копировать синтаксис Claude. Для hooks использовать Codex-формат из docs. |
| `.claude/skills/` | `.agents/skills/` | Repo-skills хранить в `.agents/skills/`. Глобальные установки не делать в starter. |
| Claude permissions / Bypass Permissions | Codex sandbox, approvals, rules, hooks | Не переносить напрямую. Оставить только безопасные правила и проверяемые hooks. |
| Claude Chrome | Codex Chrome extension или Browser plugin | Делать отдельным опциональным спринтом после проверки нужного сценария. |
| Claude slash commands | Codex IDE/CLI slash commands | Не копировать таблицу целиком. Оставить только подтверждённые команды и пометить поверхность: IDE или CLI. |
| Claude subagents | Codex subagents | Оставить как опциональный workflow: только если пользователь явно просит spawn subagents. |
| Claude MCP | Codex MCP через `codex mcp` или `config.toml` | Не ставить MCP заранее. Сначала аудит, потом локальная настройка при реальной нужде. |
| Claude memory `~/.claude/memory/` | `ai-clone/feedback/`, `AGENTS.md`, возможно Codex memories | Не обещать глобальную авто-память без отдельной проверки. Основная память - файлы проекта. |
| `business/` | `.business/` | Не создавать дубль. Использовать уже принятую папку `.business/`. |

## Имя второго этапа

Выбрано: `POST_AUTOPILOT.md`.

Причина: файл явно читается как продолжение после первого онбординга и не смешивается с основным `AUTOPILOT.md`.

## Рамка решения

- Первый `AUTOPILOT.md` остаётся короткой входной настройкой.
- `POST_AUTOPILOT.md` будет вторым уровнем: личный контекст, mastery, feedback, контекст-инжиниринг, опциональные skills/MCP/automations.
- В `AUTOPILOT.md` нужна только короткая ссылка на `POST_AUTOPILOT.md` в финале.
- Все большие темы делаются отдельными спринтами, а не одним огромным переносом `converted.md`.

## Спринты

### Спринт 0. Документация и рамки

- [x] Проверить доступ к официальным Codex docs.
- [x] Составить карту соответствий Claude -> Codex.
- [x] Решить финальное имя второго этапа: `POST_AUTOPILOT.md`.
- [x] Зафиксировать, что первый `AUTOPILOT.md` остаётся коротким входным онбордингом.

### Спринт 1. Скелет второго этапа

- [x] Создать короткий файл второго этапа без длинных объяснений.
- [x] Добавить только структуру этапов и правила остановки.
- [x] Добавить ссылку из финала `AUTOPILOT.md`.
- [x] Проверить, что файл не дублирует уже сделанные шаги первого AUTOPILOT.

Результат: создан `POST_AUTOPILOT.md` как каркас. Детали этапов не раскрыты специально: каждый следующий блок будет адаптироваться отдельным спринтом после сверки с Codex docs.

### Спринт 2. `ai-clone/`

- [x] Адаптировать идею AI-Clone под Codex и `AGENTS.md`.
- [x] Создать минимальную структуру папки.
- [x] Добавить `INDEX.md` с правилом читать только нужные файлы.
- [x] Не добавлять личные данные в starter-шаблон, только placeholders.

Результат: добавлена placeholder-структура `ai-clone/` и раскрыт Этап 1 в `POST_AUTOPILOT.md`. Папка хранит автора решений, а не бизнес проекта; `.business/` остаётся отдельным проектным контекстом.

### Спринт 3. `mastery/`

- [x] Адаптировать mastery как папку методологий, а не skills.
- [x] Создать минимальный README/INDEX.
- [x] Описать правило: один файл = один метод/автор/подход.
- [x] Проверить, что `mastery/` не конфликтует с Codex skills.

Результат: добавлена минимальная папка `mastery/` и раскрыт Этап 2 в `POST_AUTOPILOT.md`. Правило качества: одна стартовая область, 1-3 метода, каждый метод должен быть применим по шагам.

### Спринт 4. Усиление `AGENTS.md`

- [x] Обновить `templates/AGENTS.md.tmpl`, чтобы он знал про `ai-clone/` и `mastery/`.
- [x] Сохранить лимит краткости.
- [x] Не заставлять Codex читать всё подряд.
- [x] Добавить роутинг: когда читать `.business/`, когда `ai-clone/`, когда `mastery/`.

Результат: `AGENTS.md` и `templates/AGENTS.md.tmpl` получили маршрутизацию контекста. Правило осталось прежним: сначала индекс, затем только нужные файлы.

### Спринт 5. Feedback и ретро

- [x] Связать `retrospectives/` с `ai-clone/feedback/`.
- [x] Добавить правило: ошибки пользователя превращать в короткие правила.
- [x] Не делать ретро обязательным для микрозадач.

Результат: `retrospectives/README.md`, `retrospectives/TEMPLATE.md` и Этап 4 в `POST_AUTOPILOT.md` связывают сессионную историю с постоянными правилами в `ai-clone/feedback/`. Ретро не стало обязательным для микрозадач.

### Спринт 5b. Контекст-инжиниринг и review-cycle

- [x] Раскрыть правило минимального контекста в `POST_AUTOPILOT.md`.
- [x] Описать слои `.business/`, `ai-clone/`, `mastery/`, `plans/`, `retrospectives/`.
- [x] Добавить лёгкий review-cycle для заметных фич.
- [x] Не делать review-cycle обязательным для микрозадач.

Результат: Этапы 5 и 6 в `POST_AUTOPILOT.md` больше не заглушки. Они объясняют, как Codex выбирает контекст и как проверяет заметную фичу без лишней бюрократии.

### Спринт 6. Skills, plugins, MCP

- [x] Сверить с Codex docs по skills/plugins/MCP.
- [x] Убрать Claude-specific slash commands.
- [x] Оставить только аудит и правила выбора инструмента.
- [x] Не устанавливать ничего из интернета в рамках starter-шаблона.

Результат: Этап 7 в `POST_AUTOPILOT.md` описывает разницу между skills, plugins и MCP, а `.agents/skills/README.md` уточняет границы repo-skills. Никаких внешних установок не добавлено.

### Спринт 7. Browser и automations

- [x] Заменить Claude Chrome на Browser plugin / in-app browser, если применимо.
- [x] Заменить “триггеры” на Codex automations или отдельные scripts/cron только после проверки docs.
- [x] Оставить этот спринт опциональным.

Результат: Этап 8 в `POST_AUTOPILOT.md` описывает in-app browser, Chrome extension и automations как опциональные инструменты. Добавлены правила: сначала ручной тест prompt, Chrome только при реальной нужде, project automations требуют включённый Codex и доступную папку проекта.

### Спринт 8. Финальная проверка

- [x] Проверить размер и читаемость второго этапа.
- [x] Проверить, что нет `CLAUDE.md`, `.claude/`, Claude Code команд.
- [x] Запустить `git diff --check`.
- [x] Запустить `scripts/security-audit.sh`.
- [x] Обновить итог плана.

Результат: `POST_AUTOPILOT.md` ужат до 198 строк, Claude-only следов в рабочих инструкциях нет, проверки прошли.

### Спринт 9. Полировка стыковки

- [x] Проверить связку `AUTOPILOT.md` -> `POST_AUTOPILOT.md`.
- [x] Добавить автопредложение второго этапа в стартовый `AGENTS.md`.
- [x] Добавить privacy-check для заполненного `ai-clone/`.
- [x] Уточнить, что `ai-clone/` и `mastery/` читаются после прохождения `POST_AUTOPILOT.md`, а не из-за placeholder-папок.
- [x] Сократить повторяющиеся ссылки в `POST_AUTOPILOT.md`.

Результат: второй этап лучше стыкуется с первым и безопаснее ведёт себя перед commit.

## Критерии готовности

- Второй этап можно проходить после первого AUTOPILOT.
- Первый AUTOPILOT не превращён в огромный документ.
- Все новые папки имеют `INDEX.md` или README и понятное правило чтения.
- Codex не обязан читать весь контекст сразу.
- Нет Claude-only инструкций.

## Итог

- **Реализовано целиком:** да
- **Что сделано:** добавлен второй этап `POST_AUTOPILOT.md`, папки `ai-clone/` и `mastery/`, роутинг контекста в `AGENTS.md` и `templates/AGENTS.md.tmpl`, связь ретро с `ai-clone/feedback/`, правила для skills/plugins/MCP/browser/automations, privacy-check для заполненного `ai-clone/`.
- **Что не сделано и почему:** не переносился весь `converted.md`, потому что цель - короткий Codex-native workflow, а не большая библиотека.
- **Проверки:** `git diff --check`, `scripts/security-audit.sh`.
- **Уроки:** второй этап должен оставаться модульным: каждая новая папка обязана иметь индекс, а Codex должен читать только нужные файлы под задачу.
