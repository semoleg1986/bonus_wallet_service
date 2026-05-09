# Application Layer

## Роль Слоя

Application layer orchestrates use cases, but does not own domain invariants.
Он:
- принимает команды/запросы
- открывает UoW
- грузит агрегаты/правила
- вызывает доменные методы
- сохраняет результат через репозитории

## Основные Use Cases

### Commands
- `AccrueBonus`
- `RedeemQuote`
- `RedeemCommit`
- `RedeemRevert`
- `CreateBonusRule`
- `DeactivateBonusRule`

### Queries
- `GetBonusBalance`
- `ListBonusLedger`
- `ListBonusRules`

## Порты
- `BonusAccountRepository`
- `BonusLedgerRepository`
- `BonusRuleRepository`
- `UnitOfWork`
- `Clock`
- optional `IdGenerator`

## Важные orchestration rules
- write use cases должны быть idempotent-aware
- application layer не должен silently reclassify domain errors
- transport specifics не просачиваются в domain
