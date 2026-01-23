"""Tests for AgentBeats registration documentation (STORY-019).

These tests verify that the registration guide exists and contains
all required information for registering agents on agentbeats.dev.
"""

from pathlib import Path


def test_registration_guide_exists() -> None:
    """Test that docs/AGENTBEATS_REGISTRATION.md exists."""
    guide_path = Path("docs/AGENTBEATS_REGISTRATION.md")
    assert guide_path.exists(), "docs/AGENTBEATS_REGISTRATION.md must exist"


def test_registration_guide_has_step_by_step_process() -> None:
    """Test that guide includes step-by-step registration process."""
    guide_path = Path("docs/AGENTBEATS_REGISTRATION.md")
    content = guide_path.read_text()

    # Should have numbered steps or clear section headers
    assert "step" in content.lower() or "##" in content, "Must include step-by-step process"
    assert "register" in content.lower(), "Must explain registration process"
    assert "agentbeats.dev" in content.lower(), "Must reference agentbeats.dev platform"


def test_registration_guide_explains_agentbeats_id() -> None:
    """Test that guide shows how to copy agentbeats_id from platform."""
    guide_path = Path("docs/AGENTBEATS_REGISTRATION.md")
    content = guide_path.read_text()

    assert "agentbeats_id" in content, "Must explain agentbeats_id"
    assert "copy" in content.lower() or "obtain" in content.lower(), "Must show how to get agentbeats_id"


def test_registration_guide_explains_ghcr_vs_agentbeats_id() -> None:
    """Test that guide explains difference between ghcr_url (local) vs agentbeats_id (production)."""
    guide_path = Path("docs/AGENTBEATS_REGISTRATION.md")
    content = guide_path.read_text()

    assert "ghcr_url" in content or "ghcr" in content.lower(), "Must mention ghcr_url"
    assert "local" in content.lower(), "Must explain local usage"
    assert "production" in content.lower(), "Must explain production usage"


def test_registration_guide_includes_verification_steps() -> None:
    """Test that guide includes verification steps to confirm agents are registered correctly."""
    guide_path = Path("docs/AGENTBEATS_REGISTRATION.md")
    content = guide_path.read_text()

    assert "verify" in content.lower() or "test" in content.lower() or "confirm" in content.lower(), \
        "Must include verification steps"


def test_readme_links_to_registration_guide() -> None:
    """Test that README.md links to the registration guide."""
    readme_path = Path("README.md")
    content = readme_path.read_text()

    assert "AGENTBEATS_REGISTRATION" in content or "registration" in content.lower(), \
        "README.md must link to registration guide"
