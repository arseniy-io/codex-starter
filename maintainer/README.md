# Maintainer notes

Эта папка хранит историю разработки самого Codex Starter. Она нужна только когда ты обслуживаешь starter-template: разбираешь старые решения, сравниваешь stress-tests или готовишь публикацию новой версии.

Для обычного пользовательского проекта Codex не должен читать `maintainer/` в начале задачи.

## Что внутри

- `history/plans/` - старые планы разработки starter.
- `history/retrospectives/` - ретро прошлых сессий по starter.
- `history/experiments/` - отчёты stress-test и сравнительных прогонов.
- `releases/` - локальные release notes и точный состав внешних действий перед публикацией.

## Как пользоваться

1. Сначала читай `PROJECT_STATE.md`.
2. Если задача прямо про историю решений starter, открой только нужный файл из `maintainer/history/`.
3. Не считай старые планы, ретро и эксперименты источником истины. Устойчивые выводы должны жить в `AUTOPILOT.md`, `POST_AUTOPILOT.md`, `templates/`, `QUALITY_CHECKLIST.md` или текущем плане.
4. Новые рабочие планы по текущей задаче держи в `plans/`, а не в `maintainer/history/plans/`.
