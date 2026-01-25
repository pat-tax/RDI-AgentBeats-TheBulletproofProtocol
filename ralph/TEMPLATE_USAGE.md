# Template Usage

Quick setup guide for new projects using this template.

## Setup

```bash
# 1. Clone and customize
git clone <your-repo-url> && cd <your-repo>
make setup_project          # Customize template placeholders

# 2. Install dependencies
make setup_dev              # Python deps, tooling
make setup_sandbox          # Sandbox deps (Linux/WSL2)
```

## Workflow

### Option A: Manual PRD

1. Edit `docs/PRD.md` with your requirements
2. Run Ralph:
   ```bash
   make ralph_prd_json         # PRD.md → prd.json
   make ralph_init             # Validate environment
   make ralph_run ITERATIONS=25
   ```

### Option B: Assisted PRD

```bash
make ralph_userstory        # Interactive Q&A → UserStory.md
make ralph_prd_md           # UserStory.md → PRD.md
make ralph_prd_json         # PRD.md → prd.json
make ralph_init             # Validate environment
make ralph_run ITERATIONS=25
```

### Story Dependencies

In PRD.md story breakdown, use `(depends: STORY-XXX)` syntax:

```markdown
- **Feature 2** → STORY-002: Create API, STORY-003: Integrate API (depends: STORY-002)
```

Stories with unmet dependencies are skipped until dependencies complete.

### Monitoring

```bash
make ralph_status           # Show progress
make validate               # Run linters + tests
```

### Reset / Iterate

```bash
make ralph_clean            # Reset state (removes prd.json, progress.txt)
make ralph_reorganize NEW_PRD=docs/PRD-v2.md VERSION=2  # Archive and iterate
```

## Commands Reference

| Command | Description |
|---------|-------------|
| `make ralph_userstory` | Create UserStory.md interactively |
| `make ralph_prd_md` | Generate PRD.md from UserStory.md |
| `make ralph_prd_json` | Generate prd.json from PRD.md |
| `make ralph_init` | Validate Ralph environment |
| `make ralph_run` | Run autonomous development |
| `make ralph_status` | Show progress and status |
| `make ralph_clean` | Reset Ralph state |
| `make ralph_reorganize` | Archive and start new iteration |
| `make validate` | Run all checks (ruff, pyright, pytest) |

## Project Structure

```text
your-project/
├── .claude/              # Claude Code config (skills, rules, settings)
├── docs/
│   ├── PRD.md            # Product requirements
│   └── UserStory.md      # User stories (optional)
├── ralph/
│   ├── docs/             # prd.json, progress.txt, templates
│   └── scripts/          # Orchestration scripts
├── src/                  # Source code
├── tests/                # Tests
└── Makefile              # Build automation
```
