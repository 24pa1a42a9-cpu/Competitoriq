"""
CompetitorIQ Configuration Package
Centralizes application settings and official source registries.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory for the backend package
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
load_dotenv(BASE_DIR / ".env")


class Config:
    """Application configuration parameters."""

    # Flask Settings
    ENV = os.getenv("FLASK_ENV", "development")
    DEBUG = ENV == "development"
    PORT = int(os.getenv("FLASK_PORT", 5000))
    SECRET_KEY = os.getenv("SECRET_KEY", "competitoriq-default-secret-key")

    # SQLite Database Configuration
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///competitor_iq.db")
    if DATABASE_URL.startswith("sqlite:///"):
        db_filename = DATABASE_URL.replace("sqlite:///", "")
        DB_PATH = str(BASE_DIR / db_filename)
    else:
        DB_PATH = str(BASE_DIR / "competitor_iq.db")

    # Hindsight Memory System Configuration
    HINDSIGHT_API_KEY = os.getenv("HINDSIGHT_API_KEY", "")
    HINDSIGHT_BASE_URL = os.getenv(
        "HINDSIGHT_BASE_URL", "https://api.hindsight.vectorize.io"
    )

    # Groq LLM Configuration
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

    @classmethod
    def validate_keys(cls) -> dict:
        """
        Check which external services are configured.
        Returns a dictionary summarizing service availability.
        """
        return {
            "hindsight_configured": bool(cls.HINDSIGHT_API_KEY),
            "groq_configured": bool(cls.GROQ_API_KEY),
            "database_path": cls.DB_PATH,
        }
