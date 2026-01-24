"""
Tests for GHCR deployment scripts (STORY-014).

Tests verify build.sh and push.sh scripts for building and pushing
Docker images to GitHub Container Registry.
"""

import os
from pathlib import Path

import pytest


@pytest.fixture
def project_root():
    """Get the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def scripts_dir(project_root):
    """Get the scripts directory."""
    return project_root / "scripts"


class TestBuildScript:
    """Tests for scripts/build.sh."""

    def test_build_script_exists(self, scripts_dir):
        """build.sh script exists in scripts directory."""
        build_script = scripts_dir / "build.sh"
        assert build_script.exists(), "scripts/build.sh must exist"

    def test_build_script_is_executable(self, scripts_dir):
        """build.sh script has executable permissions."""
        build_script = scripts_dir / "build.sh"
        assert os.access(build_script, os.X_OK), "scripts/build.sh must be executable"

    def test_build_script_has_error_handling(self, scripts_dir):
        """build.sh includes error handling."""
        build_script = scripts_dir / "build.sh"
        content = build_script.read_text()
        assert "set -e" in content or "set -eo pipefail" in content, \
            "build.sh must include error handling (set -e or set -eo pipefail)"

    def test_build_script_has_status_messages(self, scripts_dir):
        """build.sh includes status messages."""
        build_script = scripts_dir / "build.sh"
        content = build_script.read_text()
        # Check for echo statements or similar output
        assert "echo" in content, "build.sh must include status messages"

    def test_build_script_builds_for_linux_amd64(self, scripts_dir):
        """build.sh builds for linux/amd64 platform."""
        build_script = scripts_dir / "build.sh"
        content = build_script.read_text()
        assert "linux/amd64" in content, \
            "build.sh must build for linux/amd64 platform"

    def test_build_script_builds_both_dockerfiles(self, scripts_dir):
        """build.sh builds both Dockerfile.green and Dockerfile.purple."""
        build_script = scripts_dir / "build.sh"
        content = build_script.read_text()
        assert "Dockerfile.green" in content, "build.sh must build Dockerfile.green"
        assert "Dockerfile.purple" in content, "build.sh must build Dockerfile.purple"


class TestPushScript:
    """Tests for scripts/push.sh."""

    def test_push_script_exists(self, scripts_dir):
        """push.sh script exists in scripts directory."""
        push_script = scripts_dir / "push.sh"
        assert push_script.exists(), "scripts/push.sh must exist"

    def test_push_script_is_executable(self, scripts_dir):
        """push.sh script has executable permissions."""
        push_script = scripts_dir / "push.sh"
        assert os.access(push_script, os.X_OK), "scripts/push.sh must be executable"

    def test_push_script_has_error_handling(self, scripts_dir):
        """push.sh includes error handling."""
        push_script = scripts_dir / "push.sh"
        content = push_script.read_text()
        assert "set -e" in content or "set -eo pipefail" in content, \
            "push.sh must include error handling (set -e or set -eo pipefail)"

    def test_push_script_has_status_messages(self, scripts_dir):
        """push.sh includes status messages."""
        push_script = scripts_dir / "push.sh"
        content = push_script.read_text()
        assert "echo" in content, "push.sh must include status messages"

    def test_push_script_accepts_github_username_env(self, scripts_dir):
        """push.sh accepts GITHUB_USERNAME environment variable."""
        push_script = scripts_dir / "push.sh"
        content = push_script.read_text()
        assert "GITHUB_USERNAME" in content, \
            "push.sh must accept GITHUB_USERNAME environment variable"

    def test_push_script_authenticates_with_cr_pat(self, scripts_dir):
        """push.sh authenticates with GHCR using CR_PAT token."""
        push_script = scripts_dir / "push.sh"
        content = push_script.read_text()
        assert "CR_PAT" in content, \
            "push.sh must authenticate using CR_PAT token"

    def test_push_script_pushes_to_ghcr(self, scripts_dir):
        """push.sh pushes images to ghcr.io."""
        push_script = scripts_dir / "push.sh"
        content = push_script.read_text()
        assert "ghcr.io" in content, "push.sh must push to ghcr.io"

    def test_push_script_pushes_both_images(self, scripts_dir):
        """push.sh pushes both bulletproof-green and bulletproof-purple."""
        push_script = scripts_dir / "push.sh"
        content = push_script.read_text()
        assert "bulletproof-green" in content, \
            "push.sh must push bulletproof-green image"
        assert "bulletproof-purple" in content, \
            "push.sh must push bulletproof-purple image"

    def test_push_script_tags_with_latest(self, scripts_dir):
        """push.sh tags images with :latest."""
        push_script = scripts_dir / "push.sh"
        content = push_script.read_text()
        assert ":latest" in content, "push.sh must tag images with :latest"


class TestReadmeDocumentation:
    """Tests for README.md GHCR deployment documentation."""

    def test_readme_documents_ghcr_deployment(self, project_root):
        """README.md documents GHCR deployment process."""
        readme = project_root / "README.md"
        content = readme.read_text()
        # Check for GHCR-related documentation
        assert "ghcr" in content.lower() or "github container registry" in content.lower(), \
            "README.md must document GHCR deployment process"

    def test_readme_documents_build_script(self, project_root):
        """README.md documents build.sh usage."""
        readme = project_root / "README.md"
        content = readme.read_text()
        assert "build.sh" in content, "README.md must document build.sh script"

    def test_readme_documents_push_script(self, project_root):
        """README.md documents push.sh usage."""
        readme = project_root / "README.md"
        content = readme.read_text()
        assert "push.sh" in content, "README.md must document push.sh script"
