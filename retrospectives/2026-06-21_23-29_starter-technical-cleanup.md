# Ретро: technical cleanup starter

## Что сделали

- Прошли фазы 1-9 плана `plans/2026-06-21-starter-technical-cleanup.md`.
- Отделили историю разработки starter в `maintainer/history/`.
- Очистили root placeholders и перенесли заполненный SyncDesk-пример в `examples/syncdesk/`.
- Вынесли mutable onboarding state в `.codex/autopilot-state.yml`.
- Сократили root `AGENTS.md` до bootstrap-правил для starter.
- Добавили `scripts/starter-lint.py` и подключили его к publication audit.
- Уточнили Windows-first команды, `.gitattributes` и Codex hook output.
- Прогнали smoke AUTOPILOT в безопасной копии.

## Что нашли

- PowerShell pipe мог ломать hook input из-за BOM/кодировки; hook переведён на `utf-8-sig`.
- Windows hook wrapper ломался в пути с кириллицей; добавлен явный UTF-8 decode для `git rev-parse --show-toplevel`.
- `autopilot/flows/lite.md` не повторял числовую цель `3-5` файлов, хотя `AUTOPILOT.md` её задавал; исправлено после smoke-test.

## Что осталось

- Отдельно выполнить LF-нормализацию перед финальным commit.
- После нормализации повторить `starter-lint`, `security-audit.ps1`, `user-project-safety-check.ps1`, `git diff --check`.
- Перед commit показать staged scope и не использовать `git add .`.

## Вывод

Стартер стал заметно удобнее для Codex: меньше шумного контекста, понятнее state, есть механический lint, Windows-путь проверен, а AUTOPILOT smoke-test поймал реальную недосказанность в flow.
