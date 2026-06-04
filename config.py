"""
Application configuration loaded from environment variables.

Uses Pydantic Settings to validate and type-check all required settings
on startup — the bot will fail to start with a clear error if anything
is missing or malformed.
"""

from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All runtime settings, loaded from .env or environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Telegram
    bot_token: str = Field(..., description="Bot token from @BotFather")
    admin_chat_id: int = Field(..., description="Admin's Telegram user ID")

    # Google Sheets
    google_sheet_id: str = Field(..., description="Target Google Sheet ID")
    google_service_account_path: Path = Field(
        default=Path("credentials/service-account.json"),
        description="Path to service account JSON key",
    )
    google_worksheet_name: str = Field(
        default="Applications",
        description="Name of the worksheet tab to write to",
    )

    # Storage
    database_path: Path = Field(
        default=Path("data/bot.db"),
        description="Path to SQLite database file",
    )

    # Logging
    log_level: str = Field(default="INFO", description="Log level")

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        valid = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v_upper = v.upper()
        if v_upper not in valid:
            raise ValueError(f"log_level must be one of {valid}, got {v!r}")
        return v_upper

    @field_validator("google_service_account_path")
    @classmethod
    def validate_credentials_path(cls, v: Path) -> Path:
        if not v.exists():
            raise ValueError(
                f"Service account credentials not found at {v}. "
                "See README.md for setup instructions."
            )
        return v


settings = Settings()  # type: ignore[call-arg]
