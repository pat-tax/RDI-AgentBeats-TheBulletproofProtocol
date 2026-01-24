# Ralph Loop - Autonomous TDD development loop with Claude Code

Autonomous AI development loop that iteratively implements stories until all acceptance criteria pass.

## What is Ralph?

Named after Ralph Wiggum from The Simpsons, this technique by Geoffrey Huntley implements self-referential AI development loops. The agent sees its own previous work in files and git history, iteratively improving until completion.

**Core Loop:**

```text
while stories remain:
  1. Read prd.json, pick next story (passes: false)
  2. Implement story
  3. Run typecheck + tests (TDD: red → green → refactor)
  4. If passing: commit, mark done, log learnings
  5. Repeat until all pass (or context limit)
```

**Memory persists only through:**

- `prd.json` - Task status and acceptance criteria
- `progress.txt` - Learnings and patterns
- Git commits - Code changes

**Usage:**

```bash
make ralph_run ITERATIONS=25    # Run autonomous development
make ralph_status               # Check progress
```

Or interactively via [ralph-loop plugin](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/ralph-loop):

```text
/ralph-loop "Implement stories from prd.json" --max-iterations 25
/cancel-ralph   # Stop active loop
```

**Sources:**

- [Ralph Wiggum as a "software engineer"](https://ghuntley.com/ralph/) - Geoffrey Huntley
- [ralph-loop@claude-plugins-official](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/ralph-loop)

---

## Extended Functionality

### TDD Enforcement (Red-Green-Refactor)

Stories require verifiable acceptance criteria:

1. **Red** - Write failing test
2. **Green** - Implement until tests pass
3. **Refactor** - Clean up, commit, mark done

### Compound Engineering

Learnings compound over time: **Plan** → **Work** → **Assess** → **Compound**

Sources: [Compound Engineering](https://every.to/chain-of-thought/compound-engineering-how-every-codes-with-agents)

### ACE-FCA (Context Engineering)

Context window management for quality output. See `.claude/rules/context-management.md`

Source: [ACE-FCA](https://github.com/humanlayer/advanced-context-engineering-for-coding-agents/blob/main/ace-fca.md)

### Claude Code Sandbox

OS-level isolation for safer autonomous execution.

```bash
make setup_sandbox  # Install bubblewrap + socat (Linux/WSL2)
```

Source: [Claude Code Sandboxing](https://code.claude.com/docs/en/sandboxing)

### Skills and Rules

- `.claude/skills/` - Agent capabilities (generating-prd, researching-codebase)
- `.claude/rules/` - Behavioral guidelines (core-principles, context-management)

---

## Quick Start

See [TEMPLATE_USAGE.md](TEMPLATE_USAGE.md) for setup and commands reference.

## Security

**Ralph runs with `--dangerously-skip-permissions`** - all operations execute without approval.

**Only use in:** Isolated environments (DevContainers, VMs).

## Workflow

```text
PRD.md → prd.json → Ralph Loop → src/ + tests/ → progress.txt
```

## Structure

```text
ralph/
├── docs/
│   ├── README.md           # Methodology (this file)
│   ├── TEMPLATE_USAGE.md   # Setup guide
│   ├── LEARNINGS.md        # Lessons learned
│   ├── prd.json            # Story tracking (gitignored)
│   └── progress.txt        # Execution log (gitignored)
└── scripts/
    ├── ralph.sh            # Orchestration script
    └── generate_prd_json.py
```
