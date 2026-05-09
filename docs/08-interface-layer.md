# Interface Layer

## Роль Слоя

Interface layer принимает внешние HTTP/internal calls и преобразует их в application commands/queries.

Он обязан:
- извлекать actor context
- проверять bearer/service auth
- валидировать payload shape
- вызывать application facade/handlers
- возвращать стабильный error contract

## Предлагаемые HTTP Endpoints (baseline)

### Internal
- `POST /v1/bonus/accrue`
- `POST /v1/bonus/redeem/quote`
- `POST /v1/bonus/redeem/commit`
- `POST /v1/bonus/redeem/revert`

### Read
- `GET /v1/bonus/balance/{parent_global_id}`
- `GET /v1/bonus/ledger/{parent_global_id}`

### Admin (later)
- `POST /v1/admin/bonus/rules`
- `PATCH /v1/admin/bonus/rules/{id}`
- `GET /v1/admin/bonus/rules`

## Interface Principles
- никакой domain logic в router/controller
- idempotency keys и audit headers пробрасываются явно
- internal endpoints не открываются как public-by-default API
