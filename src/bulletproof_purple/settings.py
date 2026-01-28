"""Centralized settings for Purple Agent using pydantic-settings.

All configuration is loaded from environment variables with the PURPLE_ prefix.
Defaults are provided for local development.

Usage:
    from bulletproof_purple.settings import settings

    # Access settings
    port = settings.port
    timeout = settings.timeout
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class PurpleSettings(BaseSettings):
    """Purple Agent configuration settings.

    All settings can be overridden via environment variables with PURPLE_ prefix.
    For example, PURPLE_PORT=9001 will set port to 9001.
    """

    model_config = SettingsConfigDict(
        env_prefix="PURPLE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Server settings
    port: int = 8001
    host: str = "0.0.0.0"
    timeout: int = 300


@lru_cache
def get_settings() -> PurpleSettings:
    """Get cached settings instance.

    Returns:
        PurpleSettings instance (cached after first call).
    """
    return PurpleSettings()


# Convenience singleton for direct import
settings = get_settings()
