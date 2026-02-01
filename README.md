# RDI-AgentBeats-TheBulletproofProtocol

> For R&D tax credits: Measure how audit-proof, not just whether it qualifies.

**The Bulletproof Protocol** is an agentified benchmark for evaluating IRS Section 41 R&D tax credit narratives. This project submits to the AgentBeats Legal Track, providing a green agent (benchmark) that objectively evaluates R&D narratives against IRS compliance standards.

![Version](https://img.shields.io/badge/version-0.0.0-58f4c2.svg)
[![License](https://img.shields.io/badge/license-BSD3Clause-58f4c2.svg)](LICENSE.md)
[![CodeQL](https://github.com/sf-pat-tax/RDI-AgentBeats-TheBulletproofProtocol/actions/workflows/codeql.yaml/badge.svg)](https://github.com/sf-pat-tax/RDI-AgentBeats-TheBulletproofProtocol/actions/workflows/codeql.yaml)
[![CodeFactor](https://www.codefactor.io/repository/github/pat-tax/rdi-agentbeats-thebulletproofprotocol/badge)](https://www.codefactor.io/repository/github/pat-tax/rdi-agentbeats-thebulletproofprotocol)
[![ruff](https://github.com/sf-pat-tax/RDI-AgentBeats-TheBulletproofProtocol/actions/workflows/ruff.yaml/badge.svg)](https://github.com/sf-pat-tax/RDI-AgentBeats-TheBulletproofProtocol/actions/workflows/ruff.yaml)
[![pyright](https://github.com/sf-pat-tax/RDI-AgentBeats-TheBulletproofProtocol/actions/workflows/pyright.yaml/badge.svg)](https://github.com/sf-pat-tax/RDI-AgentBeats-TheBulletproofProtocol/actions/workflows/pyright.yaml)
[![pytest](https://github.com/sf-pat-tax/RDI-AgentBeats-TheBulletproofProtocol/actions/workflows/pytest.yaml/badge.svg)](https://github.com/sf-pat-tax/RDI-AgentBeats-TheBulletproofProtocol/actions/workflows/pytest.yaml)
[![Link Checker](https://github.com/sf-pat-tax/RDI-AgentBeats-TheBulletproofProtocol/actions/workflows/links-fail-fast.yaml/badge.svg)](https://github.com/sf-pat-tax/RDI-AgentBeats-TheBulletproofProtocol/actions/workflows/links-fail-fast.yaml)
[![Deploy Docs](https://github.com/sf-pat-tax/RDI-AgentBeats-TheBulletproofProtocol/actions/workflows/generate-deploy-mkdocs-ghpages.yaml/badge.svg)](https://github.com/sf-pat-tax/RDI-AgentBeats-TheBulletproofProtocol/actions/workflows/generate-deploy-mkdocs-ghpages.yaml)

## Features

- **IRS Section 41 Benchmark** - Green agent evaluates R&D narratives for tax credit compliance
- **A2A Protocol** - Agent-to-agent communication via AgentCard discovery and task execution
- **Ralph Loop** - Autonomous development using Compound Engineering and ACE-FCA principles
- **Claude Code** - Pre-configured skills, plugins, rules, and commands for AI-assisted development
- **Python Tooling** - ruff (linting/formatting), pyright (type checking), pytest (testing)
- **Docker** - Containerized agents for linux/amd64 with GHCR deployment
- **GitHub Actions** - CI/CD workflows (CodeQL, ruff, pyright, pytest, Docker publish)
- **DevContainers** - Development environment with sandbox support

## Quick Start

```bash
# 1. Setup development environment
make setup_dev

# 2. Configure environment (required for LLM features)
cp .env.example .env
# Edit .env and set GREEN_OPENAI_API_KEY=sk-your-key-here

# 3. Local testing with docker-compose
docker-compose up -d
curl http://localhost:8001/.well-known/agent-card.json  # Purple agent
curl http://localhost:8002/.well-known/agent-card.json  # Green agent

# 4. Run E2E tests
bash scripts/test_e2e.sh
```

## Configuration

**Environment Setup:**

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
# Edit .env with your values
```

**Required Settings:**
- `GREEN_OPENAI_API_KEY` - OpenAI API key for LLM-based evaluation (system falls back to rule-only scoring if not provided)

**Optional Settings:**
- All other settings have sensible defaults (ports, timeouts, LLM weights, etc.)
- See `.env.example` for full configuration reference

**Debug Current Settings:**

```bash
# View current configuration (respects environment overrides)
python -m bulletproof_green.settings
python -m bulletproof_purple.settings

# Test with overrides
GREEN_PORT=9000 python -m bulletproof_green.settings
```

**Configuration is validated at startup** - misconfigurations are caught immediately with clear error messages.

For Ralph Loop autonomous development, see [ralph/README.md](ralph/README.md).

## GHCR Deployment

Deploy Docker images to GitHub Container Registry for AgentBeats production use.

### Automated Deployment (GitHub Actions)

The repository includes a GitHub Actions workflow (`.github/workflows/docker-publish.yml`) that automatically builds and pushes Docker images to GHCR on every push to the `main` branch.

**How it works:**
1. Triggers on push to `main` branch
2. Builds both `Dockerfile.green` and `Dockerfile.purple` for `linux/amd64`
3. Authenticates with GHCR using `secrets.GITHUB_TOKEN` (automatically provided)
4. Tags images with `:latest` and `:${{ github.sha }}`
5. Pushes to `ghcr.io/${{ github.repository_owner }}/bulletproof-{green|purple}`

**No setup required** - the workflow uses GitHub's built-in `GITHUB_TOKEN` with automatic permissions for pushing to GHCR. Just push to `main` and the workflow handles the rest.

**View workflow runs:**
```
https://github.com/YOUR_USERNAME/YOUR_REPO/actions
```

### Manual Deployment

For manual deployment or local testing:

#### Prerequisites

1. **Create GitHub Personal Access Token (PAT)**:
   - Go to https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Select scopes: `write:packages`, `read:packages`, `delete:packages`
   - Copy the generated token

2. **Set Environment Variables**:
   ```bash
   export GITHUB_USERNAME=your-github-username
   export CR_PAT=your-github-pat
   ```

#### Build and Push

```bash
# Build Docker images for linux/amd64
bash scripts/build.sh

# Push images to GHCR
bash scripts/push.sh
```

### Verify Deployment

After pushing (automated or manual), verify your packages at:
```
https://github.com/YOUR_USERNAME?tab=packages
```

Your images will be available at:
- `ghcr.io/YOUR_USERNAME/bulletproof-green:latest`
- `ghcr.io/YOUR_USERNAME/bulletproof-purple:latest`

### Register on AgentBeats Platform

For production deployment, register your agents on the AgentBeats platform and update `scenario.toml` with your agent IDs.

**See the complete registration guide**: [docs/AgentBeats/SUBMISSION-GUIDE.md](docs/AgentBeats/SUBMISSION-GUIDE.md)

Quick overview:
1. Sign up at [agentbeats.dev](https://agentbeats.dev)
2. Register your green agent (benchmark) and purple agent (baseline)
3. Copy the `agentbeats_id` for each agent
4. Update `scenario.toml`:

```toml
[green_agent]
agentbeats_id = "agent_xyz123abc456"  # Your registered green agent ID

[[participants]]
agentbeats_id = "agent_abc789def012"  # Your registered purple agent ID
```

For local testing, use `docker-compose.yml` instead.

## Phase 1 Submission Checklist

This section tracks AgentBeats Legal Track Phase 1 deliverables (deadline: January 31, 2026).

### Pre-Submission Verification

Before submitting, ensure all deliverables are complete:

- [x] **Green Agent Implementation**: IRS Section 41 benchmark evaluator
  - A2A-compatible server with AgentCard discovery
  - Rule-based evaluation engine (routine engineering, vagueness, experimentation)
  - Weighted risk scoring (0-100) with component breakdown
  - Docker image: `Dockerfile.green` (linux/amd64)

- [x] **Purple Agent Implementation**: Reference baseline narrative generator
  - A2A-compatible server with AgentCard discovery
  - Template-based R&D narrative generation
  - Docker image: `Dockerfile.purple` (linux/amd64)

- [x] **Infrastructure & Deployment**
  - [x] `docker-compose.yml` for local testing
  - [x] `scenario.toml` with agent configurations
  - [x] GHCR deployment scripts (`scripts/build.sh`, `scripts/push.sh`)
  - [x] GitHub Actions workflow (`.github/workflows/docker-publish.yml`)

- [x] **Testing & Validation**
  - [x] Ground truth dataset (30 labeled narratives in `data/ground_truth.json`)
  - [x] Comprehensive E2E test script (`scripts/test_comprehensive.sh`) - 90% classification accuracy
  - [x] Benchmark validation script (`src/validate_benchmark.py`)
  - [ ] Integration tests (`tests/integration/`)
  - [ ] All tests passing: `make validate`

- [ ] **Documentation**
  - `docs/AgentBeats/ABSTRACT.md` (≤500 words describing benchmark methodology)
  - `README.md` (this file) with usage instructions
  - `docs/AgentBeats/SUBMISSION-GUIDE.md` (registration and submission guide)
  - `ralph/README.md` (Ralph Loop documentation)

- [ ] **AgentBeats Platform Registration**
  - [ ] Sign up at [agentbeats.dev](https://agentbeats.dev)
  - [ ] Register green agent → obtain `agentbeats_id`
  - [ ] Register purple agent → obtain `agentbeats_id`
  - [ ] Update `scenario.toml` with production agent IDs
  - [ ] Verify agents are publicly accessible on GHCR

- [ ] **Final Submission**
  - [ ] All Docker images pushed to GHCR and set to public
  - [ ] Leaderboard repo forked and updated with `scenario.toml`
  - [ ] GitHub Action runs successfully in leaderboard repo
  - [ ] Submit via [Phase 1 Submission Form](https://forms.gle/1C5d8KXny2JBpZhz7)

### Validation Commands

```bash
# Quick E2E test (basic validation)
bash scripts/test_e2e.sh

# Comprehensive E2E test with full ground truth dataset (30 narratives)
bash scripts/test_comprehensive.sh

# Unit tests
make test

# Build and push to GHCR
export GH_USERNAME=your-username
export GHCR_PAT=your-token
bash scripts/build.sh && bash scripts/push.sh
```

### Resources

**AgentBeats Platform**:

- **Competition Platform**: [agentbeats.dev](https://agentbeats.dev)
- **Documentation**: [docs.agentbeats.dev/tutorial](https://docs.agentbeats.dev/tutorial/)
- **Discord Support**: [discord.gg/uqZUta3MYa](https://discord.gg/uqZUta3MYa)
- **Phase 1 Submission**: [forms.gle/1C5d8KXny2JBpZhz7](https://forms.gle/1C5d8KXny2JBpZhz7)

**Official Competition Repos**: See [docs/AgentBeats/RESOURCES.md](docs/AgentBeats/RESOURCES.md)

**Project Documentation**:

- **Competition Alignment**: [docs/AgentBeats/COMPETITION-ALIGNMENT.md](docs/AgentBeats/COMPETITION-ALIGNMENT.md)
- **Submission Guide**: [docs/AgentBeats/SUBMISSION-GUIDE.md](docs/AgentBeats/SUBMISSION-GUIDE.md)
- **Abstract**: [docs/AgentBeats/ABSTRACT.md](docs/AgentBeats/ABSTRACT.md)
- **Ralph Loop**: [ralph/README.md](ralph/README.md)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development workflow, core principles, and contribution guidelines.
