"""Alert service — evaluates current and predicted AQI to generate alerts."""

from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any

IST = timezone(timedelta(hours=5, minutes=30))

# Severity thresholds
THRESHOLDS = [
    (301, "critical", "🔴 HAZARDOUS air quality. Stay indoors and close windows."),
    (201, "high",     "🟠 Very unhealthy air quality. Avoid all outdoor activity."),
    (151, "medium",   "🟡 Unhealthy air quality. Limit prolonged outdoor exertion."),
]


def _get_severity(aqi: int):
    """Return (severity, base_message) for a given AQI, or None if below threshold."""
    for threshold, severity, message in THRESHOLDS:
        if aqi >= threshold:
            return severity, message
    return None, None


def evaluate_alerts(
    measurements: List[Dict[str, Any]],
    predictions: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Evaluate current and predicted data to generate alerts.

    Args:
        measurements: list of dicts with city, pollutant, aqi_value, aqi_category, etc.
        predictions: list of dicts with city, pollutant, current_aqi, predictions[].

    Returns:
        list of alert objects sorted by severity (critical first).
    """
    now = datetime.now(IST).isoformat()
    alerts: List[Dict[str, Any]] = []
    seen_keys = set()  # deduplication

    # ── Current data alerts ──
    for m in measurements:
        aqi = m.get("aqi_value") or 0
        severity, message = _get_severity(aqi)
        if severity is None:
            continue

        key = f"current|{m['city']}|{m['pollutant']}"
        if key in seen_keys:
            continue
        seen_keys.add(key)

        alerts.append({
            "city": m["city"],
            "station": m.get("station", ""),
            "pollutant": m["pollutant"],
            "type": "current",
            "aqi": aqi,
            "severity": severity,
            "message": f"{m['city']}: {message}",
            "timestamp": now,
        })

    # ── Prediction alerts ──
    for pred in predictions:
        # Find worst predicted AQI
        worst_aqi = 0
        worst_time = ""
        for p in pred.get("predictions", []):
            if p["aqi"] > worst_aqi:
                worst_aqi = p["aqi"]
                worst_time = p.get("time", "")

        severity, message = _get_severity(worst_aqi)
        if severity is None:
            continue

        # Skip if we already have a *current* alert for the same city+pollutant
        # at the same or higher severity
        current_key = f"current|{pred['city']}|{pred['pollutant']}"
        if current_key in seen_keys:
            # Only add prediction alert if it's a worse severity
            existing = [a for a in alerts if a["city"] == pred["city"]
                        and a["pollutant"] == pred["pollutant"]
                        and a["type"] == "current"]
            if existing:
                existing_sev = existing[0]["severity"]
                sev_order = {"critical": 3, "high": 2, "medium": 1}
                if sev_order.get(severity, 0) <= sev_order.get(existing_sev, 0):
                    continue

        pred_key = f"prediction|{pred['city']}|{pred['pollutant']}"
        if pred_key in seen_keys:
            continue
        seen_keys.add(pred_key)

        alerts.append({
            "city": pred["city"],
            "station": pred.get("station", ""),
            "pollutant": pred["pollutant"],
            "type": "prediction",
            "aqi": worst_aqi,
            "severity": severity,
            "message": f"{pred['city']}: {message} (Forecast peak at {worst_time})",
            "timestamp": now,
        })

    # Sort: critical → high → medium
    severity_order = {"critical": 0, "high": 1, "medium": 2}
    alerts.sort(key=lambda a: severity_order.get(a["severity"], 99))

    return alerts
