"""Synthetic tests for the prediction service tiers."""

import pytest
from datetime import datetime, timezone, timedelta
from app.services.prediction_service import (
    _predict_arima,
    _predict_exp_smoothing,
    _predict_heuristic,
    _choose_forecast,
    HORIZON_HOURS,
)

IST = timezone(timedelta(hours=5, minutes=30))

def test_arima_prediction_smoothness():
    """Verify ARIMA produces smooth values for linear trend."""
    # Linear trend: 10, 11, 12... 29 (20 points)
    values = [float(10 + i) for i in range(20)]
    forecast = _predict_arima(values, HORIZON_HOURS)
    
    assert forecast is not None
    assert len(forecast) == HORIZON_HOURS
    # Should continue the upward trend or stabilize, not jump to 500 or 0
    assert 25 <= forecast[0] <= 35
    # Smoothness: no >50 AQI jump between steps
    for i in range(1, len(forecast)):
        assert abs(forecast[i] - forecast[i-1]) < 20

def test_exp_smoothing_fallback():
    """Verify exponential smoothing works with medium-sized data."""
    values = [100.0, 105.0, 110.0, 108.0, 112.0] # 5 points
    forecast = _predict_exp_smoothing(values, HORIZON_HOURS)
    
    assert len(forecast) == HORIZON_HOURS
    # Should b around 110-120
    assert 100 <= forecast[0] <= 130

def test_heuristic_fallback():
    """Verify heuristic works with very little data."""
    base_aqi = 150
    mean_aqi = 100
    seed = "test_city:pm25"
    forecast = _predict_heuristic(base_aqi, mean_aqi, seed, HORIZON_HOURS)
    
    assert len(forecast) == HORIZON_HOURS
    # Should drift toward mean (100)
    assert forecast[-1] < base_aqi

def test_forecast_tier_selection():
    """Verify the correct tier is chosen based on data length."""
    # Tier 1: ARIMA (>= 10)
    history_10 = [100.0] * 10
    _, method_10 = _choose_forecast("city", "pollutant", 100, 100, history_10)
    assert "ARIMA" in method_10
    
    # Tier 2: Exp Smoothing (5-9)
    history_5 = [100.0] * 5
    _, method_5 = _choose_forecast("city", "pollutant", 100, 100, history_5)
    assert "Exponential Smoothing" in method_5
    
    # Tier 3: Heuristic (< 5)
    history_2 = [100.0] * 2
    _, method_2 = _choose_forecast("city", "pollutant", 100, 100, history_2)
    assert "Heuristic" in method_2
