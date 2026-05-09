# Domain Model

## Aggregate: BonusAccount

### Ответственность
- хранить текущий balance
- применять accrual/redeem/revert операции
- не допускать уход баланса в минус
- обеспечивать optimistic concurrency boundary

### Состояние
- `parent_global_id`
- `balance`
- `updated_at`
- `version`

## Entity: BonusLedgerEntry

### Ответственность
- фиксировать факт изменения баланса
- сохранять audit context и business source

### Состояние
- `id`
- `parent_global_id`
- `direction` (`accrual|redeem|revert`)
- `amount`
- `reason`
- `source_event_id`
- `payment_id`
- `idempotency_key`
- `request_id`
- `correlation_id`
- `created_at`

## Aggregate: BonusRule

### Ответственность
- задавать активные правила начисления
- определять amount/points для trigger type и threshold

### Состояние
- `id`
- `trigger_type`
- `threshold`
- `points`
- `is_active`
- `updated_at`

## Value Objects
- `BonusBalance`
- `LedgerDirection`
- `LedgerReason`
- `TriggerType`
- `Threshold`
- `RewardAmount`
- `RedeemQuoteResult`

## Доменные События (baseline)
- `bonus_accrued`
- `bonus_redeemed`
- `bonus_reverted`
- `bonus_rule_changed`
