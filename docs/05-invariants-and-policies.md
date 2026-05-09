# Invariants And Policies

## Инварианты

1. Баланс не может быть отрицательным.
2. Каждое изменение баланса должно иметь ledger entry.
3. Повтор одного и того же accrual source не должен начислять бонусы второй раз.
4. Повтор одного и того же redeem commit не должен списывать бонусы второй раз.
5. Revert может компенсировать только ранее зафиксированный redeem.
6. Quote сам по себе не меняет баланс.
7. Max redeem per payment применяется до commit.
8. Все internal write endpoints требуют service trust.

## Политики

### Accrual Policy
- правила начисления берутся из `BonusRule`
- logic в домене/application, а не в HTTP router

### Redeem Policy
- quote и commit разделены
- commit зависит от успешного payment outcome
- revert обязателен для rollback path

### Replay Policy
- stable `source_event_id` или `idempotency_key` обязателен для write flows
- duplicate-safe behavior должен быть deterministic

### Audit Policy
- каждое изменение должно нести `request_id` и `correlation_id`
- source actor/service должен быть восстановим из данных ledger entry
