# Архитектурное Видение Bonus Wallet Service

## Назначение

`bonus_wallet_service` — bounded context для бонусного кошелька родителя.
Сервис владеет бонусным балансом, неизменяемым ledger операций, правилами начисления и списания, а также контрактами интеграции с learning- и payment-контурами.

Ключевые цели:
- держать loyalty/balance-логику отдельно от `payments_service` и `attribution-service`
- сделать начисления и списания строго идемпотентными и audit-friendly
- обеспечить детерминированный redeem flow для оплаты
- сохранить чистые границы между acquisition discount и retention loyalty

## Бизнес-ценность

Сервис обеспечивает:
- единый источник истины по бонусному балансу родителя
- прозрачный append-only audit trail всех accrual/redeem/revert операций
- конфигурируемые правила начисления без хардкода в роутерах
- безопасное применение бонусов как скидки в payment flow
- базу для дальнейшего роста в retention/family loyalty mechanics

## Границы

### Входит в контекст
- `BonusAccount`
- `BonusLedgerEntry`
- `BonusRule`
- `RedeemQuote`
- `RedeemCommit`
- `RedeemRevert`

### Не входит в контекст
- аутентификация и lifecycle токенов (`auth_service`)
- профили и parent-student source of truth (`users_service`)
- course content/progress как источник истины (`course_service`)
- payment intent / admin approve (`payments_service`)
- referral/promo/acquisition discount ownership (`attribution-service`)

## Принципы

- Ledger first: баланс не живет без истории операций
- Domain first: инварианты лежат в домене, а не в transport слое
- Clean Architecture: зависимости направлены внутрь
- Идемпотентность — часть бизнес-контракта, а не best effort
- Интеграции только через явные API/events контракты
