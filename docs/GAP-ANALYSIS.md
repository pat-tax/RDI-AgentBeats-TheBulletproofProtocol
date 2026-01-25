# Gap Analysis: Current Implementation vs AgentBeats Green Agent Template

**Date**: 2026-01-25
**Status**: Pre-submission review
**Verdict**: Functional — minor architectural gaps remain

---

## Summary

The implementation is functionally complete with all five detectors implemented, proper A2A integration, and AgentBeats-compatible scoring. Remaining gaps are architectural (template structure) and minor CLI flexibility.

---

## Validation Results

All detectors functional:

| Detector | Max Penalty | Patterns | Status |
|----------|-------------|----------|--------|
| Routine Engineering | 30 | 13 patterns | ✓ |
| Business Risk | 20 | 9 patterns | ✓ |
| Vagueness | 25 | 8 patterns | ✓ |
| Experimentation | 15 | 10 patterns | ✓ |
| Specificity | 10 | Regex metrics | ✓ |

---

## Verdict

| Question | Answer |
|----------|--------|
| Does it work as a Green Agent? | **Yes** — full evaluation pipeline functional |
| AgentBeats compatible? | **Yes** — A2A protocol, scoring format correct |
| Production ready? | **Mostly** — consider modular refactor for maintainability |
| Blocking issues? | **None** |

---

## Prioritization Matrix

| Gap | Priority | Effort | Impact | Decision |
|-----|----------|--------|--------|----------|
| Modular structure | P2 | High | Maintainability | **Defer** — functional as-is |
| `--card-url` CLI | P2 | Low | Platform compatibility | **Do** — quick win |
| Metadata fields | P3 | Low | Completeness | **Do** — quick win |

**Priority Legend**:
- P1 = Blocking submission
- P2 = Should fix before production
- P3 = Nice to have

---

## Closed Gaps (Previously Open)

| Gap | Previous Status | Current Status | Evidence |
|-----|-----------------|----------------|----------|
| Hardcoded server response | P0 Critical | **CLOSED** | `server.py` uses `GreenAgentExecutor` → `evaluator.evaluate()` → `scorer.score()` |
| Business risk detector | P1 Missing | **CLOSED** | `evaluator.py:62-72` BUSINESS_PATTERNS, `_detect_business_risk()` |
| Specificity detector | P1 Missing | **CLOSED** | `evaluator.py:100-104` SPECIFICITY_PATTERN, `_detect_lack_of_specificity()` |
| Output format (`confidence`, `risk_category`) | P2 Missing | **CLOSED** | `EvaluationResult` dataclass has all fields |

---

## Working Correctly

| Component | Status | Evidence |
|-----------|--------|----------|
| A2A Server Infrastructure | ✓ | `A2AFastAPIApplication` with `DefaultRequestHandler` |
| Agent Cards | ✓ | `get_agent_card()` returns proper `AgentCard` |
| Docker Configuration | ✓ | Multi-stage build, `linux/amd64`, non-root user |
| Ground Truth Dataset | ✓ | 20 labeled cases in `data/ground_truth.json` |
| Rule-based Evaluation | ✓ | 5/5 detectors implemented with IRS patterns |
| AgentBeats Scoring | ✓ | `AgentBeatsScorer` converts to 0.0-1.0 scale |
| Docker Compose | ✓ | Proper networking, port mapping |
| E2E Test Script | ✓ | `scripts/test_e2e.sh` with robust JSON parsing |

---

## Remaining Gaps

### P2 — Architectural: Monolithic vs Modular Structure

**Template Structure (debate_judge)**:
```
src/
├── server.py      # Entry point only: argparse, AgentCard, uvicorn.run() (~50 lines)
├── executor.py    # Task lifecycle: extends AgentExecutor (~80 lines)
├── agent.py       # Domain logic: business rules (~200 lines)
└── messenger.py   # A2A utilities
```

**Our Structure**:
```
src/bulletproof_green/
├── server.py      # Combined: AgentCard + Executor + Handler + Factory (283 lines)
├── evaluator.py   # Domain logic ✓
├── scorer.py      # Domain logic ✓
```

| Aspect | Template | Ours | Impact |
|--------|----------|------|--------|
| Entry point | Separate `server.py` | Combined | Harder to test executor separately |
| Executor | Separate `executor.py` | In `server.py` | Less reusable |
| Lines per file | ~50-80 | 283 | Lower readability |

**Recommendation**: Split `server.py` into `agent.py` (entry) + `executor.py` (task lifecycle).

---

### P2 — CLI Arguments

**Template**:
```python
parser.add_argument("--host", default="127.0.0.1")
parser.add_argument("--port", default=9009)
parser.add_argument("--card-url", help="URL to advertise in agent card")
```

**Ours**: Relies on uvicorn CLI via Dockerfile ENTRYPOINT. No `--card-url` support.

| Argument | Template | Ours |
|----------|----------|------|
| `--host` | argparse | uvicorn CLI ✓ |
| `--port` | argparse | uvicorn CLI ✓ |
| `--card-url` | argparse | **Missing** |

**Impact**: `--card-url` is needed when external URL differs from internal (load balancers, proxies).

---

### P3 — Minor: Output Metadata

Missing optional metadata fields (not blocking):

| Field | Purpose | Status |
|-------|---------|--------|
| `metadata.evaluation_time_ms` | Performance tracking | Missing |
| `metadata.rules_version` | Reproducibility | Missing |
| `metadata.irs_citations` | Legal grounding | Missing |

---

### P3 — Minor: Default Port

| Specification | Template | Ours |
|---------------|----------|------|
| Default port | 9009 | 8000 |

Not blocking — both work with AgentBeats platform.

---

## Solutions

### Solution 1: Add `--card-url` Support (P2, ~30 min)

**Problem**: AgentCard URL hardcoded to `http://localhost:8000`, breaks behind proxies/load balancers.

**Option A: Environment Variable (Recommended)**
```python
# server.py
import os

def get_agent_card(base_url: str | None = None) -> AgentCard:
    url = base_url or os.environ.get("AGENT_CARD_URL", "http://localhost:8000")
    return AgentCard(url=url, ...)
```

**Option B: Argparse (Template Pattern)**
```python
# agent.py (new entry point)
parser = argparse.ArgumentParser()
parser.add_argument("--card-url", default="http://localhost:8000")
args = parser.parse_args()
agent_card = get_agent_card(args.card_url)
```

**Recommendation**: Option A — simpler, works with existing Dockerfile ENTRYPOINT.

---

### Solution 2: Add Metadata Fields (P3, ~15 min)

**Problem**: Missing optional fields for debugging and compliance.

**Fix**: Update `server.py` response construction:

```python
import time

# In GreenAgentExecutor.execute():
start_time = time.perf_counter()
eval_result = await asyncio.to_thread(self.evaluator.evaluate, narrative)
eval_time_ms = int((time.perf_counter() - start_time) * 1000)

data_part = DataPart(data={
    # Existing fields...
    "metadata": {
        "evaluation_time_ms": eval_time_ms,
        "rules_version": "1.0.0",
        "irs_citations": ["IRS Section 41(d)(1)", "26 CFR § 1.41-4"],
    }
})
```

---

### Solution 3: Modular Refactor (P2, ~2 hours) — DEFERRED

**Problem**: `server.py` combines entry point, executor, and handler (283 lines).

**Target Structure**:
```
src/bulletproof_green/
├── agent.py       # Entry point: argparse, AgentCard, main()
├── executor.py    # GreenAgentExecutor class
├── handler.py     # GreenRequestHandler class
├── evaluator.py   # Domain logic (unchanged)
├── scorer.py      # Domain logic (unchanged)
```

**Why Defer**:
- Current implementation works correctly
- Refactor risk before deadline
- No functional benefit, only maintainability

**When to Do**: Post-submission cleanup or if adding new features.

---

## Action Plan

| # | Action | Priority | Effort | Status |
|---|--------|----------|--------|--------|
| 1 | Add `AGENT_CARD_URL` env var | P2 | 15 min | TODO |
| 2 | Add metadata to response | P3 | 15 min | TODO |
| 3 | Modular refactor | P2 | 2 hours | DEFERRED |

**Total estimated effort for P2+P3 fixes**: ~30 minutes

---

## AgentBeats Submission Workflow

### Platform Overview

AgentBeats (agentbeats.dev) uses an agent-to-agent evaluation model:
- **Green Agents** (Assessors): Evaluate participants, calculate scores
- **Purple Agents** (Participants): Agents under test

### Critical Discovery: CLI Arguments Required

The `generate_compose.py` script from the leaderboard repo generates:

```yaml
command: ["--host", "0.0.0.0", "--port", "9009", "--card-url", "http://green-agent:9009"]
```

**This means `--card-url` is NOT optional** — it's required for AgentBeats infrastructure.

### Submission Steps

#### Step 1: Register Agents on agentbeats.dev

1. Go to https://agentbeats.dev
2. Register Green Agent → receive `agentbeats_id` (UUID)
3. Register Purple Agent → receive `agentbeats_id` (UUID)

#### Step 2: Push Docker Images to GHCR (Public)

```bash
# Build images
export GH_USERNAME=<your-github-username>
bash scripts/build.sh

# Push to GHCR
export GHCR_PAT=<your-github-pat>
bash scripts/push.sh
```

Images must be **public** for AgentBeats to pull them.

#### Step 3: Create scenario.toml

```toml
[green_agent]
agentbeats_id = "<green-agent-uuid>"
image = "ghcr.io/<org>/bulletproof-green:latest"
env = {}

[[participants]]
agentbeats_id = "<purple-agent-uuid>"
name = "substantiator"
image = "ghcr.io/<org>/bulletproof-purple:latest"
env = {}

[config]
difficulty = "medium"
max_iterations = 5
target_risk_score = 20
```

#### Step 4: Generate Docker Compose

```bash
# Clone leaderboard repo structure or use generate_compose.py
python generate_compose.py --scenario scenario.toml
```

This generates:
- `docker-compose.yml` — orchestrates all containers
- `a2a-scenario.toml` — runtime configuration
- `.env.example` — environment variables template

#### Step 5: Run Locally

```bash
docker-compose up
```

The `agentbeats-client` container:
1. Waits for all agents to be healthy (via healthcheck)
2. Sends scenario to Green Agent
3. Green Agent orchestrates evaluation
4. Results written to `output/results.json`

#### Step 6: Submit Results

Results are automatically uploaded to AgentBeats leaderboard via the client container.

### Result Format

```json
{
  "participants": {
    "substantiator": "<agentbeats_id>"
  },
  "results": [
    {
      "overall_score": 0.85,
      "component_scores": {
        "correctness": 0.90,
        "safety": 0.80,
        "specificity": 0.85,
        "experimentation": 0.85
      },
      "classification": "QUALIFYING",
      "risk_score": 15
    }
  ]
}
```

---

## Updated Gap Priority

Based on AgentBeats workflow analysis:

| Gap | Previous Priority | New Priority | Reason |
|-----|-------------------|--------------|--------|
| `--card-url` CLI | P2 | **P1 CRITICAL** | Required by `generate_compose.py` |
| `--host`, `--port` CLI | ✓ (via uvicorn) | **P1 CRITICAL** | Must be positional args, not uvicorn flags |
| Default port 9009 | P3 | P2 | AgentBeats default is 9009, ours is 8000 |
| Modular structure | P2 | P3 | Not blocking submission |

### Revised Action Plan

| # | Action | Priority | Effort | Blocking? |
|---|--------|----------|--------|-----------|
| 1 | Add argparse: `--host`, `--port`, `--card-url` | **P1** | 30 min | **YES** |
| 2 | Change default port to 9009 | P2 | 5 min | No |
| 3 | Add metadata to response | P3 | 15 min | No |
| 4 | Modular refactor | P3 | 2 hours | No |

### Solution: Add CLI Arguments (P1)

Replace uvicorn factory pattern with argparse entry point:

```python
# agent.py (new entry point)
import argparse
import uvicorn
from bulletproof_green.server import get_agent_card, GreenRequestHandler
from a2a.server.apps import A2AStarletteApplication

def main():
    parser = argparse.ArgumentParser(description="Bulletproof Green Agent")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind")
    parser.add_argument("--port", type=int, default=9009, help="Port to bind")
    parser.add_argument("--card-url", help="URL to advertise in agent card")
    args = parser.parse_args()

    card_url = args.card_url or f"http://{args.host}:{args.port}"
    agent_card = get_agent_card(card_url)

    handler = GreenRequestHandler()
    app = A2AStarletteApplication(agent_card=agent_card, http_handler=handler)

    uvicorn.run(app.build(), host=args.host, port=args.port)

if __name__ == "__main__":
    main()
```

**Dockerfile update**:
```dockerfile
ENTRYPOINT ["python", "-m", "bulletproof_green.agent"]
CMD ["--host", "0.0.0.0", "--port", "9009"]
```
