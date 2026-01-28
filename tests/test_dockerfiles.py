"""Tests for Dockerfiles (STORY-010).

This test module validates the acceptance criteria for STORY-010:
- Platform: linux/amd64
- Base: Python 3.13-slim
- Exposes port 8000
- ENTRYPOINT with --host, --port arguments
- No hardcoded secrets (env vars only)
- Multi-stage build for smaller images
- uv for fast dependency management
- Both bulletproof-purple and bulletproof-green images
"""

import re
from pathlib import Path

# Define paths to Dockerfiles
PROJECT_ROOT = Path(__file__).parent.parent
DOCKERFILE_PURPLE = PROJECT_ROOT / "Dockerfile.purple"
DOCKERFILE_GREEN = PROJECT_ROOT / "Dockerfile.green"


class TestDockerfilePurple:
    """Test Dockerfile.purple meets all acceptance criteria."""

    def test_uses_python_313_slim_base(self):
        """Test Dockerfile uses Python 3.13-slim base image."""
        content = DOCKERFILE_PURPLE.read_text()
        # Should have a FROM with python:3.13-slim (may include --platform flag)
        assert re.search(r"FROM\s+.*python:3\.13-slim", content), (
            "Must use python:3.13-slim base image"
        )

    def test_exposes_port_8000(self):
        """Test Dockerfile exposes port 8000."""
        content = DOCKERFILE_PURPLE.read_text()
        assert re.search(r"EXPOSE\s+8000", content), "Must expose port 8000"

    def test_has_entrypoint(self):
        """Test Dockerfile has ENTRYPOINT defined."""
        content = DOCKERFILE_PURPLE.read_text()
        assert "ENTRYPOINT" in content, "Must have ENTRYPOINT defined"

    def test_entrypoint_supports_host_port_args(self):
        """Test ENTRYPOINT supports --host and --port arguments."""
        content = DOCKERFILE_PURPLE.read_text()
        # Check that there's a CMD or default args that can be overridden
        # and/or that the entrypoint script supports these args
        has_host_arg = "--host" in content
        has_port_arg = "--port" in content
        assert has_host_arg or has_port_arg or "uvicorn" in content, (
            "ENTRYPOINT must support --host, --port arguments"
        )

    def test_no_hardcoded_secrets(self):
        """Test no hardcoded secrets in Dockerfile."""
        content = DOCKERFILE_PURPLE.read_text()
        # Check for common secret patterns
        secret_patterns = [
            r"password\s*=\s*['\"][^'\"]+['\"]",
            r"api_key\s*=\s*['\"][^'\"]+['\"]",
            r"secret\s*=\s*['\"][^'\"]+['\"]",
            r"AWS_SECRET",
            r"GITHUB_TOKEN\s*=\s*['\"][^'\"]+['\"]",
        ]
        for pattern in secret_patterns:
            assert not re.search(pattern, content, re.IGNORECASE), (
                f"Must not contain hardcoded secrets matching {pattern}"
            )

    def test_uses_multi_stage_build(self):
        """Test Dockerfile uses multi-stage build for smaller images."""
        content = DOCKERFILE_PURPLE.read_text()
        # Count FROM statements - multi-stage means more than one
        from_count = len(re.findall(r"^FROM\s", content, re.MULTILINE))
        assert from_count >= 2, "Must use multi-stage build (at least 2 FROM statements)"

    def test_uses_uv_package_manager(self):
        """Test Dockerfile uses uv for fast dependency management."""
        content = DOCKERFILE_PURPLE.read_text()
        assert "uv" in content, "Must use uv for dependency management"

    def test_sets_linux_amd64_platform(self):
        """Test Dockerfile specifies linux/amd64 platform."""
        content = DOCKERFILE_PURPLE.read_text()
        # Platform can be in FROM line or as build arg
        has_platform = (
            "--platform=linux/amd64" in content
            or "--platform linux/amd64" in content
            or "TARGETPLATFORM" in content
            or "linux/amd64" in content
        )
        assert has_platform, "Must specify linux/amd64 platform"

    def test_copies_source_code(self):
        """Test Dockerfile copies source code."""
        content = DOCKERFILE_PURPLE.read_text()
        assert "COPY" in content, "Must copy source code"

    def test_installs_dependencies(self):
        """Test Dockerfile installs dependencies."""
        content = DOCKERFILE_PURPLE.read_text()
        # Should install via uv or pip
        has_install = "uv" in content or "pip install" in content
        assert has_install, "Must install dependencies"


class TestDockerfileGreen:
    """Test Dockerfile.green meets all acceptance criteria."""

    def test_uses_python_313_slim_base(self):
        """Test Dockerfile uses Python 3.13-slim base image."""
        content = DOCKERFILE_GREEN.read_text()
        # Should have a FROM with python:3.13-slim (may include --platform flag)
        assert re.search(r"FROM\s+.*python:3\.13-slim", content), (
            "Must use python:3.13-slim base image"
        )

    def test_exposes_port_8000(self):
        """Test Dockerfile exposes port 8000."""
        content = DOCKERFILE_GREEN.read_text()
        assert re.search(r"EXPOSE\s+8000", content), "Must expose port 8000"

    def test_has_entrypoint(self):
        """Test Dockerfile has ENTRYPOINT defined."""
        content = DOCKERFILE_GREEN.read_text()
        assert "ENTRYPOINT" in content, "Must have ENTRYPOINT defined"

    def test_entrypoint_supports_host_port_args(self):
        """Test ENTRYPOINT supports --host and --port arguments."""
        content = DOCKERFILE_GREEN.read_text()
        has_host_arg = "--host" in content
        has_port_arg = "--port" in content
        assert has_host_arg or has_port_arg or "uvicorn" in content, (
            "ENTRYPOINT must support --host, --port arguments"
        )

    def test_no_hardcoded_secrets(self):
        """Test no hardcoded secrets in Dockerfile."""
        content = DOCKERFILE_GREEN.read_text()
        secret_patterns = [
            r"password\s*=\s*['\"][^'\"]+['\"]",
            r"api_key\s*=\s*['\"][^'\"]+['\"]",
            r"secret\s*=\s*['\"][^'\"]+['\"]",
            r"AWS_SECRET",
            r"GITHUB_TOKEN\s*=\s*['\"][^'\"]+['\"]",
        ]
        for pattern in secret_patterns:
            assert not re.search(pattern, content, re.IGNORECASE), (
                f"Must not contain hardcoded secrets matching {pattern}"
            )

    def test_uses_multi_stage_build(self):
        """Test Dockerfile uses multi-stage build for smaller images."""
        content = DOCKERFILE_GREEN.read_text()
        # Count FROM statements - multi-stage means more than one
        from_count = len(re.findall(r"^FROM\s", content, re.MULTILINE))
        assert from_count >= 2, "Must use multi-stage build (at least 2 FROM statements)"

    def test_uses_uv_package_manager(self):
        """Test Dockerfile uses uv for fast dependency management."""
        content = DOCKERFILE_GREEN.read_text()
        assert "uv" in content, "Must use uv for dependency management"

    def test_sets_linux_amd64_platform(self):
        """Test Dockerfile specifies linux/amd64 platform."""
        content = DOCKERFILE_GREEN.read_text()
        has_platform = (
            "--platform=linux/amd64" in content
            or "--platform linux/amd64" in content
            or "TARGETPLATFORM" in content
            or "linux/amd64" in content
        )
        assert has_platform, "Must specify linux/amd64 platform"

    def test_copies_source_code(self):
        """Test Dockerfile copies source code."""
        content = DOCKERFILE_GREEN.read_text()
        assert "COPY" in content, "Must copy source code"

    def test_installs_dependencies(self):
        """Test Dockerfile installs dependencies."""
        content = DOCKERFILE_GREEN.read_text()
        has_install = "uv" in content or "pip install" in content
        assert has_install, "Must install dependencies"


class TestDockerfileDifferences:
    """Test that Dockerfiles are correctly differentiated for each agent."""

    def test_purple_dockerfile_references_purple_agent(self):
        """Test purple Dockerfile references the purple agent module."""
        content = DOCKERFILE_PURPLE.read_text()
        assert "bulletproof_purple" in content or "purple" in content.lower(), (
            "Dockerfile.purple must reference purple agent"
        )

    def test_green_dockerfile_references_green_agent(self):
        """Test green Dockerfile references the green agent module."""
        content = DOCKERFILE_GREEN.read_text()
        assert "bulletproof_green" in content or "green" in content.lower(), (
            "Dockerfile.green must reference green agent"
        )


class TestDockerfileBestPractices:
    """Test Dockerfiles follow best practices."""

    def test_purple_has_workdir(self):
        """Test Dockerfile.purple sets WORKDIR."""
        content = DOCKERFILE_PURPLE.read_text()
        assert "WORKDIR" in content, "Should set WORKDIR for cleaner paths"

    def test_green_has_workdir(self):
        """Test Dockerfile.green sets WORKDIR."""
        content = DOCKERFILE_GREEN.read_text()
        assert "WORKDIR" in content, "Should set WORKDIR for cleaner paths"

    def test_purple_has_non_root_user(self):
        """Test Dockerfile.purple runs as non-root user (security best practice)."""
        content = DOCKERFILE_PURPLE.read_text()
        # Check for USER directive or adduser/useradd
        has_user = "USER" in content
        assert has_user, "Should run as non-root user for security"

    def test_green_has_non_root_user(self):
        """Test Dockerfile.green runs as non-root user (security best practice)."""
        content = DOCKERFILE_GREEN.read_text()
        has_user = "USER" in content
        assert has_user, "Should run as non-root user for security"
