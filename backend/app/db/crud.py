"""CRUD operations for air quality database."""

import logging
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import async_session
from app.db.models import MeasurementRecord, PredictionRecord

logger = logging.getLogger("uvicorn.error")

IST = timezone(timedelta(hours=5, minutes=30))


# ── Measurements ──────────────────────────────────────────

async def insert_measurements(enriched: List[Dict[str, Any]]) -> int:
    """Bulk insert measurements with deduplication.

    Skips records if a measurement for the same city+pollutant already
    exists within the last 60 seconds.  Returns count inserted.
    """
    inserted = 0
    now = datetime.now(IST)
    cutoff = now - timedelta(seconds=60)

    async with async_session() as session:
        for m in enriched:
            city = m["city"]
            pollutant = m["pollutant"]

            # Check for recent duplicate
            stmt = select(func.count()).where(
                and_(
                    MeasurementRecord.city == city,
                    MeasurementRecord.pollutant == pollutant,
                    MeasurementRecord.recorded_at >= cutoff,
                )
            )
            result = await session.execute(stmt)
            count = result.scalar_one()

            if count > 0:
                continue  # skip duplicate

            record = MeasurementRecord(
                city=city,
                station=m.get("station", ""),
                pollutant=pollutant,
                value=m.get("value", 0.0),
                unit=m.get("unit", ""),
                aqi_value=m.get("aqi_value"),
                aqi_category=m.get("aqi_category"),
                recorded_at=now,
            )
            session.add(record)
            inserted += 1

        await session.commit()

    if inserted:
        logger.info("Persisted %d measurement records to DB", inserted)
    return inserted


async def get_history(
    city: Optional[str] = None,
    pollutant: Optional[str] = None,
    hours: int = 72,
) -> List[Dict[str, Any]]:
    """Retrieve historical measurements filtered by city/pollutant/time.

    Returns list of dicts sorted by time ascending.
    """
    cutoff = datetime.now(IST) - timedelta(hours=hours)

    async with async_session() as session:
        stmt = select(MeasurementRecord).where(
            MeasurementRecord.recorded_at >= cutoff
        ).order_by(MeasurementRecord.recorded_at.asc())

        if city:
            stmt = stmt.where(MeasurementRecord.city == city)
        if pollutant:
            stmt = stmt.where(MeasurementRecord.pollutant == pollutant)

        result = await session.execute(stmt)
        rows = result.scalars().all()

    return [
        {
            "id": r.id,
            "city": r.city,
            "station": r.station,
            "pollutant": r.pollutant,
            "value": r.value,
            "unit": r.unit,
            "aqi_value": r.aqi_value,
            "aqi_category": r.aqi_category,
            "recorded_at": r.recorded_at.isoformat() if r.recorded_at else None,
        }
        for r in rows
    ]


async def get_timeseries_for_prediction(
    city: str, pollutant: str, hours: int = 168
) -> List[float]:
    """Return ordered list of AQI values for a city/pollutant.

    Used as input to the ML prediction pipeline.
    Default window: 7 days (168 hours).
    """
    cutoff = datetime.now(IST) - timedelta(hours=hours)

    async with async_session() as session:
        stmt = (
            select(MeasurementRecord.aqi_value)
            .where(
                and_(
                    MeasurementRecord.city == city,
                    MeasurementRecord.pollutant == pollutant,
                    MeasurementRecord.recorded_at >= cutoff,
                    MeasurementRecord.aqi_value.is_not(None),
                )
            )
            .order_by(MeasurementRecord.recorded_at.asc())
        )
        result = await session.execute(stmt)
        return [float(row[0]) for row in result.all()]


# ── Predictions Log ───────────────────────────────────────

async def log_predictions(predictions: List[Dict[str, Any]], model_type: str) -> None:
    """Store generated predictions for audit trail."""
    now = datetime.now(IST)

    async with async_session() as session:
        for pred in predictions:
            for p in pred.get("predictions", []):
                record = PredictionRecord(
                    city=pred["city"],
                    pollutant=pred["pollutant"],
                    predicted_aqi=p["aqi"],
                    target_time=datetime.fromisoformat(p["time_iso"]),
                    model_type=model_type,
                    created_at=now,
                )
                session.add(record)

        await session.commit()
