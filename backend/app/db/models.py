"""ORM models for air quality data persistence."""

from datetime import datetime, timezone, timedelta
from sqlalchemy import Column, Integer, Float, String, DateTime, Index
from app.db.database import Base

IST = timezone(timedelta(hours=5, minutes=30))


def _now_ist():
    return datetime.now(IST)


class MeasurementRecord(Base):
    """Stores each air quality observation fetched from OpenAQ."""

    __tablename__ = "measurements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    city = Column(String(120), nullable=False, index=True)
    station = Column(String(200), nullable=False)
    pollutant = Column(String(20), nullable=False, index=True)
    value = Column(Float, nullable=False)
    unit = Column(String(20), nullable=True)
    aqi_value = Column(Integer, nullable=True)
    aqi_category = Column(String(40), nullable=True)
    recorded_at = Column(DateTime(timezone=True), nullable=False, default=_now_ist)

    __table_args__ = (
        Index("ix_measurements_city_pollutant_time", "city", "pollutant", "recorded_at"),
    )

    def __repr__(self):
        return f"<Measurement {self.city}/{self.pollutant} AQI={self.aqi_value} @ {self.recorded_at}>"


class PredictionRecord(Base):
    """Logs generated predictions for auditing."""

    __tablename__ = "predictions_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    city = Column(String(120), nullable=False, index=True)
    pollutant = Column(String(20), nullable=False)
    predicted_aqi = Column(Integer, nullable=False)
    target_time = Column(DateTime(timezone=True), nullable=False)
    model_type = Column(String(40), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_now_ist)

    def __repr__(self):
        return f"<Prediction {self.city}/{self.pollutant} AQI={self.predicted_aqi} @ {self.target_time}>"
