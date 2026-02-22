"""Green Agent configuration using pydantic-settings.

Centralizes configuration for Green Agent with environment variable support.
All configuration is loaded from environment variables with the GREEN_ prefix.
Defaults are provided for local development.

Usage:
    from bulletproof_green.settings import settings

    # Access settings
    port = settings.port
    timeout = settings.timeout
    llm_api_key = settings.llm.api_key
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMSettings(BaseSettings):
    """LLM client configuration.

    Environment variables:
        AGENTBEATS_LLM_API_KEY: API key for LLM service (fallback to GREEN_OPENAI_API_KEY)
        AGENTBEATS_LLM_BASE_URL: Base URL for LLM API
        AGENTBEATS_LLM_MODEL: Model identifier (fallback to GREEN_LLM_MODEL)
        AGENTBEATS_LLM_TEMPERATURE: Temperature setting (fallback to GREEN_LLM_TEMPERATURE)
        AGENTBEATS_LLM_TIMEOUT: Request timeout (fallback to GREEN_LLM_TIMEOUT)
    """

    model_config = SettingsConfigDict(env_prefix="AGENTBEATS_LLM_")

    api_key: str | None = Field(default=None, validation_alias="AGENTBEATS_LLM_API_KEY")
    base_url: str = "https://api.openai.com/v1"
    model: str = Field(default="gpt-4", validation_alias="AGENTBEATS_LLM_MODEL")
    temperature: float = Field(default=0.0, ge=0.0, le=2.0)
    timeout: float = Field(default=30.0, gt=0.0)

    @field_validator("temperature")
    @classmethod
    def validate_temperature(cls, v: float) -> float:
        """Validate temperature is in valid range (0-2)."""
        if not 0 <= v <= 2:
            raise ValueError("temperature must be between 0 and 2")
        return v

    @field_validator("timeout")
    @classmethod
    def validate_timeout(cls, v: float) -> float:
        """Validate timeout is positive."""
        if v <= 0:
            raise ValueError("timeout must be positive")
        return v


class GreenSettings(BaseSettings):
    """Green Agent configuration settings.

    All settings can be overridden via environment variables with GREEN_ prefix.
    For example, GREEN_PORT=9009 will set port to 9009.

    Environment variables:
        GREEN_HOST: Server host (default: 0.0.0.0)
        GREEN_PORT: Server port (default: 9009)
        GREEN_PURPLE_PORT: Purple agent port (default: 9010)
        GREEN_TIMEOUT: Request timeout in seconds (default: 300)
        GREEN_AGENT_CARD_URL: AgentCard URL (default: http://{host}:{port})
        GREEN_CARD_URL: Alternative AgentCard URL
        GREEN_PURPLE_AGENT_URL: Purple Agent URL (default: http://{host}:{purple_port})
        GREEN_OUTPUT_FILE: Output file path (default: output/results.json)
        AGENT_UUID: Agent identifier (default: green-agent)
        GREEN_OPENAI_API_KEY: OpenAI API key (legacy, prefer AGENTBEATS_LLM_API_KEY)
    """

    model_config = SettingsConfigDict(
        env_prefix="GREEN_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Server settings (aligned with docker-compose-local.yml)
    host: str = "0.0.0.0"
    port: int = Field(default=9009, description="Container port (host: 9009)")
    purple_port: int = 9010
    timeout: int = Field(default=300, gt=0)

    # Agent identity
    agent_uuid: str = Field(default="green-agent", validation_alias="AGENT_UUID")

    # Agent card settings (legacy and new)
    agent_card_url: str | None = Field(
        default=None,
        description="Legacy AgentCard URL (if None, defaults to http://{host}:{port})",
    )
    card_url: str | None = Field(
        default=None,
        description="AgentCard URL (if None, defaults to http://{host}:{port})",
    )
    agent_card_timeout: int = Field(default=30, gt=0)
    agent_card_cache_ttl: int = Field(default=300, gt=0)

    # Purple Agent connection (aligned with docker-compose-local.yml)
    purple_agent_url: str = Field(
        default="http://localhost:9010",
        description="Purple agent URL (container uses http://purple:9010)",
    )

    # Output settings
    output_file: Path = Field(
        default=Path("output/results.json"),
        description="Output file path for evaluation results",
    )

    # LLM settings (nested and legacy flat structure for backwards compatibility)
    llm: LLMSettings = Field(default_factory=LLMSettings)

    # Legacy LLM settings (kept for backwards compatibility)
    openai_api_key: str | None = Field(default=None, description="Legacy: prefer llm.api_key")
    llm_model: str = Field(default="gpt-4", description="Legacy: prefer llm.model")
    llm_temperature: float = Field(
        default=0.0, ge=0.0, le=2.0, description="Legacy: prefer llm.temperature"
    )
    llm_timeout: float = Field(default=30.0, gt=0.0, description="Legacy: prefer llm.timeout")

    # LLM Judge hybrid scoring weights
    llm_alpha: float = Field(default=0.7, ge=0.0, le=1.0)
    llm_beta: float = Field(default=0.3, ge=0.0, le=1.0)

    # Arena mode settings
    arena_max_iterations: int = Field(default=5, gt=0)
    arena_target_risk_score: int = Field(default=20, ge=0, le=100)

    # Validators
    @field_validator("port", "purple_port")
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
