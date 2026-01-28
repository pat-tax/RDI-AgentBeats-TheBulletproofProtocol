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

    # Server settings
    port: int = 8000
    host: str = "0.0.0.0"
    timeout: int = 300

    # Purple Agent connection
    purple_agent_url: str = "http://localhost:8001"

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


@lru_cache
def get_settings() -> GreenSettings:
    """Get cached settings instance.

    Returns:
        GreenSettings instance (cached after first call).
    """
    return GreenSettings()


# Convenience singleton for direct import
settings = get_settings()
