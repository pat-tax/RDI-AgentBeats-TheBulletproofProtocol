# Technical Implementation Guide: Bulletproof Protocol for AgentBeats

**Status**: Implementation Phase
**Timeline**: 9 days until Phase 1 deadline (Jan 31, 2026)
**Approach**: Minimal Viable Benchmark (KISS principle)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                   AgentBeats Platform                    │
└─────────────────────────────────────────────────────────┘
                            │
                            │ A2A Protocol
                            │
        ┌───────────────────┴───────────────────┐
        │                                       │
┌───────▼────────┐                    ┌────────▼────────┐
│  Agent B       │◄──Assessment────►  │   Agent A       │
│  (Green Agent) │    Request         │ (Purple Agent)  │
│  Examiner      │                    │ Substantiator   │
└───────┬────────┘                    └────────┬────────┘
        │                                      │
        │ Evaluates                            │ Generates
        │ Risk Score (0-100)                   │ Narrative
        │ Redline Markup                       │ (Mock Data)
        │                                      │
        └──────────────────┬───────────────────┘
                           │
                           │ Iterative Loop
                           │
                    ┌──────▼──────┐
                    │  Artifact   │
                    │  (JSON)     │
                    │  Results    │
                    └─────────────┘
```

---

## A2A Protocol Implementation

### Python SDK Setup

**Installation**:
```bash
pip install "a2a-sdk[http-server]"
```

**Dependencies**:
- Python 3.13 (project standard)
- a2a-sdk
- FastAPI/Starlette (HTTP server)
- uvicorn (ASGI server)

### Server Pattern

```python
from a2a.server import AgentExecutor, DefaultRequestHandler
from a2a.server.starlette import create_app
import uvicorn

class MyAgentExecutor(AgentExecutor):
    async def execute(self, task_id: str, input_data: dict) -> dict:
        # Core agent logic here
        return {"result": "..."}

def main():
    executor = MyAgentExecutor()
    handler = DefaultRequestHandler(agent_executor=executor)
    app = create_app(
        agent_card={
            "name": "agent-name",
            "description": "...",
            "version": "1.0.0"
        },
        http_handler=handler
    )
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Docker ENTRYPOINT Pattern

```python
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--card-url", default="http://localhost:8000")
    args = parser.parse_args()

    uvicorn.run(app, host=args.host, port=args.port)
```

---

## IRS Section 41 Evaluation Rules

### Four-Part Test (All Required)

| Test | Criteria | Agent B Check |
|------|----------|---------------|
| **1. Section 174** | R&D costs in experimental/laboratory sense | Verifies technical nature, not business process |
| **2. Technical Info** | Relies on hard sciences, engineering, computer science | Detects absence of technical foundation |
| **3. Business Component** | Applies to identifiable product/system | Requires discrete component identification |
| **4. Process of Experimentation** | ≥80% activities evaluate alternatives | Counts evidence of alternative evaluation |

### Red Flags (Non-Qualifying Patterns)

**Agent B detects these patterns and penalizes Risk Score:**

1. **Routine Engineering Keywords**:
   - "debugging production issues"
   - "porting to new platform"
   - "rewriting in new language"
   - "ERP implementation"
   - "quality assurance testing"
   - "vendor configuration"

2. **Vague Language (Unsubstantiated)**:
   - "optimized performance" (no metrics)
   - "improved user experience" (no measurement)
   - "upgraded system" (no technical detail)
   - "enhanced reliability" (no failure data)

3. **Business Risk vs Technical Risk**:
   - Market validation concerns
   - User preference testing
   - Sales/marketing activities
   - Training program development

4. **Missing Experimentation Evidence**:
   - No documented alternatives
   - No uncertainty description
   - No evaluation methodology
   - No failure citations

5. **Post-Commercial Production**:
   - "after release" timeline mentions
   - "maintenance work"
   - "bug fixes in production"

### Green Flags (Qualifying Patterns)

**Agent B rewards these patterns (lower Risk Score):**

1. **Technical Uncertainty Keywords**:
   - "algorithm design uncertain"
   - "architectural approach unknown"
   - "performance characteristics unclear"
   - "integration method undefined"

2. **Experimentation Evidence**:
   - "evaluated N alternatives"
   - "tested approaches A, B, C"
   - "benchmarked performance"
   - "failed attempt: [specific]"

3. **Specific Metrics**:
   - "reduced latency by 40ms"
   - "achieved 99.9% uptime"
   - "10x throughput improvement"
   - "decreased memory usage from X to Y"

4. **Hypothesis-Test-Failure Pattern**:
   - "hypothesized that..."
   - "tested by implementing..."
   - "failed due to [technical reason]"
   - "iterated with approach..."

5. **Hard Science Foundation**:
   - "applied algorithm X from CS theory"
   - "leveraged principles of distributed systems"
   - "utilized cryptographic protocol Y"
   - "implemented based on engineering model Z"

---

## Risk Scoring Algorithm

### Weighted Calculation (0-100 scale)

```python
risk_score = (
    routine_engineering_penalty * 0.30 +
    vagueness_penalty * 0.25 +
    business_risk_penalty * 0.20 +
    missing_experimentation_penalty * 0.15 +
    lack_of_specificity_penalty * 0.10
)

# Lower score = lower audit risk
# Target: < 20 for "audit-proof"
```

### Penalty Breakdown

| Component | Weight | Max Penalty | Triggers |
|-----------|--------|-------------|----------|
| **Routine Engineering** | 30% | 30 pts | Keywords: debugging, porting, maintenance |
| **Vagueness** | 25% | 25 pts | No metrics, generic claims, buzzwords |
| **Business Risk** | 20% | 20 pts | Market concerns, not technical |
| **No Experimentation** | 15% | 15 pts | Missing alternatives, no evaluation |
| **Lack of Specificity** | 10% | 10 pts | No numbers, no concrete details |

### Redline Markup Format

```json
{
  "risk_score": 65,
  "issues": [
    {
      "line": 12,
      "pattern": "optimized performance",
      "severity": "high",
      "reason": "Vague claim without metrics (IRS Red Flag: unsubstantiated improvement)",
      "suggestion": "Specify metric: 'reduced response time from 200ms to 40ms'"
    }
  ],
  "summary": "Narrative contains 3 high-severity issues typical of rejected claims"
}
```

---

## Implementation Plan (9 Days)

### Days 1-2: Agent B (Green Agent) - MVP

**Goal**: Basic A2A server with 5 core IRS rules

**Files to Create**:
```
src/bulletproof_green/
├── __init__.py
├── server.py              # A2A server entrypoint
├── examiner.py            # AgentExecutor implementation
├── rules/
│   ├── __init__.py
│   ├── routine_engineering.py
│   ├── vagueness_detector.py
│   └── experimentation_checker.py
├── scorer.py              # Risk score calculation
└── redline.py             # Markup generation

Dockerfile.green
agent-card-green.json
```

**Core Rules (Minimal Set)**:
1. Routine engineering keyword detection (10 keywords)
2. Vagueness detection (lack of metrics)
3. Experimentation evidence check (alternatives mentioned?)
4. Specificity scoring (numbers present?)
5. Business vs technical risk (market/sales keywords)

### Days 3-4: Agent A (Purple Agent) - Baseline

**Goal**: Template-based narrative generator with mock data

**Files to Create**:
```
src/bulletproof_purple/
├── __init__.py
├── server.py              # A2A server entrypoint
├── substantiator.py       # AgentExecutor implementation
├── templates/
│   ├── __init__.py
│   └── four_part_test.py  # IRS Section 41 template
├── mock_data.py           # Simulated engineering data
└── generator.py           # Narrative construction

Dockerfile.purple
agent-card-purple.json
```

**Mock Data Sources**:
- 5 sample "projects" with commit messages
- 3-5 technical uncertainties per project
- 2-3 alternatives evaluated
- Specific metrics (latency, throughput, error rates)

### Days 5-6: Assessment Flow + Docker

**Goal**: End-to-end A2A assessment working locally

**Files to Create**:
```
scenario.toml
docker-compose.yml
.dockerignore
```

**Testing**:
```bash
# Build and start containers
docker-compose build
docker-compose up -d

# Verify A2A handshake
curl http://localhost:8001/.well-known/agent-card.json
curl http://localhost:8002/.well-known/agent-card.json

# Run e2e assessment test
pytest tests/integration/test_e2e_assessment.py

# Check results output
cat results/local_benchmark.json
# Verify structure: {participant_id, pass_rate, traffic_light_green_pct, n_tasks, risk_scores[]}

# Query results with DuckDB (optional)
duckdb -c "SELECT participant_id, ROUND(pass_rate, 2) AS pass_rate, ROUND(traffic_light_green_pct, 2) AS green_pct, n_tasks FROM read_json_auto('results/local_benchmark.json')"
```

### Days 7-8: Demo + Documentation

**Goal**: Submission package ready

**Deliverables**:
- README.md with setup instructions
- Abstract (300 words) describing benchmark
- Record 3-minute demo video
- Test on clean machine

### Day 9: Submit

**Actions**:
1. Register agents on agentbeats.dev
2. Push Docker images to GHCR
3. Submit Phase 1 form
4. Buffer for last-minute issues

---

## File Structure (Minimal)

```
bulletproof-protocol/
├── src/
│   ├── bulletproof_green/         # Agent B (Green)
│   │   ├── server.py
│   │   ├── examiner.py
│   │   ├── rules/
│   │   ├── scorer.py
│   │   └── redline.py
│   └── bulletproof_purple/        # Agent A (Purple)
│       ├── server.py
│       ├── substantiator.py
│       ├── templates/
│       └── mock_data.py
├── Dockerfile.green
├── Dockerfile.purple
├── agent-card-green.json
├── agent-card-purple.json
├── scenario.toml
├── docker-compose.yml
├── README.md
├── ABSTRACT.md
└── pyproject.toml
```

---

## Key Sources & References

### A2A Protocol
- [Official Python SDK](https://github.com/a2aproject/a2a-python)
- [A2A Protocol Spec](https://a2a-protocol.org/latest/)
- [Google ADK Docs](https://google.github.io/adk-docs/a2a/intro/)
- [AgentBeats Tutorial](https://github.com/RDI-Foundation/agentbeats-tutorial)

### IRS Section 41
- [IRS Audit Techniques Guide - Qualified Research Activities](https://www.irs.gov/businesses/audit-techniques-guide-credit-for-increasing-research-activities-ie-research-tax-credit-irc-ss-41-qualified-research-activities)
- [IRS Software Development Guidelines](https://www.irs.gov/businesses/audit-guidelines-on-the-application-of-the-process-of-experimentation-for-all-software)
- [26 USC 41 - Credit for Increasing Research Activities](https://uscode.house.gov/view.xhtml?req=(title:26+section:41+edition:prelim))
- [26 CFR § 1.41-4 - Qualified Research Regulations](https://www.law.cornell.edu/cfr/text/26/1.41-4)

---

## Success Criteria

**Phase 1 Submission Requirements Met**:
- [ ] A2A-compatible green agent (Docker image)
- [ ] A2A-compatible baseline purple agent (Docker image)
- [ ] End-to-end assessment flow works
- [ ] Abstract written (300 words)
- [ ] README with clear setup instructions
- [ ] 3-minute demo video recorded
- [ ] Registered on agentbeats.dev
- [ ] Submitted via Phase 1 form

**Technical Quality**:
- [ ] Docker builds on linux/amd64
- [ ] Accepts --host, --port, --card-url arguments
- [ ] Returns valid JSON artifacts
- [ ] Risk score calculation consistent
- [ ] Redline markup actionable

**Benchmark Validity**:
- [ ] Evaluates real legal domain criteria (IRS Section 41)
- [ ] Clear scoring methodology (0-100 scale)
- [ ] Reproducible results (same input → same score)
- [ ] Addresses gap (no existing R&D tax benchmark)
- [ ] Practical use case (startups, tax professionals)
