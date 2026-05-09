# ADR-0001: Bounded Context Для Bonus Wallet Service

## Статус
Proposed

## Дата
2026-05-09

## Контекст
Платформа уже имеет отдельные bounded contexts для auth, users, course, payments, attribution и live. Bonus/loyalty capability нельзя чисто встроить ни в `payments_service`, ни в `attribution-service` без смешивания разных доменных осей.

## Решение
Ввести отдельный `bonus_wallet_service`, который владеет:
- бонусным балансом родителя
- append-only ledger операций
- правилами начисления
- quote/commit/revert контрактом

Сервис не владеет:
- payment intent lifecycle
- referral/promo attribution
- user profile source of truth
- course progress source of truth

## Последствия
Плюсы:
- чистый ownership loyalty ledger
- проще обеспечить audit и strict idempotency
- проще расширять retention-механики позже

Минусы:
- еще один сервис и deploy surface
- дополнительные integration contracts
