# Admin / Reporting Baseline

## Цель

Следующий продуктовый слой для `bonus_wallet_service` — сделать бонусный контур
не только внутренне рабочим, но и наблюдаемым/управляемым для операторов.

На этом этапе нам не нужен большой backoffice. Нужен минимальный набор:
- читать баланс родителя
- читать ledger операций
- читать активные правила
- смотреть агрегированные totals по начислениям и списаниям

Этот слой должен быть:
- read-first
- audit-friendly
- без опасных write-операций по умолчанию

## Минимальный Scope

### Phase 1. Admin Read API

Обязательный минимум:
- `GET /v1/admin/bonus/accounts/{parent_id}`
- `GET /v1/admin/bonus/accounts/{parent_id}/ledger`
- `GET /v1/admin/bonus/rules`

Что это дает:
- support может объяснить текущий баланс
- support видит, почему начислились/списались бонусы
- support видит, какие правила сейчас активны

### Phase 2. Admin Reporting API

Минимальные агрегаты:
- `GET /v1/admin/bonus/reports/summary`
- `GET /v1/admin/bonus/reports/by-reason`
- `GET /v1/admin/bonus/reports/ledger.csv`

Что это дает:
- базовую операционную картину по бонусам
- прозрачность по `course_completed_reward` и другим reason-кодам
- удобный экспорт для ручной сверки

### Phase 3. Admin Write Operations (later)

Только после read/reporting baseline:
- `POST /v1/admin/bonus/rules`
- `POST /v1/admin/bonus/rules/{rule_id}/deactivate`
- optional later: manual correction / adjustment

Причина такого порядка:
- write-операции сразу повышают риск
- сначала нужно дать прозрачность и read-side
- потом уже добавлять управляемость

## Recommended Endpoint Set

### 1. Account Snapshot

`GET /v1/admin/bonus/accounts/{parent_id}`

Назначение:
- быстро вернуть текущую картину по одному кошельку

Минимальный ответ:
- `parent_id`
- `balance`
- `currency` or `points_unit`
- `last_activity_at`
- `accruals_total`
- `redeemed_total`
- `reverted_total`

### 2. Ledger History

`GET /v1/admin/bonus/accounts/{parent_id}/ledger`

Фильтры:
- `limit`
- `offset`
- `reason_code`
- `entry_type`
- `date_from`
- `date_to`

Минимальный ответ по entry:
- `entry_id`
- `entry_type`
- `amount`
- `reason_code`
- `reference_id`
- `idempotency_key`
- `created_at`
- `created_by`

### 3. Rules Read API

`GET /v1/admin/bonus/rules`

Фильтры:
- `active_only`
- `reason_code`

Минимальный ответ:
- `rule_id`
- `name`
- `reason_code`
- `award_amount`
- `active`
- `created_at`
- `deactivated_at`

### 4. Summary Report

`GET /v1/admin/bonus/reports/summary`

Назначение:
- дать общий health snapshot бонусной системы

Минимальные поля:
- `wallets_with_positive_balance`
- `total_balance_outstanding`
- `total_accrued`
- `total_redeemed`
- `total_reverted`
- `period_from`
- `period_to`

### 5. Reason Breakdown

`GET /v1/admin/bonus/reports/by-reason`

Назначение:
- понять, какие reason-коды реально двигают систему

Минимальные поля:
- `reason_code`
- `entries_count`
- `total_amount`

### 6. CSV Export

`GET /v1/admin/bonus/reports/ledger.csv`

Назначение:
- ручная сверка support/finance
- off-platform export

## Что НЕ делать в первой итерации

Не нужно сразу добавлять:
- parent-facing UI API
- complex filtering/search DSL
- mutable ledger edits
- массовые ручные начисления
- expiration engine
- fraud scoring

Это хорошие следующие слои, но не baseline.

## Access / Security

Для admin/reporting scope:
- только bearer auth
- только `admin` role
- все read endpoints логируют `request_id` / `correlation_id`
- write-admin операции later должны оставлять retained audit evidence

## Read Model Expectations

Чтобы reporting не бил по основному write path:
- summary/report endpoints могут читать из SQL напрямую
- later можно выделить отдельные read projections
- но в первой версии это не обязательно

## Recommended Delivery Order

1. `GET /v1/admin/bonus/accounts/{parent_id}`
2. `GET /v1/admin/bonus/accounts/{parent_id}/ledger`
3. `GET /v1/admin/bonus/rules`
4. `GET /v1/admin/bonus/reports/summary`
5. `GET /v1/admin/bonus/reports/by-reason`
6. `GET /v1/admin/bonus/reports/ledger.csv`

## Minimum Done Criteria

Слой можно считать минимально готовым, если:
- support может объяснить баланс конкретного родителя
- support видит ledger с reason-кодами и reference ids
- операторы видят aggregate totals за период
- есть CSV export для ручной сверки
- все admin endpoints закрыты bearer admin auth
