# Quality checklist

Используй перед публикацией шаблона или после крупной правки.

## Structure

- [ ] Каждая рабочая папка описана в `STRUCTURE.md`.
- [ ] `README.md` объясняет быстрый старт без устаревающих цен, тарифов и неподтверждённых обещаний.
- [ ] `AGENTS.md` содержит только устойчивые правила проекта.
- [ ] `AUTOPILOT.md` можно пройти по шагам без чтения исходного README.
- [ ] `AUTOPILOT.md` предлагает компактный и расширенный путь `.business/` и объясняет разницу.
- [ ] В чистом starter `AUTOPILOT.md` начинается с `completed: false`, `last_completed_step: 0`, `started_at: null` и не содержит заполненных `os`, `project_type`, `stack`.
- [ ] `POST_AUTOPILOT.md` можно пройти после первого онбординга, не раздувая `AGENTS.md`.

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
- [ ] Проверить, что AUTOPILOT предлагает компактный/расширенный путь `.business/`.
- [ ] Проверить, что после AUTOPILOT предлагается `POST_AUTOPILOT.md`.
- [ ] Проверить, что `plan → implement → verify → retro` объясняется без обязательного `hello-test` в корне проекта.
