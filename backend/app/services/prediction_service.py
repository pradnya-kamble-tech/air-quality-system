"""Prediction service — ML-based AQI forecasting.

Strategy (tiered by data availability):
  1. ARIMA(1,1,1) — when ≥10 historical observations exist
  2. Exponential Smoothing — when 5-9 observations exist
  3. Heuristic fallback — when <5 observations (original logic)

All tiers produce the *same* output format so callers are unaffected.
"""

import logging
import math
import hashlib
import warnings
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional

import numpy as np

from app.schemas.air_quality import AirQualityMeasurement
from app.services.aqi_calculator import calculate_aqi
from app.services.data_collector import collector

logger = logging.getLogger("uvicorn.error")

HORIZON_HOURS = 6
IST = timezone(timedelta(hours=5, minutes=30))

# Minimum data requirements per tier
MIN_ARIMA = 10
MIN_EXP_SMOOTH = 5


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  TIER 1 — ARIMA
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _predict_arima(values: List[float], steps: int) -> Optional[List[float]]:
    """Run ARIMA(1,1,1) forecast.  Returns None on failure."""
    try:
        from statsmodels.tsa.arima.model import ARIMA

        arr = np.array(values, dtype=float)

        # Suppress convergence warnings — we handle failures gracefully
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            model = ARIMA(arr, order=(1, 1, 1))
            fitted = model.fit()
            forecast = fitted.forecast(steps=steps)

        result = [max(0, min(500, round(float(v)))) for v in forecast]
        logger.info("ARIMA forecast produced %d steps from %d observations", steps, len(values))
        return result

    except Exception as exc:
        logger.warning("ARIMA failed (%s), falling back", exc)
        return None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  TIER 2 — Exponential Smoothing
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _predict_exp_smoothing(values: List[float], steps: int, alpha: float = 0.3) -> List[float]:
    """Simple exponential smoothing forecast."""
    # Compute smoothed level
    level = values[0]
    for v in values[1:]:
        level = alpha * v + (1 - alpha) * level

    # Trend: average change over last few observations
    recent = values[-min(5, len(values)):]
    if len(recent) >= 2:
        trend = (recent[-1] - recent[0]) / (len(recent) - 1)
    else:
        trend = 0.0

    # Dampen trend over forecast horizon
    result = []
    for step in range(1, steps + 1):
        damping = 0.85 ** step  # trend decays
        predicted = level + trend * step * damping
        result.append(max(0, min(500, round(predicted))))

    logger.info("Exponential smoothing forecast from %d observations", len(values))
    return result


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  TIER 3 — Heuristic Fallback (original logic, simplified)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _deterministic_jitter(seed: str, step: int) -> float:
    """Small deterministic variation in [-1, 1]."""
    h = hashlib.md5(f"{seed}:{step}".encode()).hexdigest()
    return (int(h[:8], 16) / 0xFFFFFFFF) * 2 - 1


def _predict_heuristic(
    base_aqi: float, mean_aqi: float, seed: str, steps: int
) -> List[float]:
    """Original mean-reversion heuristic."""
    result = []
    current = base_aqi
    for step in range(1, steps + 1):
        pull = (mean_aqi - current) * 0.10
        jitter = _deterministic_jitter(seed, step) * current * 0.05
        current = current + pull + jitter
        result.append(max(0, min(500, round(current))))
    return result


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  PUBLIC API
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _choose_forecast(
    city: str,
    pollutant: str,
    current_aqi: float,
    mean_aqi: float,
    db_history: Optional[List[float]] = None,
) -> tuple:
    """Pick the best forecasting method and return (predictions, method_name)."""
    # Prefer DB history if supplied
    history = db_history

    # Fall back to in-memory collector
    if not history or len(history) < MIN_EXP_SMOOTH:
        history = collector.get_aqi_values(city, pollutant)

    # Ensure current value is always included at the end
    if history and abs(history[-1] - current_aqi) > 1:
        history = history + [current_aqi]
    elif not history:
        history = [current_aqi]

    # Tier 1: ARIMA
    if len(history) >= MIN_ARIMA:
        result = _predict_arima(history, HORIZON_HOURS)
        if result:
            return result, "ARIMA(1,1,1)"

    # Tier 2: Exponential Smoothing
    if len(history) >= MIN_EXP_SMOOTH:
        result = _predict_exp_smoothing(history, HORIZON_HOURS)
        return result, "Exponential Smoothing"

    # Tier 3: Heuristic
    seed = f"{city}:{pollutant}"
    result = _predict_heuristic(current_aqi, mean_aqi, seed, HORIZON_HOURS)
    return result, "Heuristic (Mean-Reversion)"


def generate_predictions(
    measurements: List[AirQualityMeasurement],
    db_history: Optional[Dict[str, List[float]]] = None,
) -> List[Dict[str, Any]]:
    """Generate AQI forecasts for each city/pollutant pair.

    Args:
        measurements: current live readings
        db_history: optional dict mapping "city|pollutant" → list of AQI floats
                    from database (Step 9).  Falls back to in-memory collector.
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
    methods_used = set()

    for key, group in groups.items():
        base_aqi = float(group["current_aqi"])
        mean_aqi = pollutant_means.get(group["pollutant"], base_aqi)

        # Get DB history for this key if available
        key_history = (db_history or {}).get(key)

        forecast_values, method = _choose_forecast(
            group["city"], group["pollutant"], base_aqi, mean_aqi, key_history
        )
        methods_used.add(method)

        predictions = []
        for step, predicted_aqi in enumerate(forecast_values, start=1):
            future_time = now + timedelta(hours=step)

            # Map predicted AQI back to category/color
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

    # Log what methods were used
    logger.info("Prediction methods used: %s", ", ".join(methods_used) or "none")

    return results
