# Error Format

## Goal

HTTP API должен использовать единый предсказуемый error contract.

## Baseline

### 400 Bad Request
- validation errors
- malformed payload

### 401 Unauthorized
- отсутствует bearer/service token
- невалидный token

### 403 Forbidden
- actor/service не имеет права на операцию

### 404 Not Found
- bonus account / rule / redeem context не найден

### 409 Conflict
- duplicate operation by idempotency policy
- optimistic locking conflict
- revert requested for unknown prior redeem

### 422 Unprocessable Entity
- business rule violation if contract chooses semantic validation status

## Response Fields
- `status` or `statusCode`
- `error`
- `message` / `detail`
- `request_id`
- `correlation_id`

## Requirement

Ошибки должны быть стабильны и пригодны для audit/ops анализа.
