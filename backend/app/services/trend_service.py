"""Trend service — in-memory trend detection across refresh cycles."""

from typing import Dict, Optional

# In-memory storage: key = "city|pollutant" → previous AQI value
_previous_values: Dict[str, int] = {}

STABLE_THRESHOLD = 5  # AQI change within ±5 = stable


def detect_trend(city: str, pollutant: str, current_aqi: int) -> str:
    """Compare current AQI with previous value to determine trend.

    Returns: "increasing", "decreasing", or "stable"
    """
    key = f"{city}|{pollutant}"
    previous = _previous_values.get(key)

    # Store current value for next comparison
    _previous_values[key] = current_aqi

    if previous is None:
        return "stable"  # No previous data → default to stable

    diff = current_aqi - previous
    if diff > STABLE_THRESHOLD:
        return "increasing"
    elif diff < -STABLE_THRESHOLD:
        return "decreasing"
    return "stable"


def get_all_trends() -> Dict[str, str]:
    """Return snapshot of all stored trends (for debugging)."""
    return dict(_previous_values)
