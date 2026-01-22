<!-- markdownlint-disable MD024 no-duplicate-heading -->

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

**Types of changes**: `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`

## [Unreleased]

### Added

- **TDD workflow enforcement**: Automated validation of test-first development with RED/GREEN commit markers and chronological verification
- **Auto-documentation generation**: Automatic README.md and example.py creation after story completion, reflecting actual filesystem and completed work
- **Interactive project setup**: Auto-detection of git repo, author, and Python version with interactive app name prompt and standardized bracket-dash placeholders
- **Assisted workflow skills**: Claude Code skills (`building-userstory`, `generating-prd-from-userstory`) guide users through UserStory → PRD → implementation
- **CI/CD automation**: GitHub Actions workflows for pytest, ruff, pyright, and MkDocs deployment
- **DevContainer configurations**: Template (Alpine ~10MB) and project (full Python + Node + Docker) containers for instant development
- **Python version management**: Single source of truth for Python version across pyproject.toml, pyright, ruff, and devcontainer
- **Security documentation**: Prominent warnings about `--dangerously-skip-permissions` flag with safe usage guidelines
