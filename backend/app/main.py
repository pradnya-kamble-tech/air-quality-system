"""Air Quality Monitor API — FastAPI Application Entry Point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.api.routes.health import router as health_router
from app.api.routes.air_quality import router as air_quality_router
from app.api.routes.predictions import router as predictions_router
from app.api.routes.alerts import router as alerts_router

logger = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Application lifespan: runs on startup and shutdown."""
    logger.info(
        "🚀 %s starting in %s mode on %s:%s",
        settings.APP_NAME,
        settings.ENV,
        settings.HOST,
        settings.PORT,
    )
    yield
    logger.info("👋 %s shutting down", settings.APP_NAME)


app = FastAPI(
    title=settings.APP_NAME,
    description="Real-time air quality monitoring and prediction system for India",
    version="0.1.0",
    lifespan=lifespan,
)

# Include routers
app.include_router(health_router)
app.include_router(air_quality_router)
app.include_router(predictions_router)
app.include_router(alerts_router)


@app.get("/")
async def root():
    """Root endpoint — confirms the API is running."""
    return {
        "message": "Air Quality API is running 🚀",
        "environment": settings.ENV,
    }
