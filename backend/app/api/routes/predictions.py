"""Prediction routes — AQI forecasting endpoint."""

from fastapi import APIRouter

from app.schemas.predictions import PredictionsResponse
from app.services.openaq_service import fetch_india_air_quality
from app.services.prediction_service import generate_predictions

router = APIRouter(prefix="/api", tags=["Predictions"])


@router.get("/predictions", response_model=PredictionsResponse)
async def get_predictions():
    """Generate short-term AQI predictions based on current air quality data."""
    measurements = await fetch_india_air_quality()
    forecasts = generate_predictions(measurements)
    return PredictionsResponse(data=forecasts)
