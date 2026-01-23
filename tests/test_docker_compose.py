"""Tests for docker-compose.yml configuration and runtime behavior.

These tests verify that docker-compose.yml correctly configures both agents
for local integration testing.
"""

import subprocess
import time


def test_docker_compose_file_exists() -> None:
    """Test that docker-compose.yml exists."""
    import os

    assert os.path.exists(
        "/workspaces/RDI-AgentBeats-TheBulletproofProtocol/docker-compose.yml"
    ), "docker-compose.yml file not found"


def test_docker_compose_defines_green_service_on_port_8001() -> None:
    """Test that bulletproof-green service is defined with port 8001."""
    result = subprocess.run(
        ["docker-compose", "config"],
        cwd="/workspaces/RDI-AgentBeats-TheBulletproofProtocol",
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, f"docker-compose config failed: {result.stderr}"
    assert "bulletproof-green" in result.stdout, "bulletproof-green service not found"
    assert "8001:8000" in result.stdout, "Port 8001 mapping not found for green service"


def test_docker_compose_defines_purple_service_on_port_8002() -> None:
    """Test that bulletproof-purple service is defined with port 8002."""
    result = subprocess.run(
        ["docker-compose", "config"],
        cwd="/workspaces/RDI-AgentBeats-TheBulletproofProtocol",
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, f"docker-compose config failed: {result.stderr}"
    assert (
        "bulletproof-purple" in result.stdout
    ), "bulletproof-purple service not found"
    assert (
        "8002:8000" in result.stdout
    ), "Port 8002 mapping not found for purple service"


def test_docker_compose_uses_local_dockerfiles_with_platform() -> None:
    """Test that both services build from local Dockerfiles with platform: linux/amd64."""
    result = subprocess.run(
        ["docker-compose", "config"],
        cwd="/workspaces/RDI-AgentBeats-TheBulletproofProtocol",
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, f"docker-compose config failed: {result.stderr}"

    # Check for build configuration
    assert "Dockerfile.green" in result.stdout, "Dockerfile.green not referenced"
    assert "Dockerfile.purple" in result.stdout, "Dockerfile.purple not referenced"

    # Check for platform specification
    assert (
        "linux/amd64" in result.stdout
    ), "platform: linux/amd64 not found in configuration"


def test_docker_compose_defines_shared_network() -> None:
    """Test that services connect via shared network (agentbeats)."""
    result = subprocess.run(
        ["docker-compose", "config"],
        cwd="/workspaces/RDI-AgentBeats-TheBulletproofProtocol",
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, f"docker-compose config failed: {result.stderr}"
    assert "agentbeats" in result.stdout, "agentbeats network not found"


def test_docker_compose_up_starts_both_agents() -> None:
    """Test that docker-compose up -d starts both agents successfully."""
    # Clean up any existing containers
    subprocess.run(
        ["docker-compose", "down"],
        cwd="/workspaces/RDI-AgentBeats-TheBulletproofProtocol",
        capture_output=True,
    )

    try:
        # Start services
        result = subprocess.run(
            ["docker-compose", "up", "-d"],
            cwd="/workspaces/RDI-AgentBeats-TheBulletproofProtocol",
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"docker-compose up failed: {result.stderr}"

        # Wait for services to start
        time.sleep(5)

        # Check that both containers are running
        ps_result = subprocess.run(
            ["docker-compose", "ps"],
            cwd="/workspaces/RDI-AgentBeats-TheBulletproofProtocol",
            capture_output=True,
            text=True,
        )

        assert (
            "bulletproof-green" in ps_result.stdout
            or "bulletproofprotocol-bulletproof-green" in ps_result.stdout
            or "bulletproof_green" in ps_result.stdout
        ), "Green agent container not found in ps output"
        assert (
            "bulletproof-purple" in ps_result.stdout
            or "bulletproofprotocol-bulletproof-purple" in ps_result.stdout
            or "bulletproof_purple" in ps_result.stdout
        ), "Purple agent container not found in ps output"

    finally:
        # Clean up
        subprocess.run(
            ["docker-compose", "down"],
            cwd="/workspaces/RDI-AgentBeats-TheBulletproofProtocol",
            capture_output=True,
        )


def test_agent_cards_respond() -> None:
    """Test that both agents respond with valid agent cards."""
    # Clean up any existing containers
    subprocess.run(
        ["docker-compose", "down"],
        cwd="/workspaces/RDI-AgentBeats-TheBulletproofProtocol",
        capture_output=True,
    )

    try:
        # Start services
        subprocess.run(
            ["docker-compose", "up", "-d"],
            cwd="/workspaces/RDI-AgentBeats-TheBulletproofProtocol",
            capture_output=True,
            check=True,
        )

        # Wait for services to be ready
        time.sleep(8)

        # Test green agent agent-card
        green_result = subprocess.run(
            ["curl", "-s", "http://localhost:8001/.well-known/agent-card.json"],
            capture_output=True,
            text=True,
        )

        assert (
            green_result.returncode == 0
        ), f"Green agent curl failed: {green_result.stderr}"
        assert "bulletproof-green" in green_result.stdout.lower(), (
            f"Green agent card doesn't contain expected name. "
            f"Response: {green_result.stdout}"
        )

        # Test purple agent agent-card
        purple_result = subprocess.run(
            ["curl", "-s", "http://localhost:8002/.well-known/agent-card.json"],
            capture_output=True,
            text=True,
        )

        assert (
            purple_result.returncode == 0
        ), f"Purple agent curl failed: {purple_result.stderr}"
        assert "bulletproof-purple" in purple_result.stdout.lower(), (
            f"Purple agent card doesn't contain expected name. "
            f"Response: {purple_result.stdout}"
        )

    finally:
        # Clean up
        subprocess.run(
            ["docker-compose", "down"],
            cwd="/workspaces/RDI-AgentBeats-TheBulletproofProtocol",
            capture_output=True,
        )
