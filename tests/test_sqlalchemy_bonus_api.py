from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from src.interface.http.app import create_app
from src.interface.http.observability import reset_metrics
from src.interface.http.wiring import reset_runtime_state

SERVICE_TOKEN = "dev-service-token"


def _client() -> TestClient:
    reset_metrics()
    reset_runtime_state()
    return TestClient(create_app())


def test_sqlite_runtime_persists_balance_across_app_recreation(
    monkeypatch, tmp_path: Path
) -> None:
    db_path = tmp_path / "bonus_wallet.sqlite3"
    monkeypatch.setenv("BONUS_USE_INMEMORY", "0")
    monkeypatch.setenv("BONUS_AUTO_CREATE_SCHEMA", "1")
    monkeypatch.setenv("BONUS_DATABASE_URL", f"sqlite:///{db_path}")

    headers = {"X-Service-Token": SERVICE_TOKEN}

    first_client = _client()
    accrue_response = first_client.post(
        "/internal/v1/bonus/accruals",
        headers=headers,
        json={
            "parent_id": "sql-parent-1",
            "amount": 75,
            "reason_code": "bootstrap_reward",
            "reference_id": "course-progress-1",
            "idempotency_key": "accrue-sql-1",
        },
    )
    assert accrue_response.status_code == 200
    assert accrue_response.json()["balance_after"] == 75

    second_client = _client()
    balance_response = second_client.get(
        "/internal/v1/bonus/balance/sql-parent-1",
        headers=headers,
    )
    assert balance_response.status_code == 200
    assert balance_response.json() == {
        "parent_id": "sql-parent-1",
        "balance": 75,
    }
