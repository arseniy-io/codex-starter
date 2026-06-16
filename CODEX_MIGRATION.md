# Codex migration notes

Коротко: что пересобрано и почему.

| Пункт | Что изменено | Почему |
|---|---|---|
| Durable-инструкции | `CLAUDE.md` заменён на `AGENTS.md` | Codex использует `AGENTS.md` как repo-level правила. |
| Project config | Добавлена `.codex/config.toml` | Project-настройки Codex должны жить отдельно от промптов и README. |
| Guardrails | Добавлен `.codex/hooks/pre_tool_use_policy.py` | Опасные команды лучше ловить детерминированным скриптом, а не только просьбой в тексте. |
| Skills | Добавлена `.agents/skills/` | Локальные repo-skills должны быть отделены от личных/global skills. |
| README | Переписан под Codex | Старые ссылки на Claude/Anthropic и тарифы не применимы к Codex. |
| AUTOPILOT | Переписан под 10 Codex-шагов | Онбординг теперь настраивает `AGENTS.md`, `.codex/`, guardrails и `.business/`. |
| Templates | `AGENTS.md.tmpl` и `codex-config.toml.example` | Финальный проект должен генерировать Codex-native инструкции. |
| Prompts | Setup-prompts обновлены под Codex | Пользователь не должен копировать несуществующие `.claude/settings.json` workflows. |
| Troubleshooting | Переписан под Codex | Диагностика теперь идёт слоями: surface, auth, workspace, сеть, config. |
| VS Code | `.business/`, `.codex/`, `.agents/` видны в sidebar | Новичку важно видеть все рабочие папки методологии. |
| Security audit | Проверяет `.codex/config.local.toml` | Локальные настройки Codex не должны попадать в git. |
| Methodology | `.business/`, `plans/`, `retrospectives/` сохранены | Это не Claude-специфика, а полезный рабочий цикл для Codex. |
