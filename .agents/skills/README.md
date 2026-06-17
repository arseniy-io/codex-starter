# Local Codex skills

Клади сюда только skills, которые нужны именно этому репозиторию.

Skill нужен, когда один и тот же workflow повторяется и его стоит упаковать в `SKILL.md`. Не складывай сюда MCP-серверы, plugins и случайные промпты.

Формат одного skill:

```
.agents/skills/
└── skill-name/
    ├── SKILL.md
    ├── scripts/
    └── assets/
```

Перед установкой любого skill проведи аудит: `README.md`, `SKILL.md`, scripts, внешние URL, доступ к `.env`, операции удаления.

Если workflow нужен во всех проектах - это кандидат на личный/global skill. Если нужно распространять набор skills, hooks, apps или MCP - это кандидат на plugin.
