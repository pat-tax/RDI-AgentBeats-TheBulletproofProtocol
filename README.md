# RDI-AgentBeats-TheBulletproofProtocol

A recursive adversarial agent system where a "Virtual IRS Auditor" ruthlessly critiques and trains a "Generator Agent" to write audit-proof R> What a time to be aliveD tax credit claims.

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

For detailed setup and usage, see [docs/TEMPLATE_USAGE.md](docs/TEMPLATE_USAGE.md).

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

See `scripts/ralph/ralph.sh:135` for implementation details.

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

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development workflow, core principles, and contribution guidelines.
