"""Tests for scenario.toml configuration file (STORY-013)."""

import tomllib
from pathlib import Path

import pytest


def test_scenario_toml_exists() -> None:
    """Verify scenario.toml file exists at project root."""
    scenario_path = Path(__file__).parent.parent / "scenario.toml"
    assert scenario_path.exists(), "scenario.toml must exist at project root"


def test_scenario_toml_valid_syntax() -> None:
    """Verify scenario.toml has valid TOML syntax."""
    scenario_path = Path(__file__).parent.parent / "scenario.toml"
    with open(scenario_path, "rb") as f:
        config = tomllib.load(f)
    assert isinstance(config, dict), "scenario.toml must be valid TOML"


def test_scenario_toml_has_green_agent_section() -> None:
    """Verify scenario.toml includes [green_agent] section."""
    scenario_path = Path(__file__).parent.parent / "scenario.toml"
    with open(scenario_path, "rb") as f:
        config = tomllib.load(f)

    assert "green_agent" in config, "[green_agent] section must exist"
    assert "agentbeats_id" in config["green_agent"], "[green_agent] must have agentbeats_id field"
    assert "env" in config["green_agent"], "[green_agent] must have env field"


def test_scenario_toml_has_participants_section() -> None:
    """Verify scenario.toml includes [[participants]] section for purple agent."""
    scenario_path = Path(__file__).parent.parent / "scenario.toml"
    with open(scenario_path, "rb") as f:
        config = tomllib.load(f)

    assert "participants" in config, "[[participants]] section must exist"
    assert isinstance(config["participants"], list), "participants must be an array"
    assert len(config["participants"]) > 0, "At least one participant must be defined"

    # Check first participant has required fields
    participant = config["participants"][0]
    assert "agentbeats_id" in participant, "participant must have agentbeats_id"
    assert "name" in participant, "participant must have name field"
    assert "env" in participant, "participant must have env field"


def test_scenario_toml_has_config_section() -> None:
    """Verify scenario.toml includes [config] section with required fields."""
    scenario_path = Path(__file__).parent.parent / "scenario.toml"
    with open(scenario_path, "rb") as f:
        config = tomllib.load(f)

    assert "config" in config, "[config] section must exist"

    # Verify required config fields
    assert "difficulty" in config["config"], "[config] must have difficulty field"
    assert "max_iterations" in config["config"], "[config] must have max_iterations field"
    assert "target_risk_score" in config["config"], "[config] must have target_risk_score field"


def test_scenario_toml_matches_template_format() -> None:
    """Verify scenario.toml follows agentbeats-leaderboard-template format."""
    scenario_path = Path(__file__).parent.parent / "scenario.toml"
    research_path = Path(__file__).parent.parent / "docs/research/scenario.toml"

    with open(scenario_path, "rb") as f:
        config = tomllib.load(f)

    with open(research_path, "rb") as f:
        template = tomllib.load(f)

    # Verify top-level structure matches
    assert set(config.keys()) == set(template.keys()), "scenario.toml must have same top-level keys as template"

    # Verify green_agent structure
    assert set(config["green_agent"].keys()) == set(template["green_agent"].keys()), "green_agent section must match template structure"

    # Verify participants structure
    assert isinstance(config["participants"], list), "participants must be an array"
    if len(template["participants"]) > 0:
        template_participant_keys = set(template["participants"][0].keys())
        for participant in config["participants"]:
            assert set(participant.keys()) == template_participant_keys, "participant structure must match template"

    # Verify config structure
    assert set(config["config"].keys()) == set(template["config"].keys()), "config section must match template structure"
