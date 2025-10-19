from fastapi import APIRouter

router = APIRouter()


@router.get("/health", tags=["system"])
def healthcheck() -> dict[str, str]:
    """Return a simple health status payload."""
    return {"status": "healthy"}
