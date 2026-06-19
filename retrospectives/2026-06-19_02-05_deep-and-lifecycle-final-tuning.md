# Ретро: финальная настройка deep и lifecycle

Дата: 2026-06-19

## Задача

После 9 прогонов AUTOPILOT доработать первую и вторую части: защитить `deep` от распухания и усилить ведение проекта после онбординга.

## Что сделано

- В `AUTOPILOT.md` добавлено правило: `deep` не равен большой библиотеке.
- Для `deep` добавлен обязательный блок `MVP vs later`.
- Для `PROJECT_STATE.md` добавлена deep-карта: scope, data, roles, integrations, trust/security, MVP vs later.
- В `POST_AUTOPILOT.md` усилены правила актуальности, очистки и lifecycle.
- Обновлены `templates/PROJECT_STATE.md.tmpl`, `AGENTS.md`, `templates/AGENTS.md.tmpl`, `QUALITY_CHECKLIST.md`.

## Вывод

AUTOPILOT стал лучше удерживать тяжёлые проекты: он видит риски, но не обязан превращать каждый риск в отдельную библиотеку.

## Следующий шаг

Провести финальный smoke-test нового `deep` и затем оценить итоговую версию автопилота.
