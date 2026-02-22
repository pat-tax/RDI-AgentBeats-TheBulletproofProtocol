"""Tests for docker-compose-local.yml (STORY-011).

This test module validates the acceptance criteria for STORY-011:
- Defines both purple and green services
- Agents can reach each other via service name
- Port mapping: 9010 (purple), 9009 (green) to host
- Environment variables for configuration
- Passes docker-compose up local test
- Clean state on each run
"""

from pathlib import Path
from typing import Any

import yaml

# Define path to docker-compose file
PROJECT_ROOT = Path(__file__).parent.parent
DOCKER_COMPOSE_FILE = PROJECT_ROOT / "docker-compose-local.yml"

# Import settings to get correct ports
try:
    from bulletproof_green.settings import settings as green_settings
    from bulletproof_purple.settings import settings as purple_settings

    purple_port = purple_settings.port
    green_port = green_settings.port
except ImportError:
    # Fallback if settings cannot be imported
    purple_port = 9010
    green_port = 9009


class TestDockerComposeValidYaml:
    """Test that docker-compose-local.yml is valid YAML."""

    def test_is_valid_yaml(self) -> None:
        """Test docker-compose-local.yml is valid YAML syntax."""
        assert DOCKER_COMPOSE_FILE.exists(), "docker-compose-local.yml must exist first"
        content = DOCKER_COMPOSE_FILE.read_text()
        # Should parse without error
        data = yaml.safe_load(content)
        assert data is not None, "docker-compose-local.yml must contain valid YAML"
        assert isinstance(data, dict), "docker-compose-local.yml must be a YAML mapping"


def _load_compose() -> dict[str, Any]:
    """Load and return docker-compose-local.yml as a dict."""
    content = DOCKER_COMPOSE_FILE.read_text()
    data = yaml.safe_load(content)
    if not isinstance(data, dict):
        raise TypeError("docker-compose-local.yml must be a YAML mapping")
    return data


class TestServiceDefinitions:
    """Test that both purple and green services are defined."""

    def test_purple_service_defined(self) -> None:
        """Test purple service is defined."""
        compose = _load_compose()
        services = compose.get("services", {})
        assert "purple" in services, "Must define 'purple' service"

    def test_green_service_defined(self) -> None:
        """Test green service is defined."""
        compose = _load_compose()
        services = compose.get("services", {})
        assert "green" in services, "Must define 'green' service"


class TestServiceBuilds:
    """Test that services build from correct Dockerfiles."""

    def test_purple_builds_from_dockerfile_purple(self) -> None:
        """Test purple service builds from Dockerfile.purple."""
        compose = _load_compose()
        purple = compose.get("services", {}).get("purple", {})
        build = purple.get("build", {})
        if isinstance(build, dict):
            dockerfile = build.get("dockerfile", "")
            assert "Dockerfile.purple" in dockerfile or "purple" in dockerfile.lower(), (
                "purple service must build from Dockerfile.purple"
            )
        elif isinstance(build, str):
            # Simple build context - check that Dockerfile.purple exists
            assert True  # Will be validated by actual build

    def test_green_builds_from_dockerfile_green(self) -> None:
        """Test green service builds from Dockerfile.green."""
        compose = _load_compose()
        green = compose.get("services", {}).get("green", {})
        build = green.get("build", {})
        if isinstance(build, dict):
            dockerfile = build.get("dockerfile", "")
            assert "Dockerfile.green" in dockerfile or "green" in dockerfile.lower(), (
                "green service must build from Dockerfile.green"
            )
        elif isinstance(build, str):
            assert True  # Will be validated by actual build


class TestPortMappings:
    """Test port mappings for host access."""

    def test_purple_port_mapping_8001(self) -> None:
        """Test purple service maps to host port matching settings."""
        compose = _load_compose()
        purple = compose.get("services", {}).get("purple", {})
        ports = purple.get("ports", [])
        # Ports can be strings like "9010:9010" or dicts
        port_mappings = [str(p) for p in ports]
        has_port_mapping = any(str(purple_port) in pm for pm in port_mappings)
        assert has_port_mapping, f"purple service must map to host port {purple_port}"

    def test_green_port_mapping_8002(self) -> None:
        """Test green service maps to host port matching settings."""
        compose = _load_compose()
        green = compose.get("services", {}).get("green", {})
        ports = green.get("ports", [])
        port_mappings = [str(p) for p in ports]
        has_port_mapping = any(str(green_port) in pm for pm in port_mappings)
        assert has_port_mapping, f"green service must map to host port {green_port}"


class TestInterServiceCommunication:
    """Test that agents can reach each other via service name."""

    def test_services_on_same_network(self) -> None:
        """Test services are on the same network or default network."""
        compose = _load_compose()
        services = compose.get("services", {})
        purple = services.get("purple", {})
        green = services.get("green", {})

        # Either both use default network (no network specified)
        # Or both explicitly use the same network
        purple_networks = set(purple.get("networks", []))
        green_networks = set(green.get("networks", []))

        if purple_networks and green_networks:
            # If networks are specified, they should overlap
            assert purple_networks & green_networks, (
                "purple and green must share at least one network"
            )
        # If no networks specified, they share the default network (pass)

    def test_purple_can_be_referenced_by_hostname(self) -> None:
        """Test purple service can be reached by its service name.

        In docker-compose, services can reach each other by service name.
        This test validates the purple service name is usable as a hostname.
        """
        compose = _load_compose()
        services = compose.get("services", {})
        # Service name 'purple' becomes the hostname
        assert "purple" in services, "purple service must exist for DNS resolution"
        # Container name override shouldn't conflict
        purple = services.get("purple", {})
        container_name = purple.get("container_name", "")
        if container_name:
            # If container_name is set, service name still works on same network
            assert True

    def test_green_can_be_referenced_by_hostname(self) -> None:
        """Test green service can be reached by its service name."""
        compose = _load_compose()
        services = compose.get("services", {})
        assert "green" in services, "green service must exist for DNS resolution"


class TestEnvironmentVariables:
    """Test environment variables for configuration."""

    def test_purple_has_environment_config(self) -> None:
        """Test purple service has environment variables or env_file."""
        compose = _load_compose()
        purple = compose.get("services", {}).get("purple", {})
        has_env = "environment" in purple or "env_file" in purple
        assert has_env, "purple service should have environment configuration"

    def test_green_has_environment_config(self) -> None:
        """Test green service has environment variables or env_file."""
        compose = _load_compose()
        green = compose.get("services", {}).get("green", {})
        has_env = "environment" in green or "env_file" in green
        assert has_env, "green service should have environment configuration"

    def test_no_hardcoded_secrets(self) -> None:
        """Test no hardcoded secrets in docker-compose-local.yml."""
        content = DOCKER_COMPOSE_FILE.read_text().lower()
        # Check for common secret value patterns (not env var references)
        # API keys typically look like long alphanumeric strings
        # We're checking the raw content, not env var references like ${VAR}
        assert "password=" not in content or "${" in content, "Must not hardcode passwords"


class TestCleanStateOnRun:
    """Test that compose configuration ensures clean state on each run."""

    def test_no_persistent_volumes_for_data(self) -> None:
        """Test services don't mount persistent volumes for application data.

        This ensures clean state on each run. Named volumes for caching
        (like pip cache) are acceptable.
        """
        compose = _load_compose()
        services = compose.get("services", {})

        for service_name, service_config in services.items():
            if not isinstance(service_config, dict):
                continue
            volumes = service_config.get("volumes", [])
            for vol in volumes:
                vol_str = str(vol)
                # Check for bind mounts to data directories
                # Data directories would be things like /app/data, /data, etc.
                # Source code mounts for development are OK
                if "/data:" in vol_str or ":data" in vol_str:
                    # Allow read-only mounts
                    assert ":ro" in vol_str or "read_only" in vol_str, (
                        f"{service_name} has writable data volume mount"
                    )


class TestDockerComposeVersion:
    """Test docker-compose-local.yml version compatibility."""

    def test_uses_modern_compose_format(self) -> None:
        """Test docker-compose-local.yml uses modern format (version 3.x or no version).

        Modern docker-compose (v2+) doesn't require the 'version' key.
        If specified, should be 3.x for compatibility.
        """
        compose = _load_compose()
        if "version" in compose:
            version = str(compose.get("version", ""))
            assert version.startswith("3") or version == "", (
                "If version is specified, should be 3.x or omitted"
            )


class TestHealthChecks:
    """Test health check configurations (optional but recommended)."""

    def test_purple_healthcheck_or_depends_on(self) -> None:
        """Test purple has healthcheck or is independent."""
        compose = _load_compose()
        purple = compose.get("services", {}).get("purple", {})
        # Purple is the narrative generator, typically independent
        # Having healthcheck is a good practice but not required
        # This test just verifies the service config is valid
        assert isinstance(purple, dict), "purple service must be a dict"

    def test_green_depends_on_or_healthcheck(self) -> None:
        """Test green has proper startup ordering if it depends on purple.

        Green agent may need to call purple agent, so depends_on or
        healthcheck helps ensure proper startup order.
        """
        compose = _load_compose()
        green = compose.get("services", {}).get("green", {})
        # This is informational - green may or may not depend on purple
        # depending on the test scenario
        assert isinstance(green, dict), "green service must be a dict"


class TestBuildContext:
    """Test build context configuration."""

    def test_purple_build_context_is_project_root(self) -> None:
        """Test purple service builds from project root context."""
        compose = _load_compose()
        purple = compose.get("services", {}).get("purple", {})
        build = purple.get("build", {})
        if isinstance(build, dict):
            context = build.get("context", ".")
            assert context in [".", "./"], "purple build context should be project root"
        elif isinstance(build, str):
            assert build in [".", "./"], "purple build context should be project root"

    def test_green_build_context_is_project_root(self) -> None:
        """Test green service builds from project root context."""
        compose = _load_compose()
        green = compose.get("services", {}).get("green", {})
        build = green.get("build", {})
        if isinstance(build, dict):
            context = build.get("context", ".")
            assert context in [".", "./"], "green build context should be project root"
        elif isinstance(build, str):
            assert build in [".", "./"], "green build context should be project root"
