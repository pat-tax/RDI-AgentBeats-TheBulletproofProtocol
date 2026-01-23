<!-- markdownlint-disable MD024 no-duplicate-heading -->

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

**Types of changes**: `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`

## [Unreleased]

### Added

#### Bulletproof Protocol (AgentBeats Phase 1 - Complete)

- **Purple Agent (Reference Implementation)**: A2A-compatible narrative generator with 3 IRS Section 41 templates (qualifying, non-qualifying, edge cases)
- **Green Agent (Benchmark Evaluator)**: IRS Section 41 compliance benchmark with weighted risk scoring (0-100) and 5 detection modules (routine engineering 30%, vagueness 25%, business risk 20%, experimentation 15%, specificity 10%)
- **Ground truth dataset**: 20 labeled narratives (10 qualifying, 10 non-qualifying) for validation
- **Docker infrastructure**: Multi-platform (linux/amd64) containers with GHCR publishing via GitHub Actions
- **Integration test suite**: End-to-end A2A protocol validation and benchmark accuracy testing
- **Benchmark validation script**: Automated accuracy, precision, recall, and F1 score calculation
- **AgentBeats registration guide**: Complete workflow from agent setup to leaderboard submission

#### Documentation & Architecture

- **RAA architecture**: Recursive Adversarial Agents (RAA) terminology and design principles
- **Agent naming convention**: Explicit mapping between domain names (Agent A/B) and AgentBeats names (Purple/Green)
- **Domain focus**: LegalTech/FinTech/RegTech specialization with IRS Section 41 compliance
- **Consolidated documentation**: Unified Ralph Loop and AgentBeats specifications in docs/

#### Ralph Loop Enhancements

- **TDD workflow enforcement**: Automated validation of test-first development with RED/GREEN commit markers and chronological verification
- **Skill refactoring**: Renamed to descriptive names (`generating-interactive-userstory-md`, `generating-prd-md-from-userstory-md`, `generating-prd`)
- **State preservation**: Hash-based content change detection in prd.json with incremental regeneration
- **Auto-documentation generation**: Automatic README.md and example.py creation after story completion
- **Interactive project setup**: Auto-detection of git repo, author, and Python version with interactive app name prompt

#### Infrastructure

- **CI/CD automation**: GitHub Actions workflows for pytest, ruff, pyright, MkDocs deployment, and GHCR publishing
- **DevContainer configurations**: Template (Alpine ~10MB) and project (full Python + Node + Docker) containers for instant development
- **Python version management**: Single source of truth for Python version across pyproject.toml, pyright, ruff, and devcontainer
- **Security documentation**: Prominent warnings about `--dangerously-skip-permissions` flag with safe usage guidelines

### Changed

- **Documentation structure**: Moved validate_benchmark.py from scripts/ to src/ for better organization
- **Environment variables**: Renamed GITHUB_PAT → GHCR_PAT, GITHUB_USERNAME → GH_USERNAME for clarity
