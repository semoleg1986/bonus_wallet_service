# Integration Contracts

## `course_service` -> `bonus_wallet_service`

### Purpose
Передать факт learning milestone для начисления бонусов.

### Candidate triggers
- `lesson_completed`
- `module_completed`
- `course_completed`
- `test_passed`

### Contract expectations
- должен существовать stable `source_event_id`
- повторная доставка не должна создавать второй accrual
- parent identity должна быть разрешима deterministically

## `payments_service` -> `bonus_wallet_service`

### Quote
`payments_service` запрашивает допустимое списание для payment context.

### Commit
После успешного payment outcome фиксируется списание.

### Revert
При rollback/cancel/failure фиксируется компенсирующее начисление.

### Contract expectations
- `quote` side-effect free
- `commit` strict idempotent by payment business key
- `revert` duplicate-safe and compensating

## `users_service` -> `bonus_wallet_service`

### Purpose
Разрешить identity/relationship context.

### Contract expectations
- `users_service` не владеет бонусным балансом
- parent-student relation используется как внешний факт, не как ledger state

## Auth / Trust
- bearer auth для parent/admin reads
- `X-Service-Token` для internal write flows
- contracts versioned explicitly before breaking changes

## Admin / Reporting Surface

### Purpose
Дать support/admin прозрачность по бонусному контуру без вмешательства в ledger state.

### First endpoints
- account snapshot
- ledger read
- rules read
- aggregate summary
- csv export

### Contract expectations
- read endpoints не меняют state
- ledger entries остаются append-only
- admin/reporting filters не должны менять business semantics ledger
