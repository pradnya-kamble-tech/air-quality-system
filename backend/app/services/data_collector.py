"""In-memory time-series data collector for ML predictions.

Accumulates AQI observations over API refresh cycles so the ARIMA model
has historical context to train on.  Thread-safe and capped per series.
"""

import threading
from collections import defaultdict, deque
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple

IST = timezone(timedelta(hours=5, minutes=30))

# Maximum data points stored per (city, pollutant) key
MAX_POINTS_PER_SERIES = 500


class _TimeSeriesStore:
    """Thread-safe store for time-series AQI data."""

    def __init__(self, max_points: int = MAX_POINTS_PER_SERIES):
        self._lock = threading.Lock()
        self._max = max_points
        # key: "city|pollutant" → deque of (datetime, float_aqi)
        self._series: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=self._max)
        )

    # ── Write ──────────────────────────────────────────────

    def add_observation(
        self,
        city: str,
        pollutant: str,
        aqi_value: float,
        timestamp: Optional[datetime] = None,
    ) -> None:
        """Append a single observation.  Duplicates within 30s are skipped."""
        ts = timestamp or datetime.now(IST)
        key = f"{city}|{pollutant}"
        with self._lock:
            series = self._series[key]
            # Deduplicate: skip if last entry is within 30 seconds
            if series:
                last_ts = series[-1][0]
                if abs((ts - last_ts).total_seconds()) < 30:
                    return
            series.append((ts, float(aqi_value)))

    def add_bulk(self, observations: List[Dict]) -> int:
        """Add many observations at once.

        Each dict must have: city, pollutant, aqi_value.
        Optional: timestamp (datetime).
        Returns count of actually inserted points.
        """
        count = 0
        for obs in observations:
            before = self.series_length(obs["city"], obs["pollutant"])
            self.add_observation(
                city=obs["city"],
                pollutant=obs["pollutant"],
                aqi_value=obs["aqi_value"],
                timestamp=obs.get("timestamp"),
            )
            after = self.series_length(obs["city"], obs["pollutant"])
            if after > before:
                count += 1
        return count

    # ── Read ───────────────────────────────────────────────

    def get_series(
        self, city: str, pollutant: str
    ) -> List[Tuple[datetime, float]]:
        """Return sorted list of (timestamp, aqi) for a city/pollutant."""
        key = f"{city}|{pollutant}"
        with self._lock:
            return list(self._series.get(key, []))

    def get_aqi_values(self, city: str, pollutant: str) -> List[float]:
        """Return just the AQI values (ordered by time) for model input."""
        return [v for _, v in self.get_series(city, pollutant)]

    def series_length(self, city: str, pollutant: str) -> int:
        key = f"{city}|{pollutant}"
        with self._lock:
            return len(self._series.get(key, []))

    def all_keys(self) -> List[str]:
        """Return all city|pollutant keys with data."""
        with self._lock:
            return list(self._series.keys())

    def stats(self) -> Dict[str, int]:
        """Return {key: count} summary for diagnostics."""
        with self._lock:
            return {k: len(v) for k, v in self._series.items()}


# ── Module-level singleton ─────────────────────────────────

collector = _TimeSeriesStore()
