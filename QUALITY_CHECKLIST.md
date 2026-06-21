# Quality checklist

Используй перед публикацией шаблона или после крупной правки.

## Structure

- [ ] Каждая рабочая папка описана в `STRUCTURE.md`.
- [ ] `README.md` объясняет быстрый старт без устаревающих цен, тарифов и неподтверждённых обещаний.
- [ ] `AGENTS.md` содержит только устойчивые правила проекта.
- [ ] `PROJECT_STATE.md` короткий и показывает текущий фокус, первые файлы для чтения и следующий шаг.
- [ ] `AUTOPILOT.md` можно пройти по шагам без чтения исходного README.
- [ ] `AUTOPILOT.md` выбирает один масштаб `lite`, `standard` или `deep`, а подробности шага 8 лежат в `autopilot/flows/`.
- [ ] Перед заменой финальных `AGENTS.md` и `PROJECT_STATE.md` AUTOPILOT показывает preview и ждёт подтверждения.
- [ ] В чистом starter `AUTOPILOT.md` начинается с `completed: false`, `current_stage: start`, `current_flow: null`, `last_completed_step: 0`, `last_completed_substep: null`, `started_at: null` и не содержит заполненных `os`, `project_type`, `stack`.
- [ ] `POST_AUTOPILOT.md` можно пройти после первого онбординга, не раздувая `AGENTS.md`.

## Adaptivity

- [ ] AUTOPILOT умеет выбрать глубину `lite`, `standard` или `deep`.
- [ ] `lite`-проект по умолчанию ограничен `PROJECT_STATE.md`, `.business/INDEX.md` и 3-5 короткими `.business`-файлами.
- [ ] Маленький проект не получает лишние `ai-clone/`, `mastery/` и большую библиотеку без причины.
- [ ] `standard`-проект по умолчанию ограничен 6-10 рабочими файлами, а не всей `.business/`.
- [ ] В `standard` не создаются `roles-and-permissions`, `security-model`, `integrations`, `roadmap` и `execution` без явного deep-триггера.
- [ ] Слабые deep-триггеры записываются как `Осторожно позже`, а не разворачиваются в отдельный risk/trust слой.
- [ ] Для коротких или мутных ответов пользователя AUTOPILOT отделяет факты, интерпретации и вопросы на потом.
- [ ] Сложный продукт с ролями, данными, платежами, API, файлами или интеграциями получает отдельный risk/trust слой.
- [ ] В `deep` есть блок `MVP vs later`, а новые файлы создаются только если влияют на MVP, trust/security или ближайшее решение.
- [ ] `PROJECT_STATE.md` для `deep` содержит короткую карту `Scope/MVP`, `Data`, `Roles`, `Integrations`, `Trust/Security`, `MVP vs later`.
- [ ] В личном экспертном проекте `.business/`, `ai-clone/` и `mastery/` не смешиваются.
- [ ] В `.business/INDEX.md` есть минимальный набор файлов, которые Codex обычно должен читать дальше.
- [ ] `PROJECT_STATE.md` не дублирует `.business/`, `ai-clone/`, `mastery/`, планы или ретро.
- [ ] В `PROJECT_STATE.md` указано не больше 2-5 ключевых файлов проекта.
- [ ] Новый Codex-маршрут короткий: `AGENTS.md` → `PROJECT_STATE.md` → индекс нужной зоны → 1-3 файла.
- [ ] У основных слоёв есть lifecycle: когда читать, когда обновлять и когда не трогать.
- [ ] Устаревшие файлы убраны из индексов или помечены как deprecated/archived.
- [ ] Планы, ретро и experiments не используются как постоянный источник истины вместо `PROJECT_STATE.md` и индексов.

## Stress Tests

- [ ] Тестовые копии не меняют основной starter: свои `AGENTS.md`, `PROJECT_STATE.md`, планы, ретро и отчёты они пишут только внутри своей папки.
- [ ] Общий starter хранит только сравнительные отчёты волн и методологические выводы, а не отчёты одного тестового проекта.
- [ ] Все Markdown-отчёты сохраняются в UTF-8 и читаются без mojibake/вопросиков.

## Codex-native

- [ ] Repo-инструкции лежат в `AGENTS.md`.
- [ ] Project-зона Codex лежит в `.codex/`.
- [ ] Локальные skills лежат в `.agents/skills/`.
- [ ] Config не переопределяет модель, sandbox или approvals без явной причины.
- [ ] Hooks подключаются только по актуальной официальной схеме Codex.

## Prompts

- [ ] Prompts не ссылаются на старые Claude/Anthropic настройки.
- [ ] Prompts не содержат точных цен, лимитов или тарифов без проверки актуальных источников.
- [ ] Prompts требуют официальную документацию для деплоя, платежей, MCP и внешних SDK.
- [ ] Prompts не предлагают опасные учебные действия на реальном коде.

## Safety

- [ ] `.env`, `.env.local`, `.env.*.local` игнорируются.
- [ ] `.codex/config.local.toml` игнорируется.
- [ ] `.business/` снимается с tracking после заполнения реальными данными.
- [ ] После заполнения `ai-clone/` privacy-gate зафиксировал решение: private tracked, ignored или safe summary only.
- [ ] `mastery/` не содержит длинных копий copyrighted-текста.
- [ ] Финальный commit делается только после просмотра staged-файлов и отдельного подтверждения пользователя.
- [ ] Pre-commit hook блокирует секреты и случайный коммит `.business/`.
- [ ] Security audit проходит: `scripts/security-audit.ps1` на Windows или `scripts/security-audit.sh` в bash/Git Bash.
- [ ] `.codex/hooks/pre_tool_use_policy.py` блокирует опасные shell/PowerShell примеры.

## Example

- [ ] `examples/coffeeshop/` содержит пример `AGENTS.md`.
- [ ] Пример показывает `.business/`, `plans/`, `retrospectives/`.
- [ ] Пример явно помечен как вымышленный.
- [ ] Пример не содержит реальных контактов, email, ключей или персональных данных.

## Final Test

- [ ] Открыть новый Codex-чат с чистым контекстом.
- [ ] Написать `привет`.
- [ ] Проверить, что AUTOPILOT стартует и ведёт по шагам.
- [ ] Проверить, что AUTOPILOT выбирает один масштаб `lite`, `standard` или `deep`.
- [ ] Проверить, что Codex читает `autopilot/flows/common.md` и только выбранный flow.
- [ ] Проверить, что после AUTOPILOT предлагается `POST_AUTOPILOT.md`.
- [ ] Проверить, что `plan → implement → verify → retro` объясняется без обязательного `hello-test` в корне проекта.
- [ ] В новом окне Codex может назвать текущий фокус и следующий шаг, не читая всю `.business/`.
- [ ] Для публикации starter пройти `autopilot/NEW_WINDOW_TEST.md` и записать один главный следующий пункт улучшения.
