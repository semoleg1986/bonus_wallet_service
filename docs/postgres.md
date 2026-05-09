# PostgreSQL Baseline

## Минимальные таблицы
- `bonus_accounts`
- `bonus_ledger`
- `bonus_rules`

## Recommended notes
- `bonus_ledger` append-only
- unique index on `idempotency_key`
- optimistic concurrency on `bonus_accounts.version`
- indexes on `parent_global_id`, `source_event_id`, `payment_id`

## Future migrations
1. initial wallet tables
2. rule management extensions
3. optional reporting projections
