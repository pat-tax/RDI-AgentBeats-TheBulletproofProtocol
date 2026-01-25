---
name: generating-prd-json-from-prd-md
description: Generates prd.json task tracking file from PRD.md requirements document. Use when initializing Ralph loop or when the user asks to convert PRD to JSON format for autonomous execution.
model: haiku
allowed-tools: Read, Write, Bash
---

# PRD to JSON Conversion

Converts `docs/PRD.md` into `ralph/docs/prd.json` for Ralph loop task tracking.

## Purpose

**Initial generation**: Extracts features from PRD.md → creates prd.json stories
**Incremental updates**: Preserves completion status, detects content changes via SHA-256 hash
**Content changes**: Resets story status when title/description/acceptance modified (triggers re-testing)

## PRD.md Required Structure

```markdown
## Functional Requirements

#### Feature N: [Name]

**Description**: [What this feature does]

**Acceptance Criteria**:
- [ ] Criterion 1
- [ ] Criterion 2

**Files Implemented**:
- path/to/file.py
```

**Extraction**: Parse `#### Feature N:` headings top-to-bottom, extract description, acceptance, files.

**Edge cases**: Missing acceptance → extract from description; Missing files → empty array; No features → ABORT

## Story ID Assignment

**Sequential, append-only**: STORY-001, STORY-002, etc. in PRD.md order

**CRITICAL**: Always append new features to END of PRD.md (reordering breaks status preservation)

## prd.json Schema

Template: `ralph/docs/templates/prd.json.template` (read for structure, populate from PRD.md)

**Required fields**:
- `project`, `description`, `source`, `generated`, `stories[]`

**Each story**:
- `id`: STORY-XXX (sequential)
- `title`: 3-7 words
- `description`: 1-2 sentences
- `acceptance`: Array of criteria
- `files`: Array of paths
- `passes`: Boolean (false initially)
- `completed_at`: ISO timestamp (null initially)
- `content_hash`: SHA-256 hex of `title + "|" + description + "|" + json.dumps(acceptance, sort_keys=True)` (use Python `hashlib.sha256().hexdigest()`, not OS tools)

## State Preservation (Incremental Mode)

When `ralph/docs/prd.json` exists:

1. Read existing status: `{story_id: {passes, completed_at, content_hash}}`
2. Generate new stories from PRD.md
3. For each story:
   - **ID exists + hash matches** → preserve `passes` and `completed_at`
   - **ID exists + hash differs** → reset to `passes: false`, log "STORY-XXX content changed, re-test needed"
   - **New ID** → set `passes: false`
4. Write merged result

**Dependency note**: Content changes require re-running integration tests with dependent stories (manual tracking)

## Error Handling

**ABORT** (don't write prd.json):
- PRD.md not found at `docs/PRD.md`
- No `#### Feature` headings found
- Existing prd.json corrupted (invalid JSON)
- Parsing failure (malformed PRD.md)

**WARN** (write prd.json, log warning):
- Missing acceptance criteria
- Missing files list
- Non-standard heading format

## Usage

```bash
/generating-prd
```

**Output**: `ralph/docs/prd.json`

**Verify**:
```bash
jq '.stories | length' ralph/docs/prd.json
jq '.stories[] | select(.passes == false)' ralph/docs/prd.json
```

**Next**: `make ralph_run`
