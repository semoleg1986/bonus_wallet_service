# Actors And Use Cases

## Actors

### Parent
- читает баланс
- инициирует применение бонусов в payment flow

### Admin / Support
- просматривает ledger и правила
- при необходимости управляет правилами начисления
- читает account snapshot и aggregate reports

### `course_service`
- поставляет learning milestones для accrual

### `payments_service`
- запрашивает quote
- завершает commit/revert после payment результата

## Primary Use Cases

### 1. Начислить бонусы за завершение урока
1. `course_service` передает internal accrual command
2. `bonus_wallet_service` проверяет idempotency
3. применяет активные `BonusRule`
4. создает ledger entry `accrual`
5. обновляет баланс

### 2. Рассчитать допустимое списание при оплате
1. `payments_service` вызывает `redeem/quote`
2. сервис проверяет баланс, лимиты, payment context
3. возвращает допустимый discount snapshot

### 3. Зафиксировать списание после оплаты
1. `payments_service` вызывает `redeem/commit`
2. сервис проверяет idempotency и достаточность баланса
3. создает ledger entry `redeem`
4. уменьшает баланс

### 4. Откатить списание
1. payment flow завершается неуспешно или откатывается
2. `payments_service` вызывает `redeem/revert`
3. сервис создает compensating ledger entry `revert`
4. восстанавливает баланс

### 5. Прочитать баланс родителя
1. parent/admin запрашивает balance
2. сервис возвращает актуальный balance snapshot

### 6. Прочитать ledger и account snapshot для поддержки
1. admin/support запрашивает account snapshot
2. сервис возвращает текущий баланс и агрегированные totals
3. при необходимости support читает ledger операций

### 7. Получить aggregate reporting
1. admin/support запрашивает summary/by-reason/csv export
2. сервис возвращает агрегированные данные по начислениям и списаниям
