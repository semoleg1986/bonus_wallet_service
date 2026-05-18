# bonus_wallet_service

Bonus wallet service for parent accounts.

## Responsibility

`bonus_wallet_service` owns:
- parent bonus account balance
- bonus ledger entries
- accrual and redeem rules
- admin bonus reporting and exports

## Local run

### Install
```bash
make install
```

### Run with uvicorn
```bash
uvicorn src.interface.http.main:app --host 0.0.0.0 --port 8006 --reload
```

### Health
```bash
curl -fsS http://127.0.0.1:8006/healthz
```

## Environment

Primary settings are defined in:
- [settings.py](/Users/olegsemenov/Programming/curs/bonus_wallet_service/src/infrastructure/config/settings.py)

Key variables:
- `BONUS_APP_PORT`
- `BONUS_DATABASE_URL`
- `BONUS_USE_INMEMORY`
- `BONUS_AUTH_JWKS_URL`
- `BONUS_SERVICE_TOKEN`

## Tests and quality

```bash
make test
make lint
make format
```

## Documentation

- [00-vision.md](/Users/olegsemenov/Programming/curs/bonus_wallet_service/docs/00-vision.md)
- [10-integration-contracts.md](/Users/olegsemenov/Programming/curs/bonus_wallet_service/docs/10-integration-contracts.md)
- [11-admin-reporting-baseline.md](/Users/olegsemenov/Programming/curs/bonus_wallet_service/docs/11-admin-reporting-baseline.md)
- [postgres.md](/Users/olegsemenov/Programming/curs/bonus_wallet_service/docs/postgres.md)
