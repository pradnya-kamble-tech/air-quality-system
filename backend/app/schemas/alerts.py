"""Pydantic schemas for alerts."""

from typing import List
from pydantic import BaseModel


class Alert(BaseModel):
    """A single air quality alert."""

    city: str
    station: str
    pollutant: str
    type: str          # "current" | "prediction"
    aqi: int
    severity: str      # "medium" | "high" | "critical"
    message: str
    timestamp: str


class AlertsResponse(BaseModel):
    """Top-level alerts response model."""

    alerts: List[Alert]
    count: int
