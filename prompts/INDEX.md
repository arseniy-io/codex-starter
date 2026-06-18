# Промпты - индекс

Библиотека готовых workflow-промптов. Проверяй её, когда пользователь просит промпт или задача похожа на повторяемый сценарий.

## Как пользоваться

1. Найди в таблице задачу, которая совпадает с твоей.
2. Открой файл по ссылке - там промпт целиком.
3. Используй файл как workflow-промпт: подставь свои значения в квадратные скобки `[...]`.
4. Если Codex уже умеет выполнить задачу напрямую, попроси его прочитать нужный workflow и следовать ему.

## Таблица - если тебе надо, возьми

### Setup (настройка окружения)

| Задача | Промпт |
|---|---|
| Настроить голосовой ввод (Wispr Flow / диктовка) + быстрые скриншоты | [`setup/01-voice-screenshot.md`](./setup/01-voice-screenshot.md) |
| Звуковые хуки (уведомление при завершении задачи) | [`setup/02-hooks.md`](./setup/02-hooks.md) |
| Защита от опасных команд (`rm -rf`, утечка `.env` и т.д.) | [`setup/03-security.md`](./setup/03-security.md) |
| Интервью и заполнение `.business/` (fallback если AUTOPILOT не сработал) | [`setup/04-business-interview.md`](./setup/04-business-interview.md) |
| Сгенерировать `AGENTS.md` под свой проект | [`setup/05-agents-md-generation.md`](./setup/05-agents-md-generation.md) |
| Создать папку `plans/` с правилами | [`setup/06-plans-folder.md`](./setup/06-plans-folder.md) |
| Проверить рабочий цикл без учебного мусора | [`setup/07-test-cycle.md`](./setup/07-test-cycle.md) |
| Установить скилы (Bulletproof / Skill Creator / Frontend Design / PDF) с аудитом | [`setup/08-skills-install.md`](./setup/08-skills-install.md) |
| Подключить Playwright MCP (браузерная автоматизация) | [`setup/09-playwright.md`](./setup/09-playwright.md) |

### Launch (запуск в продакшн)

| Задача | Промпт |
|---|---|
| Залить код на GitHub | [`launch/01-github.md`](./launch/01-github.md) |
| Задеплоить проект (Vercel / Amvera / Railway / свой сервер) | [`launch/02-deploy.md`](./launch/02-deploy.md) |
| Подключить приём платежей (Stripe / YooKassa / CloudPayments) | [`launch/03-payments.md`](./launch/03-payments.md) |

### Methodology (методологические приёмы)

| Задача | Промпт |
|---|---|
| Критика плана через 3 независимых ревью | [`methodology/plan-critique.md`](./methodology/plan-critique.md) |
| «10 причин обосраться» - стресс-тест перед важным шагом | [`methodology/10-reasons.md`](./methodology/10-reasons.md) |
| Импорт существующего кода в `.business/` | [`methodology/import-existing-project.md`](./methodology/import-existing-project.md) |
| Планирование недели | [`methodology/weekly-planning.md`](./methodology/weekly-planning.md) |

## Правило

> «Если задача похожа на повторяемый workflow, сначала проверь этот INDEX.»

Не открывай промпты на всякий случай перед каждой задачей.
