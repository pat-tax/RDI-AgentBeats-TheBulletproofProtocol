"""Tests for GHCR workflow (STORY-012).

This test module validates the acceptance criteria for STORY-012:
- GitHub Actions workflow on push/tag
- Builds: ghcr.io/<org>/bulletproof-green:latest
- Builds: ghcr.io/<org>/bulletproof-purple:latest
- Semantic version tags (v1.0.0, v1.0.1, etc)
- Package visibility: public
- GITHUB_TOKEN with packages:write scope
- docker/build-push-action@v5
"""

import re
from pathlib import Path
from typing import Any

import yaml

# Define path to workflow file
PROJECT_ROOT = Path(__file__).parent.parent
WORKFLOW_FILE = PROJECT_ROOT / ".github" / "workflows" / "docker-build-push.yml"


class TestWorkflowFileExists:
    """Test that the workflow file exists."""

    def test_workflow_file_exists(self) -> None:
        """Test .github/workflows/docker-build-push.yml exists."""
        assert WORKFLOW_FILE.exists(), (
            ".github/workflows/docker-build-push.yml must exist"
        )


class TestWorkflowValidYaml:
    """Test that the workflow file is valid YAML."""

    def test_is_valid_yaml(self) -> None:
        """Test workflow file is valid YAML syntax."""
        assert WORKFLOW_FILE.exists(), "Workflow file must exist first"
        content = WORKFLOW_FILE.read_text()
        data = yaml.safe_load(content)
        assert data is not None, "Workflow file must contain valid YAML"
        assert isinstance(data, dict), "Workflow file must be a YAML mapping"


def _load_workflow() -> dict[str, Any]:
    """Load and return workflow file as a dict."""
    content = WORKFLOW_FILE.read_text()
    data = yaml.safe_load(content)
    if not isinstance(data, dict):
        raise TypeError("Workflow file must be a YAML mapping")
    return data


class TestWorkflowTriggers:
    """Test workflow triggers on push/tag."""

    def test_on_key_exists(self) -> None:
        """Test 'on' key exists for workflow triggers."""
        workflow = _load_workflow()
        assert "on" in workflow, "Workflow must have 'on' triggers"

    def test_triggers_on_push(self) -> None:
        """Test workflow triggers on push events."""
        workflow = _load_workflow()
        on_config = workflow.get("on", {})
        # Can be a list, dict, or have push key
        if isinstance(on_config, list):
            assert "push" in on_config, "Workflow must trigger on push"
        elif isinstance(on_config, dict):
            assert "push" in on_config, "Workflow must trigger on push"
        else:
            assert on_config == "push", "Workflow must trigger on push"

    def test_triggers_on_tags(self) -> None:
        """Test workflow triggers on tag push for semantic versioning."""
        workflow = _load_workflow()
        on_config = workflow.get("on", {})
        if isinstance(on_config, dict):
            push_config = on_config.get("push", {})
            if isinstance(push_config, dict):
                tags = push_config.get("tags", [])
                # Should have tag trigger pattern like v*
                has_tag_trigger = bool(tags)
                assert has_tag_trigger, (
                    "Workflow must trigger on tags for semantic versioning"
                )


class TestWorkflowPermissions:
    """Test workflow has correct permissions."""

    def test_permissions_key_exists(self) -> None:
        """Test 'permissions' key exists."""
        workflow = _load_workflow()
        # Permissions can be at top level or job level
        has_top_level = "permissions" in workflow
        jobs = workflow.get("jobs", {})
        has_job_level = any(
            "permissions" in job
            for job in jobs.values()
            if isinstance(job, dict)
        )
        assert has_top_level or has_job_level, (
            "Workflow must have permissions defined"
        )

    def test_packages_write_permission(self) -> None:
        """Test workflow has packages:write permission for GHCR push."""
        workflow = _load_workflow()
        content = WORKFLOW_FILE.read_text()
        # Check for packages: write in the content
        assert "packages: write" in content or "packages:write" in content, (
            "Workflow must have packages:write permission"
        )


class TestWorkflowJobs:
    """Test workflow job configuration."""

    def test_jobs_key_exists(self) -> None:
        """Test 'jobs' key exists."""
        workflow = _load_workflow()
        assert "jobs" in workflow, "Workflow must have 'jobs' key"

    def test_has_build_job(self) -> None:
        """Test workflow has a build-related job."""
        workflow = _load_workflow()
        jobs = workflow.get("jobs", {})
        assert len(jobs) > 0, "Workflow must have at least one job"


class TestDockerBuildPushAction:
    """Test usage of docker/build-push-action."""

    def test_uses_build_push_action_v5(self) -> None:
        """Test workflow uses docker/build-push-action@v5."""
        content = WORKFLOW_FILE.read_text()
        # Should use v5 as specified in acceptance criteria
        assert re.search(
            r"docker/build-push-action@v5", content
        ), "Workflow must use docker/build-push-action@v5"


class TestDockerBuildxSetup:
    """Test Docker Buildx setup."""

    def test_uses_buildx_action(self) -> None:
        """Test workflow sets up Docker Buildx."""
        content = WORKFLOW_FILE.read_text()
        assert "docker/setup-buildx-action" in content, (
            "Workflow must set up Docker Buildx"
        )


class TestGHCRLogin:
    """Test GitHub Container Registry login."""

    def test_uses_login_action(self) -> None:
        """Test workflow uses docker/login-action for GHCR."""
        content = WORKFLOW_FILE.read_text()
        assert "docker/login-action" in content, (
            "Workflow must use docker/login-action for GHCR"
        )

    def test_logs_into_ghcr(self) -> None:
        """Test workflow logs into ghcr.io registry."""
        content = WORKFLOW_FILE.read_text()
        assert "ghcr.io" in content, "Workflow must log into ghcr.io"

    def test_uses_github_token(self) -> None:
        """Test workflow uses GITHUB_TOKEN for authentication."""
        content = WORKFLOW_FILE.read_text()
        assert "secrets.GITHUB_TOKEN" in content or "GITHUB_TOKEN" in content, (
            "Workflow must use GITHUB_TOKEN for GHCR authentication"
        )


class TestImageBuilds:
    """Test both agent images are built."""

    def test_builds_green_image(self) -> None:
        """Test workflow builds bulletproof-green image."""
        content = WORKFLOW_FILE.read_text()
        assert "bulletproof-green" in content, (
            "Workflow must build bulletproof-green image"
        )

    def test_builds_purple_image(self) -> None:
        """Test workflow builds bulletproof-purple image."""
        content = WORKFLOW_FILE.read_text()
        assert "bulletproof-purple" in content, (
            "Workflow must build bulletproof-purple image"
        )

    def test_uses_dockerfile_green(self) -> None:
        """Test workflow references Dockerfile.green."""
        content = WORKFLOW_FILE.read_text()
        assert "Dockerfile.green" in content, (
            "Workflow must use Dockerfile.green"
        )

    def test_uses_dockerfile_purple(self) -> None:
        """Test workflow references Dockerfile.purple."""
        content = WORKFLOW_FILE.read_text()
        assert "Dockerfile.purple" in content, (
            "Workflow must use Dockerfile.purple"
        )


class TestSemanticVersionTags:
    """Test semantic version tag support."""

    def test_supports_semver_tags(self) -> None:
        """Test workflow supports semantic version tags (v1.0.0, v1.0.1, etc)."""
        content = WORKFLOW_FILE.read_text()
        # Should have tag extraction for semver
        # Common patterns: type=semver, type=ref, or tag patterns like v*
        has_semver_support = (
            "semver" in content.lower()
            or re.search(r"tags:\s*\n\s*-\s*['\"]?v", content)
            or "type=ref" in content
            or "type=semver" in content
        )
        assert has_semver_support, (
            "Workflow must support semantic version tags"
        )

    def test_latest_tag_support(self) -> None:
        """Test workflow supports 'latest' tag."""
        content = WORKFLOW_FILE.read_text()
        assert "latest" in content, "Workflow must support 'latest' tag"


class TestMetadataExtraction:
    """Test Docker metadata extraction."""

    def test_uses_metadata_action(self) -> None:
        """Test workflow uses docker/metadata-action for tags/labels."""
        content = WORKFLOW_FILE.read_text()
        assert "docker/metadata-action" in content, (
            "Workflow must use docker/metadata-action for tag management"
        )


class TestLinuxAmd64Platform:
    """Test linux/amd64 platform build."""

    def test_builds_for_linux_amd64(self) -> None:
        """Test workflow builds for linux/amd64 platform."""
        content = WORKFLOW_FILE.read_text()
        assert "linux/amd64" in content, (
            "Workflow must build for linux/amd64 platform"
        )


class TestCheckoutAction:
    """Test repository checkout."""

    def test_uses_checkout_action(self) -> None:
        """Test workflow checks out repository."""
        content = WORKFLOW_FILE.read_text()
        assert "actions/checkout" in content, (
            "Workflow must use actions/checkout"
        )


class TestNoHardcodedSecrets:
    """Test no hardcoded secrets in workflow."""

    def test_no_hardcoded_tokens(self) -> None:
        """Test no hardcoded tokens or secrets."""
        content = WORKFLOW_FILE.read_text()
        # Check for common secret patterns that aren't variable references
        # Real secrets would be long alphanumeric strings
        secret_patterns = [
            r"ghp_[a-zA-Z0-9]{36}",  # GitHub PAT
            r"ghs_[a-zA-Z0-9]{36}",  # GitHub Server token
            r"github_pat_[a-zA-Z0-9_]{82}",  # Fine-grained PAT
        ]
        for pattern in secret_patterns:
            assert not re.search(pattern, content), (
                f"Must not contain hardcoded tokens matching {pattern}"
            )
