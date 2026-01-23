"""
Tests for GitHub Actions Docker publish workflow (STORY-018).

Tests verify .github/workflows/docker-publish.yml workflow for automated
Docker image builds and GHCR pushes on git push.
"""

from pathlib import Path

import pytest


@pytest.fixture
def project_root():
    """Get the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def workflows_dir(project_root):
    """Get the .github/workflows directory."""
    return project_root / ".github" / "workflows"


@pytest.fixture
def workflow_file(workflows_dir):
    """Get the docker-publish.yml workflow file."""
    return workflows_dir / "docker-publish.yml"


class TestDockerPublishWorkflow:
    """Tests for .github/workflows/docker-publish.yml."""

    def test_workflow_file_exists(self, workflow_file):
        """docker-publish.yml workflow file exists."""
        assert workflow_file.exists(), \
            ".github/workflows/docker-publish.yml must exist"

    def test_workflow_triggers_on_push_to_main(self, workflow_file):
        """Workflow triggers on push to main branch."""
        content = workflow_file.read_text()

        # Check for push trigger on main branch
        assert "push:" in content or "on: push" in content or "on:\n  push:" in content, \
            "Workflow must have push trigger"
        assert "main" in content, \
            "Workflow must trigger on push to main branch"

    def test_workflow_runs_on_linux(self, workflow_file):
        """Workflow runs on ubuntu-latest runner."""
        content = workflow_file.read_text()

        # Check for ubuntu-latest runner
        assert "runs-on: ubuntu-latest" in content, \
            "Workflow must run on ubuntu-latest runner"

    def test_workflow_authenticates_with_ghcr(self, workflow_file):
        """Workflow authenticates with GHCR using secrets.GITHUB_TOKEN."""
        content = workflow_file.read_text()

        # Check for GITHUB_TOKEN usage
        assert "GITHUB_TOKEN" in content or "github.token" in content, \
            "Workflow must authenticate with GHCR using secrets.GITHUB_TOKEN or github.token"

    def test_workflow_builds_both_dockerfiles(self, workflow_file):
        """Workflow builds both Dockerfile.green and Dockerfile.purple."""
        content = workflow_file.read_text()

        # Check for both Dockerfiles
        assert "Dockerfile.green" in content, \
            "Workflow must build Dockerfile.green"
        assert "Dockerfile.purple" in content, \
            "Workflow must build Dockerfile.purple"

    def test_workflow_tags_with_latest(self, workflow_file):
        """Workflow tags images with :latest."""
        content = workflow_file.read_text()

        assert ":latest" in content or "latest" in content, \
            "Workflow must tag images with :latest"

    def test_workflow_tags_with_sha(self, workflow_file):
        """Workflow tags images with commit SHA."""
        content = workflow_file.read_text()

        # Check for GitHub SHA variable or docker metadata-action with type=sha
        assert "github.sha" in content or "${{ github.sha }}" in content or "${GITHUB_SHA}" in content or "type=sha" in content, \
            "Workflow must tag images with commit SHA using github.sha or type=sha"

    def test_workflow_pushes_to_ghcr(self, workflow_file):
        """Workflow pushes images to ghcr.io."""
        content = workflow_file.read_text()

        assert "ghcr.io" in content, \
            "Workflow must push images to ghcr.io"

    def test_workflow_uses_repository_owner(self, workflow_file):
        """Workflow uses github.repository_owner for image naming."""
        content = workflow_file.read_text()

        assert "github.repository_owner" in content or "repository_owner" in content, \
            "Workflow must use github.repository_owner for dynamic image naming"

    def test_workflow_pushes_bulletproof_green(self, workflow_file):
        """Workflow pushes bulletproof-green image."""
        content = workflow_file.read_text()

        assert "bulletproof-green" in content, \
            "Workflow must push bulletproof-green image"

    def test_workflow_pushes_bulletproof_purple(self, workflow_file):
        """Workflow pushes bulletproof-purple image."""
        content = workflow_file.read_text()

        assert "bulletproof-purple" in content, \
            "Workflow must push bulletproof-purple image"

    def test_workflow_specifies_linux_amd64_platform(self, workflow_file):
        """Workflow builds for linux/amd64 platform."""
        content = workflow_file.read_text()

        assert "linux/amd64" in content, \
            "Workflow must specify linux/amd64 platform for builds"


class TestReadmeDocumentation:
    """Tests for README.md GitHub Actions documentation."""

    def test_readme_documents_github_actions(self, project_root):
        """README.md documents GitHub Actions workflow."""
        readme = project_root / "README.md"
        content = readme.read_text()

        # Check for GitHub Actions documentation
        assert "github actions" in content.lower() or "github action" in content.lower(), \
            "README.md must document GitHub Actions workflow"

    def test_readme_documents_workflow_setup(self, project_root):
        """README.md documents GitHub Actions setup."""
        readme = project_root / "README.md"
        content = readme.read_text()

        # Check for workflow or CI/CD documentation
        assert "workflow" in content.lower() or "ci/cd" in content.lower() or "docker-publish" in content, \
            "README.md must document GitHub Actions setup"
