"""Air quality data routes."""

import logging
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
from app.services.data_collector import collector
from app.db.crud import insert_measurements, get_timeseries_for_prediction

logger = logging.getLogger("uvicorn.error")

router = APIRouter(prefix="/api", tags=["Air Quality"])


@router.get("/air-quality", response_model=AirQualityResponse)
async def get_air_quality():
    """Fetch latest air quality data for Indian cities from OpenAQ and process intelligence."""
    measurements = await fetch_india_air_quality()

    # Enrich each measurement with AQI + intelligence
    enriched_dicts = []
    collector_batch = []
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
            "unit": m.unit,
            "aqi_value": aqi_value,
            "aqi_category": aqi_category,
            "aqi_color": aqi["aqi_color"],
        })
        collector_batch.append({
            "city": m.city,
            "pollutant": m.pollutant,
            "aqi_value": aqi_value,
        })

    # Feed observations into ML data collector (in-memory)
    collector.add_bulk(collector_batch)

    # Persist to database (non-blocking, best-effort)
    try:
        await insert_measurements(enriched_dicts)
    except Exception as exc:
        logger.warning("DB insert failed (non-critical): %s", exc)

    # Build DB history for prediction engine
    db_history = {}
    try:
        seen_keys = set()
        for m in measurements:
            key = f"{m.city}|{m.pollutant}"
            if key not in seen_keys:
                seen_keys.add(key)
                history = await get_timeseries_for_prediction(m.city, m.pollutant)
                if history:
                    db_history[key] = history
    except Exception as exc:
        logger.warning("DB history fetch failed (non-critical): %s", exc)

    # Generate daily insight
    predictions = generate_predictions(measurements, db_history=db_history or None)
    alerts = evaluate_alerts(enriched_dicts, predictions)
    daily_insight = generate_daily_insight(enriched_dicts, len(alerts))

    return AirQualityResponse(data=measurements, daily_insight=daily_insight)

