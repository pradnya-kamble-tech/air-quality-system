"""History routes — past air quality data endpoint."""

from typing import Optional
from fastapi import APIRouter, Query

from app.db.crud import get_history

router = APIRouter(prefix="/api", tags=["History"])


@router.get("/history")
async def get_air_quality_history(
    city: Optional[str] = Query(None, description="Filter by city name"),
    pollutant: Optional[str] = Query(None, description="Filter by pollutant (e.g. pm25)"),
    hours: int = Query(72, ge=1, le=720, description="How many hours of history to return"),
):
    """Return historical air quality measurements from the database.

    Supports filtering by city, pollutant, and time range.
    """
    records = await get_history(city=city, pollutant=pollutant, hours=hours)
    return {
        "data": records,
        "count": len(records),
        "filters": {
            "city": city,
            "pollutant": pollutant,
            "hours": hours,
        },
    }
