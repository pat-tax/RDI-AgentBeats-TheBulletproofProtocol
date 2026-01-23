---
title: Product Requirements Document
version: 1.0
applies-to: Agents and humans
purpose: Functional requirements and acceptance criteria for all user stories
---

# Product Requirements Document: The Bulletproof Protocol

## Project Overview

**Project Name**: The Bulletproof Protocol (Adversarial R&D Tax Agent)

**Description**: A recursive adversarial agent system that treats R&D tax credit substantiation as a Generative Adversarial Network (GAN) of text. Two opposing agents—Agent A (The R&D Substantiator) and Agent B (The Virtual Examiner)—engage in recursive debate to generate audit-proof IRS Section 41 compliant narratives.

**Problem Statement**: Current LLMs are too agreeable to act as effective legal defense in tax compliance. Traditional approaches to R&D tax credit claims lack adversarial validation, resulting in 4-hour manual drafting processes, high audit risk, and missed opportunities for startups to access non-dilutive capital.

**Goals**:
- Reduce human drafting time from 4 hours to 5 minutes (90%+ efficiency gain)
- Generate IRS Section 41 compliant narratives with Risk Score < 20
- Accurately distinguish business risk from technical risk
- Deliver working demo for AgentBeats competition

**Target Users**:
- Tax professionals at Silicon Valley Tax
- Startup founders/CFOs seeking R&D tax credits
- IP attorneys/technical writers

**User Stories Reference**: See `docs/UserStory.md` for detailed user stories and value proposition.

---

## Functional Requirements

### Core Features

#### Feature 1: Purple Agent - Reference Implementation (Baseline Narrative Generator)

**Description**: A simple R&D narrative generator that serves as a reference implementation for testing the Green Agent benchmark. Generates sample IRS Section 41 narratives with varying quality levels to demonstrate benchmark capabilities.

**User Stories**:
- As a benchmark developer, I want a baseline purple agent that generates test narratives, so that I can validate the green agent's evaluation capabilities.

**Acceptance Criteria**:
- [x] Exposes A2A-compatible HTTP server with AgentCard discovery
- [x] Generates 300-500 word R&D narratives in IRS Section 41 format
- [x] Includes at least 3 narrative templates (qualifying, non-qualifying, edge cases)
- [x] Returns structured artifacts with narrative text
- [x] Handles async task execution via A2A protocol

**Technical Requirements**:
- A2A protocol implementation (a2a-sdk)
- Template-based narrative generation
- FastAPI/Starlette HTTP server
- Docker containerization (linux/amd64)

**Files Implemented**:
- `src/bulletproof_purple/server.py` - A2A server entrypoint
- `src/bulletproof_purple/executor.py` - AgentExecutor implementation
- `src/bulletproof_purple/generator.py` - Narrative generation logic
- `src/bulletproof_purple/templates.py` - IRS Section 41 narrative templates
- `src/bulletproof_purple/__init__.py` - Package initialization
- `Dockerfile.purple` - Container build specification
- `tests/test_purple_agent_server.py` - Server tests
- `tests/test_purple_agent_executor.py` - Executor tests

---

#### Feature 2: Green Agent - IRS Section 41 Benchmark (The Actual Submission)

**Description**: An AgentBeats benchmark that evaluates R&D tax credit narratives for IRS Section 41 compliance. Detects routine engineering, vague language, missing experimentation evidence. Outputs Risk Score (0-100) and classification (QUALIFYING/NON_QUALIFYING).

**User Stories**:
- As a benchmark user, I want to submit purple agents that generate R&D narratives and receive objective IRS Section 41 compliance scores, so that I can compare narrative quality across different implementations.

**Acceptance Criteria**:
- [x] Exposes A2A-compatible HTTP server with AgentCard discovery
- [x] Evaluates narratives using IRS Section 41 audit standards
- [x] Detects routine engineering patterns (debugging, maintenance, production issues)
- [x] Flags vague language without numeric substantiation
- [x] Verifies process of experimentation documentation (uncertainty, alternatives, failures)
- [x] Outputs Risk Score (0-100) with weighted component scores
- [x] Returns classification: QUALIFYING if risk_score < 20, else NON_QUALIFYING
- [x] Provides structured JSON artifact with evaluation results

**Technical Requirements**:
- A2A protocol implementation (a2a-sdk)
- Rule-based evaluation engine with IRS Section 41 alignment
- Modular detector architecture (routine engineering, vagueness, experimentation)
- Weighted risk scoring algorithm (30% + 25% + 20% + 15% + 10%)
- Docker containerization (linux/amd64)

**Files Implemented**:
- `src/bulletproof_green/server.py` - A2A server entrypoint
- `src/bulletproof_green/executor.py` - AgentExecutor implementation
- `src/bulletproof_green/evaluator.py` - Narrative evaluation orchestrator
- `src/bulletproof_green/rules/routine_engineering.py` - Routine engineering detector (30% weight)
- `src/bulletproof_green/rules/vagueness_detector.py` - Vagueness detection (25% weight)
- `src/bulletproof_green/rules/experimentation_checker.py` - Experimentation verification (15% weight)
- `src/bulletproof_green/scorer.py` - Weighted risk scoring (0-100)
- `src/bulletproof_green/__init__.py` - Package initialization
- `Dockerfile.green` - Container build specification
- `tests/test_green_agent_server.py` - Server tests
- `tests/test_green_agent_executor.py` - Executor tests
- `tests/test_routine_engineering.py` - Routine detector tests
- `tests/test_vagueness_detector.py` - Vagueness detector tests
- `tests/test_experimentation_checker.py` - Experimentation tests
- `tests/test_scorer.py` - Risk scorer tests

**Component Weights**:
- Routine Engineering: 30% (max 30 points)
- Vagueness: 25% (max 25 points)
- Business Risk: 20% (max 20 points) - *pending implementation*
- Experimentation: 15% (max 15 points)
- Specificity: 10% (max 10 points) - *pending implementation*

---

## Out of Scope (Future Enhancements)

The following features are **NOT required for AgentBeats Phase 1 benchmark submission** and are deferred to future versions:

### Feature 3: Recursive Adversarial Loop (Future Enhancement)
- **Status**: Out of scope for Phase 1
- **Rationale**: AgentBeats requires a benchmark (evaluator), not a full product with iterative refinement
- **Future Use**: Production deployment for actual tax credit claim generation

### Feature 4: SVT Integration & Training Data Pipeline (Future Enhancement)
- **Status**: Out of scope for Phase 1
- **Rationale**: Benchmark uses rule-based evaluation, not ML requiring training data
- **Future Use**: Production deployment with historical audit data fine-tuning

### Feature 5: CLI Interface & Workflow Management (Future Enhancement)
- **Status**: Out of scope for Phase 1
- **Rationale**: AgentBeats agents interact via A2A protocol, not CLI
- **Future Use**: Production deployment for tax professionals

---

## Non-Functional Requirements

### Performance
- **Efficiency**: Reduce human drafting time from 4 hours to 5 minutes (90%+ efficiency gain)
- **Convergence**: Adversarial loop completes in ≤ 10 iterations for typical projects
- **Responsiveness**: CLI operations provide feedback within 2 seconds (except long-running tasks which show progress)

### Compliance & Accuracy

**Agent B (Green Agent) Evaluation Metrics**:

| Metric | Target | Validation Method | Benchmark |
|--------|--------|-------------------|-----------|
| **Classification Accuracy** | ≥ 70% | 20-case labeled test set | IRS AI: 61.2% ([TIGTA 2025](https://www.tigta.gov/reports/audit/irs-could-leverage-examination-results-artificial-intelligence-examination-case)) |
| **F1 Score** | ≥ 0.72 | Precision/Recall harmonic mean | IRS AI: 0.42 |
| **Precision** | ≥ 75% | TP / (TP + FP) | Minimize false approvals |
| **Recall** | ≥ 70% | TP / (TP + FN) | Catch non-qualifying claims |
| **Inter-Rater Reliability** | κ ≥ 0.75 | Cohen's kappa vs 2 tax professionals | Substantial agreement |
| **Test-Retest Reliability** | r ≥ 0.95 | Same narrative, 2 evaluations | Reproducibility |

**Risk Score Calibration**:
- **0-20**: LOW RISK (audit-proof, meets all criteria)
- **21-40**: MODERATE (minor issues, likely passes)
- **41-60**: HIGH (significant gaps, needs revision)
- **61-80**: VERY HIGH (multiple disqualifying patterns)
- **81-100**: CRITICAL (obvious non-qualifying, immediate rejection)

**Component Detection Rates** (Diagnostic Metrics):
- Routine Engineering: ≥ 90% detection
- Vagueness: ≥ 80% detection
- Business Risk: ≥ 85% detection
- Missing Experimentation: ≥ 75% detection
- Lack of Specificity: ≥ 70% detection

**IRS Section 41 Adherence**: All evaluation rules cite specific IRS statutes (Section 41(d), 26 CFR § 1.41-4)

**Ground Truth Dataset**: 20 labeled narratives (10 qualifying, 10 non-qualifying) validated by 3 tax professionals

**See**: `docs/Green-Agent-Metrics-Specification.md` for complete metrics framework

### Security & Privacy
- **Data Anonymization**: All SVT training data must be anonymized (PII redacted) before processing
- **Confidentiality**: No client-specific information exposed in logs or outputs
- **Access Control**: Training data directory restricted to authorized users only

### Code Quality
- **Validation**: All code must pass `make validate` (ruff, pyright, pytest)
- **Principles**: Follow KISS, DRY, YAGNI principles per project guidelines
- **Test Coverage**: ≥ 80% test coverage for all modules
- **Documentation**: Docstrings for all public APIs, README with usage examples

### Usability
- **Human-in-the-Loop**: Final output includes 5-minute human review by SVT Partner
- **Audit Trail**: Complete version history (all drafts, critiques, scores) for transparency
- **Error Messages**: Clear, actionable error messages for common failure modes

### Platform Support
- **Python 3.13**: Implementation must be compatible with Python 3.13 environment
- **Cross-Platform**: CLI works on Linux, macOS, Windows (via bash/zsh/powershell)
- **Dependencies**: Minimize external dependencies, prefer stdlib where possible

---

## AgentBeats Competition Requirements

### Competition Track: Legal Domain Agent Benchmark

**Track**: Legal Track (agentbeats.org)
**Submission Type**: Agentified Agent Benchmark
**Role**: Green Agent = Benchmark (judges purple agents), Purple Agent = Reference Implementation (demonstrates benchmark usage)

**Judging Environment Architecture**:
- **1 Green Agent** (this project's benchmark) evaluates **N Purple Agents** (competitors)
- Leaderboard repo GitHub Action spins up judging environment using `scenario.toml`
- All agents pulled from GHCR (public images)
- Results sent to agentbeats.dev as structured JSON

### A2A Protocol Compliance

Both Green (Examiner/Benchmark) and Purple (Substantiator/Reference) agents must implement A2A protocol:

- **AgentCard Discovery**: Expose `/.well-known/agent-card.json` with name, description, version, capabilities
- **Task Execution**: Handle `task/send` requests, return `task/result` with artifacts
- **Streaming Updates**: Emit progress updates via SSE during long-running evaluations
- **Error Handling**: Return structured errors (4xx/5xx) with actionable messages

### Infrastructure Requirements

| Requirement | Specification |
|-------------|---------------|
| **Docker Platform** | `linux/amd64` (required by AgentBeats) |
| **Container Registry** | GHCR (`ghcr.io/{username}/{agent-name}:latest`) |
| **Visibility** | Public (required for AgentBeats to pull images) |
| **Configuration** | `scenario.toml` with agent IDs and environment variables |
| **Local Testing** | `docker-compose.yml` for end-to-end validation |

### Agent Registration Process

**Step 1: Register agents on agentbeats.dev**
1. Create account at agentbeats.dev
2. Register Green Agent (Benchmark) → receive `agentbeats_id` for green agent
3. Register Purple Agent (Reference) → receive `agentbeats_id` for purple agent
4. Save both IDs for scenario.toml configuration

**Step 2: scenario.toml Configuration**

```toml
[green_agent]
agentbeats_id = "green-agent-id-from-agentbeats-dev"  # Production
# For local testing, use: ghcr_url = "ghcr.io/username/bulletproof-green:latest"

[[participants]]
name = "bulletproof-purple-reference"
agentbeats_id = "purple-agent-id-from-agentbeats-dev"  # Production
# For local testing, use: ghcr_url = "ghcr.io/username/bulletproof-purple:latest"
```

**Local Testing vs Production**:
- **Local Testing**: Use `ghcr_url` field with direct GHCR image URLs
- **Production Submission**: Use `agentbeats_id` field with registered agent IDs
- Leaderboard repo accepts both formats

### Submission Deliverables

**Phase 1 (January 31, 2026)**:
- [ ] Register both agents on agentbeats.dev (get agent IDs)
- [ ] Green agent Docker image on GHCR (public, `ghcr.io/{username}/bulletproof-green:latest`)
- [ ] Purple agent Docker image on GHCR (public, `ghcr.io/{username}/bulletproof-purple:latest`)
- [ ] `scenario.toml` with registered `agentbeats_id` for both agents
- [ ] Leaderboard repo fork with updated scenario.toml
- [ ] Abstract.md (≤500 words)
- [ ] README.md with usage instructions
- [ ] Demo video (3-5 minutes)
- [ ] Verify GitHub Action sends valid JSON to agentbeats.dev

### Files Required

| File | Purpose |
|------|---------|
| `Dockerfile.green` | Green agent container build |
| `Dockerfile.purple` | Purple agent container build |
| `docker-compose.yml` | Local testing infrastructure |
| `scenario.toml` | AgentBeats assessment configuration |
| `.github/workflows/docker-publish.yml` | CI/CD to GHCR |

---

## Out of Scope

1. **Non-software R&D claims**: Focus only on software/high-tech R&D. Manufacturing, biotech, pharmaceutical, or other industries are excluded.
2. **Direct IRS submission**: System generates claims for human review but does NOT directly file with IRS. Tax professionals retain final approval and submission control.
3. **Multi-jurisdiction support**: Initially US-only (IRS Section 41). State-level R&D credits (California, New York, etc.) and international R&D tax programs are excluded.
4. **Real-time collaboration**: Single-user workflow initially. Multi-user editing, approval chains, or team collaboration features are not included.
5. **Graphical UI**: CLI-only interface for initial version. Web-based or desktop GUI is out of scope.
6. **Automated payroll integration**: Manual input of personnel/payroll data. Automatic integration with payroll systems (Gusto, ADP) is excluded.

---

## Reference Documentation

The following documents provide detailed research and implementation guidance:

| Document | Purpose |
|----------|---------|
| `docs/AgentBeats/AgentBeats-Research.md` | Competition overview, timeline, Phase 1 requirements, judging criteria |
| `docs/AgentBeats/AgentBeats-Benchmark-Design-Principles.md` | AAA paradigm, task/outcome validity, benchmark quality checklist |
| `docs/AgentBeats/Green-Agent-Metrics-Specification.md` | Detailed metrics framework, validation plan, ground truth dataset spec |
| `docs/AgentBeats/Technical-Implementation-Guide.md` | 9-day implementation roadmap, IRS Section 41 rules, risk scoring algorithm |
| `docs/AgentBeats/Local-Testing-and-Deployment.md` | Docker setup, docker-compose, GHCR deployment, scenario.toml configuration |
| `docs/UserStory.md` | User stories and acceptance criteria |

### Key External Resources

- **A2A Protocol**: [a2a-protocol.org/latest/](https://a2a-protocol.org/latest/)
- **IRS Audit Techniques Guide**: [irs.gov/businesses/research-credit-claims-audit-techniques-guide](https://www.irs.gov/businesses/research-credit-claims-audit-techniques-guide-rccatg-credit-for-increasing-research-activities)
- **IRS AI Baseline (TIGTA 2025)**: [tigta.gov/reports/audit/irs-could-leverage-examination-results-artificial-intelligence-examination-case](https://www.tigta.gov/reports/audit/irs-could-leverage-examination-results-artificial-intelligence-examination-case)
- **AgentBeats Leaderboard Template**: [github.com/RDI-Foundation/agentbeats-leaderboard-template](https://github.com/RDI-Foundation/agentbeats-leaderboard-template)

---

## Notes for Ralph Loop

When using the `generating-prd` skill to convert this PRD to `ralph/docs/prd.json`:

### Story Structure Guidelines

1. **Atomic Stories**: Each feature should be broken into atomic stories implementable in a single context window (100-300 lines)
2. **Story Breakdown (Actual Implementation)** (21 stories total):
   - Feature 1 (Purple Agent) → STORY-001: Purple A2A server, STORY-002: Purple executor, STORY-003: Dockerfile.purple
   - Feature 2 (Green Agent) → STORY-004: Green A2A server, STORY-005: Green executor, STORY-006: Routine engineering detector, STORY-007: Vagueness detector, STORY-008: Experimentation checker, STORY-009: Risk scorer, **STORY-010: Integrate detectors into evaluator**, STORY-011: Dockerfile.green
   - Infrastructure → STORY-012: docker-compose, STORY-013: scenario.toml, STORY-014: GHCR scripts
   - Testing & Validation → STORY-015: Integration tests, STORY-016: Ground truth dataset, STORY-017: Benchmark validation
   - Deployment → STORY-018: GitHub Actions, STORY-019: Registration guide, STORY-020: Abstract, STORY-021: README
3. **Integration Stories**: STORY-010 is critical - it wires the detectors (STORY-006-009) into the evaluator (STORY-005). Without explicit integration stories, components remain orphaned modules that pass unit tests but never get used. See `ralph/docs/LEARNING.md` for lessons learned.
4. **Acceptance Criteria**: Each checkbox becomes testable acceptance criteria in prd.json
5. **Files Implemented**: Actual files match prd.json (not PRD.md expectations)
6. **Dependencies**: Green agent depends on Purple agent for testing; STORY-010 depends on STORY-006, 007, 008, 009

### CRITICAL: AgentBeats Deployment Workflow

**Legal Track Benchmark Submission Process:**

This project is submitting a **benchmark** (green agent) to the Legal Track. The green agent will judge purple agents (including our reference implementation and competitor agents).

**Implementation must follow this exact sequence:**

1. **Purple Agent FIRST** (Reference Implementation):
   - Implement A2A-compatible server (`src/bulletproof_purple/server.py`)
   - Simple narrative generator that demonstrates benchmark usage
   - Create `Dockerfile.purple` (platform: `linux/amd64`)
   - Build and push to GHCR: `ghcr.io/{username}/bulletproof-purple:latest`
   - Make image **PUBLIC** in GHCR settings
   - **WHY**: Green agent (benchmark) needs purple agent to test against. Cannot validate the benchmark without a test subject.

2. **Green Agent SECOND** (The Actual Benchmark):
   - Implement A2A-compatible server (`src/bulletproof_green/server.py`)
   - Implement IRS Section 41 evaluation logic (this is the benchmark's core value)
   - Must produce consistent, reliable judgments of purple agents
   - Create `Dockerfile.green` (platform: `linux/amd64`)
   - Build and push to GHCR: `ghcr.io/{username}/bulletproof-green:latest`
   - Make image **PUBLIC** in GHCR settings
   - **WHY**: This is the deliverable being submitted to AgentBeats

3. **Agent Registration** (agentbeats.dev):
   - Create account at agentbeats.dev
   - Register green agent → get `agentbeats_id`
   - Register purple agent (reference) → get `agentbeats_id`
   - Save both IDs for scenario.toml
   - **WHY**: AgentBeats platform needs to track which agents are benchmarks vs participants

4. **Leaderboard Repo Setup** (The Judging Environment):
   - Clone/fork `github.com/RDI-Foundation/agentbeats-leaderboard-template`
   - Update `scenario.toml`:
     ```toml
     [green_agent]
     agentbeats_id = "your-green-agent-id"  # Production
     # ghcr_url = "ghcr.io/{username}/bulletproof-green:latest"  # Local testing

     [[participants]]
     name = "bulletproof-purple-reference"
     agentbeats_id = "your-purple-agent-id"  # Production
     # ghcr_url = "ghcr.io/{username}/bulletproof-purple:latest"  # Local testing
     ```
   - GitHub Actions in leaderboard repo will:
     - Spin up judging environment: 1 green agent + N purple agents
     - Pull all agents from GHCR based on scenario.toml
     - Run assessment scenarios (green judges all purples)
     - **Send results to agentbeats.dev as structured JSON**
   - **WHY**: This is the actual submission mechanism - leaderboard repo orchestrates the benchmark evaluation

5. **Validation Requirements**:
   - Both agents must expose `/.well-known/agent-card.json` (A2A protocol)
   - Both agents must handle `task/send` requests and return `task/result` with artifacts
   - **Green agent MUST return structured output**: `{risk_score: 0-100, classification: "QUALIFYING"|"NON_QUALIFYING", component_scores: {...}, redline: {...}}`
   - Purple agent must accept prompts and return R&D narratives
   - Scenario.toml must contain valid `agentbeats_id` for production, or `ghcr_url` for local testing
   - Leaderboard GitHub Action must send valid JSON to agentbeats.dev (results endpoint)

### Implementation Priority for prd.json

**MUST-HAVE (P0) - Required for competition submission:**
- [ ] Purple agent A2A server + basic narrative generation
- [ ] Green agent A2A server + IRS Section 41 evaluation
- [ ] `Dockerfile.purple` and `Dockerfile.green` (linux/amd64)
- [ ] `scenario.toml` configuration
- [ ] GHCR deployment scripts
- [ ] `docker-compose.yml` for local testing

**SHOULD-HAVE (P1) - Improves benchmark quality:**
- [ ] Advanced purple agent (adversarial narratives)
- [ ] Ground truth dataset (20 labeled cases)
- [ ] Inter-rater reliability validation
- [ ] GitHub Actions workflow for automated GHCR push

**NICE-TO-HAVE (P2) - Polish:**
- [ ] CLI for local testing
- [ ] SVT fine-tuning integration
- [ ] Recursive adversarial loop

### Testing Checklist for prd.json Stories

**Local Testing Phase** (use `ghcr_url` in scenario.toml):
1. ✅ Local docker-compose runs both agents successfully
2. ✅ `curl http://localhost:8001/.well-known/agent-card.json` returns valid AgentCard
3. ✅ Can send test narrative to purple agent and receive narrative response
4. ✅ Can send narrative to green agent and receive structured judgment (`{risk_score, classification}`)
5. ✅ E2E test runs: purple generates narrative, green evaluates, results saved to `results/local_benchmark.json`
6. ✅ Results JSON contains: `{participant_id, pass_rate, traffic_light_green_pct, n_tasks, risk_scores[]}`
7. ✅ Results are queryable with DuckDB for leaderboard-style analysis
8. ✅ Docker images build for `linux/amd64` platform
9. ✅ Images successfully push to GHCR and are publicly accessible

**Production Testing Phase** (use `agentbeats_id` in scenario.toml):
10. ✅ Both agents registered on agentbeats.dev with valid agent IDs
11. ✅ Scenario.toml updated with production `agentbeats_id` values
12. ✅ Cloned leaderboard repo can pull agents from GHCR using agent IDs
13. ✅ Leaderboard GitHub Action completes successfully
14. ✅ Leaderboard GitHub Action sends valid JSON to agentbeats.dev
15. ✅ Results appear on agentbeats.dev dashboard

**Critical Path**: Purple Agent → Green Agent → GHCR Deployment → Local Testing → Agent Registration → Production Testing → Submission

Keep stories atomic, specific, and testable. **Prioritize Purple Agent → Green Agent → Deployment → Registration** in that order.
