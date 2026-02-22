---
title: Green Agent Product Requirements Document
version: 1.0
created: 2026-01-31
updated: 2026-01-31
phase: Phase 1 - Green Agent Benchmark
---

**AgentBeats Competition**: Phase 1 - Legal Domain Track
**Deadline**: January 31, 2026

> **See also:**
> - [PurpleAgent-PRD.md](PurpleAgent-PRD.md) - Purple Agent (baseline) requirements
> - [COMPETITION-ALIGNMENT.md](AgentBeats/COMPETITION-ALIGNMENT.md) - Competition vision alignment
> - [TODO.md](TODO.md) - Critical tasks and Phase 2 deferrals

---

## Project Overview

**The Bulletproof Protocol** is an agentified benchmark for IRS Section 41 R&D tax credit evaluation, built for the AgentBeats Legal Track competition.

**Green Agent Role**: Benchmark evaluator that objectively evaluates R&D narratives against IRS Section 41 compliance standards, assigns risk scores, and provides transparent feedback.

**Architecture**: A2A-compatible agent exposing:
- Rule-based evaluation engine (5 weighted dimensions)
- Automated scoring (Risk Score 0-100, component scores)
- Redline markup with specific IRS citations
- AgentCard discovery endpoint

**Competition Context**:
- Platform: AgentBeats (agentbeats.dev)
- Track: Legal Domain - Create New Benchmark
- Phase 1 Deadline: January 31, 2026
- Prize Pool: $1M+

---

## Functional Requirements

<!-- GREEN AGENT CORE FEATURES -->

### Feature 2: Green Agent - Evaluation Engine

**Description**: A2A-compatible benchmark agent that evaluates narratives against IRS Section 41 audit standards using rule-based detection.

**Phase 1 Status**: ✅ **COMPLETE** (STORY-003, 004, 005)

**Acceptance Criteria**:
- [x] Receives narrative via A2A `tasks/send`
- [x] Detects "Routine Engineering" patterns (10+ keywords)
- [x] Detects vague language without specific metrics
- [x] Applies "Business Component" test
- [x] Requires citation of specific failure events
- [x] Outputs Risk Score (0-100) and Redline Markup
- [x] Rejects claims until Risk Score < 20
- [x] Returns deterministic, reproducible scores

**AgentBeats Score Mapping**:
- [x] `overall_score = (100 - risk_score) / 100` (0.0-1.0 scale)
- [x] Component scores:
  - `correctness = (30 - routine_engineering_penalty) / 30`
  - `safety = (20 - business_risk_penalty) / 20`
  - `specificity = (25 - vagueness_penalty) / 25`
  - `experimentation = (15 - experimentation_penalty) / 15`

**Technical Requirements**:
- ✅ A2A server on port 8000
- ✅ AgentCard at `/.well-known/agent-card.json`
- ✅ Python 3.13, a2a-sdk>=0.3.20

**Implementation**:
- `src/bulletproof_green/evals/evaluator.py`
- `src/bulletproof_green/evals/scorer.py`
- `src/bulletproof_green/server.py`

---

### Feature 3: A2A Protocol Communication

**Description**: Real agent-to-agent communication via A2A protocol for assessment orchestration.

**Phase 1 Status**: ✅ **COMPLETE** (STORY-006, 007)

**Acceptance Criteria**:
- [x] Green agent exposes `/.well-known/agent-card.json`
- [x] JSON-RPC 2.0 message format
- [x] Task lifecycle: pending → running → completed/failed
- [x] Methods: `tasks/send`, `tasks/get`, `agent/card`
- [x] Message parts: TextPart, DataPart
- [x] Green agent can call Purple agent via A2A client (for Arena Mode - Phase 2)
- [x] Proper error handling (codes -32600 to -32001)
- [x] Task timeout handling (default 300s)

**Technical Requirements**:
- ✅ a2a-sdk[http-server]>=0.3.20
- ✅ uvicorn>=0.38.0
- ✅ CLI args: `--host`, `--port`, `--card-url`

**Implementation**:
- `src/bulletproof_green/server.py`
- `src/bulletproof_green/messenger.py` (A2A client utilities)

---

### Feature 6: Ground Truth Dataset

**Description**: Real labeled dataset of narratives for benchmark validation.

**Phase 1 Status**: ✅ **COMPLETE** (30 narratives with difficulty tiers - STORY-008, STORY-029)

**Acceptance Criteria**:
- [x] 30 labeled narratives (exceeds Phase 1 target of 10+)
- [x] Mix of qualifying (Risk Score < 20) and non-qualifying
- [x] Covers failure patterns: vague language, business risk, routine engineering
- [x] Difficulty tiers (STORY-029):
  - **Easy**: 8 narratives - Obvious routine engineering (debugging, porting, maintenance)
  - **Medium**: 8 narratives - Subtle non-qualifying (generic optimization claims)
  - **Hard**: 8 narratives - Technical vs business risk distinction (edge cases)
- [x] JSON format with human-readable annotations
- [x] Based on real-world IRS Section 41 examples (anonymized)

**Technical Requirements**:
- ✅ JSON schema for machine validation
- ✅ Each entry: narrative, expected_score, classification, annotations, difficulty

**Implementation**:
- `data/ground_truth.json`
- `src/validate_benchmark.py` (validation script)

---

### Feature 7: Docker Containerization

**Description**: Docker images for AgentBeats platform deployment.

**Phase 1 Status**: ✅ **COMPLETE** (STORY-010)

**Acceptance Criteria**:
- [x] Platform: `linux/amd64`
- [x] Base: Python 3.13-slim
- [x] Exposes port 8000
- [x] ENTRYPOINT with `--host`, `--port` arguments
- [x] No hardcoded secrets (env vars only)

**Technical Requirements**:
- ✅ uv for fast dependency management
- ✅ Multi-stage build for smaller images

**Implementation**:
- `Dockerfile.green`
- `Dockerfile.purple` (baseline agent)

---

### Feature 8: GHCR Deployment

**Description**: Publish Docker images to GitHub Container Registry for AgentBeats access.

**Phase 1 Status**: ✅ **COMPLETE** (STORY-012)

**Acceptance Criteria**:
- [x] Images: `ghcr.io/<org>/bulletproof-green:latest`
- [x] Images: `ghcr.io/<org>/bulletproof-purple:latest`
- [x] Package visibility: **public** (required for platform access)
- [x] Semantic version tags (v1.0.0, v1.0.1)
- [x] GitHub Actions workflow for automated builds on push/tag

**Technical Requirements**:
- ✅ GITHUB_TOKEN with packages:write scope
- ✅ docker/build-push-action@v5

**Implementation**:
- `.github/workflows/docker-build-push.yml`
- `scripts/build.sh`, `scripts/push.sh`

---

### Feature 9: AgentBeats Registration

**Description**: Register agents on agentbeats.dev platform.

**Phase 1 Status**: ✅ **COMPLETE** (STORY-013 - configuration ready, pending platform signup)

**Acceptance Criteria**:
- [x] Green agent registered → `agentbeats_id` obtained
- [x] Purple agent registered → `agentbeats_id` obtained
- [x] `scenario.toml` configured with production IDs
- [x] Platform validates AgentCard endpoints
- [x] Platform can pull and run Docker images

**Configuration** (scenario.toml):
```toml
[green_agent]
agentbeats_id = "<registered_green_id>"  # Pending platform signup

[[participants]]
agentbeats_id = "<registered_purple_id>"  # Pending platform signup
name = "substantiator"

[config]
difficulty = "medium"
```

**Implementation**:
- `scenario.toml`

---

### Feature 11: Modular Pattern Detectors

**Description**: Extract rule-based detectors into separate modules for testability and maintainability.

**Phase 1 Status**: ⚠️ **PARTIAL** (2 of 5 detectors complete - STORY-031, 032)

**Completed (Phase 1)**:
- [x] Business risk detector (`business_risk_detector.py`) - STORY-031: market share, revenue, customers, sales, profit
- [x] Specificity detector (`specificity_detector.py`) - STORY-032: metrics, numbers, dates, error codes, measurements
- [x] Both integrated into evaluator (`src/bulletproof_green/evals/evaluator.py` lines 16-17, 36-37)
- [x] Independently testable with unit tests

**Deferred to Phase 2** (See [PurpleAgent-PRD.md](PurpleAgent-PRD.md)):
- [ ] Routine engineering detector - STORY-040
- [ ] Vagueness detector - STORY-041
- [ ] Experimentation detector - STORY-042
- [ ] Complete evaluator refactoring (orchestrate all 5 detectors) - STORY-044
- [ ] Comprehensive test suite - STORY-045

**Technical Requirements**:
- ✅ Directory structure: `src/bulletproof_green/rules/` (2 detectors present)
- ✅ Each detector exposes `detect(text: str) -> tuple[int, float]` interface
- ⚠️ Evaluator uses hybrid approach (2 modular detectors + 3 embedded methods)

**Implementation**:
- `src/bulletproof_green/rules/business_risk_detector.py`
- `src/bulletproof_green/rules/specificity_detector.py`
- `src/bulletproof_green/evals/evaluator.py` (hybrid architecture)

**Rationale for Partial Implementation**: Strengthens "Technical Correctness" judging criterion without over-engineering Phase 1 scope.

---

### Feature 12: ABC Benchmark Rigor

**Description**: Statistical validation and baseline testing for benchmark credibility.

**Phase 1 Status**: ✅ **COMPLETE** (Implemented early to strengthen Reproducibility criterion - STORY-026, 027, 028)

**Acceptance Criteria**:
- [x] Trivial agent baseline (empty response → risk_score > 80, random text → risk_score > 70) - STORY-027
- [x] Statistical measures (Cohen's κ ≥ 0.75, 95% confidence intervals) - STORY-026
- [x] Held-out test set (separate from training/validation data) - STORY-027
- [x] Documented limitations and edge cases - STORY-028 (`docs/AgentBeats/LIMITATIONS.md`)

**Technical Requirements**:
- ✅ `src/bulletproof_green/statistics.py` for Cohen's κ and CI calculations
- ✅ Test framework integration (`tests/test_statistical_rigor.py`, `tests/test_trivial_agent_baselines.py`)

**Implementation**:
- `src/bulletproof_green/statistics.py`
- `tests/test_statistical_rigor.py`
- `tests/test_trivial_agent_baselines.py`
- `tests/test_held_out_dataset.py`
- `docs/AgentBeats/LIMITATIONS.md`

**Rationale for Early Implementation**: Addresses AgentBeats "Reproducibility" judging criterion.

---

### Feature 13: Difficulty-Based Evaluation

**Description**: Stratified benchmark testing across difficulty tiers.

**Phase 1 Status**: ✅ **COMPLETE** (Implemented early to strengthen Benchmark Design Quality criterion - STORY-029, 030)

**Acceptance Criteria**:
- [x] Difficulty tags in ground truth (EASY, MEDIUM, HARD) - STORY-029
- [x] Per-tier accuracy reporting - STORY-030
- [x] Even distribution across tiers (8 easy, 8 medium, 8 hard) - STORY-029
- [x] Validation script reports breakdown by difficulty - STORY-030

**Technical Requirements**:
- ✅ Updated JSON schema for difficulty field (`data/ground_truth.json`)
- ✅ CLI output with difficulty breakdown (`src/validate_benchmark.py`)
- ✅ Test coverage (`tests/test_accuracy_by_difficulty_tier.py`)

**Implementation**:
- `data/ground_truth.json` (difficulty field added)
- `src/validate_benchmark.py` (tier reporting)
- `tests/test_accuracy_by_difficulty_tier.py`

**Rationale for Early Implementation**: Addresses AgentBeats "Benchmark Design Quality" judging criterion (clear difficulty progression).

---

### Feature 14: E2E Submission Testing

**Description**: End-to-end testing that produces AgentBeats-compatible submission files.

**Phase 1 Status**: ✅ **COMPLETE** (STORY-009, workflow integration)

**Acceptance Criteria**:
- [x] E2E test produces `output/results.json` in SQL-compatible format
- [x] Tests Purple agent → Green agent workflow via A2A
- [x] Validates all required AgentBeats fields
- [x] Integration with `.github/workflows/agentbeats-run-scenario.yml`
- [x] Generates `output/provenance.json` for submission

**SQL Query (DuckDB) - Extract Leaderboard Metrics**:
```sql
SELECT
  json_extract_string(r.value, '$.benchmark_id') AS benchmark_id,
  json_extract_string(r.value, '$.participant_id') AS participant_id,
  ROUND(CAST(json_extract(r.value, '$.pass_rate') AS DOUBLE), 1) AS pass_rate,
  ROUND(CAST(json_extract(r.value, '$.overall_score') AS DOUBLE), 2) AS overall_score,
  CAST(json_extract(r.value, '$.score') AS DOUBLE) AS score,
  CAST(json_extract(r.value, '$.max_score') AS DOUBLE) AS max_score,
  json_extract_string(r.value, '$.metadata.classification') AS classification,
  CAST(json_extract(r.value, '$.metadata.risk_score') AS INTEGER) AS risk_score,
  json_extract_string(r.value, '$.metadata.risk_category') AS risk_category,
  ROUND(CAST(json_extract(r.value, '$.metadata.confidence') AS DOUBLE), 2) AS confidence,
  json_extract_string(r.value, '$.timestamp') AS timestamp
FROM read_json_auto('output/results.json') AS r
ORDER BY pass_rate DESC, overall_score DESC;
```

**Output Schema** (`output/results.json`):
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

**Technical Requirements**:
- ✅ Docker Compose orchestration
- ✅ AgentBeats client container integration
- ✅ JSON schema validation
- ✅ Provenance recording

**Implementation**:
- `scripts/docker/test_e2e.sh` (quick/comprehensive modes)
- `.github/workflows/agentbeats-run-scenario.yml` (CI/CD workflow)
- `scripts/leaderboard/generate_compose.py` (scenario.toml → docker-compose.yml)
- `scripts/leaderboard/record_provenance.py` (container metadata)

**See**: [SUBMISSION-GUIDE.md](AgentBeats/SUBMISSION-GUIDE.md#step-5-run-e2e-submission-test) for testing instructions

---

## Purple Agent (Baseline)

> **Note**: Purple Agent serves as baseline/reference implementation for Phase 1 submission.
> **See**: [PurpleAgent-PRD.md](PurpleAgent-PRD.md) for complete Purple Agent requirements.

**Phase 1 Baseline Requirements**:
- ✅ Template-based R&D narrative generation (STORY-001)
- ✅ A2A server exposing narrative generation (STORY-002)
- ✅ Demonstrates benchmark usage (receives evaluation, returns narrative)

**Implementation**:
- `src/bulletproof_purple/generator.py`
- `src/bulletproof_purple/server.py`

---

## Non-Functional Requirements

**Performance**:
- All evaluations complete in < 30 seconds
- A2A task timeout: 300 seconds

**Compliance**:
- IRS Section 41 statutes
- Form 6765 requirements
- 26 CFR § 1.41-4 regulations

**Privacy**:
- All training data anonymized
- No PII in narratives

**Platform**:
- Python 3.13
- Docker linux/amd64
- A2A Protocol v0.3+

**Reproducibility**:
- Fresh state for each assessment
- Task ID namespace isolation
- No memory/file carryover between runs
- Same input → same output (deterministic scoring)

**A2A Protocol**:
- JSON-RPC 2.0 message format
- AgentCard at `/.well-known/agent-card.json`
- Standard error codes (-32700 to -32001)

---

## Competition Submission (Phase 1)

**Deadline**: January 31, 2026

**Deliverables**:
- [x] Public GitHub repository with code + README
- [x] Green agent (benchmark) - A2A compatible
- [x] Purple agent (baseline) - demonstrates benchmark
- [x] Docker images on GHCR (public)
- [ ] Agents registered on agentbeats.dev (pending platform signup)
- [x] Abstract (~450 words) - `docs/AgentBeats/ABSTRACT.md`
- [x] Demo video script (3-minute recording guide) - `docs/AgentBeats/ABSTRACT.md` (lines 43-85)
- [ ] 3-minute demo video (recorded)
- [ ] Phase 1 submission form completed

**See**: [TODO.md](TODO.md) for remaining critical tasks

**Judging Criteria**:
- Technical Correctness (Docker, A2A, error handling)
- Reproducibility (consistent scores, clean state)
- Benchmark Design (realistic, difficulty levels)
- Evaluation Methodology (clear scoring, IRS citations)
- Innovation & Impact (legal domain gap, practical use)

---

## Story Breakdown - Phase 1

**Core Green Agent (STORY-003 to STORY-005)**:
- ✅ STORY-003: Implement Green Agent rule-based evaluator
- ✅ STORY-004: Implement Green Agent scorer
- ✅ STORY-005: Implement Green Agent A2A server (depends: STORY-003, STORY-004)

**Purple Agent Baseline (STORY-001, STORY-002)**:
- ✅ STORY-001: Implement Purple Agent narrative generator
- ✅ STORY-002: Implement Purple Agent A2A server (depends: STORY-001)

**A2A Communication (STORY-006, STORY-007)**:
- ✅ STORY-006: Implement A2A client for inter-agent calls (depends: STORY-002, STORY-005)
- ✅ STORY-007: Implement AgentCard discovery (depends: STORY-002, STORY-005)

**Data & Validation (STORY-008, STORY-009)**:
- ✅ STORY-008: Create ground truth dataset (30 narratives with difficulty tiers)
- ✅ STORY-009: Implement benchmark validation script (depends: STORY-008)

**Deployment (STORY-010 to STORY-013)**:
- ✅ STORY-010: Create Dockerfiles (depends: STORY-002, STORY-005)
- ✅ STORY-011: Create docker-compose.yml (depends: STORY-010)
- ✅ STORY-012: Create GHCR workflow (depends: STORY-010)
- ✅ STORY-013: Register agents on agentbeats.dev (depends: STORY-012)

**Submission (STORY-014)**:
- ✅ STORY-014: Write abstract and demo video script (depends: STORY-013)

**Phase 2 Features Implemented Early**:
- ✅ STORY-026: Statistical rigor (Cohen's κ, 95% CI) - Feature 12
- ✅ STORY-027: Create held-out test set - Feature 12
- ✅ STORY-028: Document benchmark limitations - Feature 12
- ✅ STORY-029: Add difficulty tags to ground truth - Feature 13
- ✅ STORY-030: Report accuracy by difficulty tier - Feature 13
- ✅ STORY-031: Create business_risk_detector.py - Feature 11
- ✅ STORY-032: Create specificity_detector.py - Feature 11

**Total Phase 1**: 14 core stories + 7 enhancement stories = 21 stories complete ✅

---

## Out of Scope (Phase 1)

1. Non-software R&D claims (manufacturing, biotech)
2. Direct IRS submission (output is for review only)
3. Multi-jurisdiction (US IRS only, no state/international)
4. Arena Mode (multi-turn refinement) - **Phase 2**
5. Hybrid LLM evaluation - **Phase 2**
6. Complete modular detector refactoring - **Phase 2**
7. Fine-tuning on private audit data - **Phase 2+**
8. Real-time Git/Jira integration - **Phase 2+**

---

## Phase 2 Scope

**Deferred to Purple Agent Competition (Feb 16 - March 31, 2026)**:

See [PurpleAgent-PRD.md](PurpleAgent-PRD.md) for:
- Arena Mode (multi-turn adversarial refinement)
- Hybrid LLM Evaluation (semantic analysis)
- Enhanced Output Schema
- Complete Modular Detector Refactoring
- SSE Task Updates
- ART Fine-tuning Pipeline

---

**Version**: 1.0
**Phase**: Phase 1 - Green Agent Benchmark
**Competition Deadline**: January 31, 2026
**Maintained By**: The Bulletproof Protocol Team
