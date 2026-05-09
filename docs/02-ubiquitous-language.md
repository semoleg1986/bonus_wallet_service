# Ubiquitous Language

## Базовые Термины

### BonusAccount
Корневой агрегат кошелька родителя. Хранит текущий баланс и concurrency/version boundary.

### BonusBalance
Value object текущего доступного бонусного остатка.

### BonusLedgerEntry
Неизменяемая запись истории изменения баланса.

### Accrual
Начисление бонусов в пользу родителя.

### RedeemQuote
Предварительный расчет допустимого списания бонусов для конкретного payment context.

### RedeemCommit
Фактическое списание бонусов после успешного подтверждения оплаты.

### RedeemRevert
Компенсация ранее выполненного списания при откате/ошибке payment flow.

### BonusRule
Конфигурируемое правило начисления бонусов по trigger type.

### TriggerType
Тип триггера начисления.
Примеры:
- `lesson_completed`
- `module_completed`
- `course_completed`
- `test_passed`

### SourceEventId
Стабильный бизнес-идентификатор события, по которому проверяется replay/idempotency.

### IdempotencyKey
Явный ключ, по которому повторная операция не создает второе изменение баланса.

### ParentGlobalId
Канонический идентификатор родителя в loyalty контуре.

### PaymentContext
Набор данных, достаточный для расчета применимого bonus discount при оплате.

### MaxRedeemLimit
Политика верхней границы списания бонусов на один платеж.
