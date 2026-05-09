from fastapi.testclient import TestClient

from src.interface.http.app import create_app
from src.interface.http.observability import reset_metrics
from src.interface.http.wiring import reset_runtime_state

SERVICE_TOKEN = "dev-service-token"


def _client() -> TestClient:
    reset_metrics()
    reset_runtime_state()
    return TestClient(create_app())


def test_internal_routes_require_service_token() -> None:
    response = _client().get("/internal/v1/bonus/balance/parent-1")

    assert response.status_code == 401
    assert response.json()["detail"] == "Требуется X-Service-Token."


def test_accrue_balance_quote_commit_and_revert_flow() -> None:
    client = _client()
    headers = {"X-Service-Token": SERVICE_TOKEN}

    accrue_response = client.post(
        "/internal/v1/bonus/accruals",
        headers=headers,
        json={
            "parent_id": "parent-1",
            "amount": 150,
            "reason_code": "lesson_completion_reward",
            "reference_id": "lesson-1",
            "idempotency_key": "accrue-1",
        },
    )
    assert accrue_response.status_code == 200
    assert accrue_response.json()["balance_after"] == 150

    balance_response = client.get(
        "/internal/v1/bonus/balance/parent-1",
        headers=headers,
    )
    assert balance_response.status_code == 200
    assert balance_response.json() == {"parent_id": "parent-1", "balance": 150}

    quote_response = client.post(
        "/internal/v1/bonus/redemptions/quote",
        headers=headers,
        json={
            "parent_id": "parent-1",
            "requested_amount": 90,
            "payment_intent_id": "pi-1",
        },
    )
    assert quote_response.status_code == 200
    assert quote_response.json()["allowed_amount"] == 90

    commit_response = client.post(
        "/internal/v1/bonus/redemptions/commit",
        headers=headers,
        json={
            "parent_id": "parent-1",
            "amount": 90,
            "payment_intent_id": "pi-1",
            "idempotency_key": "commit-1",
        },
    )
    assert commit_response.status_code == 200
    assert commit_response.json()["balance_after"] == 60
    assert commit_response.json()["operation"] == "redeem_commit"

    replay_response = client.post(
        "/internal/v1/bonus/redemptions/commit",
        headers=headers,
        json={
            "parent_id": "parent-1",
            "amount": 90,
            "payment_intent_id": "pi-1",
            "idempotency_key": "commit-1",
        },
    )
    assert replay_response.status_code == 200
    assert replay_response.json()["entry_id"] == commit_response.json()["entry_id"]

    revert_response = client.post(
        "/internal/v1/bonus/redemptions/revert",
        headers=headers,
        json={
            "parent_id": "parent-1",
            "amount": 90,
            "payment_intent_id": "pi-1",
            "idempotency_key": "revert-1",
        },
    )
    assert revert_response.status_code == 200
    assert revert_response.json()["balance_after"] == 150
    assert revert_response.json()["operation"] == "redeem_revert"


def test_commit_redeem_fails_when_balance_is_insufficient() -> None:
    client = _client()
    headers = {"X-Service-Token": SERVICE_TOKEN}

    response = client.post(
        "/internal/v1/bonus/redemptions/commit",
        headers=headers,
        json={
            "parent_id": "parent-2",
            "amount": 10,
            "payment_intent_id": "pi-2",
            "idempotency_key": "commit-low-balance",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Недостаточно бонусного баланса."


def test_rule_lifecycle_create_list_and_deactivate() -> None:
    client = _client()
    headers = {"X-Service-Token": SERVICE_TOKEN}

    create_response = client.post(
        "/internal/v1/bonus/rules",
        headers=headers,
        json={
            "trigger_type": "lesson_completed",
            "threshold": 3,
            "points": 25,
        },
    )
    assert create_response.status_code == 200
    rule_id = create_response.json()["rule_id"]
    assert create_response.json()["is_active"] is True

    list_response = client.get("/internal/v1/bonus/rules", headers=headers)
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
    assert list_response.json()[0]["rule_id"] == rule_id

    deactivate_response = client.post(
        f"/internal/v1/bonus/rules/{rule_id}/deactivate",
        headers=headers,
    )
    assert deactivate_response.status_code == 200
    assert deactivate_response.json()["is_active"] is False

    active_list_response = client.get(
        "/internal/v1/bonus/rules?active_only=true",
        headers=headers,
    )
    assert active_list_response.status_code == 200
    assert active_list_response.json() == []
