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

from pydantic import field_validator
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

    # Validators
    @field_validator("port")
    @classmethod
    def validate_port(cls, v: int) -> int:
        """Validate port is in valid range (1-65535)."""
        if not 1 <= v <= 65535:
            raise ValueError("port must be between 1 and 65535")
        return v

    @field_validator("timeout")
    @classmethod
    def validate_positive_int(cls, v: int) -> int:
        """Validate timeout is positive."""
        if v <= 0:
            raise ValueError("timeout must be positive")
        return v


@lru_cache
def get_settings() -> PurpleSettings:
    """Get cached settings instance.

    Returns:
        PurpleSettings instance (cached after first call).
    """
    return PurpleSettings()


# Convenience singleton for direct import
settings = get_settings()


if __name__ == "__main__":
    """Debug command to dump current settings.

    Usage:
        python -m bulletproof_purple.settings
    """
    import json
    import sys

    try:
        settings_dict = settings.model_dump()
        print(json.dumps(settings_dict, indent=2))
    except Exception as e:
        print(f"Error loading settings: {e}", file=sys.stderr)
        sys.exit(1)
