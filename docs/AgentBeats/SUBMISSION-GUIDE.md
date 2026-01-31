# AgentBeats Phase 1 Submission Guide

> **Deadline:** January 31, 2026 | **Track:** Create New Benchmark (Legal Domain)

## Submission Requirements

| # | Requirement | Status |
|---|-------------|--------|
| 1 | **Abstract** - Brief description of tasks your green agent evaluates | [ABSTRACT.md](ABSTRACT.md) |
| 2 | **Public GitHub repo** - Complete source code + README with setup/usage | This repo |
| 3 | **Baseline purple agent(s)** - A2A-compatible agent showing benchmark evaluation | `bulletproof_purple` |
| 4 | **Docker image** - Packaged green agent, runs end-to-end without manual intervention | `Dockerfile.green` |
| 5 | **AgentBeats registration** - Register green + purple agents on platform | [agentbeats.dev](https://agentbeats.dev) |
| 6 | **Demo video** - Up to 3 minutes demonstrating green agent | TBD |

## Judging Criteria

### 1. Technical Correctness, Implementation Quality, Documentation
- Clean, well-documented code
- Clear README with overview, setup, usage instructions
- Docker image builds and runs without issues
- Reasonable resource requirements (compute, memory, time)
- Robust error handling and logging
- Correct task logic and scoring

### 2. Reproducibility
- Consistent results across runs with same agents
- Easy for any A2A-compatible agent to run

### 3. Benchmark Design Quality
- Tasks are realistic, meaningful, representative of real-world capabilities
- Clear difficulty progression or diverse skill assessment
- Tests agentic capabilities (reasoning, planning, multi-step execution)
- Avoids trivial tasks or those solved by simple heuristics

### 4. Evaluation Methodology
- Clear, objective, justifiable scoring criteria
- Automated evaluation where possible
- Appropriate metrics for task type
- Goes beyond binary pass/fail to nuanced evaluation
- Captures multiple dimensions (accuracy, efficiency, safety)

### 5. Innovation & Impact
- Original contribution to evaluation landscape
- Addresses gaps in existing evaluation coverage
- Creative approach to difficult-to-evaluate capabilities
- Clear use case and target audience
- Complementary to existing benchmarks

---

## Architecture

```text
┌─────────────────────────────────────────────────────┐
│                 AgentBeats Platform                  │
└─────────────────────────────────────────────────────┘
                          │ A2A Protocol
          ┌───────────────┴───────────────┐
          ▼                               ▼
┌──────────────────┐            ┌──────────────────┐
│   Green Agent    │◄──────────►│  Purple Agent    │
│   (Examiner)     │ Assessment │ (Substantiator)  │
│   Port: 8002     │            │   Port: 8001     │
└──────────────────┘            └──────────────────┘
```

| Component | Role | Output |
|-----------|------|--------|
| **Green (Examiner)** | Evaluates IRS Section 41 compliance | Risk Score (0-100), Redline markup |
| **Purple (Substantiator)** | Generates R&D narratives for evaluation | Narrative artifact |

### File Structure

```text
src/bulletproof_green/
├── agent.py        # Domain logic
├── executor.py     # A2A protocol adapter
├── server.py       # HTTP transport
└── evals/          # Evaluation: evaluator.py, scorer.py, llm_judge.py
```

---

## Implementation Essentials

### A2A Protocol

- JSON-RPC 2.0 communication
- AgentCard at `/.well-known/agent-card.json`
- Task states: `pending → running → completed/failed`
- SDK: `pip install "a2a-sdk[http-server]"`

### Docker Requirements

```dockerfile
# Must support these ENTRYPOINT parameters
ENTRYPOINT ["python", "-m", "bulletproof_green.server"]
CMD ["--host", "0.0.0.0", "--port", "8000"]
```

- Platform: `linux/amd64`
- Bind to `0.0.0.0` (not localhost)
- Stateless: fresh state per assessment (use `task_id` for namespacing)

### Evaluation Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| **Risk Score** | 0-100 scale (0 = audit-proof) | < 20 for qualifying |
| **Classification** | QUALIFYING / NON_QUALIFYING | 90%+ accuracy |
| **Component Scores** | correctness, safety, specificity, experimentation | 0.0-1.0 each |

```
overall_score = (100 - risk_score) / 100
```

---

## Testing & Deployment

### Local Testing

```bash
# Build and start
docker-compose build && docker-compose up -d

# Verify agents
curl http://localhost:8001/.well-known/agent-card.json  # Purple
curl http://localhost:8002/.well-known/agent-card.json  # Green

# Run E2E tests
bash scripts/test_e2e.sh
```

### Push to GHCR

```bash
# Authenticate
echo $CR_PAT | docker login ghcr.io -u $GITHUB_USERNAME --password-stdin

# Tag and push
docker tag bulletproof-green:local ghcr.io/$GITHUB_USERNAME/bulletproof-green:latest
docker push ghcr.io/$GITHUB_USERNAME/bulletproof-green:latest

# Make packages PUBLIC in GitHub settings
```

### Register on AgentBeats

1. Visit [agentbeats.dev](https://agentbeats.dev)
2. Register Green Agent:
   - Name: `Bulletproof Green Agent`
   - Image: `ghcr.io/YOUR_USERNAME/bulletproof-green:latest`
3. Register Purple Agent:
   - Name: `Bulletproof Purple Agent`
   - Image: `ghcr.io/YOUR_USERNAME/bulletproof-purple:latest`
4. Copy `agentbeats_id` values to `scenario.toml`

### Update scenario.toml

```toml
[green_agent]
agentbeats_id = "agent_xyz123"  # From registration

[[participants]]
agentbeats_id = "agent_abc789"  # From registration
name = "substantiator"
```

---

## E2E Submission Testing

### Step 5: Run E2E Submission Test

Before submitting, validate your agents produce AgentBeats-compatible output:

```bash
# Quick smoke test (2 narratives, ~60s)
./scripts/docker/test_e2e.sh quick

# Comprehensive test (30 narratives from ground truth, ~10min)
./scripts/docker/test_e2e.sh comprehensive

# Verify output format
cat logs/e2e_*/results.json | jq '.'
```

**Expected Output** (`output/results.json`):
```json
{
  "benchmark_id": "bulletproof-green-v1",
  "participant_id": "purple-baseline",
  "score": 3.0,
  "max_score": 4.0,
  "pass_rate": 75.0,
  "overall_score": 0.75,
  "timestamp": "2026-01-31T18:00:00Z",
  "metadata": {
    "classification": "qualifying",
    "risk_score": 18,
    "risk_category": "low",
    "confidence": 0.95,
    "component_scores": {
      "correctness": 0.90,
      "safety": 0.95,
      "specificity": 0.80,
      "experimentation": 0.85
    }
  }
}
```

### Step 6: Validate SQL Compatibility

AgentBeats leaderboard uses DuckDB to query results. Verify your output is compatible:

```bash
# Install DuckDB (if not already installed)
pip install duckdb

# Test SQL extraction
duckdb << 'SQL'
SELECT
  json_extract_string(r.value, '$.benchmark_id') AS benchmark_id,
  json_extract_string(r.value, '$.participant_id') AS participant_id,
  ROUND(CAST(json_extract(r.value, '$.pass_rate') AS DOUBLE), 1) AS pass_rate,
  ROUND(CAST(json_extract(r.value, '$.overall_score') AS DOUBLE), 2) AS overall_score,
  CAST(json_extract(r.value, '$.score') AS DOUBLE) AS score,
  CAST(json_extract(r.value, '$.max_score') AS DOUBLE) AS max_score,
  json_extract_string(r.value, '$.metadata.classification') AS classification,
  CAST(json_extract(r.value, '$.metadata.risk_score') AS INTEGER) AS risk_score,
  json_extract_string(r.value, '$.timestamp') AS timestamp
FROM read_json_auto('logs/e2e_*/results.json') AS r
ORDER BY pass_rate DESC, overall_score DESC;
SQL
```

**Expected Output:**
```
┌──────────────────────┬──────────────────┬───────────┬───────────────┬───────┬───────────┬────────────────┬────────────┬──────────────────────┐
│    benchmark_id      │ participant_id   │ pass_rate │ overall_score │ score │ max_score │ classification │ risk_score │      timestamp       │
├──────────────────────┼──────────────────┼───────────┼───────────────┼───────┼───────────┼────────────────┼────────────┼──────────────────────┤
│ bulletproof-green-v1 │ purple-baseline  │      75.0 │          0.75 │   3.0 │       4.0 │ qualifying     │         18 │ 2026-01-31T18:00:00Z │
└──────────────────────┴──────────────────┴───────────┴───────────────┴───────┴───────────┴────────────────┴────────────┴──────────────────────┘
```

### Step 7: Test GitHub Workflow (Optional)

Test the full AgentBeats submission workflow:

```bash
# Prerequisites:
# - Agents registered on agentbeats.dev
# - scenario.toml updated with production agentbeats_id values
# - Docker images pushed to GHCR (public)

# Trigger workflow manually
gh workflow run agentbeats-run-scenario.yml

# Monitor workflow
gh run watch

# Check outputs
ls -la submissions/  # scenario.toml + provenance.json
ls -la results/      # results.json
```

**Workflow produces:**
- `submissions/USERNAME-TIMESTAMP.toml` - Scenario configuration
- `submissions/USERNAME-TIMESTAMP.provenance.json` - Container metadata
- `results/USERNAME-TIMESTAMP.json` - Evaluation results

**Submission via PR:**
1. Workflow creates branch: `submission-USERNAME-TIMESTAMP`
2. Opens PR to agentbeats/leaderboard
3. ⚠️ **IMPORTANT**: Uncheck "Allow edits and access to secrets by maintainers"

---

## Pre-Submission Checklist

### Requirements
- [ ] Abstract written ([ABSTRACT.md](ABSTRACT.md))
- [ ] Public GitHub repo with README
- [ ] Purple agent (baseline) implemented
- [ ] Docker images build on `linux/amd64`
- [ ] Agents registered on agentbeats.dev
- [ ] Demo video recorded (up to 3 min)

### Technical Quality
- [ ] `docker-compose up` runs without errors
- [ ] AgentCard endpoints respond correctly
- [ ] E2E tests pass (`./scripts/docker/test_e2e.sh comprehensive`)
- [ ] `output/results.json` validates against SQL schema
- [ ] SQL query extracts metrics correctly (see Step 6)
- [ ] Same input produces same output (reproducible)
- [ ] Error handling and logging implemented

### Benchmark Quality
- [ ] Tasks test agentic capabilities (not trivial)
- [ ] Clear scoring methodology documented
- [ ] Multiple evaluation dimensions (accuracy, safety, etc.)
- [ ] Ground truth dataset validates accuracy

### Final Steps
- [ ] Images pushed to GHCR (public visibility)
- [ ] `scenario.toml` updated with production IDs
- [ ] Submit via [Phase 1 Form](https://forms.gle/1C5d8KXny2JBpZhz7)

---

## Resources

See [RESOURCES.md](RESOURCES.md) for all external links.

**Quick Links:**
- Platform: [agentbeats.dev](https://agentbeats.dev)
- Discord: [discord.gg/uqZUta3MYa](https://discord.gg/uqZUta3MYa)
- Submission Form: [forms.gle/1C5d8KXny2JBpZhz7](https://forms.gle/1C5d8KXny2JBpZhz7)
