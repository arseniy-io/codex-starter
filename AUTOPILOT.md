# AUTOPILOT - онбординг Codex Starter

> Это файл для Codex. Если ты пользователь и читаешь это вручную: открой проект в Codex и напиши любую фразу. Codex сам продолжит с нужного шага.

## Панель управления для Codex

**Цель:** настроить проект так, чтобы новое окно Codex быстро понимало задачу и читало минимум файлов.

**Главный результат:** `AGENTS.md`, `PROJECT_STATE.md`, `business/INDEX.md`, `business/life-metrics.md`, `business/raw/` и короткий набор рабочих контекстных файлов.

**Когда запускать:** только если `autopilot.completed: false` в `.codex/autopilot-state.yml` и пользователь готов настраивать проект.

**Когда не запускать:** если пользователь просит аудит, оценку, список улучшений или обслуживает сам starter-template.

**Главное правило:** не создавай файл, если непонятно, когда Codex будет читать его в будущих задачах.

**Критерий успеха:** после онбординга новое окно Codex понимает проект через `AGENTS.md` -> `PROJECT_STATE.md` -> индекс нужной зоны -> 1-3 релевантных файла.

## State-файл

Изменяемое состояние онбординга хранится в `.codex/autopilot-state.yml`, секция `autopilot`.

`AUTOPILOT.md` - стабильный сценарий. Не записывай state, ответы пользователя и статус прохождения в заголовок этого файла.

## Правила для Codex

1. Перед стартом открой `.codex/autopilot-state.yml` и прочитай секцию `autopilot`.
2. Иди по шагам 1-10 и обновляй state-файл после каждого шага.
3. Если сессия прервалась, прочитай `autopilot.current_stage`, `autopilot.current_flow`, `autopilot.last_completed_step` и `autopilot.last_completed_substep`, затем продолжи с ближайшего незавершённого действия.
4. Не включай рискованные режимы без подтверждений пользователя.
5. Перед shell-командами объясняй, зачем они нужны.
6. Говори коротко: пользователь учится, ему нужна ясность, а не лекция.
7. Не коммить `business/` после заполнения реальными данными.
8. Если AUTOPILOT проходит в тестовой копии, все изменения, планы, ретро и отчёты пиши только внутри этой копии. Не меняй основной starter.
9. Все Markdown-файлы сохраняй в UTF-8, чтобы отчёты читались без mojibake/вопросиков.
10. Не говори, что AUTOPILOT завершён, пока `.codex/autopilot-state.yml` не показывает `autopilot.completed: true`, `autopilot.current_stage: done`, `autopilot.last_completed_step: 10`.

## State-поля

- `current_stage` - где продолжать: `start`, `project_type`, `stack`, `codex_surfaces`, `security`, `git`, `business_pause`, `business_context`, `final_files`, `final_commit`, `done`.
- `current_flow` - выбранный flow шага 8: `lite`, `standard`, `deep` или `null`.
- `last_completed_step` - последний завершённый номер шага: `0-10`. Для подшагов шага 8 не смешивай номер с текстом.
- `last_completed_substep` - короткий подшаг, например `depth_selected`, `lite_files_created`, `standard_files_created`, `deep_products`, `business_index_checked`.

Если `autopilot.current_stage: business_context`, сначала открой `autopilot/flows/common.md`, затем только файл из `autopilot.current_flow`.

## Режимы работы

- **Онбординг:** если `autopilot.completed: false` и пользователь готов настраивать проект, выполняй шаги 1-10 и меняй файлы.
- **Аудит:** если пользователь просит “проанализировать”, “оценить”, “найти улучшения” или “разобрать прохождение AUTOPILOT”, только читай файлы и дай список улучшений. Не редактируй и не коммить.
- **Правка шаблона:** меняй `AUTOPILOT.md`, `templates/`, `plans/`, `retrospectives/` только после прямой просьбы внести изменения. Делай это отдельной веткой и отдельным коммитом.
- **Завершённый AUTOPILOT:** если `autopilot.completed: true`, не продолжай шаги заново, пока пользователь явно не попросит повторный онбординг.

---

## Шаг 1. Приветствие и калибровка

Скажи:

> «Привет. Я проведу тебя через настройку проекта под Codex: контекст, правила, планы, ретро и безопасность. Мы выберем масштаб настройки позже: `lite`, `standard` или `deep`. Что за проект ты делаешь одним предложением?»

Затем спроси ОС: Windows / macOS / Linux. Запиши в `.codex/autopilot-state.yml`: `autopilot.os: windows|macos|linux`.

Проверь `.vscode/settings.json`: `business/` должна быть видна в сайдбаре.

Обнови state: `last_completed_step: 1`, `current_stage: project_type`, `last_completed_substep: null`.

## Шаг 2. Тип проекта

Спроси:

> «Какой тип проекта: коммерческий, некоммерческий, open-source, внутренний инструмент или учебный?»

Запиши `autopilot.project_type` в `.codex/autopilot-state.yml`.

Обнови state: `last_completed_step: 2`, `current_stage: stack`, `last_completed_substep: null`.

## Шаг 3. Стек

Спроси стек: Next.js/React, Vue/Nuxt, Svelte, Python, Node backend, mobile, low-code, другое, пока не знаю.

Запиши `autopilot.stack` в `.codex/autopilot-state.yml`.

Обнови state: `last_completed_step: 3`, `current_stage: codex_surfaces`, `last_completed_substep: null`.

## Шаг 4. Codex-поверхности

Объясни коротко:

- `AGENTS.md` - durable-инструкции для репозитория.
- `.codex/config.toml` - project-level настройки Codex.
- `.codex/hooks.json` - подключение project hooks.
- `.codex/hooks/` - deterministic guardrails.
- `.agents/skills/` - локальные repo-skills, если проекту нужны reusable workflows.

Покажи, что эти папки/файлы существуют или создай отсутствующие пустые папки.

Обнови state: `last_completed_step: 4`, `current_stage: security`, `last_completed_substep: null`.

## Шаг 5. Безопасность

Сделай три проверки:

1. В `.gitignore` есть `.env`, `.env.local`, `.codex/config.local.toml`.
2. User project safety check проходит:
   - Windows/PowerShell: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/user-project-safety-check.ps1`;
   - macOS/Linux/Git Bash: `bash scripts/user-project-safety-check.sh`.
   Если `autopilot.os: windows`, сначала используй PowerShell-вариант. Bash-вариант запускай только если пользователь явно работает из Git Bash или macOS/Linux.
3. `.codex/hooks.json` подключает `PreToolUse` hook для shell-команд.
4. `.codex/hooks/pre_tool_use_policy.py` блокирует опасный пример:

Windows/PowerShell:

```powershell
'{"tool":"shell","input":{"command":"rm -rf tmp"}}' | python .codex/hooks/pre_tool_use_policy.py
```

macOS/Linux/Git Bash:

```bash
echo '{"tool":"shell","input":{"command":"rm -rf tmp"}}' | python .codex/hooks/pre_tool_use_policy.py
```

Объясни пользователю: `user-project-safety-check` проверяет только общие риски проекта. `scripts/security-audit.*` нужен для публикации самого starter-template и содержит дополнительные проверки автора/бренда. Hook-policy не заменяет осторожность, но ловит очевидно опасные команды. В новом окружении Codex может попросить trust-review для project-local hooks.

Обнови state: `last_completed_step: 5`, `current_stage: git`, `last_completed_substep: null`.

## Шаг 6. Git

Проверь:

```bash
git rev-parse --is-inside-work-tree
git config user.name
git config user.email
git status --short --branch
```

Если папка не является git-репозиторием, не запускай `git init` автоматически. Скажи: «Git здесь не инициализирован, поэтому шаги stage/commit пропущу. Онбординг можно продолжить, но финальный commit будет недоступен в этой копии». Обнови state как обычно и запиши `last_completed_substep: git_unavailable`.

Если git доступен и имя/email пустые, спроси пользователя и настрой локально для проекта.

Обнови state: `last_completed_step: 6`, `current_stage: business_pause`, `last_completed_substep: git_checked|git_unavailable`.

## Шаг 7. Пауза перед бизнес-интервью

Скажи:

> «Техническая часть готова. Дальше заполним `business/` - это контекст, который будет экономить токены и улучшать решения. Продолжаем сейчас или сделаем паузу?»

Если пользователь выбирает паузу, остановись после обновления state: `last_completed_step: 7`, `current_stage: business_pause`, `last_completed_substep: paused_before_business`.

Если пользователь продолжает, обнови state: `last_completed_step: 7`, `current_stage: business_context`, `last_completed_substep: business_started`, затем переходи к шагу 8 и выбери единую глубину онбординга: `lite`, `standard` или `deep`.

Если пользователь хочет быстрый старт, рекомендуй `lite`: минимальный `business/INDEX.md`, `business/life-metrics.md`, `business/raw/`, 3-5 коротких `business`-файлов, `PROJECT_STATE.md` и ближайший следующий шаг. Если видишь сильный deep-триггер, предупреди об этом и предложи `standard` или `deep`.

Не создавай файл, если непонятно, когда Codex будет читать его в будущих задачах.

## Шаг 8. Интервью и заполнение `business/`

Сначала выбери глубину онбординга и объясни её пользователю. Используй только одну шкалу:

- `lite` - маленький лендинг, личная страница, портфолио, локальная услуга, простой внутренний инструмент. Цель: 3-5 коротких бизнес-файлов, `business/life-metrics.md`, `business/raw/`, `PROJECT_STATE.md` и понятный следующий шаг. `ai-clone/` и `mastery/` остаются базовыми placeholder-слоями starter, но не заполняй их глубоко без прямой задачи про стиль, голос, предпочтения или методологию.
- `standard` - обычный продукт или коммерческий сайт средней сложности. Цель: 6-10 рабочих файлов, а не вся `business/`. Не создавай `roles-and-permissions`, `security-model`, `integrations`, `roadmap` и `execution` без явного deep-триггера.
- `deep` - SaaS, marketplace, продукт с ролями, платежами, интеграциями, пользовательскими данными или долгим roadmap. Цель: кроме обычного бизнес-контекста создать короткие файлы про scope, роли, данные, security/trust и интеграции.

Если пользователь просит пройти быстро или проект маленький, рекомендуй `lite` и скажи, что глубокое заполнение `ai-clone/` и `mastery/`, `POST_AUTOPILOT.md`, глубокие методологии и опциональные интеграции можно оставить на потом.

Целевой стартовый маршрут после онбординга: `lite` - 4-5 файлов всего, `standard` - 5-6 файлов всего, `deep` - 6-7 файлов всего вместе с `AGENTS.md`, `PROJECT_STATE.md`, `business/INDEX.md` и `business/life-metrics.md`. `business/raw/` не входит в стартовый маршрут.

Скажи коротко:

> «Сейчас выберем глубину онбординга: `lite`, `standard` или `deep`. Я дам рекомендацию по масштабу проекта, но финальный выбор за тобой.»

Оцени проект по ответам шагов 1-3 и скажи:

> «Моя рекомендация: `[lite/standard/deep]`, потому что [1-2 причины]. Выбираем так или хочешь другой режим?»

Запиши выбор в `.codex/autopilot-state.yml`:

```yaml
autopilot:
  onboarding_depth: lite|standard|deep
```

Обнови state: `last_completed_step: 8`, `current_stage: business_context`, `current_flow: lite|standard|deep`, `last_completed_substep: depth_selected`.

Дальше читай только нужные инструкции:

1. Всегда прочитай `autopilot/flows/common.md`.
2. Если выбран `lite`, прочитай `autopilot/flows/lite.md`.
3. Если выбран `standard`, прочитай `autopilot/flows/standard.md`.
4. Если выбран `deep`, прочитай `autopilot/flows/deep.md`.
5. После выбранного flow выполни раздел `Финал шага 8` из `autopilot/flows/common.md`, затем вернись к этому файлу и переходи к шагу 9.

## Шаг 9. Генерация финального `AGENTS.md` и проверка рабочего цикла

Возьми `templates/AGENTS.md.tmpl`, заполни:

- `{{PROJECT_NAME}}`
- `{{PROJECT_ONE_LINER}}`
- `{{STACK}}`
- `{{LANGUAGE_RULE}}`

Спроси язык общения. По умолчанию: «Всегда отвечай на русском».

Возьми `templates/PROJECT_STATE.md.tmpl`, заполни:

- `{{PROJECT_NAME}}`
- `{{PROJECT_ONE_LINER}}`
- `{{CURRENT_FOCUS}}` - текущая стадия и главный фокус после онбординга;
- `{{PRIMARY_PLAN_OR_CONTEXT}}` - 1 актуальный план или главный контекстный файл;
- `{{KEY_CONTEXT_FILES}}` - 2-5 файлов, которые чаще всего нужны для правильных решений. Для `lite` это может быть 1-2 бизнес-файла; для `deep` добавь risk/trust входы вроде ролей, данных, интеграций, security или MVP scope;
- `{{NEXT_STEP}}` - ближайший понятный следующий шаг.

Если проект `deep`, добавь в `PROJECT_STATE.md` короткий блок `Deep-карта`:

- `Scope/MVP` - где лежит текущий рабочий scope;
- `Data` - где описаны данные, приватность и границы;
- `Roles` - где описаны роли и права;
- `Integrations` - где описаны API, webhooks или внешние системы;
- `Trust/Security` - где описаны риски доверия, audit, export, payments или AI safety;
- `MVP vs later` - где видно, что делаем сейчас и что отложено.

В этом блоке указывай только входные файлы, не пересказывай их содержимое.

Перед записью покажи пользователю короткий preview:

1. Что изменится в `AGENTS.md`: 5-8 пунктов правил, язык общения, маршрут чтения.
2. Что изменится в `PROJECT_STATE.md`: проект, текущий фокус, ключевые файлы, следующий шаг.
3. Какие старые AUTOPILOT-инструкции уйдут из корневого `AGENTS.md`.

Спроси подтверждение: «Можно заменить `AGENTS.md` и `PROJECT_STATE.md` этими версиями?»

Только после подтверждения перезапиши корневой `AGENTS.md`. Почему: стартовый `AGENTS.md` содержит AUTOPILOT-сторож, а после онбординга нужен чистый проектный файл.

Только после подтверждения создай или обнови корневой `PROJECT_STATE.md`. Почему: это короткий вход для новых окон Codex, чтобы не читать все папки ради понимания проекта.

Проверь вход нового окна Codex:

1. Назови маршрут чтения для новой сессии: `AGENTS.md` -> `PROJECT_STATE.md` -> `business/INDEX.md` -> 1-3 нужных файла. Если задача про живые цифры, добавляется `business/life-metrics.md`.
2. Для `lite` маршрут должен занимать 4-5 файлов всего, для `standard` - 5-6 файлов всего, для `deep` - 6-7 файлов всего вместе с короткой deep-картой в `PROJECT_STATE.md`.
3. Если для понимания проекта нужно больше файлов, не продолжай онбординг. Сначала сократи `PROJECT_STATE.md`, обнови `business/INDEX.md` и убери лишние файлы из обязательного чтения.
4. Это не аудит всей папки. Проверяй только стартовый маршрут и минимальный набор чтения.
5. Для отдельной проверки starter перед публикацией используй `autopilot/NEW_WINDOW_TEST.md`.

Проверка рабочего цикла без учебного мусора:

1. Покажи пользователю, где лежат `plans/TEMPLATE.md` и `retrospectives/TEMPLATE.md`.
2. Коротко объясни цикл `plan → implement → verify → retro`.
3. Не создавай `HELLO.md`, hello-план и hello-ретро по умолчанию.
4. Если пользователь хочет живую демонстрацию, создай её только в `examples/hello-cycle/`, а не в корне проекта.
5. Для реальной следующей задачи создай настоящий план с названием этой задачи.
6. Обнови `PROJECT_STATE.md`: поставь актуальный план или контекст и ближайший следующий шаг.

Почему: учебные файлы полезны для демонстрации, но в реальном проекте они быстро превращаются в шум. В `plans/` и `retrospectives/` должны попадать реальные задачи и заметные сессии.

Обнови state: `last_completed_step: 9`, `current_stage: final_commit`, `current_flow: null`, `last_completed_substep: final_files_created`.

Перед переходом к шагу 10 проверь, что `AGENTS.md` и `PROJECT_STATE.md` уже записаны после preview/подтверждения, а стартовый маршрут укладывается в лимит выбранного flow. Если нет - не переходи к финалу, сначала исправь маршрут.

## Шаг 10. Финал и первый коммит

Сначала проверь, есть ли git-репозиторий:

```bash
git rev-parse --is-inside-work-tree
```

Если git недоступен, это не блокирует завершение AUTOPILOT в тестовой копии или локальной папке без repo. Скажи, что stage/commit пропущены из-за отсутствия `.git`, и переходи к финальному обновлению state-файла.

Если git доступен, перед коммитом:

1. Убедись, что `business/` есть в `.gitignore`. В starter она должна быть ignored по умолчанию, потому что после онбординга там реальные данные проекта.
2. Если `business/` когда-либо была tracked, сними её с tracking:

Windows/PowerShell:

```powershell
$trackedBusiness = git ls-files 'business/*'
if ($trackedBusiness) { git rm -r --cached business/ }
```

macOS/Linux/Git Bash:

```bash
if [ -n "$(git ls-files 'business/*')" ]; then git rm -r --cached business/; fi
```

3. Убедись, что `business/`, `.env` и локальные Codex config не попали в индекс.
4. Покажи `git status --short` и коротко объясни, какие файлы предлагаешь включить в первый коммит.

Если всё чисто и пользователь согласен, стейджи файлы поимённо. Не используй `git add -A` как основной путь.

Шаблон команды:

```bash
git add -- AGENTS.md PROJECT_STATE.md .gitignore .codex/config.toml .codex/hooks.json .codex/hooks/pre_tool_use_policy.py
```

Добавь к команде только те файлы, которые реально изменены и безопасны для первого коммита. Если список длинный, сначала покажи его пользователю и попроси подтверждение.

После stage покажи:

```bash
git status --short
```

Если в staged нет `business/`, `.env`, локальных config и лишних личных файлов, коротко покажи итог staged-файлов и спроси финальное подтверждение на commit.

Только после подтверждения сделай commit:

```bash
git commit -m "chore: initial setup via codex-starter"
```

Почему: даже первый коммит должен быть контролируемым. В обычной работе и в финале AUTOPILOT стейджить файлы поимённо.

Если пользователь хочет продолжать настройку, покажи `prompts/INDEX.md` и выдели три первых полезных промпта. Это optional follow-up, не условие завершения базового AUTOPILOT:

- `prompts/setup/01-voice-screenshot.md`
- `prompts/methodology/plan-critique.md`
- `prompts/methodology/10-reasons.md`

Обнови `.codex/autopilot-state.yml`:

```yaml
autopilot:
  completed: true
  current_stage: done
  current_flow: null
  last_completed_step: 10
  last_completed_substep: onboarding_complete
```

После обновления state-файла перечитай `.codex/autopilot-state.yml` и убедись, что там действительно `autopilot.completed: true`, `autopilot.current_stage: done`, `autopilot.last_completed_step: 10`. Только после этого говори, что онбординг завершён.

Скажи:

> «Онбординг завершён. Теперь в новом окне Codex сначала читает `AGENTS.md`, затем `PROJECT_STATE.md`, берёт только нужный контекст, пишет план, реализует, проверяет и оставляет ретро.»

Если пользователь хочет второй уровень настройки, предложи продолжить по `POST_AUTOPILOT.md`: личный контекст, mastery, feedback loop, контекст-инжиниринг и опциональные интеграции. Для `lite` и большинства быстрых проходов подчеркни, что это отдельный необязательный этап, а не часть базового онбординга.
