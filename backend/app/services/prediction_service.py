"""Prediction service — generates short-term AQI forecasts.

Uses a simple weighted moving average with mean-reversion and
deterministic jitter to produce 6 hourly AQI predictions per
city/pollutant combination.
"""

import hashlib
import math
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any

from app.schemas.air_quality import AirQualityMeasurement
from app.services.aqi_calculator import calculate_aqi

HORIZON_HOURS = 6
IST = timezone(timedelta(hours=5, minutes=30))


def _deterministic_jitter(seed: str, step: int) -> float:
    """Generate a small deterministic variation from a seed string and step index.

    Returns a value in [-1.0, 1.0], consistent across calls with the same seed+step.
    """
    h = hashlib.md5(f"{seed}:{step}".encode()).hexdigest()
    # Use first 8 hex chars → 32-bit integer → normalize to [-1, 1]
    return (int(h[:8], 16) / 0xFFFFFFFF) * 2 - 1


def generate_predictions(
    measurements: List[AirQualityMeasurement],
) -> List[Dict[str, Any]]:
    """Generate AQI forecasts for each city/pollutant pair.

    Strategy:
    - Base = current AQI for that city/pollutant
    - Group mean = average AQI across all stations for that pollutant
    - Each hourly step drifts toward the group mean (mean-reversion, 10% pull)
    - Small deterministic jitter (±5%) adds realistic variation
    - Values clamped to [0, 500]
    """
    # Group by (city, pollutant)
    groups: Dict[str, Dict[str, Any]] = {}
    pollutant_values: Dict[str, List[float]] = {}

    for m in measurements:
        aqi_info = calculate_aqi(m.pollutant, m.value)
        key = f"{m.city}|{m.pollutant}"

        if key not in groups:
            groups[key] = {
                "city": m.city,
                "station": m.station,
                "pollutant": m.pollutant,
                "current_value": m.value,
                "current_aqi": aqi_info["aqi_value"],
                "current_category": aqi_info["aqi_category"],
                "current_color": aqi_info["aqi_color"],
                "unit": m.unit,
            }

        pollutant_values.setdefault(m.pollutant, []).append(aqi_info["aqi_value"])

    # Compute pollutant-level mean AQI
    pollutant_means: Dict[str, float] = {
        p: sum(vals) / len(vals) for p, vals in pollutant_values.items()
    }

    now = datetime.now(IST)
    results: List[Dict[str, Any]] = []

    for key, group in groups.items():
        base_aqi = float(group["current_aqi"])
        mean_aqi = pollutant_means.get(group["pollutant"], base_aqi)
        seed = f"{group['city']}:{group['pollutant']}"

        predictions = []
        current = base_aqi

        for step in range(1, HORIZON_HOURS + 1):
            future_time = now + timedelta(hours=step)

            # Mean-reversion pull (10% toward group mean)
            pull = (mean_aqi - current) * 0.10

            # Deterministic jitter (±5% of current value)
            jitter = _deterministic_jitter(seed, step) * current * 0.05

            # Next value
            current = current + pull + jitter

            # Clamp to valid AQI range
            predicted_aqi = max(0, min(500, round(current)))

            # Get category and color for the predicted AQI
            # Reverse-map: use a dummy pollutant lookup since we already have AQI
            # We use the raw value proportional mapping from the original pollutant
            raw_ratio = group["current_value"] / max(group["current_aqi"], 1)
            estimated_raw = predicted_aqi * raw_ratio
            aqi_info = calculate_aqi(group["pollutant"], estimated_raw)

            predictions.append({
                "time": future_time.strftime("%I:%M %p"),
                "time_iso": future_time.isoformat(),
                "hour_offset": step,
                "aqi": predicted_aqi,
                "category": aqi_info["aqi_category"],
                "color": aqi_info["aqi_color"],
            })

        results.append({
            "city": group["city"],
            "station": group["station"],
            "pollutant": group["pollutant"],
            "current_aqi": group["current_aqi"],
            "current_category": group["current_category"],
            "current_color": group["current_color"],
            "predictions": predictions,
        })

    # Sort by city name for consistent ordering
    results.sort(key=lambda x: x["city"])

    return results
