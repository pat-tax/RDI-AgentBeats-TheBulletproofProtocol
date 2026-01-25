"""Tests for scenario.toml (STORY-013).

This test module validates the acceptance criteria for STORY-013:
- Green agent registered -> agentbeats_id obtained
- Purple agent registered -> agentbeats_id obtained
- scenario.toml configured with production IDs
- Platform validates AgentCard endpoints
- Platform can pull and run Docker images from GHCR
"""

import re
import tomllib
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
SCENARIO_TOML = PROJECT_ROOT / "scenario.toml"


class TestScenarioTomlExists:
    """Test that scenario.toml exists in project root."""

    def test_scenario_toml_exists(self) -> None:
        """Test scenario.toml exists in project root."""
        assert SCENARIO_TOML.exists(), "scenario.toml must exist in project root"


class TestScenarioTomlValidSyntax:
    """Test that scenario.toml is valid TOML syntax."""

    def test_is_valid_toml(self) -> None:
        """Test scenario.toml is valid TOML syntax."""
        assert SCENARIO_TOML.exists(), "scenario.toml must exist first"
        content = SCENARIO_TOML.read_bytes()
        data = tomllib.loads(content.decode("utf-8"))
        assert data is not None, "scenario.toml must contain valid TOML"
        assert isinstance(data, dict), "scenario.toml must be a TOML table"


def _load_scenario() -> dict:
    """Load and return scenario.toml as a dict."""
    content = SCENARIO_TOML.read_bytes()
    data = tomllib.loads(content.decode("utf-8"))
    if not isinstance(data, dict):
        raise TypeError("scenario.toml must be a TOML table")
    return data


class TestGreenAgentConfiguration:
    """Test green agent configuration in scenario.toml."""

    def test_green_agent_section_exists(self) -> None:
        """Test [green_agent] section exists."""
        scenario = _load_scenario()
        assert "green_agent" in scenario, "scenario.toml must have [green_agent] section"

    def test_green_agent_has_agentbeats_id(self) -> None:
        """Test green_agent has agentbeats_id field."""
        scenario = _load_scenario()
        green_agent = scenario.get("green_agent", {})
        assert "agentbeats_id" in green_agent, "green_agent must have agentbeats_id"

    def test_green_agent_agentbeats_id_is_not_empty(self) -> None:
        """Test green_agent agentbeats_id is not empty (agent registered)."""
        scenario = _load_scenario()
        green_agent = scenario.get("green_agent", {})
        agentbeats_id = green_agent.get("agentbeats_id", "")
        assert agentbeats_id, "green_agent agentbeats_id must not be empty (register on agentbeats.dev)"

    def test_green_agent_agentbeats_id_format(self) -> None:
        """Test green_agent agentbeats_id has valid format."""
        scenario = _load_scenario()
        green_agent = scenario.get("green_agent", {})
        agentbeats_id = green_agent.get("agentbeats_id", "")
        # AgentBeats IDs are typically alphanumeric with underscores or hyphens
        # Format: agent_xyz123abc456 or similar UUID-like patterns
        assert re.match(
            r"^[a-zA-Z0-9_-]+$", agentbeats_id
        ), f"green_agent agentbeats_id has invalid format: {agentbeats_id}"

    def test_green_agent_has_env_config(self) -> None:
        """Test green_agent has env configuration."""
        scenario = _load_scenario()
        green_agent = scenario.get("green_agent", {})
        assert "env" in green_agent, "green_agent must have env configuration"


class TestParticipantsConfiguration:
    """Test participants (purple agent) configuration in scenario.toml."""

    def test_participants_section_exists(self) -> None:
        """Test [[participants]] section exists."""
        scenario = _load_scenario()
        assert "participants" in scenario, "scenario.toml must have [[participants]] section"

    def test_participants_is_list(self) -> None:
        """Test participants is a list (array of tables)."""
        scenario = _load_scenario()
        participants = scenario.get("participants", [])
        assert isinstance(participants, list), "participants must be a list"

    def test_participants_has_at_least_one_entry(self) -> None:
        """Test participants has at least one entry (purple agent)."""
        scenario = _load_scenario()
        participants = scenario.get("participants", [])
        assert len(participants) >= 1, "participants must have at least one entry"

    def test_purple_participant_has_agentbeats_id(self) -> None:
        """Test purple participant has agentbeats_id field."""
        scenario = _load_scenario()
        participants = scenario.get("participants", [])
        assert len(participants) >= 1, "participants must have at least one entry"
        purple_participant = participants[0]
        assert "agentbeats_id" in purple_participant, "participant must have agentbeats_id"

    def test_purple_participant_agentbeats_id_is_not_empty(self) -> None:
        """Test purple participant agentbeats_id is not empty (agent registered)."""
        scenario = _load_scenario()
        participants = scenario.get("participants", [])
        assert len(participants) >= 1, "participants must have at least one entry"
        purple_participant = participants[0]
        agentbeats_id = purple_participant.get("agentbeats_id", "")
        assert agentbeats_id, "participant agentbeats_id must not be empty (register on agentbeats.dev)"

    def test_purple_participant_agentbeats_id_format(self) -> None:
        """Test purple participant agentbeats_id has valid format."""
        scenario = _load_scenario()
        participants = scenario.get("participants", [])
        assert len(participants) >= 1, "participants must have at least one entry"
        purple_participant = participants[0]
        agentbeats_id = purple_participant.get("agentbeats_id", "")
        assert re.match(
            r"^[a-zA-Z0-9_-]+$", agentbeats_id
        ), f"participant agentbeats_id has invalid format: {agentbeats_id}"

    def test_purple_participant_has_name(self) -> None:
        """Test purple participant has name field."""
        scenario = _load_scenario()
        participants = scenario.get("participants", [])
        assert len(participants) >= 1, "participants must have at least one entry"
        purple_participant = participants[0]
        assert "name" in purple_participant, "participant must have name"

    def test_purple_participant_name_is_substantiator(self) -> None:
        """Test purple participant name is 'substantiator'."""
        scenario = _load_scenario()
        participants = scenario.get("participants", [])
        assert len(participants) >= 1, "participants must have at least one entry"
        purple_participant = participants[0]
        name = purple_participant.get("name", "")
        assert name == "substantiator", f"participant name must be 'substantiator', got '{name}'"


class TestConfigSection:
    """Test [config] section in scenario.toml."""

    def test_config_section_exists(self) -> None:
        """Test [config] section exists."""
        scenario = _load_scenario()
        assert "config" in scenario, "scenario.toml must have [config] section"

    def test_config_has_difficulty(self) -> None:
        """Test config has difficulty setting."""
        scenario = _load_scenario()
        config = scenario.get("config", {})
        assert "difficulty" in config, "config must have difficulty setting"

    def test_config_has_max_iterations(self) -> None:
        """Test config has max_iterations setting."""
        scenario = _load_scenario()
        config = scenario.get("config", {})
        assert "max_iterations" in config, "config must have max_iterations setting"

    def test_config_max_iterations_is_positive(self) -> None:
        """Test config max_iterations is a positive integer."""
        scenario = _load_scenario()
        config = scenario.get("config", {})
        max_iterations = config.get("max_iterations", 0)
        assert isinstance(max_iterations, int), "max_iterations must be an integer"
        assert max_iterations > 0, "max_iterations must be positive"

    def test_config_has_target_risk_score(self) -> None:
        """Test config has target_risk_score setting."""
        scenario = _load_scenario()
        config = scenario.get("config", {})
        assert "target_risk_score" in config, "config must have target_risk_score setting"

    def test_config_target_risk_score_in_valid_range(self) -> None:
        """Test config target_risk_score is in valid range (0-100)."""
        scenario = _load_scenario()
        config = scenario.get("config", {})
        target_risk_score = config.get("target_risk_score", -1)
        assert isinstance(target_risk_score, int), "target_risk_score must be an integer"
        assert 0 <= target_risk_score <= 100, "target_risk_score must be in range 0-100"

    def test_config_has_evaluation_mode(self) -> None:
        """Test config has evaluation_mode setting."""
        scenario = _load_scenario()
        config = scenario.get("config", {})
        assert "evaluation_mode" in config, "config must have evaluation_mode setting"


class TestAgentIdsAreDistinct:
    """Test that green and purple agent IDs are distinct."""

    def test_green_and_purple_ids_are_different(self) -> None:
        """Test green_agent and participant agentbeats_ids are different."""
        scenario = _load_scenario()
        green_agent = scenario.get("green_agent", {})
        participants = scenario.get("participants", [])

        green_id = green_agent.get("agentbeats_id", "")
        if not participants:
            return  # No participants to compare

        purple_id = participants[0].get("agentbeats_id", "")

        # Both IDs must be non-empty for this check to be meaningful
        if green_id and purple_id:
            assert green_id != purple_id, (
                "green_agent and participant must have different agentbeats_ids"
            )


class TestNoHardcodedSecrets:
    """Test no hardcoded secrets in scenario.toml."""

    def test_no_plaintext_api_keys(self) -> None:
        """Test no plaintext API keys in scenario.toml."""
        content = SCENARIO_TOML.read_text()
        # Check for common secret patterns that aren't env var references
        # Env var references look like ${VAR_NAME} or $VAR_NAME
        secret_patterns = [
            r'api_key\s*=\s*"[^$][^"]{10,}"',  # Long string not starting with $
            r'secret\s*=\s*"[^$][^"]{10,}"',
            r'password\s*=\s*"[^$][^"]{5,}"',
            r'token\s*=\s*"[^$][^"]{10,}"',
        ]
        for pattern in secret_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            assert not match, f"Potential hardcoded secret found: {pattern}"

    def test_env_vars_use_placeholder_syntax(self) -> None:
        """Test environment variables use ${VAR_NAME} placeholder syntax."""
        scenario = _load_scenario()
        green_agent = scenario.get("green_agent", {})
        env = green_agent.get("env", {})

        for key, value in env.items():
            if isinstance(value, str) and value.startswith("${"):
                # Valid placeholder syntax
                assert value.endswith("}"), f"Invalid env var placeholder: {value}"
