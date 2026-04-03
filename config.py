"""Application configuration loaded from environment variables."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    """Application settings."""

    telegram_token: str
    admin_ids: set[int]
    gemini_api_key: str
    openrouter_api_key: str
    groq_api_key: str
    default_timezone: str = "Europe/Moscow"
    default_he_grams: int = 12
    default_language: str = "ru"
    rate_limit_requests: int = 30
    rate_limit_window: int = 3600
    db_path: str = "data/diabot.db"


def load_settings() -> Settings:
    """Load settings from environment variables.

    Raises:
        ValueError: If required variables are missing.
    """
    load_dotenv()

    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_TOKEN environment variable is required")

    admin_ids_str = os.getenv("ADMIN_IDS", "")
    admin_ids = {int(x.strip()) for x in admin_ids_str.split(",") if x.strip()}

    gemini_key = os.getenv("GEMINI_API_KEY", "")
    openrouter_key = os.getenv("OPENROUTER_API_KEY", "")
    groq_key = os.getenv("GROQ_API_KEY", "")

    if not any([gemini_key, openrouter_key, groq_key]):
        raise ValueError(
            "At least one LLM API key is required "
            "(GEMINI_API_KEY, OPENROUTER_API_KEY, or GROQ_API_KEY)"
        )

    return Settings(
        telegram_token=token,
        admin_ids=admin_ids,
        gemini_api_key=gemini_key,
        openrouter_api_key=openrouter_key,
        groq_api_key=groq_key,
        default_timezone=os.getenv("DEFAULT_TIMEZONE", "Europe/Moscow"),
        default_he_grams=int(os.getenv("DEFAULT_HE_GRAMS", "12")),
        default_language=os.getenv("DEFAULT_LANGUAGE", "ru"),
        rate_limit_requests=int(os.getenv("RATE_LIMIT_REQUESTS", "30")),
        rate_limit_window=int(os.getenv("RATE_LIMIT_WINDOW", "3600")),
        db_path=os.getenv("DB_PATH", "data/diabot.db"),
    )
