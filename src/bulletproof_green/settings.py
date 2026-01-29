"""Centralized settings for Green Agent using pydantic-settings.

All configuration is loaded from environment variables with the GREEN_ prefix.
Defaults are provided for local development.

Usage:
    from bulletproof_green.settings import settings

    # Access settings
    port = settings.port
    timeout = settings.timeout
"""

from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class GreenSettings(BaseSettings):
    """Green Agent configuration settings.

    All settings can be overridden via environment variables with GREEN_ prefix.
    For example, GREEN_PORT=9000 will set port to 9000.
    """

    model_config = SettingsConfigDict(
        env_prefix="GREEN_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Server settings (aligned with docker-compose-local.yml)
    host: str = "0.0.0.0"
    port: int = 9009  # Container port (host: 9009)
    purple_port: int = 9010
    timeout: int = 300
    agent_card_url: str | None = None  # If None, defaults to http://{host}:{port}

    # Purple Agent connection (aligned with docker-compose-local.yml)
    purple_agent_url: str = f"http://{host}:{purple_port}"

    # Agent card settings
    agent_card_timeout: int = 30
    agent_card_cache_ttl: int = 300

    # LLM Judge settings
    openai_api_key: str | None = None
    llm_model: str = "gpt-4"
    llm_temperature: float = 0.0
    llm_alpha: float = 0.7
    llm_beta: float = 0.3
    llm_timeout: float = 30.0

    # Arena mode settings
    arena_max_iterations: int = 5
    arena_target_risk_score: int = 20

    # Validators
    @field_validator("port")
    @classmethod
    def validate_port(cls, v: int) -> int:
        """Validate port is in valid range (1-65535)."""
        if not 1 <= v <= 65535:
            raise ValueError("port must be between 1 and 65535")
        return v

    @field_validator("timeout", "agent_card_timeout", "agent_card_cache_ttl")
    @classmethod
    def validate_positive_int(cls, v: int) -> int:
        """Validate integer values are positive."""
        if v <= 0:
            raise ValueError("value must be positive")
        return v

    @field_validator("llm_alpha", "llm_beta")
    @classmethod
    def validate_weight(cls, v: float) -> float:
        """Validate weight is in valid range (0-1)."""
        if not 0 <= v <= 1:
            raise ValueError("weight must be between 0 and 1")
        return v

    @field_validator("llm_temperature")
    @classmethod
    def validate_temperature(cls, v: float) -> float:
        """Validate temperature is in valid range (0-2)."""
        if not 0 <= v <= 2:
            raise ValueError("temperature must be between 0 and 2")
        return v

    @field_validator("llm_timeout")
    @classmethod
    def validate_positive_float(cls, v: float) -> float:
        """Validate float values are positive."""
        if v <= 0:
            raise ValueError("timeout must be positive")
        return v

    @field_validator("arena_max_iterations")
    @classmethod
    def validate_max_iterations(cls, v: int) -> int:
        """Validate max iterations is positive."""
        if v <= 0:
            raise ValueError("max_iterations must be positive")
        return v

    @field_validator("arena_target_risk_score")
    @classmethod
    def validate_risk_score(cls, v: int) -> int:
        """Validate risk score is in valid range (0-100)."""
        if not 0 <= v <= 100:
            raise ValueError("risk_score must be between 0 and 100")
        return v


@lru_cache
def get_settings() -> GreenSettings:
    """Get cached settings instance.

    Returns:
        GreenSettings instance (cached after first call).
    """
    return GreenSettings()


# Convenience singleton for direct import
settings = get_settings()


if __name__ == "__main__":
    """Debug command to dump current settings.

    Usage:
        python -m bulletproof_green.settings
    """
    import json
    import sys

    try:
        settings_dict = settings.model_dump()
        print(json.dumps(settings_dict, indent=2))
    except Exception as e:
        print(f"Error loading settings: {e}", file=sys.stderr)
        sys.exit(1)
