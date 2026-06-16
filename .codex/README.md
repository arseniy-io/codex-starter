# Codex project settings

Эта папка хранит project-level настройки Codex для шаблона.

## Что здесь лежит

- `config.toml` - минимальный project config без рискованных переопределений.
- `hooks/pre_tool_use_policy.py` - локальная проверка команд и tool input на опасные паттерны.

## Почему так

Codex использует `AGENTS.md` для durable-инструкций, `.codex/config.toml` для project config и hooks для детерминированных проверок вокруг tool calls. В этом шаблоне активные настройки сделаны консервативно: они не меняют sandbox/approval/model пользователя, а только дают проверяемую основу для безопасности.

## Как подключать hook

Перед подключением проверь актуальный формат hooks в официальной документации Codex:

https://developers.openai.com/codex/hooks

Затем привяжи `hooks/pre_tool_use_policy.py` к pre-tool-use событию для shell/terminal tools. Скрипт читает JSON из stdin, ищет опасные команды и возвращает JSON с `decision: "block"` при срабатывании.
