"""Purple Agent configuration using pydantic-settings.

Centralizes configuration for Purple Agent with environment variable support.
All configuration is loaded from environment variables with the PURPLE_ prefix.
Defaults are provided for local development.

Usage:
    from bulletproof_purple.settings import settings

    # Access settings
    port = settings.port
    timeout = settings.timeout
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class PurpleSettings(BaseSettings):
    """Purple Agent configuration settings.

    All settings can be overridden via environment variables with PURPLE_ prefix.
    For example, PURPLE_PORT=9010 will set port to 9010.

    Environment variables:
        PURPLE_HOST: Server host (default: 0.0.0.0)
        PURPLE_PORT: Server port (default: 9010)
        PURPLE_TIMEOUT: Request timeout in seconds (default: 300)
        PURPLE_AGENT_CARD_URL: AgentCard URL (default: http://{host}:{port})
        PURPLE_CARD_URL: Alternative AgentCard URL
        PURPLE_OUTPUT_FILE: Output file path (default: output/narratives.json)
        AGENT_UUID: Agent identifier (default: purple-agent)
    """

    model_config = SettingsConfigDict(
        env_prefix="PURPLE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Server settings (aligned with docker-compose-local.yml)
    host: str = "0.0.0.0"
    port: int = Field(default=9010, description="Container port (host: 9010)")
    timeout: int = Field(default=300, gt=0)

    # Agent identity
    agent_uuid: str = Field(default="purple-agent", validation_alias="AGENT_UUID")

    # Agent card settings (legacy and new)
    agent_card_url: str | None = Field(
        default=None,
        description="Legacy AgentCard URL (if None, defaults to http://{host}:{port})",
    )
    card_url: str | None = Field(
        default=None,
        description="AgentCard URL (if None, defaults to http://{host}:{port})",
    )

    # Output settings
    output_file: Path = Field(
        default=Path("output/narratives.json"),
        description="Output file path for generated narratives",
    )

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

    def get_card_url(self) -> str:
        """Get AgentCard URL, constructing from host/port if not explicitly set.

        Priority:
            1. card_url (new field)
            2. agent_card_url (legacy field)
            3. Constructed from host:port

        Returns:
            AgentCard URL string
        """
        if self.card_url:
            return self.card_url
        if self.agent_card_url:
            return self.agent_card_url
        return f"http://{self.host}:{self.port}"


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
