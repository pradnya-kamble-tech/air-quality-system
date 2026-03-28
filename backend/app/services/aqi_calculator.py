"""AQI Calculator — converts raw pollutant concentrations to AQI values.

Uses simplified breakpoint tables with linear interpolation.
"""

from typing import Dict, Tuple, List

# (C_low, C_high, AQI_low, AQI_high, category, color)
Breakpoint = Tuple[float, float, int, int, str, str]

# Breakpoint tables per pollutant (µg/m³)
_BREAKPOINTS: Dict[str, List[Breakpoint]] = {
    "pm25": [
        (0,    30,   0,   50,  "Good",                   "#34d399"),
        (30.1, 60,   51,  100, "Moderate",               "#fbbf24"),
        (60.1, 90,   101, 150, "Unhealthy (Sensitive)",   "#fb923c"),
        (90.1, 120,  151, 200, "Unhealthy",              "#f87171"),
        (120.1, 250, 201, 300, "Very Unhealthy",         "#a78bfa"),
        (250.1, 500, 301, 500, "Hazardous",              "#9f1239"),
    ],
    "pm10": [
        (0,    50,   0,   50,  "Good",                   "#34d399"),
        (50.1, 100,  51,  100, "Moderate",               "#fbbf24"),
        (100.1, 250, 101, 150, "Unhealthy (Sensitive)",   "#fb923c"),
        (250.1, 350, 151, 200, "Unhealthy",              "#f87171"),
        (350.1, 430, 201, 300, "Very Unhealthy",         "#a78bfa"),
        (430.1, 600, 301, 500, "Hazardous",              "#9f1239"),
    ],
    "no2": [
        (0,    40,   0,   50,  "Good",                   "#34d399"),
        (40.1, 80,   51,  100, "Moderate",               "#fbbf24"),
        (80.1, 180,  101, 150, "Unhealthy (Sensitive)",   "#fb923c"),
        (180.1, 280, 151, 200, "Unhealthy",              "#f87171"),
        (280.1, 400, 201, 300, "Very Unhealthy",         "#a78bfa"),
        (400.1, 600, 301, 500, "Hazardous",              "#9f1239"),
    ],
    "o3": [
        (0,    50,   0,   50,  "Good",                   "#34d399"),
        (50.1, 100,  51,  100, "Moderate",               "#fbbf24"),
        (100.1, 168, 101, 150, "Unhealthy (Sensitive)",   "#fb923c"),
        (168.1, 208, 151, 200, "Unhealthy",              "#f87171"),
        (208.1, 748, 201, 300, "Very Unhealthy",         "#a78bfa"),
        (748.1, 1000, 301, 500, "Hazardous",             "#9f1239"),
    ],
}

# Fallback for unknown pollutants
_DEFAULT_BREAKPOINTS: List[Breakpoint] = [
    (0,    50,   0,   50,  "Good",                   "#34d399"),
    (50.1, 100,  51,  100, "Moderate",               "#fbbf24"),
    (100.1, 150, 101, 150, "Unhealthy (Sensitive)",   "#fb923c"),
    (150.1, 200, 151, 200, "Unhealthy",              "#f87171"),
    (200.1, 300, 201, 300, "Very Unhealthy",         "#a78bfa"),
    (300.1, 500, 301, 500, "Hazardous",              "#9f1239"),
]


def calculate_aqi(pollutant: str, value: float) -> Dict[str, object]:
    """Calculate AQI value, category, and color for a given pollutant and concentration.

    Returns:
        dict with keys: aqi_value (int), aqi_category (str), aqi_color (str)
    """
    key = pollutant.lower().replace(".", "").replace("_", "")
    breakpoints = _BREAKPOINTS.get(key, _DEFAULT_BREAKPOINTS)

    # Clamp negative values
    if value < 0:
        value = 0.0

    for c_low, c_high, aqi_low, aqi_high, category, color in breakpoints:
        if value <= c_high:
            # Linear interpolation
            if c_high == c_low:
                aqi = aqi_low
            else:
                aqi = round(((aqi_high - aqi_low) / (c_high - c_low)) * (value - c_low) + aqi_low)
            return {
                "aqi_value": max(0, min(500, aqi)),
                "aqi_category": category,
                "aqi_color": color,
            }

    # Value exceeds all breakpoints → Hazardous
    return {
        "aqi_value": 500,
        "aqi_category": "Hazardous",
        "aqi_color": "#9f1239",
    }
