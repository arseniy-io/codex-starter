# Codex project settings

Эта папка хранит project-level настройки Codex для шаблона.

## Что здесь лежит

- `config.toml` - минимальный project config без рискованных переопределений.
- `hooks.json` - project hook registration для Codex.
- `hooks/pre_tool_use_policy.py` - локальная проверка команд и tool input на опасные паттерны.

## Почему так

Codex использует `AGENTS.md` для durable-инструкций, `.codex/config.toml` для project config и hooks для детерминированных проверок вокруг tool calls. В этом шаблоне активные настройки сделаны консервативно: они не меняют sandbox/approval/model пользователя, а только дают проверяемую основу для безопасности.

## Как работает hook

Hook подключён через `.codex/hooks.json` к `PreToolUse` для shell-команд. Скрипт читает JSON из stdin, ищет опасные команды и возвращает JSON с `decision: "block"` при срабатывании.

При первом запуске в новом окружении Codex может попросить trust-review для project-local hooks. Это нормально: пользователь должен понимать, что repo-level hook запускает локальный Python-скрипт.

Если схема hooks изменилась, сверяйся с официальной документацией Codex:

https://developers.openai.com/codex/hooks
