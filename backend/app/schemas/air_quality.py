"""Pydantic schemas for air quality data."""

from typing import List, Optional
from pydantic import BaseModel


class AirQualityMeasurement(BaseModel):
    """A single air quality measurement from a station."""

    city: str
    station: str
    pollutant: str
    value: float
    unit: str
    timestamp: str
    # AQI fields
    aqi_value: Optional[int] = None
    aqi_category: Optional[str] = None
    aqi_color: Optional[str] = None
    # Intelligence fields (Step 7)
    health_advice: Optional[str] = None
    decision_status: Optional[str] = None
    decision_label: Optional[str] = None
    decision_emoji: Optional[str] = None
    score: Optional[float] = None
    trend: Optional[str] = None


class AirQualityResponse(BaseModel):
    """Structured response wrapping a list of measurements."""

    data: List[AirQualityMeasurement]
    source: str = "OpenAQ"
    country: str = "India"
    daily_insight: Optional[str] = None
