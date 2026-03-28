"""Application configuration loaded from environment variables."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the backend directory
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Settings:
    """Application settings loaded from environment variables."""

    ENV: str = os.getenv("ENV", "development")
    APP_NAME: str = os.getenv("APP_NAME", "Air Quality Monitor API")
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))
    OPENAQ_API_KEY: str = os.getenv("OPENAQ_API_KEY", "")


settings = Settings()
