# Ретро: SaaS AUTOPILOT stress-test

**Дата:** 2026-06-18 19:18
**Длительность:** ~35 минут
**План:** `plans/2026-06-18-autopilot-multi-persona-stress-test.md`

## 1. Задача

Смоделировать fresh onboarding и POST_AUTOPILOT для сложного B2B SaaS с техническим фаундером, несмотря на уже завершенный starter.

## 2. Как решал

Сначала прочитал локальные инструкции, AUTOPILOT/POST_AUTOPILOT, план стресс-теста и нужные индексы. Затем заменил доменный контекст на SyncDesk, разделил SaaS-сложность по файлам и создал обязательные экспериментальные отчеты.

## 3. Решил?

- [x] Да, полностью
- [ ] Частично: что сделано, что не сделано
- [ ] Нет: почему

## 4. Что можно было лучше

Сразу использовать отдельный режим "fresh rerun", если бы он был в starter. Также стоило бы иметь SaaS-шаблон вопросов, чтобы роли, billing, integrations и security не приходилось доставать вручную.

## 5. Как было / как стало

- **Было:** контекст AI-консультанта для заказа сайта, старый `ai-clone/`, mastery для client discovery сайта, completed state без режима повторного прохода.
- **Стало:** SyncDesk как B2B SaaS, отдельные файлы для ролей, интеграций, security и roadmap, `ai-clone/` технического фаундера, product-strategy mastery, экспериментальные отчеты.

## Follow-up

- Добавить в baseline SaaS-ветку AUTOPILOT.
- Добавить подсказку про hidden folders.
- Добавить domain invariants в шаблон `AGENTS.md`.

## Feedback rule

Если пользователь просит "сложный SaaS", Codex должен сразу проверять роли, tenant isolation, audit log, billing limits, интеграционные сбои и roadmap boundaries.
