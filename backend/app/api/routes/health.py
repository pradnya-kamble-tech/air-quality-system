"""Health check route for the Air Quality Backend."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """Return service health status."""
    return {
        "status": "OK",
        "service": "Air Quality Backend",
        "region": "India",
    }
