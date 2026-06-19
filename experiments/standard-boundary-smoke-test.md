# Smoke-test: граница standard -> deep

Дата: 2026-06-19

## Что проверяли

Проверка после второй волны: сможет ли обновлённый `standard` остаться средним режимом и не превратиться в `deep` через лишние файлы.

Тестовый сценарий:

> «Нужен каталог услуг с простой админкой. Чтобы я мог менять услуги и цены, смотреть заявки. Может потом подключим оплату или интеграции, но пока не знаю.»

## Ожидаемый режим

`standard`.

Почему:

- проект сложнее лендинга;
- есть каталог, заявки и простая админка;
- но платежи и интеграции пока только "может потом";
- нет сильной ролевой модели, файлов, экспорта, audit trail или пользовательских данных.

## Что должен создать standard

Обязательно:

- `.business/INDEX.md`;
- `.business/company/about.md`;
- `.business/products/overview.md`;
- `.business/audience/avatar.md`;
- `.business/marketing/funnel.md`.

По необходимости:

- `.business/products/pricing.md`;
- `.business/audience/objections.md`;
- `.business/marketing/channels.md`;
- `.business/assets/brand-guidelines.md`;
- `.business/goals/kpi.md`;
- `.business/economics/revenue.md` или `.business/economics/costs.md`.

Итого: 6-10 рабочих файлов.

## Чего standard не должен создавать без deep-триггера

- `.business/products/roles-and-permissions.md`;
- `.business/products/security-model.md`;
- `.business/products/integrations.md`;
- `.business/products/roadmap.md`;
- `.business/execution/`;
- полный набор `goals/`;
- полный набор `economics/`.

## Как фиксировать слабые deep-триггеры

Если пользователь говорит "потом оплата", "потом интеграции", "возможно роли", это не повод создавать deep-слой.

Правильное действие: добавить короткую секцию `Осторожно позже` в `.business/INDEX.md` или `PROJECT_STATE.md`.

## Результат проверки

Обновлённый `standard` стал измеримым:

- 6-10 файлов;
- запрет deep-like файлов без сильного триггера;
- слабые триггеры остаются заметкой, а не отдельной библиотекой;
- новое окно Codex читает `AGENTS.md` -> `PROJECT_STATE.md` -> `.business/INDEX.md` -> 2-4 файла.

## Вывод

Граница `standard` -> `deep` стала заметно чище. Можно переходить к третьей волне, где deep-триггеры должны быть уже настоящими, а не выдуманными заранее.
