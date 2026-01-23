# RDI-AgentBeats-TheBulletproofProtocol

**The Bulletproof Protocol** is an agentified benchmark for evaluating IRS Section 41 R&D tax credit narratives. This project submits to the AgentBeats Legal Track, providing a green agent (benchmark) that objectively evaluates R&D narratives against IRS compliance standards.

![Version](https://img.shields.io/badge/version-0.0.0-58f4c2.svg)
[![License](https://img.shields.io/badge/license-BSD3Clause-58f4c2.svg)](LICENSE.md)
[![CodeQL](https://github.com/sf-pat-tax/RDI-AgentBeats-TheBulletproofProtocol/actions/workflows/codeql.yaml/badge.svg)](https://github.com/sf-pat-tax/RDI-AgentBeats-TheBulletproofProtocol/actions/workflows/codeql.yaml)
[![CodeFactor](https://www.codefactor.io/repository/github/sf-pat-tax/RDI-AgentBeats-TheBulletproofProtocol/badge)](https://www.codefactor.io/repository/github/sf-pat-tax/RDI-AgentBeats-TheBulletproofProtocol)
[![ruff](https://github.com/sf-pat-tax/RDI-AgentBeats-TheBulletproofProtocol/actions/workflows/ruff.yaml/badge.svg)](https://github.com/sf-pat-tax/RDI-AgentBeats-TheBulletproofProtocol/actions/workflows/ruff.yaml)
[![pyright](https://github.com/sf-pat-tax/RDI-AgentBeats-TheBulletproofProtocol/actions/workflows/pyright.yaml/badge.svg)](https://github.com/sf-pat-tax/RDI-AgentBeats-TheBulletproofProtocol/actions/workflows/pyright.yaml)
[![pytest](https://github.com/sf-pat-tax/RDI-AgentBeats-TheBulletproofProtocol/actions/workflows/pytest.yaml/badge.svg)](https://github.com/sf-pat-tax/RDI-AgentBeats-TheBulletproofProtocol/actions/workflows/pytest.yaml)
[![Link Checker](https://github.com/sf-pat-tax/RDI-AgentBeats-TheBulletproofProtocol/actions/workflows/links-fail-fast.yaml/badge.svg)](https://github.com/sf-pat-tax/RDI-AgentBeats-TheBulletproofProtocol/actions/workflows/links-fail-fast.yaml)
[![Deploy Docs](https://github.com/sf-pat-tax/RDI-AgentBeats-TheBulletproofProtocol/actions/workflows/generate-deploy-mkdocs-ghpages.yaml/badge.svg)](https://github.com/sf-pat-tax/RDI-AgentBeats-TheBulletproofProtocol/actions/workflows/generate-deploy-mkdocs-ghpages.yaml)

## Features

- **Interactive User Story** - Generate a UserStory.md in colab with Claude Code
- **Semi-Interactive PRD** - Let Claude Code generate the PRD.md from scratch or using the UserStory.md and steer if necessary
- **Ralph Loop** - Autonomous development using a shell loop
- **Claude Code** - Pre-configured skills, plugins, rules, and commands for AI-assisted development
- **Makefile** - User Story and PRD generation, Ralph orchestration, build automation and validation commands
- **Python Tooling** - ruff (linting/formatting), pyright (type checking), pytest (testing)
- **MkDocs** - Auto-generated documentation with GitHub Pages deployment
- **GitHub Actions** - CI/CD workflows (CodeQL, ruff, pyright, pytest, link checking, docs deployment)
- **DevContainers** - Template (Alpine ~10MB) and actual project (Python/Node/Docker ~1GB+)
- **VS Code** - Workspace settings, tasks, and extensions for optimal Python development

## Quick Start

```bash
# 1. Customize template with your project details
# The devcontainer needs a rebuild, if the python version was changed
make setup_project

# 2.1 [If necessary] Setup development environment, if not done by devcontainer.json
make setup_dev

# 2.2 [Optional]
make ralph_userstory            # Interactive User Story using CC
make ralph_prd                  # Generate PRD.md from UserStory.md 

# 3. Write requirements in docs/PRD.md, then run Ralph
make ralph_init                 # Initialize (creates prd.json)
make ralph_run [ITERATIONS=25]  # Run autonomous development
make ralph_status               # Check progress

# 4. Post-run options
# Reset state (removes prd.json, progress.txt)
make ralph_clean
# Archive and start new iteration
make ralph_reorganize NEW_PRD=docs/PRD-v2.md [VERSION=2]
```

For detailed setup and usage, see [ralph/docs/TEMPLATE_USAGE.md](ralph/docs/TEMPLATE_USAGE.md).

## ⚠️ Security Disclaimer

**Ralph Loop runs with `--dangerously-skip-permissions`** which bypasses all Claude Code permission restrictions (including those in `.claude/settings.json`). This enables fully autonomous operation but means:

- All bash commands execute without approval
- File operations (read/write/delete) happen automatically
- Git operations (commit/push) run without confirmation
- Network requests might be unrestricted

**Only use Ralph Loop in**:
- Isolated development environments (DevContainers, VMs)
- Repositories you control and can restore
- Projects with proper version control and backups

**Never run Ralph Loop**:
- In production environments
- On repositories with sensitive data
- On your main development machine without isolation

See `ralph/scripts/ralph.sh:135` for implementation details.

## Workflow

```text
Document Flow:
  UserStory.md (Why) → PRD.md (What) → prd.json → Implementation → progress.txt

Human Workflow (Manual):
  [Write UserStory.md →] Write PRD.md → make ralph_init → make ralph_run

Human Workflow (Assisted - Optional):
  [make ralph_userstory → make ralph_prd →] make ralph_init → make ralph_run

Agent Workflow:
  PRD.md → prd.json (generating-prd skill) → Ralph Loop → src/ + tests/
  Uses: .claude/skills/, .claude/rules/

Mandatory for Both:
  CONTRIBUTING.md - Core principles (KISS, DRY, YAGNI)
  Makefile        - Build automation and validation
  .gitmessage     - Commit message format
```

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

**See the complete registration guide**: [docs/AgentBeats/AGENTBEATS_REGISTRATION.md](docs/AgentBeats/AGENTBEATS_REGISTRATION.md)

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
  - `docker-compose.yml` for local testing
  - `scenario.toml` with agent configurations
  - GHCR deployment scripts (`scripts/build.sh`, `scripts/push.sh`)
  - GitHub Actions workflow (`.github/workflows/docker-publish.yml`)

- [x] **Testing & Validation**
  - Ground truth dataset (20 labeled narratives in `data/ground_truth.json`)
  - Benchmark validation script (`src/validate_benchmark.py`)
  - Integration tests (`tests/integration/`)
  - All tests passing: `make validate`

- [x] **Documentation**
  - `Abstract.md` (≤500 words describing benchmark methodology)
  - `README.md` (this file) with usage instructions
  - `docs/AgentBeats/AGENTBEATS_REGISTRATION.md` (registration guide)
  - `docs/PRD.md` (product requirements)

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

Run these commands to verify everything works:

```bash
# 1. Local testing
docker-compose up -d
curl http://localhost:8001/.well-known/agent-card.json  # Green agent
curl http://localhost:8002/.well-known/agent-card.json  # Purple agent

# 2. Run integration tests
make test

# 3. Validate benchmark metrics
python src/validate_benchmark.py

# 4. Build and push to GHCR
bash scripts/build.sh
bash scripts/push.sh

# 5. Verify images are public
docker pull ghcr.io/YOUR_USERNAME/bulletproof-green:latest
docker pull ghcr.io/YOUR_USERNAME/bulletproof-purple:latest
```

### Resources

- **Competition Platform**: [agentbeats.dev](https://agentbeats.dev)
- **Documentation**: [docs.agentbeats.dev/tutorial](https://docs.agentbeats.dev/tutorial/)
- **Discord Support**: [discord.gg/uqZUta3MYa](https://discord.gg/uqZUta3MYa)
- **Phase 1 Submission**: [forms.gle/1C5d8KXny2JBpZhz7](https://forms.gle/1C5d8KXny2JBpZhz7)
- **Registration Guide**: [docs/AgentBeats/AGENTBEATS_REGISTRATION.md](docs/AgentBeats/AGENTBEATS_REGISTRATION.md)
- **Abstract**: [Abstract.md](Abstract.md)
- **PRD**: [docs/PRD.md](docs/PRD.md)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development workflow, core principles, and contribution guidelines.
