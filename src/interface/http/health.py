"""Health endpoints."""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/healthz")
def healthz() -> dict[str, str]:
    """Basic liveness check."""

    return {"status": "ok"}
