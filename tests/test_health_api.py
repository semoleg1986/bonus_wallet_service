from fastapi.testclient import TestClient

from src.interface.http.app import create_app
from src.interface.http.observability import reset_metrics


def _client() -> TestClient:
    reset_metrics()
    return TestClient(create_app())


def test_healthz_returns_ok_and_headers() -> None:
    response = _client().get(
        "/healthz",
        headers={
            "X-Request-ID": "req-bonus-health-001",
            "X-Correlation-ID": "corr-bonus-health-001",
        },
    )

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert response.headers.get("X-Request-ID") == "req-bonus-health-001"
    assert response.headers.get("X-Correlation-ID") == "corr-bonus-health-001"
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("Referrer-Policy") == "no-referrer"
    assert (
        response.headers.get("Permissions-Policy")
        == "camera=(), microphone=(), geolocation=()"
    )


def test_metrics_endpoint_exposes_prometheus_http_metrics() -> None:
    client = _client()

    client.get("/healthz")
    response = client.get("/metrics")

    assert response.status_code == 200
    assert "http_requests_total" in response.text
    assert "http_request_duration_seconds" in response.text
    assert "http_errors_total" in response.text
    expected_line = (
        'http_requests_total{service="bonus_wallet_service",method="GET",'
        'path="/healthz",status="200"} 1'
    )
    assert expected_line in response.text
