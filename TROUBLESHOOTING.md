# TROUBLESHOOTING

Решения типовых проблем при настройке и работе с Codex Starter.

## Установка и авторизация

### Codex не запускается в терминале Windows

Проверь, что Git установлен и доступен:

```powershell
git --version
```

Если Codex просит bash, укажи путь к Git Bash в настройках Codex или запускай проект из Git Bash. На Windows часто подходит:

```powershell
C:\Program Files\Git\bin\bash.exe
```

### Codex не видит репозиторий

Открой именно корень проекта, где лежат `AGENTS.md`, `.git/`, `.business/`, `plans/` и `prompts/`.

Проверь:

```bash
git status --short --branch
```

### Нет доступа к модели или сервису

Обычно причина одна из трёх:

1. Ты не авторизован в нужной поверхности Codex.
2. Аккаунт или workspace не имеет доступа к выбранной модели/функции.
3. Сеть/VPN блокирует соединение.

Действуй слоями: перелогинься, проверь workspace/account, затем проверь сеть.

### В VS Code не вижу Codex

1. Проверь, что установлено именно расширение Codex/OpenAI, а не другой coding assistant.
2. Выполни `Developer: Reload Window`.
3. Открой корень проекта, а не вложенную папку.

## Папки и файлы

### Не вижу `.business/` в сайдбаре VS Code

В `.vscode/settings.json` должно быть:

```json
{
  "files.exclude": {
    "**/.business": false
  }
}
```

После изменения перезагрузи окно VS Code.

### Codex не читает правила

Проверь, что файл называется ровно `AGENTS.md` и лежит в корне репозитория. Если у тебя монорепозиторий, можно добавить вложенный `AGENTS.md` в подпапку: ближайший файл с правилами должен описывать именно этот subtree.

### Нужно несколько бизнес-контекстов

Лучший вариант - отдельный репозиторий на каждый проект. Если нужен монорепозиторий, явно опиши в `AGENTS.md`, какой `.business/` относится к какой подпапке.

## Работа с Codex

### Codex долго думает

Сначала подожди. Если задача зависла:

1. Попроси короткий статус.
2. Сузь задачу до одного результата.
3. Попроси прочитать только нужные файлы, а не весь репозиторий.

### Codex делает не то

Чаще всего не хватает контекста или критериев готовности. Добавь:

- какие файлы смотреть;
- какой результат нужен;
- какие проверки запустить;
- что не трогать.

### Контекст разросся

Используй правило шаблона: для продуктовых задач читать `.business/INDEX.md`, а затем только нужные файлы из `.business/`. Не загружай все планы, ретро и бизнес-документы без причины.

### Режим без подтверждений

Не включай рискованные режимы до первого чистого коммита. Сначала должны быть:

1. `git status` без неожиданных изменений;
2. `.env` и `.business/` защищены от коммита;
3. pre-commit hook установлен;
4. понятно, как откатить изменения через git.

## Hooks и безопасность

### Как проверить policy-hook

Windows/PowerShell:

```powershell
'{"tool":"shell","input":{"command":"rm -rf tmp"}}' | python .codex/hooks/pre_tool_use_policy.py
'{"tool":"shell","input":{"command":"git status --short"}}' | python .codex/hooks/pre_tool_use_policy.py
```

macOS/Linux/Git Bash:

```bash
echo '{"tool":"shell","input":{"command":"rm -rf tmp"}}' | python .codex/hooks/pre_tool_use_policy.py
echo '{"tool":"shell","input":{"command":"git status --short"}}' | python .codex/hooks/pre_tool_use_policy.py
```

Первый пример должен вернуть `permissionDecision: deny`, второй - `permissionDecision: allow`.

### Security audit не запускается через `bash` на Windows

Если `bash scripts/security-audit.sh` уходит в WSL и падает, запусти PowerShell-версию:

```powershell
python scripts/starter-lint.py
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/security-audit.ps1
```

Если хочешь использовать bash, запускай через Git Bash напрямую:

```powershell
& 'C:\Program Files\Git\bin\bash.exe' scripts/security-audit.sh
```

### Случайно закоммитил `.env`

1. Удали файл из индекса:

```bash
git rm --cached .env
```

2. Убедись, что `.env` есть в `.gitignore`.
3. Закоммить удаление из индекса.
4. Если секрет уже попал в публичный репозиторий, сразу ротируй ключи.

## Git

### `git commit` говорит `please tell me who you are`

Настрой имя и email локально для проекта:

```bash
git config user.name "Твоё Имя"
git config user.email "email@example.com"
```

### Git показывает чужие изменения

Не откатывай их автоматически. Попроси Codex работать только со своими файлами и стейджить изменения поимённо.
