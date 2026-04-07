"""Intelligence service — generates human-friendly air quality insights.

Provides: health advice, go-outside decision, AQI score, daily insight.
"""

import hashlib
from typing import Dict, List, Any

# ── Health Advice Templates ──
_ADVICE = {
    "Good": [
        "Air quality is excellent! Perfect for outdoor activities. 🌿",
        "Breathe easy — the air is clean and fresh today. ☀️",
        "Great conditions for a jog, walk, or outdoor exercise. 🏃",
        "Fresh air all around — enjoy the outdoors! 🌤️",
        "Air is pristine. An ideal day for outdoor plans. 🌻",
    ],
    "Moderate": [
        "Air quality is fair. Outdoor activities are fine for most people. 👍",
        "Conditions are acceptable. Sensitive individuals may want to limit prolonged effort. 🌥️",
        "A decent day, but keep an eye on conditions if you have respiratory concerns. 💨",
        "Mostly safe outside. Consider shorter outdoor sessions if sensitive. 🍃",
        "Air is okay — just stay aware if you feel any discomfort. 🌬️",
    ],
    "Unhealthy (Sensitive)": [
        "Sensitive groups should reduce outdoor exertion. Others can proceed with caution. ⚠️",
        "Consider keeping outdoor time shorter today. Indoor activities are a good alternative. 🏠",
        "Air quality is declining. Wear a mask if spending extended time outside. 😷",
        "Not ideal for prolonged outdoor activity. Take breaks indoors regularly. 🚶",
        "If you have asthma or respiratory issues, minimize time outside today. 💛",
    ],
    "Unhealthy": [
        "Air quality is unhealthy. Limit outdoor exposure for everyone. 🟠",
        "Stay indoors when possible. Close windows and use air purifiers. 🏡",
        "Avoid heavy exercise outdoors. Short trips only if necessary. ⛔",
        "Protect yourself — wear an N95 mask if you must go outside. 😷",
        "Health risk is elevated. Keep children and elderly indoors. 🛡️",
    ],
    "Very Unhealthy": [
        "Air is very unhealthy. Avoid all outdoor activities if possible. 🔴",
        "Serious health risk — stay indoors with windows sealed. 🚨",
        "Do NOT exercise outside. Use air purifiers indoors. ⚠️",
        "Health emergency conditions. Limit all outdoor exposure. 🆘",
        "Dangerous air quality. Only go outside if absolutely necessary. 🛑",
    ],
    "Hazardous": [
        "HAZARDOUS conditions. Everyone should stay indoors immediately. 🚫",
        "Extreme health danger. Seal windows, use air purifiers, avoid all outdoor time. ☠️",
        "Air quality is at emergency levels. Do not go outside under any circumstances. 🆘",
        "Life-threatening air pollution. Stay indoors, seek medical help if feeling unwell. 🏥",
        "Maximum danger level. Protect yourself and your family — stay inside. 🛑",
    ],
}

# ── Decision Engine ──
_DECISIONS = {
    "Good":                   {"status": "yes",     "label": "Safe to go out",       "emoji": "✅"},
    "Moderate":               {"status": "yes",     "label": "Safe for most",        "emoji": "✅"},
    "Unhealthy (Sensitive)":  {"status": "limited", "label": "Be cautious",          "emoji": "⚠️"},
    "Unhealthy":              {"status": "limited", "label": "Limit outdoor time",   "emoji": "⚠️"},
    "Very Unhealthy":         {"status": "no",      "label": "Stay indoors",         "emoji": "❌"},
    "Hazardous":              {"status": "no",      "label": "Do not go outside",    "emoji": "❌"},
}


def _pick_advice(category: str, city: str) -> str:
    """Pick a deterministic advice string based on category and city."""
    options = _ADVICE.get(category, _ADVICE["Moderate"])
    idx = int(hashlib.md5(city.encode()).hexdigest()[:8], 16) % len(options)
    return options[idx]


def generate_health_advice(aqi_category: str, city: str) -> str:
    """Generate natural health advice based on AQI category."""
    return _pick_advice(aqi_category, city)


def get_decision(aqi_category: str) -> Dict[str, str]:
    """Return go-outside decision for given AQI category."""
    return _DECISIONS.get(aqi_category, _DECISIONS["Moderate"])


def calculate_score(aqi_value: int) -> float:
    """Convert AQI to a 0–10 score (10 = best air quality)."""
    score = max(0.0, 10.0 - (aqi_value / 50.0))
    return round(min(10.0, score), 1)


def generate_daily_insight(
    measurements: List[Dict[str, Any]],
    alerts_count: int = 0,
) -> str:
    """Generate a one-line daily insight headline from aggregate data."""
    if not measurements:
        return "Waiting for air quality data..."

    aqis = [m.get("aqi_value", 0) for m in measurements if m.get("aqi_value") is not None]
    if not aqis:
        return "Monitoring air quality across India..."

    avg_aqi = sum(aqis) / len(aqis)
    best = min(measurements, key=lambda m: m.get("aqi_value", 999))
    worst = max(measurements, key=lambda m: m.get("aqi_value", 0))

    if alerts_count >= 3:
        return f"⚠️ Multiple air quality alerts active. {worst.get('city', 'A city')} reporting highest pollution levels."
    elif avg_aqi <= 50:
        return f"🌿 Air quality is excellent across monitored cities. {best.get('city', 'Best city')} leads with cleanest air."
    elif avg_aqi <= 100:
        return f"🌤️ Air quality is generally acceptable. {best.get('city', 'Best city')} has the freshest air today."
    elif avg_aqi <= 150:
        return f"🌥️ Moderate pollution detected in some areas. {worst.get('city', 'A city')} shows elevated levels."
    elif avg_aqi <= 200:
        return f"🟠 Unhealthy air quality in several cities. {worst.get('city', 'A city')} is most affected — take precautions."
    else:
        return f"🔴 Dangerous pollution levels detected. {worst.get('city', 'A city')} reporting very unhealthy conditions. Stay safe."


def generate_forecast_insight(forecast_values: List[float], method: str) -> str:
    """Summarize the ML forecast trend in a human-friendly way."""
    if not forecast_values or len(forecast_values) < 2:
        return "Not enough data for trend analysis."

    start = forecast_values[0]
    end = forecast_values[-1]
    diff = end - start

    trend = "stable"
    if diff > 10:
        trend = "trending upward 📈"
    elif diff < -10:
        trend = "trending downward 📉"

    if "ARIMA" in method:
        model_name = "ARIMA model"
    elif "Smoothing" in method:
        model_name = "Exponential Smoothing"
    else:
        model_name = "Heuristic model"

    return f"The {model_name} detects levels are {trend} over the next 6 hours."

