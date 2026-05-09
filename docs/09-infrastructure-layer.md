# Infrastructure Layer

## Ответственность

Infrastructure layer предоставляет адаптеры для портов application слоя.

## Базовые компоненты
- DB session / engine factory
- SQLAlchemy repositories
- Unit of Work
- config/settings loader
- observability / metrics adapters
- optional outbox/inbox support

## Persistence Baseline

Минимальный production-ready вариант:
- PostgreSQL
- append-only `bonus_ledger`
- отдельная таблица `bonus_accounts`
- optimistic concurrency через `version`

## Integration Baseline
- internal HTTP service auth via `X-Service-Token`
- optional async event consumer later
- no cross-service DB access

## Observability Baseline
- structured HTTP logs
- Prometheus metrics
- centralized error tracking through current platform observability stack
