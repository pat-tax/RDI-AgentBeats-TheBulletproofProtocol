"""Tests for Dockerfile.purple build and runtime behavior.

These tests verify that the purple agent Docker container builds successfully
and runs the purple agent server on startup.
"""

import subprocess
import time

import pytest


def test_dockerfile_purple_builds_successfully() -> None:
    """Test that Dockerfile.purple builds successfully on linux/amd64 platform."""
    result = subprocess.run(
        [
            "docker",
            "build",
            "--platform",
            "linux/amd64",
            "-f",
            "Dockerfile.purple",
            "-t",
            "test-purple:latest",
            ".",
        ],
        cwd="/workspaces/RDI-AgentBeats-TheBulletproofProtocol",
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, f"Docker build failed: {result.stderr}"


def test_dockerfile_purple_exposes_port_8000() -> None:
    """Test that the container configuration exposes port 8000."""
    # First build the image
    subprocess.run(
        [
            "docker",
            "build",
            "--platform",
            "linux/amd64",
            "-f",
            "Dockerfile.purple",
            "-t",
            "test-purple:latest",
            ".",
        ],
        cwd="/workspaces/RDI-AgentBeats-TheBulletproofProtocol",
        check=True,
        capture_output=True,
    )

    # Inspect the image to check exposed ports
    result = subprocess.run(
        ["docker", "inspect", "test-purple:latest"],
        capture_output=True,
        text=True,
        check=True,
    )

    assert "8000/tcp" in result.stdout, "Port 8000 is not exposed in the Dockerfile"


def test_dockerfile_purple_runs_server() -> None:
    """Test that docker run successfully starts the purple agent server."""
    # Build the image first
    subprocess.run(
        [
            "docker",
            "build",
            "--platform",
            "linux/amd64",
            "-f",
            "Dockerfile.purple",
            "-t",
            "test-purple:latest",
            ".",
        ],
        cwd="/workspaces/RDI-AgentBeats-TheBulletproofProtocol",
        check=True,
        capture_output=True,
    )

    # Start container
    container_id = subprocess.run(
        [
            "docker",
            "run",
            "-d",
            "--platform",
            "linux/amd64",
            "-p",
            "8000:8000",
            "test-purple:latest",
        ],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    try:
        # Wait for server to start
        time.sleep(3)

        # Check if container is still running
        result = subprocess.run(
            ["docker", "ps", "-q", "-f", f"id={container_id}"],
            capture_output=True,
            text=True,
        )

        assert container_id in result.stdout, "Container exited unexpectedly"

        # Check container logs for startup confirmation
        logs = subprocess.run(
            ["docker", "logs", container_id],
            capture_output=True,
            text=True,
        )

        assert (
            "uvicorn" in logs.stdout.lower() or "started" in logs.stdout.lower()
        ), f"Server doesn't appear to be running. Logs: {logs.stdout}"

    finally:
        # Clean up
        subprocess.run(["docker", "stop", container_id], capture_output=True)
        subprocess.run(["docker", "rm", container_id], capture_output=True)


def test_dockerfile_purple_includes_python_313() -> None:
    """Test that the container includes Python 3.13."""
    # Build the image
    subprocess.run(
        [
            "docker",
            "build",
            "--platform",
            "linux/amd64",
            "-f",
            "Dockerfile.purple",
            "-t",
            "test-purple:latest",
            ".",
        ],
        cwd="/workspaces/RDI-AgentBeats-TheBulletproofProtocol",
        check=True,
        capture_output=True,
    )

    # Check Python version
    result = subprocess.run(
        [
            "docker",
            "run",
            "--rm",
            "--platform",
            "linux/amd64",
            "test-purple:latest",
            "python",
            "--version",
        ],
        capture_output=True,
        text=True,
    )

    assert "Python 3.13" in result.stdout, f"Expected Python 3.13, got: {result.stdout}"


def test_dockerfile_purple_includes_a2a_sdk() -> None:
    """Test that the container includes a2a-sdk[http-server]>=0.3.0."""
    # Build the image
    subprocess.run(
        [
            "docker",
            "build",
            "--platform",
            "linux/amd64",
            "-f",
            "Dockerfile.purple",
            "-t",
            "test-purple:latest",
            ".",
        ],
        cwd="/workspaces/RDI-AgentBeats-TheBulletproofProtocol",
        check=True,
        capture_output=True,
    )

    # Check if a2a-sdk is installed
    result = subprocess.run(
        [
            "docker",
            "run",
            "--rm",
            "--platform",
            "linux/amd64",
            "test-purple:latest",
            "python",
            "-c",
            "import a2a; print(a2a.__version__)",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, f"a2a-sdk not installed: {result.stderr}"
    version = result.stdout.strip()
    assert version, "Could not determine a2a-sdk version"
