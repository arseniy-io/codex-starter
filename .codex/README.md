# Codex project settings

Эта папка хранит project-level настройки Codex для шаблона.

## Что здесь лежит

- `config.toml` - минимальный project config без рискованных переопределений.
- `autopilot-state.yml` - изменяемое состояние первого и второго этапа онбординга.
- `hooks.json` - project hook registration для Codex.
- `hooks/pre_tool_use_policy.py` - локальная проверка команд и tool input на опасные паттерны.

## Почему так

Codex использует `AGENTS.md` для durable-инструкций, `.codex/config.toml` для project config и hooks для детерминированных проверок вокруг tool calls. `.codex/autopilot-state.yml` отделяет изменяемое состояние онбординга от стабильных сценариев `AUTOPILOT.md` и `POST_AUTOPILOT.md`. В этом шаблоне активные настройки сделаны консервативно: они не меняют sandbox/approval/model пользователя, а только дают проверяемую основу для безопасности.

## Как работает hook

Hook подключён через `.codex/hooks.json` к `PreToolUse` для shell-команд. Скрипт читает JSON из stdin, ищет опасные команды и возвращает `hookSpecificOutput.permissionDecision: "deny"` при срабатывании или `"allow"` для безопасного smoke-test примера.

Команда hook резолвит корень репозитория через `git rev-parse --show-toplevel`, поэтому не зависит от того, из какой подпапки Codex запустил shell-команду. Windows-команда явно декодирует путь как UTF-8, чтобы не ломаться в папках с кириллицей.

При первом запуске в новом окружении Codex может попросить trust-review для project-local hooks. Это нормально: пользователь должен понимать, что repo-level hook запускает локальный Python-скрипт.

Hook - это guardrail для очевидно опасных действий, а не полноценная security-граница. Не заменяй им review, `.gitignore`, staged-scope и явное подтверждение рискованных операций.

Если схема hooks изменилась, сверяйся с официальной документацией Codex:

https://developers.openai.com/codex/hooks
