# Bounded Context И Границы

## Название Контекста

**Контекст Бонусного Кошелька И Loyalty Ledger**

## Назначение Контекста

Контекст управляет бонусным балансом родителя и всеми фактами его изменения.
Он не принимает решения по оплате курса и не владеет прогрессом обучения, но принимает их как внешние факты и применяет собственные правила начисления/списания.

## Ответственность

Контекст обязан:
1. хранить бонусный баланс родителя
2. хранить append-only ledger всех операций
3. обеспечивать идемпотентность начисления/списания/компенсации
4. применять конфигурируемые правила начисления
5. рассчитывать доступный бонусный quote для оплаты
6. выполнять commit/revert списания после payment результата
7. предоставлять balance/read API и audit-friendly trace

## Структура Агрегатов

```shell
BonusAccount (Aggregate Root)
`- Balance (Value Object)

BonusLedgerEntry (Entity / append-only record)
`- Direction (Value Object)
`- Reason (Value Object)

BonusRule (Aggregate Root)
`- TriggerType (Value Object)
`- Threshold (Value Object)
```

## Внешние Зависимости

Зависит от:
- `auth_service` для identity/roles актора
- `users_service` для parent identity и parent-student relation context
- `course_service` как producer learning milestones
- `payments_service` как consumer/producer redeem lifecycle

Не зависит от:
- прямого доступа к БД внешних сервисов
- UI/BFF оркестрации
- referral/promo логики acquisition-контура

## Точки Интеграции

Входящие:
- internal accrual команды по learning milestones
- internal redeem quote / commit / revert команды
- balance read запросы

Исходящие:
- audit/ledger reads
- optional events для reporting/analytics

## Явные Границы

Контекст не должен:
- сам подтверждать оплату
- сам рассчитывать канал/реферальную скидку
- мутировать course/user агрегаты
- становиться источником истины по learning progress
