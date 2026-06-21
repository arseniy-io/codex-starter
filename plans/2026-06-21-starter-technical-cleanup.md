# План: technical cleanup Codex Starter

**Дата:** 2026-06-21
**Автор:** Codex
**Статус:** в работе

## Цель

Сделать Codex Starter чище, понятнее и удобнее для Codex без раздувания структуры: пройти по функциям шаблона маленькими фазами, после каждой фазы проверять результат и фиксировать вывод.

## Контекст

Пользователь хочет улучшить текущую техническую структуру starter-template, а не добавлять всё больше новых возможностей. Предыдущий аудит показал, что основная идея starter сильная: `AGENTS.md` -> `PROJECT_STATE.md` -> индекс нужной зоны -> 1-3 релевантных файла. Главные риски сейчас: смешение чистого шаблона с историей разработки, заполненные примеры в рабочих папках, дублирование правил, mutable-состояние в `AUTOPILOT.md`, ручной checklist вместо автоматической проверки.

Работа идёт итеративно: одна фаза -> правки -> проверки -> короткий вывод -> следующая фаза.

## Принцип работы

После каждой фазы:

- проверить diff;
- проверить, не появились ли лишние файлы или новая обязательная ветка чтения;
- запустить релевантные проверки;
- обновить этот план: что сделано, что осталось, какой вывод;
- только потом переходить дальше.

## Фазы

### Фаза 1. Разделить чистый шаблон и историю разработки

- [x] Просмотреть `plans/`, `retrospectives/`, `experiments/` и определить, что должно остаться в release-версии starter.
- [x] Предложить минимальный clean-template набор: README/TEMPLATE, 1-2 примера, без старой рабочей истории в ежедневном маршруте Codex.
- [x] Перенести или пометить лишнюю историю так, чтобы новый Codex не считал её обязательным контекстом.
- [x] Проверить `PROJECT_STATE.md`, `STRUCTURE.md`, `QUALITY_CHECKLIST.md` на соответствие новому маршруту.
- [x] Вывод после фазы: стало ли меньше шума для нового окна Codex.

**Вывод Фазы 1:** история разработки starter перенесена в `maintainer/history/`. В `plans/`, `retrospectives/`, `experiments/` остались чистые рабочие входы: README/TEMPLATE и текущий активный план. `PROJECT_STATE.md`, `STRUCTURE.md`, `QUALITY_CHECKLIST.md`, `README.md`, `AGENTS.md` и README рабочих папок теперь явно объясняют, что `maintainer/` читается только при обслуживании самого starter. Новый Codex получает меньше шума и меньше риска принять старые планы/ретро/эксперименты за текущий проектный контекст.

Дополнительно во время проверки найден Windows-баг в `.codex/hooks/pre_tool_use_policy.py`: PowerShell pipe передавал JSON с BOM/кодировкой так, что `sys.stdin` декодировал payload неверно и policy возвращал разрешение. Hook переведён на чтение `sys.stdin.buffer.read().decode("utf-8-sig")`, после чего smoke-test корректно различает опасные и безопасные команды.

**Проверки Фазы 1:**

- [x] `git diff --check`
- [x] локальные markdown-ссылки
- [x] `scripts/security-audit.ps1`
- [x] `scripts/user-project-safety-check.ps1`
- [x] hook smoke-test

### Фаза 2. Очистить рабочие placeholders от конкретных примеров

- [x] Проверить `ai-clone/` и `mastery/` на конкретные данные, которые выглядят как реальный пользовательский контекст.
- [x] Перенести заполненный пример SyncDesk/технического фаундера в `examples/`, если он нужен как демонстрация.
- [x] Сделать корневой `ai-clone/` нейтральным placeholder-слоем.
- [x] Проверить, что `POST_AUTOPILOT.md` по-прежнему может заполнить `ai-clone/` через интервью.
- [x] Вывод после фазы: новый проект больше не наследует чужую личность или SaaS-предпочтения.

**Вывод Фазы 2:** `mastery/` уже был нейтральным, а корневой `ai-clone/` очищен от SyncDesk, SaaS-лексики и конкретного профиля фаундера. Заполненный пример сохранён в `examples/syncdesk/ai-clone/` и добавлен в `examples/README.md` как вымышленная демонстрация. Теперь новый проект не наследует чужой голос, SaaS-предпочтения и feedback-правила, но пользователь всё ещё может посмотреть пример заполнения.

**Проверки Фазы 2:**

- [x] поиск SyncDesk/enterprise/SaaS-конкретики в корневых `ai-clone/` и `mastery/`
- [x] локальные markdown-ссылки
- [x] `git diff --check`
- [x] `scripts/security-audit.ps1`
- [x] `scripts/user-project-safety-check.ps1`

### Фаза 3. Развести сценарий AUTOPILOT и состояние прохождения

- [x] Проанализировать текущий frontmatter `AUTOPILOT.md` и `POST_AUTOPILOT.md`.
- [x] Спроектировать отдельный state-файл, например `.codex/autopilot-state.yml`, без усложнения пользовательского маршрута.
- [x] Обновить инструкции так, чтобы `AUTOPILOT.md` оставался стабильным сценарием, а state менялся отдельно.
- [x] Проверить resume-сценарий: Codex понимает, где продолжать после обрыва.
- [x] Вывод после фазы: сценарий меньше портится во время прохождения.

**Вывод Фазы 3:** изменяемое состояние первого и второго онбординга вынесено в `.codex/autopilot-state.yml`. `AUTOPILOT.md` и `POST_AUTOPILOT.md` больше не начинаются с YAML-frontmatter и остаются стабильными сценариями. `AGENTS.md`, `autopilot/flows/`, `autopilot/NEW_WINDOW_TEST.md`, `.codex/README.md`, `README.md`, `STRUCTURE.md`, `QUALITY_CHECKLIST.md` и `templates/AGENTS.md.tmpl` обновлены под новую схему. Resume-сценарий теперь опирается на `autopilot.current_stage`, `autopilot.current_flow`, `autopilot.last_completed_step` и `autopilot.last_completed_substep` в state-файле.

**Проверки Фазы 3:**

- [x] `AUTOPILOT.md` и `POST_AUTOPILOT.md` не начинаются с YAML-frontmatter
- [x] `.codex/autopilot-state.yml` содержит baseline state
- [x] поиск старой схемы в рабочих инструкциях
- [x] локальные markdown-ссылки
- [x] `git diff --check`
- [x] `scripts/security-audit.ps1`
- [x] `scripts/user-project-safety-check.ps1`

### Фаза 4. Сократить дублирование правил

- [x] Сравнить `AGENTS.md`, `AUTOPILOT.md`, `POST_AUTOPILOT.md`, `templates/AGENTS.md.tmpl`, `templates/PROJECT_STATE.md.tmpl`.
- [x] Оставить bootstrap-правила в `AGENTS.md`, сценарные правила в `AUTOPILOT.md`, финальные проектные правила в templates.
- [x] Убрать или смягчить повторы, которые могут расходиться со временем.
- [x] Проверить, что стартовый маршрут нового Codex остался понятным.
- [x] Вывод после фазы: меньше drift-риска между файлами.

**Вывод Фазы 4:** корневой `AGENTS.md` ужат до bootstrap-правил для starter-template: AUTOPILOT-сторож, короткий маршрут обслуживания, правила работы с изменениями, безопасность и язык. Подробные финальные правила пользовательского проекта остаются в `templates/AGENTS.md.tmpl`, а сценарная логика - в `AUTOPILOT.md` и `POST_AUTOPILOT.md`. Это снижает drift-риск: теперь при правке lifecycle, масштаба проекта, review-cycle или skills/browser не нужно синхронно менять корневой `AGENTS.md`.

**Проверки Фазы 4:**

- [x] `AGENTS.md` не дублирует финальные template-блоки `Масштаб проекта`, `Review-Cycle`, `Skills/Browser`
- [x] стартовый маршрут `AGENTS.md` -> `PROJECT_STATE.md` -> нужный сценарий остаётся понятным
- [x] локальные markdown-ссылки
- [x] `git diff --check`
- [x] `scripts/security-audit.ps1`
- [x] `scripts/user-project-safety-check.ps1`

### Фаза 5. Сделать проверки механическими

- [x] Спроектировать один общий `starter-lint` или расширить существующие scripts без лишней зависимости.
- [x] Проверять `.codex/autopilot-state.yml`, root `.business/`, локальные markdown-ссылки, UTF-8/mojibake, hook smoke-test, `git diff --check`, старые agent-specific следы в рабочих инструкциях.
- [x] Добавить Windows-first запуск и понятные сообщения об ошибках.
- [x] Подключить проверку к `QUALITY_CHECKLIST.md` и, если уместно, к GitHub Actions.
- [x] Вывод после фазы: Codex может сам проверить starter перед публикацией.

**Вывод Фазы 5:** добавлен `scripts/starter-lint.py` без сторонних зависимостей. Он проверяет baseline `.codex/autopilot-state.yml`, отсутствие YAML-frontmatter в сценариях, отсутствие корневой `.business/`, локальные markdown-ссылки, явный mojibake, hook smoke-test, `git diff --check` и старые agent-specific следы в рабочих инструкциях. Lint подключён в `README.md`, `QUALITY_CHECKLIST.md` и `.github/workflows/security-audit.yml` перед `security-audit`.

**Проверки Фазы 5:**

- [x] `python scripts/starter-lint.py`
- [x] `scripts/security-audit.ps1`
- [x] `scripts/user-project-safety-check.ps1`
- [x] `git diff --check`

### Фаза 6. Уточнить Windows/Linux маршруты команд

- [x] Проверить README, AUTOPILOT, TROUBLESHOOTING, scripts на команды, которые ведут себя по-разному в PowerShell и bash.
- [x] Сделать Windows PowerShell first, Git Bash/Linux как отдельный путь.
- [x] Убрать неочевидные glob-примеры, которые ломаются в PowerShell.
- [x] Проверить PowerShell-версии scripts и зафиксировать bash-ограничения.
- [x] Вывод после фазы: пользователь на Windows не попадает в ложные ошибки.

**Вывод Фазы 6:** `.gitattributes` расширен до явной LF-политики для Markdown, templates, TOML, JSON, YAML, Python, PowerShell, shell-скриптов и sample-файлов. `starter-lint` теперь проверяет эту политику автоматически. В `README.md`, `TROUBLESHOOTING.md`, `AUTOPILOT.md` и `QUALITY_CHECKLIST.md` уточнены Windows/PowerShell-first маршруты: PowerShell-команды идут основным путём для Windows, а bash-команды явно подписаны как macOS/Linux/Git Bash. Ручной hook smoke-test теперь есть в двух вариантах, а publication audit начинается со `starter-lint`.

**Проверки Фазы 6:**

- [x] `python scripts/starter-lint.py`
- [x] `git diff --check`
- [x] `scripts/security-audit.ps1`
- [x] `scripts/user-project-safety-check.ps1`

**Наблюдение:** `git diff --check` проходит, но Git всё ещё печатает предупреждения о будущей замене CRLF на LF для части уже изменённых файлов рабочей копии. Это ожидаемо после добавления `.gitattributes`; фактическую нормализацию лучше делать отдельным именованным шагом перед финальным commit, чтобы diff line endings не смешался с логическими правками.

### Фаза 7. Актуализировать Codex-native surfaces

- [x] Сверить `.codex/hooks.json`, `.codex/config.toml`, `.agents/skills/README.md` с актуальной официальной документацией Codex.
- [x] Проверить формат output hook-policy и matcher.
- [x] Уточнить README и `.codex/README.md`, если схема или формулировки устарели.
- [x] Не добавлять model/sandbox/approval defaults без реальной причины.
- [x] Вывод после фазы: starter остаётся Codex-native, а не просто markdown-методологией.

**Вывод Фазы 7:** Codex manual helper не смог скачать `codex-manual.md` из-за timeout, поэтому сверка выполнена через официальный fallback на `developers.openai.com/codex/*`. `.codex/hooks.json` обновлён: matcher стал точным `^Bash$`, hook-команда резолвит repo root через `git rev-parse --show-toplevel`, Windows-команда явно декодирует путь как UTF-8 и не ломается в папках с кириллицей, добавлен `statusMessage`. `.codex/hooks/pre_tool_use_policy.py` переведён на актуальный hook output `hookSpecificOutput.permissionDecision: deny|allow`. `starter-lint` теперь проверяет регистрацию hook и новый формат output. `.codex/README.md`, `.agents/skills/README.md`, `QUALITY_CHECKLIST.md`, `TROUBLESHOOTING.md` и `prompts/setup/03-security.md` обновлены под новую схему. `.codex/config.toml` оставлен минимальным: model/sandbox/approval defaults не добавлялись.

**Проверки Фазы 7:**

- [x] `python scripts/starter-lint.py`
- [x] `git diff --check`
- [x] `scripts/security-audit.ps1`
- [x] `scripts/user-project-safety-check.ps1`
- [x] hook smoke-test из подпапки с кириллицей в пути: опасный пример даёт `permissionDecision: deny`, безопасный пример даёт `permissionDecision: allow`

**Наблюдение:** `git diff --check` проходит, но Git продолжает предупреждать о будущей LF-нормализации файлов, изменённых до введения `.gitattributes`. Это остаётся отдельным механическим шагом перед финальным commit.

### Фаза 8. Финальный большой аудит

- [x] Пройти `QUALITY_CHECKLIST.md`.
- [x] Запустить все доступные проверки: PowerShell safety/audit, hook smoke-test, markdown links, `git diff --check`, новый `starter-lint`, если он появится.
- [x] Проверить чистоту git status и staged scope.
- [x] Составить итоговый аудит: что стало лучше, что сознательно оставлено, какие риски остались.
- [x] Вывод после фазы: starter готов к тестовому AUTOPILOT.

**Вывод Фазы 8:** финальный аудит подтверждает, что starter стал чище как шаблон для Codex: история разработки вынесена в `maintainer/history/`, рабочие `plans/`, `retrospectives/`, `experiments/` больше не тащат старые прогоны в обычный маршрут чтения, `PROJECT_STATE.md` снова отражает текущий фокус, root `ai-clone/` нейтрален, SyncDesk-пример лежит в `examples/`, mutable state вынесен в `.codex/autopilot-state.yml`, `starter-lint` закрывает основные структурные проверки, а Codex-native hook обновлён под актуальный output.

**Что сознательно оставлено:** `POST_AUTOPILOT.md`, `ai-clone/` и `mastery/` остаются в starter как optional-второй этап, но их заполнение регулируется privacy-gate. `maintainer/history/` остаётся в репозитории как история решений, но не входит в обычный маршрут нового Codex-окна. `.codex/config.toml` оставлен минимальным и не задаёт model/sandbox/approval defaults.

**Оставшиеся риски перед публикацией:**

- Нужно выполнить отдельную LF-нормализацию перед финальным commit, чтобы Git перестал предупреждать о `CRLF will be replaced by LF` в уже изменённых файлах.
- Нужно прогнать тестовый AUTOPILOT в безопасной копии или отдельном worktree, чтобы проверить поведение нового окна не только механически, но и сценарно.
- Codex manual helper во время фазы 7 не достучался до `developers.openai.com` из-за timeout; hook-схема сверялась через официальный web fallback, но перед релизом полезно повторить docs check при стабильной сети.

**Проверки Фазы 8:**

- [x] `python scripts/starter-lint.py`
- [x] `scripts/security-audit.ps1`
- [x] `scripts/user-project-safety-check.ps1`
- [x] `git diff --check`
- [x] `.codex/autopilot-state.yml` содержит baseline state
- [x] root `.business/` отсутствует и не tracked
- [x] staged scope пустой: `git diff --cached --name-status` без вывода
- [x] старые maintainer-файлы перенесены в `maintainer/history/`, а рабочие папки содержат только текущие README/TEMPLATE/активный план

### Фаза 9. Тестовый AUTOPILOT

- [x] Подготовить безопасную тестовую копию или отдельный worktree.
- [x] Прогнать `autopilot/NEW_WINDOW_TEST.md`.
- [x] Проверить сценарии `lite`, `standard`, `deep` хотя бы smoke-level.
- [x] Убедиться, что тестовые изменения не попали в основной starter.
- [x] Записать один главный следующий пункт улучшения после теста.

**Вывод Фазы 9:** тестовый AUTOPILOT прогнан в безопасной копии без `.git`: `C:\Users\Arseniy\OneDrive\Рабочий стол\codex-starter-autopilot-test-20260621-232638`. Smoke-harness проверил baseline state, стартовую AUTOPILOT-фразу, режим обслуживания starter без запуска AUTOPILOT, audit-without-edits, route `common.md` -> выбранный flow, ограничения `lite`, запрет deep-файлов в `standard`, `MVP vs later` в `deep`, no-git ветку без `git init`, preview/confirmation перед заменой `AGENTS.md` и `PROJECT_STATE.md`. Отдельно проверено, что в тестовой копии `user-project-safety-check.ps1` проходит без `.git`, hook блокирует опасную команду, `.business/` не создаётся сама по себе.

**Что сломалось и исправлено:** первый smoke выявил, что `AUTOPILOT.md` явно говорит про `lite` как 3-5 коротких бизнес-файлов, но `autopilot/flows/lite.md` сам по себе не повторял числовую цель. Исправлено: в `lite.md` добавлена строка `Цель lite - 3-5 коротких бизнес-файлов`.

**Один следующий пункт улучшения:** перед финальным commit сделать отдельную LF-нормализацию и затем повторить `starter-lint`/audit, чтобы Git warnings про `CRLF will be replaced by LF` не смешивались с логическими правками.

**Пост-аудит после Фазы 9:** LF-нормализация выполнена отдельным механическим шагом: `git ls-files --eol` больше не показывает `w/crlf` или `w/mixed`, `git diff --check` проходит без warning. Повторены проверки `python scripts/starter-lint.py`, `scripts/security-audit.ps1`, `scripts/user-project-safety-check.ps1`. Codex manual helper повторно запускался, но вернул HTTP 403 для `codex-manual.md`; актуальность Codex surfaces повторно сверена через официальный web fallback `developers.openai.com`. Две тестовые копии AUTOPILOT на рабочем столе удалены после проверки путей.

## Критерии готовности

- [x] Новый Codex понимает starter через короткий маршрут и не читает историю разработки как обязательный контекст.
- [x] Корневые placeholders не содержат конкретного чужого пользовательского профиля.
- [x] `AUTOPILOT.md` не смешивает сценарий и mutable state или смешивает это осознанно с понятной причиной.
- [x] Основные правила не дублируются в конфликтующих местах.
- [x] Есть механическая проверка качества starter перед публикацией.
- [x] Windows-путь запуска проверок понятен и не падает из-за WSL/bash.
- [x] Codex-native файлы актуальны и не задают рискованные defaults.
- [x] Финальный аудит и тестовый AUTOPILOT пройдены.

## Риски

- Слишком сильная чистка может убрать полезные примеры. Противодействие: переносить примеры в `examples/`, а не удалять без причины.
- Разделение state и сценария может усложнить AUTOPILOT. Противодействие: сначала спроектировать минимальный state-файл и проверить resume-сценарий.
- Механический lint может стать ещё одной тяжёлой функцией. Противодействие: один простой скрипт без новых зависимостей.
- Обновление Codex hooks может зависеть от актуальной документации. Противодействие: сверять с официальными docs и фиксировать bounded uncertainty, если docs недоступны.

## Открытые вопросы

- Решено в Фазе 1: история разработки starter перенесена в `maintainer/history/`, а обычный маршрут чтения нового Codex-окна туда не ведёт.
- Решено в Фазе 3: state переносится в `.codex/autopilot-state.yml`, а `AUTOPILOT.md` и `POST_AUTOPILOT.md` остаются стабильными сценариями.
- Решено в Фазе 5: `starter-lint` сделан Python-скриптом без сторонних зависимостей, чтобы одинаково запускаться из Windows PowerShell, macOS/Linux и CI.

---

## Итог

- **Реализовано целиком:** да, фазы 1-9 выполнены.
- **Что сделано:** starter очищен от лишней истории в ежедневном маршруте, примеры отделены от placeholders, mutable state вынесен из сценариев, root `AGENTS.md` сокращён до bootstrap, добавлен `starter-lint`, уточнены Windows/Linux маршруты, обновлены Codex-native hooks, проведён финальный аудит и smoke-прогон AUTOPILOT в безопасной копии.
- **Что не сделано и почему:** живой новый Codex-чат оставлен на самый конец по решению пользователя; commit/stage не выполнялись без отдельного подтверждения.
- **Что добавить в бэклог:** если перед релизом manual helper снова будет доступен, повторить Codex manual check; сейчас helper вернул HTTP 403, поэтому использован официальный web fallback.
- **Уроки:** тестовая копия реально полезна: она поймала недосказанность в `lite.md`, которую обычный lint не видел.
