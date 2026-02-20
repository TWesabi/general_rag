"""Health check endpoint."""

from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "rag-system"}


@router.get("/ready")
async def readiness_check():
    """Readiness check endpoint."""
    # TODO: Add actual readiness checks (Weaviate connection, etc.)
    return {"status": "ready"}
