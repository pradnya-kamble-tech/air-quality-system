"""Isolated tests for the database layer."""

import pytest
import asyncio
from datetime import datetime, timezone, timedelta
from app.db.database import init_db, engine, Base
from app.db.crud import insert_measurements, get_history, get_timeseries_for_prediction

IST = timezone(timedelta(hours=5, minutes=30))

@pytest.mark.asyncio
async def test_db_persistence_and_history():
    """Verify measurements can be persisted and retrieved."""
    # Ensure tables are clean for test
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    # Synthetic measurements
    now = datetime.now(IST)
    measurements = [
        {
            "city": "TestCity",
            "station": "Station A",
            "pollutant": "pm25",
            "value": 10.0,
            "unit": "ug/m3",
            "aqi_value": 50,
            "aqi_category": "Good",
        },
        {
            "city": "TestCity",
            "station": "Station A",
            "pollutant": "pm25",
            "value": 12.0,
            "unit": "ug/m3",
            "aqi_value": 55,
            "aqi_category": "Good",
        }
    ]
    
    # Insert (first time)
    inserted = await insert_measurements(measurements)
    assert inserted == 2
    
    # Insert again (deduplication check - within 60s)
    inserted_again = await insert_measurements(measurements)
    assert inserted_again == 0
    
    # Retrieve history
    history = await get_history(city="TestCity", pollutant="pm25")
    assert len(history) == 2
    assert history[0]["aqi_value"] == 50
    assert history[1]["aqi_value"] == 55
    
    # Timeseries for prediction
    ts = await get_timeseries_for_prediction("TestCity", "pm25")
    assert ts == [50.0, 55.0]

@pytest.mark.asyncio
async def test_history_filtering():
    """Verify history filtering by city/pollutant."""
    # Already populated from previous test if using same DB, but we dropped all in first test
    # Let's add more
    measurements = [
        {"city": "CityA", "pollutant": "pm25", "value": 1.0, "aqi_value": 10},
        {"city": "CityB", "pollutant": "pm25", "value": 2.0, "aqi_value": 20},
        {"city": "CityA", "pollutant": "no2", "value": 3.0, "aqi_value": 30},
    ]
    await insert_measurements(measurements)
    
    # Filter by city
    history_a = await get_history(city="CityA")
    assert len(history_a) == 2
    
    # Filter by pollutant
    history_no2 = await get_history(pollutant="no2")
    assert len(history_no2) == 1
    assert history_no2[0]["city"] == "CityA"
