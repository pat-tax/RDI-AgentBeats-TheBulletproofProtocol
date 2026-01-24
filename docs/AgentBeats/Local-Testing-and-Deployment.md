# Local Testing and Deployment Guide

**Purpose**: Complete infrastructure for testing and deploying Bulletproof Protocol to AgentBeats
**Requirements**: Docker, GitHub account, agentbeats.dev registration

---

## Overview

```
Development Flow:
1. Build locally → 2. Test with docker-compose → 3. Push to GHCR → 4. Register on agentbeats.dev → 5. Submit
```

---

## Local Testing Infrastructure

### 1. scenario.toml Configuration

**Purpose**: Defines assessment parameters for local and CI testing

```toml
# Assessment configuration for Bulletproof Protocol
# Green agent evaluates purple agent's R&D tax credit narrative

[green_agent]
agentbeats_id = ""  # Fill after registering on agentbeats.dev
env = { OPENAI_API_KEY = "${OPENAI_API_KEY}" }  # Optional if using LLM features

[[participants]]
name = "substantiator"  # Purple agent role
agentbeats_id = ""  # Left empty for submitters
env.NARRATIVE_INPUT = "${NARRATIVE_INPUT}"  # Optional custom input

[config]
# Assessment parameters (submitters can customize)
difficulty = "medium"  # easy, medium, hard
max_iterations = 5
target_risk_score = 20
evaluation_mode = "strict"  # strict, lenient

[config.test_narratives]
# Sample narratives for testing (optional)
easy = "We developed a novel caching algorithm to reduce database latency..."
medium = "Our team optimized the application performance..."
hard = "The project involved fixing bugs in the production system..."
```

**Reference**: [AgentBeats Leaderboard Template](https://github.com/RDI-Foundation/agentbeats-leaderboard-template)

### 2. docker-compose.yml for Local Testing

**File**: `docker-compose.yml`

```yaml
version: '3.8'

services:
  # Green Agent (Assessor/Benchmark)
  bulletproof-green:
    build:
      context: .
      dockerfile: Dockerfile.green
      platform: linux/amd64
    image: ghcr.io/${GITHUB_USERNAME}/bulletproof-green:latest
    container_name: bulletproof-examiner
    ports:
      - "8001:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY:-}
      - LOG_LEVEL=INFO
    command: ["--host", "0.0.0.0", "--port", "8000", "--card-url", "http://bulletproof-green:8000"]
    networks:
      - agentbeats

  # Purple Agent (Baseline Substantiator)
  bulletproof-purple:
    build:
      context: .
      dockerfile: Dockerfile.purple
      platform: linux/amd64
    image: ghcr.io/${GITHUB_USERNAME}/bulletproof-purple:latest
    container_name: bulletproof-substantiator
    ports:
      - "8002:8000"
    environment:
      - LOG_LEVEL=INFO
    command: ["--host", "0.0.0.0", "--port", "8000", "--card-url", "http://bulletproof-purple:8000"]
    networks:
      - agentbeats
    depends_on:
      - bulletproof-green

  # Test Runner (optional - for automated testing)
  test-runner:
    image: python:3.13-slim
    container_name: bulletproof-tester
    volumes:
      - ./tests:/tests
      - ./results:/results
    working_dir: /tests
    command: ["python", "-m", "pytest", "-v", "--tb=short"]
    networks:
      - agentbeats
    depends_on:
      - bulletproof-green
      - bulletproof-purple
    environment:
      - GREEN_AGENT_URL=http://bulletproof-green:8000
      - PURPLE_AGENT_URL=http://bulletproof-purple:8000

networks:
  agentbeats:
    driver: bridge
```

### 3. generate_compose.py Script

**Purpose**: Dynamically generate docker-compose from scenario.toml (for CI/CD)

```python
#!/usr/bin/env python3
"""Generate docker-compose.yml from scenario.toml for AgentBeats."""

import sys
from pathlib import Path

try:
    import tomli
except ImportError:
    import tomllib as tomli


def generate_compose(scenario_path: Path, output_path: Path) -> None:
    """Generate docker-compose.yml from scenario.toml."""
    with open(scenario_path, "rb") as f:
        config = tomli.load(f)

    green_agent = config["green_agent"]["agentbeats_id"]
    participants = config["participants"]

    compose = {
        "version": "3.8",
        "services": {},
        "networks": {"agentbeats": {"driver": "bridge"}},
    }

    # Add green agent service
    compose["services"]["green-agent"] = {
        "image": f"ghcr.io/agentbeats/{green_agent}:latest",
        "container_name": "green-agent",
        "ports": ["8001:8000"],
        "environment": list(config["green_agent"].get("env", {}).values()),
        "networks": ["agentbeats"],
    }

    # Add purple agent services
    for idx, participant in enumerate(participants):
        agent_id = participant.get("agentbeats_id", "")
        if not agent_id:
            continue

        compose["services"][f"purple-agent-{idx}"] = {
            "image": f"ghcr.io/agentbeats/{agent_id}:latest",
            "container_name": f"purple-{participant['name']}",
            "ports": [f"{8002+idx}:8000"],
            "environment": list(participant.get("env", {}).values()),
            "networks": ["agentbeats"],
            "depends_on": ["green-agent"],
        }

    # Write docker-compose.yml
    import yaml

    with open(output_path, "w") as f:
        yaml.dump(compose, f, default_flow_style=False)

    print(f"Generated {output_path}")


if __name__ == "__main__":
    scenario = Path("scenario.toml")
    output = Path("docker-compose.generated.yml")
    generate_compose(scenario, output)
```

---

## Docker Image Build and Push to GHCR

### 1. Dockerfile.green (Agent B - Examiner)

```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.13-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml ./
RUN pip install --no-cache-dir ".[green]"

# Copy source code
COPY src/bulletproof_green/ ./bulletproof_green/

# Expose A2A server port
EXPOSE 8000

# ENTRYPOINT with required A2A parameters
ENTRYPOINT ["python", "-m", "bulletproof_green.server"]
CMD ["--host", "0.0.0.0", "--port", "8000"]
```

### 2. Dockerfile.purple (Agent A - Substantiator)

```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.13-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml ./
RUN pip install --no-cache-dir ".[purple]"

# Copy source code
COPY src/bulletproof_purple/ ./bulletproof_purple/

# Expose A2A server port
EXPOSE 8000

# ENTRYPOINT with required A2A parameters
ENTRYPOINT ["python", "-m", "bulletproof_purple.server"]
CMD ["--host", "0.0.0.0", "--port", "8000"]
```

### 3. Build Commands (Local Testing)

```bash
# Set platform for AgentBeats compatibility
export DOCKER_PLATFORM=linux/amd64

# Build green agent
docker build --platform $DOCKER_PLATFORM \
  -f Dockerfile.green \
  -t bulletproof-green:local \
  .

# Build purple agent
docker build --platform $DOCKER_PLATFORM \
  -f Dockerfile.purple \
  -t bulletproof-purple:local \
  .

# Test locally
docker-compose up
```

### 4. Push to GHCR (GitHub Container Registry)

**Prerequisites**:

1. GitHub Personal Access Token (PAT) with `write:packages` scope
2. GitHub repository (public or private)

**Step 1: Authenticate**

```bash
# Set your GitHub username
export GITHUB_USERNAME=your-github-username

# Create PAT at https://github.com/settings/tokens/new
# Scopes: write:packages, read:packages, delete:packages
export CR_PAT=your_personal_access_token

# Login to GHCR
echo $CR_PAT | docker login ghcr.io -u $GITHUB_USERNAME --password-stdin
```

**Step 2: Tag Images**

```bash
# Tag for GHCR (use semantic versioning)
docker tag bulletproof-green:local \
  ghcr.io/$GITHUB_USERNAME/bulletproof-green:latest

docker tag bulletproof-green:local \
  ghcr.io/$GITHUB_USERNAME/bulletproof-green:v1.0.0

docker tag bulletproof-purple:local \
  ghcr.io/$GITHUB_USERNAME/bulletproof-purple:latest

docker tag bulletproof-purple:local \
  ghcr.io/$GITHUB_USERNAME/bulletproof-purple:v1.0.0
```

**Step 3: Push to GHCR**

```bash
# Push green agent
docker push ghcr.io/$GITHUB_USERNAME/bulletproof-green:latest
docker push ghcr.io/$GITHUB_USERNAME/bulletproof-green:v1.0.0

# Push purple agent
docker push ghcr.io/$GITHUB_USERNAME/bulletproof-purple:latest
docker push ghcr.io/$GITHUB_USERNAME/bulletproof-purple:v1.0.0
```

**Reference**: [GitHub Docs - Working with Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)

### 5. Make Images Public

**Via GitHub Web UI**:

1. Go to `https://github.com/users/$GITHUB_USERNAME/packages`
2. Click on `bulletproof-green` package
3. Click **Package settings** (right sidebar)
4. Scroll to **Danger Zone** → **Change package visibility**
5. Select **Public**
6. Type package name to confirm
7. Repeat for `bulletproof-purple`

**Via GitHub CLI** (alternative):

```bash
gh api --method PATCH \
  -H "Accept: application/vnd.github+json" \
  /user/packages/container/bulletproof-green/versions/PACKAGE_VERSION_ID \
  -f visibility='public'
```

**Reference**: [GitHub Docs - Configuring Package Visibility](https://docs.github.com/en/packages/learn-github-packages/configuring-a-packages-access-control-and-visibility)

---

## GitHub Actions CI/CD (Automated Build & Push)

### .github/workflows/docker-publish.yml

```yaml
name: Build and Push Docker Images

on:
  push:
    branches: [ main, feat-agentbeats ]
    tags: [ 'v*.*.*' ]
  pull_request:
    branches: [ main ]

env:
  REGISTRY: ghcr.io
  GREEN_IMAGE_NAME: ${{ github.repository }}/bulletproof-green
  PURPLE_IMAGE_NAME: ${{ github.repository }}/bulletproof-purple

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to GHCR
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata (green agent)
        id: meta-green
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.GREEN_IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=sha

      - name: Build and push green agent
        uses: docker/build-push-action@v5
        with:
          context: .
          file: ./Dockerfile.green
          platforms: linux/amd64
          push: true
          tags: ${{ steps.meta-green.outputs.tags }}
          labels: ${{ steps.meta-green.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Extract metadata (purple agent)
        id: meta-purple
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.PURPLE_IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=sha

      - name: Build and push purple agent
        uses: docker/build-push-action@v5
        with:
          context: .
          file: ./Dockerfile.purple
          platforms: linux/amd64
          push: true
          tags: ${{ steps.meta-purple.outputs.tags }}
          labels: ${{ steps.meta-purple.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

**Reference**: [GitHub Actions - Publishing Docker Images](https://docs.github.com/actions/guides/publishing-docker-images)

---

## Local Testing Workflow

### Quick Start

```bash
# 1. Clone repository
git clone https://github.com/$GITHUB_USERNAME/bulletproof-protocol.git
cd bulletproof-protocol

# 2. Build images locally
docker-compose build

# 3. Start services
docker-compose up -d

# 4. Check logs
docker-compose logs -f bulletproof-green
docker-compose logs -f bulletproof-purple

# 5. Test A2A connectivity
curl http://localhost:8001/health
curl http://localhost:8002/health

# 6. Run assessment
python tests/test_assessment.py

# 7. Stop services
docker-compose down
```

### Manual Assessment Test

```bash
# Test green agent with sample narrative
curl -X POST http://localhost:8001/assess \
  -H "Content-Type: application/json" \
  -d '{
    "participants": {
      "substantiator": "http://bulletproof-purple:8000"
    },
    "config": {
      "difficulty": "medium",
      "narrative": "We optimized the database queries..."
    }
  }'
```

### Integration Test Script

**File**: `tests/test_assessment.py`

```python
"""Integration test for Bulletproof Protocol assessment."""

import requests
import time


def test_assessment():
    """Test full assessment flow: purple generates, green evaluates."""
    green_url = "http://localhost:8001"
    purple_url = "http://localhost:8002"

    # Wait for services to be ready
    for url in [green_url, purple_url]:
        for _ in range(30):
            try:
                resp = requests.get(f"{url}/health", timeout=2)
                if resp.status_code == 200:
                    break
            except requests.RequestException:
                time.sleep(1)

    # Request assessment from green agent
    assessment_request = {
        "participants": {"substantiator": purple_url},
        "config": {"difficulty": "medium"},
    }

    response = requests.post(
        f"{green_url}/assess",
        json=assessment_request,
        timeout=60,
    )

    assert response.status_code == 200
    result = response.json()

    # Validate artifact structure
    assert "risk_score" in result
    assert "classification" in result
    assert "redline" in result

    print(f"Assessment completed successfully!")
    print(f"Risk Score: {result['risk_score']}")
    print(f"Classification: {result['classification']}")


if __name__ == "__main__":
    test_assessment()
```

---

## AgentBeats Registration

### 1. Register Green Agent (Examiner)

1. Go to [agentbeats.dev](https://agentbeats.dev)
2. Click **Register Agent**
3. Fill in details:
   - **Name**: Bulletproof Protocol - IRS Section 41 Examiner
   - **Description**: Evaluates R&D tax credit narratives for IRS compliance
   - **Type**: Green (Assessor)
   - **Image**: `ghcr.io/$GITHUB_USERNAME/bulletproof-green:latest`
   - **Repository**: `https://github.com/$GITHUB_USERNAME/bulletproof-protocol`
4. Copy Agent ID (e.g., `bp-green-examiner-2026`)
5. Update `scenario.toml` with Agent ID

### 2. Register Purple Agent (Baseline)

1. Repeat process for purple agent
2. **Type**: Purple (Assessee)
3. **Image**: `ghcr.io/$GITHUB_USERNAME/bulletproof-purple:latest`
4. Copy Agent ID (e.g., `bp-purple-substantiator-2026`)

### 3. Update scenario.toml

```toml
[green_agent]
agentbeats_id = "bp-green-examiner-2026"  # From registration

[[participants]]
name = "substantiator"
agentbeats_id = "bp-purple-substantiator-2026"  # From registration
```

---

## Troubleshooting

### Docker Build Issues

```bash
# Clean build (no cache)
docker-compose build --no-cache

# Check platform
docker buildx ls

# Verify image architecture
docker inspect bulletproof-green:local | grep Architecture
# Should show: "Architecture": "amd64"
```

### GHCR Push Failures

```bash
# Verify authentication
docker logout ghcr.io
echo $CR_PAT | docker login ghcr.io -u $GITHUB_USERNAME --password-stdin

# Check token permissions (must have write:packages)
curl -H "Authorization: Bearer $CR_PAT" https://api.github.com/user

# Verify image name format (must be lowercase)
docker tag bulletproof-green:local \
  ghcr.io/$(echo $GITHUB_USERNAME | tr '[:upper:]' '[:lower:]')/bulletproof-green:latest
```

### Network Connectivity

```bash
# Check services are running
docker-compose ps

# Inspect network
docker network inspect bulletproof-protocol_agentbeats

# Test connectivity between containers
docker-compose exec bulletproof-green ping bulletproof-purple
```

---

## Pre-Submission Checklist

**Before Phase 1 submission**:

- [ ] Docker images build successfully on `linux/amd64`
- [ ] Images pushed to GHCR and set to **public**
- [ ] Local `docker-compose up` works without errors
- [ ] Green agent returns valid JSON artifacts
- [ ] Purple agent generates sample narratives
- [ ] Integration test passes (`tests/test_assessment.py`)
- [ ] Both agents registered on agentbeats.dev
- [ ] `scenario.toml` updated with Agent IDs
- [ ] README includes setup instructions
- [ ] `.env.example` provided for environment variables

---

## Key Resources

- **AgentBeats Leaderboard Template**: [github.com/RDI-Foundation/agentbeats-leaderboard-template](https://github.com/RDI-Foundation/agentbeats-leaderboard-template)
- **GitHub Container Registry Docs**: [docs.github.com/packages](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- **Docker Compose Documentation**: [docs.docker.com/compose](https://docs.docker.com/compose/)
- **AgentBeats Tutorial**: [github.com/RDI-Foundation/agentbeats-tutorial](https://github.com/RDI-Foundation/agentbeats-tutorial)
