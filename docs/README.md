# Documentation Hub

> **Quick Navigation:** [Testing](#testing) | [E2E Testing](#end-to-end-testing) | [LLM Testing](#testing-with-llm-endpoint) | [Agent Registration](#registering-agents) | [Milestones](#milestones) | [Ralph Loop](#ralph-loop-development)

---

## Testing

### Testing Strategy & Best Practices

**See:** [`docs/best-practices/testing-strategy.md`](best-practices/testing-strategy.md)

**Summary:**
- ✅ **35% fewer tests** (532 → 348) through intelligent cleanup
- ✅ **78% faster runtime** (16.5s → 3.7s) with 100% pass rate maintained
- ✅ **Centralized configuration** via pydantic-settings
- 📋 **Planned:** Property-based testing with Hypothesis for edge cases

**Key Principles:**
1. **Test behavior, not structure** - No more "field exists" tests
2. **Trust frameworks** - Pydantic validates, pyright type-checks
3. **Remove redundancy** - If import fails, other tests fail anyway
4. **Consolidate granularity** - One schema test > 8 field tests

**Quick Wins Removed:**
- Import/existence tests (Python handles this)
- Field existence tests (Pydantic handles this)
- Default value tests (testing constants)
- Over-granular tests (8 tests → 1 schema test)
- Type checks (pyright handles this)

---

## End-to-End Testing

### Current Implementation State

**Available E2E Tests:**

```bash
# Quick E2E test (basic validation)
bash scripts/test_e2e.sh

# Comprehensive E2E test with full ground truth dataset (30 narratives)
bash scripts/test_comprehensive.sh

# Docker-based E2E (agents in containers)
docker-compose up -d
bash scripts/test_e2e.sh
```

### E2E Test Coverage

**1. Basic Validation (`test_e2e.sh`)**
- ✅ Purple agent generates narrative
- ✅ Green agent evaluates narrative
- ✅ AgentCard discovery works
- ✅ JSON-RPC protocol compliance
- ✅ Response schema validation

**2. Comprehensive Validation (`test_comprehensive.sh`)**
- ✅ 30 ground truth narratives (qualifying/non-qualifying/edge cases)
- ✅ Classification accuracy ≥90%
- ✅ Risk score consistency
- ✅ Component score validation
- ✅ Redline issue detection

**3. Integration Tests**
- ✅ Agent-to-agent communication (Purple → Green)
- ✅ Arena mode multi-turn refinement
- ✅ Hybrid scoring (rule-based + LLM)
- ✅ Timeout handling
- ✅ Error recovery

### Running E2E Tests

**Local (without Docker):**
```bash
# Terminal 1: Start Purple agent
python -m bulletproof_purple.server

# Terminal 2: Start Green agent
python -m bulletproof_green.server

# Terminal 3: Run E2E tests
bash scripts/test_e2e.sh
```

**Docker Compose:**
```bash
# Start both agents
docker-compose up -d

# Verify agents are running
curl http://localhost:8001/.well-known/agent-card.json  # Purple
curl http://localhost:8002/.well-known/agent-card.json  # Green

# Run E2E tests
bash scripts/test_e2e.sh

# Cleanup
docker-compose down
```

**CI/CD (GitHub Actions):**
```yaml
# .github/workflows/pytest.yaml already includes E2E tests
# Runs on every push/PR
```

---

## Testing with LLM Endpoint

### Configuration

**Required Environment Variable:**
```bash
# .env file
GREEN_OPENAI_API_KEY=sk-your-actual-key-here
```

**Graceful Fallback:**
- If `GREEN_OPENAI_API_KEY` is not set → Falls back to rule-only scoring
- If OpenAI API fails → Falls back to rule-only scoring
- System logs warnings but continues operation

### LLM Hybrid Scoring

**Formula:**
```
final_score = α * rule_score + β * llm_score
where α = 0.7 (rule weight), β = 0.3 (LLM weight)
```

**Test with LLM:**
```bash
# Set API key
export GREEN_OPENAI_API_KEY=sk-your-key

# Run tests
python -m pytest tests/test_hybrid_scoring_integration.py -v

# Or run E2E with LLM
bash scripts/test_comprehensive.sh
```

### LLM Test Coverage

**Unit Tests:**
```bash
# LLM judge tests
pytest tests/test_llm_judge.py -v

# Hybrid scoring integration
pytest tests/test_hybrid_scoring_integration.py -v
```

**Expected Behavior:**
- ✅ LLM provides semantic analysis (0-1 score)
- ✅ Rule-based provides deterministic scoring
- ✅ Hybrid combines both weighted scores
- ✅ Falls back gracefully if LLM unavailable

### Mock Testing (No API Key Required)

```python
# tests/test_llm_judge.py includes mocked tests
@patch('bulletproof_green.llm_judge.AsyncOpenAI')
def test_hybrid_scoring_with_mocked_llm(mock_openai):
    # Test hybrid scoring without real API calls
    pass
```

**Run mocked tests:**
```bash
# No API key needed
pytest tests/test_llm_judge.py -v
```

---

## Registering Agents

### AgentBeats Platform Registration

**See:** [`docs/AgentBeats/SUBMISSION-GUIDE.md`](AgentBeats/SUBMISSION-GUIDE.md)

### Quick Registration Guide

**1. Sign Up:**
- Visit [agentbeats.dev](https://agentbeats.dev)
- Create account
- Navigate to "Register Agent"

**2. Register Green Agent (Benchmark):**
```
Name: Bulletproof Green Agent
Description: IRS Section 41 R&D tax credit narrative evaluator
AgentCard URL: https://your-url.com/.well-known/agent-card.json
Docker Image: ghcr.io/YOUR_USERNAME/bulletproof-green:latest
```

**3. Register Purple Agent (Baseline):**
```
Name: Bulletproof Purple Agent
Description: IRS Section 41 R&D tax credit narrative generator
AgentCard URL: https://your-url.com/.well-known/agent-card.json
Docker Image: ghcr.io/YOUR_USERNAME/bulletproof-purple:latest
```

**4. Update `scenario.toml`:**
```toml
[green_agent]
agentbeats_id = "agent_xyz123abc456"  # From registration

[[participants]]
agentbeats_id = "agent_abc789def012"  # From registration
name = "substantiator"
```

**5. Push to GHCR:**
```bash
# Build images
bash scripts/build.sh

# Push to GitHub Container Registry
export GH_USERNAME=your-username
export GHCR_PAT=your-token
bash scripts/push.sh

# Make images public in GitHub packages settings
```

**6. Submit to AgentBeats:**
- Fork [agentbeats/leaderboard](https://github.com/agentbeats/leaderboard)
- Update with your `scenario.toml`
- Submit via [Phase 1 Form](https://forms.gle/1C5d8KXny2JBpZhz7)

---

## Milestones

### ✅ Milestone 1: Successful Local E2E Test

**Completed:** 2026-01-XX

**Achievement:**
- ✅ Purple agent generates IRS-compliant narratives
- ✅ Green agent evaluates with 90%+ accuracy
- ✅ 30/30 ground truth narratives classified correctly
- ✅ JSON output schema validated
- ✅ AgentBeats format compliance verified

**Validation:**
```bash
bash scripts/test_comprehensive.sh
# Output: 30/30 narratives evaluated (90% accuracy)
```

---

### ✅ Milestone 2: Settings Refactor & Test Optimization

**Completed:** 2026-01-28

**Achievement:**
- ✅ Centralized configuration (11 Green settings, 3 Purple settings)
- ✅ Settings validators (port, timeout, weights, risk_score)
- ✅ `.env.example` with comprehensive documentation
- ✅ Debug command: `python -m bulletproof_{green,purple}.settings`
- ✅ Test suite optimization: **35% fewer tests** (532→348)
- ✅ Runtime improvement: **78% faster** (16.5s→3.7s)
- ✅ Infrastructure test cleanup: **26.5% reduction** (98→72 tests)

**Impact:**
- Developer experience: Better onboarding, clear configuration
- Code quality: No dead code, cleaner API
- Test quality: Removed brittle string-search tests
- Startup validation: Fail-fast on misconfiguration

---

### 🎯 Milestone 3: Successful Result Sent to AgentBeats.dev

**Status:** Ready for submission

**Requirements:**
- [x] Green agent implementation complete
- [x] Purple agent implementation complete
- [x] Docker images built and tested
- [x] `scenario.toml` configured
- [x] Ground truth validation (90%+ accuracy)
- [x] JSON output schema compliant
- [ ] Agents registered on agentbeats.dev
- [ ] Images pushed to GHCR (public visibility)
- [ ] Leaderboard repo forked and updated
- [ ] Phase 1 submission form completed

**JSON Output Schema:**

```json
{
  "domain": "irs-r&d",
  "score": 3.0,
  "max_score": 4.0,
  "pass_rate": 75.0,
  "task_rewards": {
    "0": 1.0,
    "1": 1.0,
    "2": 1.0,
    "3": 0.0
  },
  "time_used": 0.123,
  "overall_score": 0.75,
  "correctness": 0.8,
  "safety": 0.9,
  "specificity": 0.7,
  "experimentation": 0.6,
  "classification": "qualifying",
  "risk_score": 25,
  "risk_category": "low",
  "confidence": 0.85,
  "redline": {
    "total_issues": 2,
    "critical": 0,
    "high": 1,
    "medium": 1,
    "issues": [...]
  }
}
```

**SQL Schema (for leaderboard):**
```sql
-- AgentBeats stores results in this format
CREATE TABLE benchmark_results (
    id SERIAL PRIMARY KEY,
    benchmark_id VARCHAR(255),
    participant_id VARCHAR(255),
    score FLOAT,
    max_score FLOAT,
    pass_rate FLOAT,
    timestamp TIMESTAMP,
    metadata JSONB
);
```

**Validation Command:**
```bash
# Test JSON schema compliance
python src/validate_benchmark.py

# Expected output:
# ✓ Schema validation passed
# ✓ All required fields present
# ✓ AgentBeats format compliant
```

**Next Steps:**
1. Register agents on agentbeats.dev → get `agentbeats_id`
2. Update `scenario.toml` with production IDs
3. Push Docker images to GHCR (set to public)
4. Fork leaderboard repo and update `scenario.toml`
5. Submit via Phase 1 form

---

## Ralph Loop Development

### What is Ralph?

**Ralph** = Recursive Autonomous Loop for Product Handling

**Purpose:** Autonomous development using Compound Engineering and ACE-FCA principles

**See:** [`ralph/README.md`](../ralph/README.md)

### Ralph Story Management

**Current Stories:**
```bash
# View all stories
cat ralph/prd.json | jq '.stories[] | {id, title, status}'

# Check active story
cat ralph/prd.json | jq '.stories[] | select(.status=="in_progress")'
```

**Story Lifecycle:**
1. **research** - Agent investigates codebase
2. **planning** - Agent designs implementation
3. **implementation** - Agent writes code
4. **validation** - Agent runs tests
5. **completed** - Agent marks done

### Proceeding with Ralph Stories

**Next Story Selection:**
```bash
# Find next pending story
cat ralph/prd.json | jq '.stories[] | select(.status=="pending") | {id, title, priority}' | head -1
```

**Activate Story:**
```bash
# Claude Code will automatically:
# 1. Read story requirements from prd.json
# 2. Use researching-codebase skill
# 3. Use planning skill
# 4. Implement changes
# 5. Run validation
# 6. Update story status
```

**Manual Story Activation:**
```python
# Update ralph/prd.json
{
  "stories": [
    {
      "id": "STORY-XXX",
      "status": "in_progress",  # Changed from "pending"
      "title": "...",
      "acceptance_criteria": [...]
    }
  ]
}
```

**Story Completion:**
```bash
# After implementing story
python scripts/validate_story.py STORY-XXX

# Updates prd.json:
# - Sets status: "completed"
# - Records completion_date
# - Adds validation_results
```

### Ralph Best Practices

**Do:**
- ✅ One story at a time
- ✅ Run tests after each story
- ✅ Update prd.json with learnings
- ✅ Use compound engineering (research → plan → implement)
- ✅ Validate acceptance criteria

**Don't:**
- ❌ Skip story dependencies
- ❌ Implement without planning
- ❌ Break existing tests
- ❌ Over-engineer solutions

### Ralph Story Template

```json
{
  "id": "STORY-XXX",
  "title": "Short descriptive title",
  "status": "pending",
  "priority": "high|medium|low",
  "dependencies": ["STORY-YYY"],
  "description": "Detailed requirement",
  "acceptance_criteria": [
    "Given X, When Y, Then Z"
  ],
  "technical_notes": [
    "Implementation hints"
  ],
  "completion_date": null,
  "validation_results": null
}
```

---

## Architecture

### Code Organization Pattern

**Separation of Concerns (following debate_judge template):**

| File | Responsibility | Description |
|------|----------------|-------------|
| `agent.py` | **"What the agent does"** (domain) | AgentCard definition, GreenAgent class, evaluation logic, domain models |
| `executor.py` | **"How to invoke it"** (protocol adapter) | Thin wrapper: A2A params → Agent.run() → A2A response, task lifecycle only |
| `server.py` | **"How to expose it"** (transport) | HTTP server setup, request routing, entry point |
| `messenger.py` | **"How agents talk"** (communication) | A2A messaging utilities, inter-agent communication |

**Project Structure:**
```
src/bulletproof_green/
├── agent.py           # Domain (what it does)
├── executor.py        # Protocol adapter (how to invoke)
├── server.py          # Transport (how to expose)
├── messenger.py       # Communication (A2A messaging for all agents)
├── models.py          # Pydantic models (all data validation)
├── settings.py        # Configuration
├── arena/             # Arena mode (multi-turn refinement)
│   └── executor.py    #   - Arena orchestration (uses messenger.py)
└── evals/             # Evaluation domain
    ├── evaluator.py   #   - Rule-based evaluation
    ├── scorer.py      #   - AgentBeats scoring
    └── llm_judge.py   #   - LLM hybrid scoring
```

**Benefits:**
- ✅ **KISS**: Clear separation - domain vs protocol vs transport
- ✅ **DRY**: Agent class usable standalone without A2A overhead
- ✅ **User Success**: Testable domain logic independent of server
- ✅ **Matches Template**: Same structure as debate_judge reference implementation

---

## Additional Documentation

### AgentBeats Platform
- [Submission Guide](AgentBeats/SUBMISSION-GUIDE.md) - Requirements, checklist, deployment
- [Resources](AgentBeats/RESOURCES.md) - External links

### Project Documentation
- [Abstract](AgentBeats/ABSTRACT.md) - 500-word benchmark description
- [Green Agent PRD](GreenAgent-PRD.md) - Phase 1 requirements (benchmark)
- [Purple Agent PRD](PurpleAgent-PRD.md) - Phase 2 requirements (competition)
- [Green Agent User Story](GreenAgent-UserStory.md) - Phase 1 user stories
- [Purple Agent User Story](PurpleAgent-UserStory.md) - Phase 2 user stories
- [Gap Analysis](GAP-ANALYSIS.md) - Current state analysis

### Best Practices
- [Testing Strategy](best-practices/testing-strategy.md) - Comprehensive testing guide
- [Python Best Practices](best-practices/python-best-practices.md) - Code standards

### Project Root
- [README.md](../README.md) - Project overview and quick start
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Contribution guidelines

---

## Quick Commands Reference

```bash
# Configuration
cp .env.example .env
python -m bulletproof_green.settings  # Debug config

# Testing
pytest                                 # Unit tests
bash scripts/test_e2e.sh              # E2E tests
bash scripts/test_comprehensive.sh    # Full validation

# Development
python -m bulletproof_green.server    # Start Green agent
python -m bulletproof_purple.server   # Start Purple agent
docker-compose up -d                  # Start both agents

# Deployment
bash scripts/build.sh                 # Build Docker images
bash scripts/push.sh                  # Push to GHCR

# Validation
python src/validate_benchmark.py      # Schema validation
make validate                         # Full project validation
```

---

## Support & Resources

- **Discord:** [discord.gg/uqZUta3MYa](https://discord.gg/uqZUta3MYa)
- **Competition Platform:** [agentbeats.dev](https://agentbeats.dev)
- **Documentation:** [docs.agentbeats.dev](https://docs.agentbeats.dev)
- **Submission Form:** [forms.gle/1C5d8KXny2JBpZhz7](https://forms.gle/1C5d8KXny2JBpZhz7)
