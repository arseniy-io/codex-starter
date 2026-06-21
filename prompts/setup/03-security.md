# Guardrails безопасности Codex

**Когда брать:** до активной разработки и особенно до рискованных режимов без подтверждений.
**Что делает:** проверяет `.gitignore`, pre-commit hook и локальный policy-скрипт для опасных команд.
**Результат:** базовая защита от утечки секретов и случайного удаления файлов.

## Что защищаем

| Риск | Защита |
|---|---|
| Коммит `.env` | `.gitignore` + `.github/hooks/pre-commit.sample` |
| Массовое удаление | `.codex/hooks/pre_tool_use_policy.py` |
| Чтение `.env` целиком | правило в `AGENTS.md` + hook-policy |
| Отправка секретов наружу | pre-commit + hook-policy |

## Промпт

```prompt
Проверь и настрой guardrails безопасности для Codex Starter.

Сделай по шагам:
1. Проверь `.gitignore`: там должны быть `.env`, `.env.local`, `.env.*.local`, `.codex/config.local.toml`.
2. Проверь, что есть `.github/hooks/pre-commit.sample`, и объясни как включить его в `.git/hooks/pre-commit`.
3. Проверь `.codex/hooks/pre_tool_use_policy.py`.
4. Прогони два теста:
   - опасный: `rm -rf tmp` должен вернуть `permissionDecision: deny`;
   - безопасный: `git status --short` должен вернуть `permissionDecision: allow`.
5. Если Codex hooks надо подключить к lifecycle-событию, открой официальную документацию Codex hooks и не придумывай схему без проверки.

После каждого пункта коротко объясни: что проверил и почему это важно.
```

## Проверка

```bash
echo '{"tool":"shell","input":{"command":"rm -rf tmp"}}' | python .codex/hooks/pre_tool_use_policy.py
echo '{"tool":"shell","input":{"command":"git status --short"}}' | python .codex/hooks/pre_tool_use_policy.py
```

