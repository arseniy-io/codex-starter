# Сводка: AUTOPILOT wave 2026-06-21

## Что проверяли

Три тестовые копии в `C:\Users\Arseniy\OneDrive\Рабочий стол\тестирование`:

- `autopilot-wave-2026-06-21-lite` - локальный мастер маникюра, живые короткие ответы.
- `autopilot-wave-2026-06-21-standard` - каталог услуг с простой owner-admin панелью.
- `autopilot-wave-2026-06-21-deep` - AI CRM assistant с ролями, клиентскими данными, интеграциями, audit trail и AI trust.

Агенты работали на `gpt-5.4-mini`, reasoning `medium`, по одному.

## Итоги по flow

### Lite

`lite` выбран правильно. Контекст не раздут: создано 4 `.business`-файла, без `ai-clone/`, `mastery/`, goals, economics, roles, integrations и roadmap.

Что всплыло:

- `POST_AUTOPILOT.md` выглядит лишним хвостом для маленького проекта.
- Git-шаги ломаются в тестовой копии без `.git`.
- Нужно явно говорить, что `.business/` может создаваться с нуля.

### Standard

`standard` выбран правильно. Простая owner-admin панель не увела проект в `deep`. Создано 8 `.business`-файлов, без `roles/security/integrations/roadmap/execution`.

Что всплыло:

- `PROJECT_STATE.md` всё ещё может давать широковатый вход: 6 пунктов в "читать сначала" и 8 ключевых файлов.
- Нужен более явный лимит стартового маршрута `standard`: 4-5 файлов всего.
- Git-шаги снова невыполнимы без `.git`.

### Deep

`deep` выбран правильно. `.business` остался компактным: 4 файла и deep-карта в `PROJECT_STATE.md`.

Главная проблема:

- Агент объявил прогон завершённым, но `AUTOPILOT.md` остался `completed: false`, `current_stage: final_files`, `last_completed_step: 8`.

Что всплыло ещё:

- Нужен жёсткий completion gate.
- `deep` не должен автоматически тянуть все блоки `goals/economics/marketing/assets`.
- Нужен лимит: 5-6 файлов стартового маршрута и 4-8 рабочих `.business`-файлов по реальной необходимости.

## Общие правки

1. Добавить fallback для папок без `.git`: шаг 6/10 не блокируют онбординг и не требуют искусственно инициализировать git.
2. Запретить считать AUTOPILOT завершённым, пока frontmatter не показывает `completed: true`, `current_stage: done`, `last_completed_step: 10`.
3. Сделать `POST_AUTOPILOT.md` явно optional после базового онбординга.
4. Ужать стартовые маршруты:
   - `lite` - 3-4 файла всего;
   - `standard` - 4-5 файлов всего;
   - `deep` - 5-6 файлов всего, включая deep-карту в `PROJECT_STATE.md`.
5. Ослабить обязательность `goals/economics/marketing/assets` в `deep`: читать и создавать только если это влияет на MVP, trust/security или ближайшее решение.

