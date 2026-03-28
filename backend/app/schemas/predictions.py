"""Pydantic schemas for prediction data."""

from typing import List
from pydantic import BaseModel


class PredictionPoint(BaseModel):
    """A single predicted AQI data point."""

    time: str
    time_iso: str
    hour_offset: int
    aqi: int
    category: str
    color: str


class CityPrediction(BaseModel):
    """Forecast for a specific city/pollutant combination."""

    city: str
    station: str
    pollutant: str
    current_aqi: int
    current_category: str
    current_color: str
    predictions: List[PredictionPoint]


class PredictionsResponse(BaseModel):
    """Top-level prediction response."""

    data: List[CityPrediction]
    horizon_hours: int = 6
    method: str = "Weighted Moving Average (Mean-Reversion)"
