"""
Centralized application configuration.

Uses pydantic-settings to load environment variables from a .env file
and expose them as typed Python attributes. A single shared `settings`
instance is created at module level (Singleton pattern) so every module
can import it directly.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables / .env file."""

    PROJECT_NAME: str = "FitnessPulse API"
    VERSION: str = "1.0.0"
    GEMINI_API_KEY: str = ""
    DATABASE_URL: str = "sqlite:///./fitnesspulse.db"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
