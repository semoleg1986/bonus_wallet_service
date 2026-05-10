from __future__ import annotations

from fastapi.testclient import TestClient

from src.interface.http.app import create_app
from src.interface.http.observability import reset_metrics
from src.interface.http.wiring import (
    get_access_token_verifier,
    reset_runtime_state,
)

SERVICE_TOKEN = "dev-service-token"


class _StubVerifier:
    def decode_access(self, access_token: str) -> dict[str, str | list[str]]:
        if access_token == "admin-token":
            return {"sub": "admin-1", "roles": ["admin"]}
        if access_token == "parent-token":
            return {"sub": "parent-1", "roles": ["parent"]}
        if access_token == "teacher-token":
            return {"sub": "teacher-1", "roles": ["teacher"]}
        raise ValueError("invalid token")


def _client() -> TestClient:
    reset_metrics()
    reset_runtime_state()
    app = create_app()
    app.dependency_overrides[get_access_token_verifier] = lambda: _StubVerifier()
    return TestClient(app)


def test_parent_can_read_own_balance_and_ledger() -> None:
    client = _client()
    service_headers = {"X-Service-Token": SERVICE_TOKEN}
    parent_headers = {"Authorization": "Bearer parent-token"}

    client.post(
        "/internal/v1/bonus/accruals",
        headers=service_headers,
        json={
            "parent_id": "parent-1",
            "amount": 40,
            "reason_code": "course_completed_reward",
            "reference_id": "course-1",
            "idempotency_key": "parent-accrual-1",
        },
    )

    balance_response = client.get("/v1/parent/bonus/balance", headers=parent_headers)
    assert balance_response.status_code == 200
    assert balance_response.json() == {"parent_id": "parent-1", "balance": 40}

    ledger_response = client.get("/v1/parent/bonus/ledger", headers=parent_headers)
    assert ledger_response.status_code == 200
    payload = ledger_response.json()
    assert len(payload) == 1
    assert payload[0]["reason_code"] == "course_completed_reward"


def test_admin_routes_require_admin_role() -> None:
    client = _client()

    response = client.get(
        "/v1/admin/bonus/reports/summary",
        headers={"Authorization": "Bearer teacher-token"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Операция доступна только роли admin."


def test_admin_can_read_accounts_rules_reports_and_csv() -> None:
    client = _client()
    service_headers = {"X-Service-Token": SERVICE_TOKEN}
    admin_headers = {"Authorization": "Bearer admin-token"}

    client.post(
        "/internal/v1/bonus/accruals",
        headers=service_headers,
        json={
            "parent_id": "parent-1",
            "amount": 75,
            "reason_code": "course_completed_reward",
            "reference_id": "course-1",
            "idempotency_key": "admin-accrual-1",
        },
    )
    client.post(
        "/internal/v1/bonus/redemptions/commit",
        headers=service_headers,
        json={
            "parent_id": "parent-1",
            "amount": 25,
            "payment_intent_id": "pi-1",
            "idempotency_key": "admin-commit-1",
        },
    )
    client.post(
        "/internal/v1/bonus/accruals",
        headers=service_headers,
        json={
            "parent_id": "parent-2",
            "amount": 30,
            "reason_code": "manual_adjustment",
            "reference_id": "adj-1",
            "idempotency_key": "admin-accrual-2",
        },
    )

    rule_create_response = client.post(
        "/v1/admin/bonus/rules",
        headers=admin_headers,
        json={
            "trigger_type": "course_completed",
            "threshold": 1,
            "points": 25,
        },
    )
    assert rule_create_response.status_code == 201
    rule_id = rule_create_response.json()["rule_id"]

    rules_response = client.get("/v1/admin/bonus/rules", headers=admin_headers)
    assert rules_response.status_code == 200
    assert rules_response.json()[0]["rule_id"] == rule_id

    account_response = client.get(
        "/v1/admin/bonus/accounts/parent-1",
        headers=admin_headers,
    )
    assert account_response.status_code == 200
    assert account_response.json()["balance"] == 50
    assert account_response.json()["accruals_total"] == 75
    assert account_response.json()["redeemed_total"] == 25

    ledger_response = client.get(
        "/v1/admin/bonus/accounts/parent-1/ledger?reason_code=payment_redeem_commit",
        headers=admin_headers,
    )
    assert ledger_response.status_code == 200
    assert len(ledger_response.json()) == 1
    assert ledger_response.json()[0]["operation"] == "redeem_commit"

    summary_response = client.get(
        "/v1/admin/bonus/reports/summary",
        headers=admin_headers,
    )
    assert summary_response.status_code == 200
    assert summary_response.json()["wallets_with_positive_balance"] == 2
    assert summary_response.json()["total_balance_outstanding"] == 80
    assert summary_response.json()["total_accrued"] == 105
    assert summary_response.json()["total_redeemed"] == 25

    breakdown_response = client.get(
        "/v1/admin/bonus/reports/by-reason",
        headers=admin_headers,
    )
    assert breakdown_response.status_code == 200
    reason_codes = {item["reason_code"] for item in breakdown_response.json()}
    assert "course_completed_reward" in reason_codes
    assert "manual_adjustment" in reason_codes

    csv_response = client.get(
        "/v1/admin/bonus/reports/ledger.csv?parent_id=parent-1",
        headers=admin_headers,
    )
    assert csv_response.status_code == 200
    assert csv_response.headers["content-type"].startswith("text/csv")
    assert "course_completed_reward" in csv_response.text
    assert "payment_redeem_commit" in csv_response.text

    deactivate_response = client.post(
        f"/v1/admin/bonus/rules/{rule_id}/deactivate",
        headers=admin_headers,
    )
    assert deactivate_response.status_code == 200
    assert deactivate_response.json()["is_active"] is False
