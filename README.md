# Codex Starter

Стартовый шаблон для проектов, где Codex используется как основной coding agent. Клонируешь репозиторий, открываешь его в Codex, проходишь онбординг и получаешь: бизнес-контекст, `AGENTS.md`, рабочий цикл `plan → implement → verify → retro`, prompts-библиотеку и базовые guardrails безопасности.

Официальные точки опоры:
- [Codex docs](https://developers.openai.com/codex)
- [AGENTS.md guidance](https://developers.openai.com/codex/guides/agents-md)
- [Codex hooks](https://developers.openai.com/codex/hooks)
- [Codex skills](https://developers.openai.com/codex/skills)

## TL;DR

1. Клонируй шаблон и открой папку в Codex.
2. Напиши `привет` или `проведи меня`.
3. Codex прочитает `AGENTS.md`, увидит `AUTOPILOT.md` и проведёт тебя по настройке.

## Что получится

- `.business/` - структурированный контекст проекта: продукт, аудитория, цели, экономика, маркетинг, бренд.
- `AGENTS.md` - долговременные правила для Codex в этом репозитории.
- `.codex/` - project-level config и место для guardrails.
- `.agents/skills/` - место для локальных repo-skills, если они нужны проекту.
- `plans/` - планы реализации по задачам.
- `retrospectives/` - короткая память между сессиями.
- `prompts/` - готовые workflow-промпты под типовые задачи.
- `STRUCTURE.md` - короткая карта всех папок и зачем они нужны.
- `QUALITY_CHECKLIST.md` - критерии качества перед публикацией или крупной правкой.

## Перед стартом

Убедись, что:

- установлен Git;
- установлен Node.js, если твой стек или Codex-установка его требует;
- у тебя есть доступ к Codex в выбранной поверхности: CLI, IDE extension, desktop app или web/cloud;
- ты авторизован в OpenAI/Codex;
- VPN/сеть стабильны, если доступ к OpenAI в твоей стране нестабилен.

## Как запустить

```bash
git clone https://github.com/<your-username>/<your-codex-starter-repo> moy-proekt
cd moy-proekt
```

Если ты держишь шаблон только локально, просто скопируй папку или клонируй свой приватный репозиторий. После создания проекта проверь `git remote -v`, чтобы случайно не пушить в репозиторий шаблона.

Затем открой папку в Codex и напиши:

```text
привет
```

Если `AUTOPILOT.md` ещё не завершён, Codex начнёт онбординг.

## Структура

```
codex-starter/
├── AGENTS.md              ← правила работы Codex
├── AUTOPILOT.md           ← сценарий первого запуска
├── TROUBLESHOOTING.md     ← решения типовых проблем
├── .codex/                ← project config и guardrails
├── .agents/skills/        ← локальные repo-skills
├── .business/             ← бизнес-контекст
├── plans/                 ← планы реализации
├── retrospectives/        ← ретроспективы
├── prompts/               ← библиотека промптов
├── templates/             ← шаблоны файлов
├── scripts/               ← проверки шаблона
├── STRUCTURE.md           ← карта папок
└── QUALITY_CHECKLIST.md   ← критерии качества
```

## Безопасность

- `.env` и `.env.local` уже добавлены в `.gitignore`.
- `.business/` сначала tracked, чтобы показать структуру. После заполнения реальными данными AUTOPILOT добавит `.business/` в `.gitignore` и снимет папку с git tracking.
- Pre-commit hook проверяет staged-файлы на секреты:

```bash
cp .github/hooks/pre-commit.sample .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

- `.codex/hooks/pre_tool_use_policy.py` содержит проверяемый policy-скрипт для опасных команд. Подключай его к Codex hooks по актуальной официальной схеме.

## Как работать после онбординга

1. Перед задачей Codex читает `AGENTS.md`.
2. Для продуктовых задач он берёт только нужный контекст из `.business/`.
3. Для новой функции создаёт план в `plans/`.
4. После реализации запускает проверки стека.
5. В конце заметной сессии пишет ретро в `retrospectives/`.

## Что шаблон не делает

- Не устанавливает Codex и не настраивает твой аккаунт OpenAI.
- Не выбирает тариф и не гарантирует лимиты использования.
- Не заменяет твои ответы в бизнес-интервью.
- Не включает автоматом рискованные режимы без подтверждений.

## Если уже есть проект

Используй [`prompts/methodology/import-existing-project.md`](./prompts/methodology/import-existing-project.md). Codex прочитает структуру проекта, README и код, затем заполнит `.business/` на основе найденного и задаст вопросы по пробелам.

## FAQ

### Почему `AGENTS.md`, а не просто промпт в чат?

Промпт живёт одну сессию. `AGENTS.md` хранит durable-инструкции для репозитория: команды, стиль, правила проверки, безопасность и структуру контекста.

### Можно ли использовать с Cursor/Windsurf/другими агентами?

Методология `.business/`, `plans/`, `retrospectives/` переносима. Но `AGENTS.md`, `.codex/`, hooks и skills адаптированы под Codex.

### Сколько токенов уйдёт?

Зависит от размера проекта, частоты задач, подключённых tools/MCP/skills и того, насколько аккуратно ты держишь контекст. Правило шаблона: читать только нужные файлы, а не загружать весь `.business/` и всю историю каждый раз.

## Лицензия

MIT.

---

<sub>Изначальная методология разработана в [Школе Смысло-кодинга](https://smyslokod.ru), эта версия адаптирована под Codex.</sub>
