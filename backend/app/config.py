"""Configuration settings for AegisPay Gateway."""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "AegisPay Gateway"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Supabase Settings
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None

    # AP2 Mandate Security
    AP2_SECRET_KEY: str = "aegis_ap2_super_secret_mandate_signing_key_2026"
    AP2_ALGORITHM: str = "HS256"

    # Razorpay Settings
    RAZORPAY_KEY_ID: str = "rzp_test_default_mock_key"
    RAZORPAY_KEY_SECRET: str = "rzp_test_default_mock_secret"
    RAZORPAY_WEBHOOK_SECRET: str = "rzp_webhook_secret_2026"

    # OpenAI Settings (optional for semantic embeddings)
    OPENAI_API_KEY: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
