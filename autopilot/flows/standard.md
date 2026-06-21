# Flow: standard

Читай этот файл только если в `.codex/autopilot-state.yml` выбран `autopilot.onboarding_depth: standard`.

`standard` подходит для обычного продукта или коммерческого сайта средней сложности. Цель - 6-10 рабочих файлов, а не вся `.business/`.

## Проверка deep-триггеров

Перед созданием файлов проверь, есть ли сильный deep-триггер:

- несколько ролей с разными правами доступа;
- аккаунты пользователей, персональные данные или приватные пользовательские материалы;
- платежи, подписки, возвраты или финансовые риски;
- внешние API, webhooks, интеграции или обмен данными между системами;
- загрузка файлов, экспорт, audit trail, retention или история изменений;
- marketplace, multi-tenant, сложная админка или несколько сторон сделки;
- AI работает с пользовательскими данными, документами или решениями, где важны trust/security.

Если есть сильный deep-триггер, предложи перейти на `deep`.

Если триггер слабый, не создавай отдельные deep-файлы. Запиши короткую секцию `Осторожно позже` в `.business/INDEX.md` или `PROJECT_STATE.md`.

Слабые триггеры:

- простая админка для владельца;
- закрытые материалы без сложных ролей;
- онлайн-запись без оплаты и внешних интеграций;
- ручная обработка заявок;
- будущая интеграция, которую пользователь пока только "когда-нибудь хочет".

## Файлы

Обязательный набор:

1. `.business/INDEX.md` - карта проекта и минимальный список чтения.
2. `.business/company/about.md` - что за проект и кто за ним стоит.
3. `.business/products/overview.md` - что строим, основной scope и MVP.
4. `.business/audience/avatar.md` - кто пользователь и какая боль.
5. `.business/marketing/funnel.md` - путь от интереса до заявки/покупки.

Добавь 1-5 файлов только по реальной необходимости:

- `.business/products/pricing.md` - если есть цены, тарифы, пакеты или условия доступа;
- `.business/audience/objections.md` - если важны доверие, страхи, сравнение и возражения;
- `.business/audience/journey.md` - если путь пользователя сложнее одного действия;
- `.business/marketing/channels.md` - если уже понятны каналы привлечения;
- `.business/assets/brand-guidelines.md` - если важен визуальный стиль или тон;
- `.business/goals/kpi.md` - если есть конкретные метрики;
- `.business/economics/costs.md` или `.business/economics/revenue.md` - если экономика влияет на ближайшие решения.

В `standard` не создавай без сильного deep-триггера:

- `.business/products/roles-and-permissions.md`;
- `.business/products/security-model.md`;
- `.business/products/integrations.md`;
- `.business/products/roadmap.md`;
- `.business/execution/`;
- полный набор `goals/`;
- полный набор `economics/`.

После `products/overview.md` сделай Reality Check: назови 2-3 риска и спроси, не нужен ли `deep`. Если пользователь не подтверждает сильный deep-триггер, оставайся в `standard`.

## Успех

`standard` считается успешным, если новое окно Codex может понять проект через `AGENTS.md` -> `PROJECT_STATE.md` -> `.business/INDEX.md` -> 2-4 нужных файла.

После создания файлов обнови state: `last_completed_step: 8`, `current_stage: business_context`, `current_flow: standard`, `last_completed_substep: standard_files_created`, затем вернись в `AUTOPILOT.md` к финалу шага 8.
