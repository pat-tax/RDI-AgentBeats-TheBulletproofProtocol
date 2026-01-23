"""Tests for README submission checklist content (STORY-021)."""

from pathlib import Path


def test_readme_includes_project_overview() -> None:
    """README must include project overview and purpose."""
    readme = Path("README.md").read_text()
    assert "# RDI-AgentBeats-TheBulletproofProtocol" in readme
    assert "IRS Section 41" in readme or "R&D tax credit" in readme


def test_readme_includes_local_testing_instructions() -> None:
    """README must include local testing instructions (docker-compose up)."""
    readme = Path("README.md").read_text()
    assert "docker-compose" in readme
    assert "local" in readme.lower() or "testing" in readme.lower()


def test_readme_includes_ghcr_deployment_instructions() -> None:
    """README must include GHCR deployment instructions."""
    readme = Path("README.md").read_text()
    assert "GHCR" in readme or "GitHub Container Registry" in readme
    assert "ghcr.io" in readme


def test_readme_includes_agentbeats_registration_process() -> None:
    """README must include AgentBeats registration process."""
    readme = Path("README.md").read_text()
    assert "agentbeats" in readme.lower() or "AgentBeats" in readme
    assert "registration" in readme.lower() or "register" in readme.lower()
    # Should link to the registration guide
    assert "AGENTBEATS_REGISTRATION.md" in readme


def test_readme_includes_phase1_submission_checklist() -> None:
    """README must include Phase 1 submission checklist with all deliverables."""
    readme = Path("README.md").read_text()

    # Check for submission checklist section
    assert "submission" in readme.lower() or "checklist" in readme.lower()

    # Check for key Phase 1 deliverables mentioned
    required_items = [
        "Abstract.md",
        "scenario.toml",
        "docker",
    ]

    for item in required_items:
        assert item in readme, f"Missing required deliverable: {item}"


def test_readme_includes_links_to_supporting_docs() -> None:
    """README must include links to all supporting docs (PRD.md, research docs)."""
    readme = Path("README.md").read_text()

    # Key documentation links
    expected_links = [
        "PRD.md",
        "CONTRIBUTING.md",
    ]

    for link in expected_links:
        assert link in readme, f"Missing documentation link: {link}"


def test_readme_includes_contribution_guidelines_and_license() -> None:
    """README must include contribution guidelines and license."""
    readme = Path("README.md").read_text()

    # Check for contribution section
    assert "CONTRIBUTING" in readme or "Contributing" in readme

    # Check for license
    assert "LICENSE" in readme or "License" in readme or "BSD" in readme
