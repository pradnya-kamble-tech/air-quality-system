"""Alert routes — air quality alert endpoint."""

from fastapi import APIRouter

from app.schemas.alerts import AlertsResponse
from app.services.openaq_service import fetch_india_air_quality
from app.services.aqi_calculator import calculate_aqi
from app.services.prediction_service import generate_predictions
from app.services.alert_service import evaluate_alerts

router = APIRouter(prefix="/api", tags=["Alerts"])


@router.get("/alerts", response_model=AlertsResponse)
async def get_alerts():
    """Evaluate current and predicted data to generate active alerts."""
    # Fetch current measurements
    measurements = await fetch_india_air_quality()

    # Enrich with AQI
    measurement_dicts = []
    for m in measurements:
        aqi = calculate_aqi(m.pollutant, m.value)
        measurement_dicts.append({
            "city": m.city,
            "station": m.station,
            "pollutant": m.pollutant,
            "value": m.value,
            "unit": m.unit,
            "aqi_value": aqi["aqi_value"],
            "aqi_category": aqi["aqi_category"],
            "aqi_color": aqi["aqi_color"],
        })

    # Generate predictions
    predictions = generate_predictions(measurements)

    # Evaluate alerts
    alerts = evaluate_alerts(measurement_dicts, predictions)

    return AlertsResponse(alerts=alerts, count=len(alerts))
