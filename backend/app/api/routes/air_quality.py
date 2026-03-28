"""Air quality data routes."""

from fastapi import APIRouter

from app.schemas.air_quality import AirQualityResponse
from app.services.openaq_service import fetch_india_air_quality
from app.services.aqi_calculator import calculate_aqi
from app.services.intelligence_service import (
    generate_health_advice,
    get_decision,
    calculate_score,
    generate_daily_insight,
)
from app.services.trend_service import detect_trend
from app.services.alert_service import evaluate_alerts
from app.services.prediction_service import generate_predictions

router = APIRouter(prefix="/api", tags=["Air Quality"])


@router.get("/air-quality", response_model=AirQualityResponse)
async def get_air_quality():
    """Fetch latest air quality data for Indian cities from OpenAQ."""
    measurements = await fetch_india_air_quality()

    # Enrich each measurement with AQI + intelligence
    enriched_dicts = []
    for m in measurements:
        aqi = calculate_aqi(m.pollutant, m.value)
        aqi_value = aqi["aqi_value"]
        aqi_category = aqi["aqi_category"]

        # Intelligence
        decision = get_decision(aqi_category)
        trend = detect_trend(m.city, m.pollutant, aqi_value)

        m.aqi_value = aqi_value
        m.aqi_category = aqi_category
        m.aqi_color = aqi["aqi_color"]
        m.health_advice = generate_health_advice(aqi_category, m.city)
        m.decision_status = decision["status"]
        m.decision_label = decision["label"]
        m.decision_emoji = decision["emoji"]
        m.score = calculate_score(aqi_value)
        m.trend = trend

        enriched_dicts.append({
            "city": m.city,
            "station": m.station,
            "pollutant": m.pollutant,
            "value": m.value,
            "aqi_value": aqi_value,
            "aqi_category": aqi_category,
            "aqi_color": aqi["aqi_color"],
        })

    # Generate daily insight
    predictions = generate_predictions(measurements)
    alerts = evaluate_alerts(enriched_dicts, predictions)
    daily_insight = generate_daily_insight(enriched_dicts, len(alerts))

    return AirQualityResponse(data=measurements, daily_insight=daily_insight)
