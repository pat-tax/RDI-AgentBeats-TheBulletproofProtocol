---
title: Product Requirements Document
version: 3.0
---

# Product Requirements Document: The Bulletproof Protocol

## Project Overview

The Bulletproof Protocol is an adversarial agent benchmark for IRS Section 41 R&D tax credit evaluation, built for the AgentBeats Legal Track competition.

**Architecture**: Two A2A-compatible agents in an adversarial loop:
- **Purple Agent (R&D Substantiator)**: Generates IRS-compliant narratives from real engineering data
- **Green Agent (Virtual Examiner)**: Evaluates narratives against IRS audit standards, assigns risk scores

**Competition Context**:
- Platform: AgentBeats (agentbeats.dev)
- Track: Legal Domain
- Phase 1 Deadline: January 31, 2026
- Prize Pool: $1M+

---

## Functional Requirements

<!-- PARSER REQUIREMENT: Use exactly "#### Feature N:" format -->

#### Feature 1: Purple Agent - Narrative Generation

**Description**: A2A-compatible agent that generates IRS Section 41 compliant Four-Part Test narratives from real engineering data sources.

**Acceptance Criteria**:
- [ ] Accepts real engineering data (Git commits, technical docs, failure logs)
- [ ] Generates 500-word narrative focused on Process of Experimentation
- [ ] Follows Four-Part Test structure (Hypothesis, Test, Failure, Iteration)
- [ ] Distinguishes technical risk from business risk
- [ ] Outputs structured narrative with technical uncertainty evidence
- [ ] Returns A2A DataPart with narrative content

**Technical Requirements**:
- A2A server on port 8000
- AgentCard at `/.well-known/agent-card.json`
- Python 3.13, a2a-sdk>=0.3.20

---

#### Feature 2: Green Agent - Evaluation Engine

**Description**: A2A-compatible benchmark agent that evaluates narratives against IRS Section 41 audit standards using rule-based detection.

**Acceptance Criteria**:
- [ ] Receives narrative via A2A `tasks/send`
- [ ] Detects "Routine Engineering" patterns (10+ keywords)
- [ ] Detects vague language without specific metrics
- [ ] Applies "Business Component" test
- [ ] Requires citation of specific failure events
- [ ] Outputs Risk Score (0-100) and Redline Markup
- [ ] Rejects claims until Risk Score < 20
- [ ] Returns deterministic, reproducible scores

**AgentBeats Score Mapping**:
- [ ] `overall_score = (100 - risk_score) / 100` (0.0-1.0 scale)
- [ ] Component scores:
  - `correctness = (30 - routine_engineering_penalty) / 30`
  - `safety = (20 - business_risk_penalty) / 20`
  - `specificity = (25 - vagueness_penalty) / 25`
  - `experimentation = (15 - experimentation_penalty) / 15`

**Technical Requirements**:
- A2A server on port 8000
- AgentCard at `/.well-known/agent-card.json`
- Python 3.13, a2a-sdk>=0.3.20

---

#### Feature 3: A2A Protocol Communication

**Description**: Real agent-to-agent communication via A2A protocol for assessment orchestration.

**Acceptance Criteria**:
- [ ] Both agents expose `/.well-known/agent-card.json`
- [ ] JSON-RPC 2.0 message format
- [ ] Task lifecycle: pending → running → completed/failed
- [ ] Methods: `tasks/send`, `tasks/get`, `agent/card`
- [ ] Message parts: TextPart, DataPart
- [ ] Green agent calls Purple agent via A2A client
- [ ] Proper error handling (codes -32600 to -32001)
- [ ] Task timeout handling (default 300s)

**Technical Requirements**:
- a2a-sdk[http-server]>=0.3.20
- uvicorn>=0.38.0
- CLI args: `--host`, `--port`, `--card-url`

---

#### Feature 4: Arena Mode - Adversarial Loop [Phase 2]

**Description**: Multi-turn orchestration where Green Agent iteratively refines Purple Agent narratives via real A2A communication.

**Acceptance Criteria**:
- [ ] Green agent accepts `mode=arena` parameter
- [ ] Calls Purple agent via A2A `tasks/send` for each iteration
- [ ] Purple agent receives critique and regenerates narrative
- [ ] Loop terminates when risk_score < target OR max_iterations reached
- [ ] Returns ArenaResult with full iteration history
- [ ] Configurable: max_iterations (default: 5), target_risk_score (default: 20)

**Technical Requirements**:
- A2A client for inter-agent calls
- Task state tracking per iteration

---

#### Feature 5: Hybrid Evaluation [Phase 2]

**Description**: Combine rule-based and LLM-based evaluation for reproducible scores with semantic understanding.

**Acceptance Criteria**:
- [ ] Rule-based evaluation remains deterministic (primary)
- [ ] LLM-as-Judge provides semantic analysis (secondary)
- [ ] Combined: final_score = α*rule_score + β*llm_score
- [ ] Fallback to rule-only if LLM unavailable
- [ ] LLM uses temperature=0 for consistency

**Technical Requirements**:
- OpenAI API (GPT-4) or equivalent
- Graceful degradation

---

#### Feature 6: Ground Truth Dataset

**Description**: Real labeled dataset of narratives for benchmark validation.

**Acceptance Criteria**:
- [ ] 10+ labeled narratives (Phase 1), 20+ (Phase 2)
- [ ] Mix of qualifying (Risk Score < 20) and non-qualifying
- [ ] Covers failure patterns: vague language, business risk, routine engineering
- [ ] Difficulty tiers:
  - **Easy**: Obvious routine engineering (debugging, porting, maintenance)
  - **Medium**: Subtle non-qualifying (generic optimization claims)
  - **Hard**: Technical vs business risk distinction
- [ ] JSON format with human-readable annotations
- [ ] Based on real-world IRS Section 41 examples (anonymized)

**Technical Requirements**:
- JSON schema for machine validation
- Each entry: narrative, expected_score, classification, annotations

---

#### Feature 7: Docker Containerization

**Description**: Docker images for AgentBeats platform deployment.

**Acceptance Criteria**:
- [ ] Platform: `linux/amd64`
- [ ] Base: Python 3.13-slim
- [ ] Exposes port 8000
- [ ] ENTRYPOINT with `--host`, `--port` arguments
- [ ] Agents can reach each other via Docker network
- [ ] Passes `docker-compose up` local test
- [ ] No hardcoded secrets (env vars only)

**Technical Requirements**:
- uv for fast dependency management
- Multi-stage build for smaller images

---

#### Feature 8: GHCR Deployment

**Description**: Publish Docker images to GitHub Container Registry for AgentBeats access.

**Acceptance Criteria**:
- [ ] Images: `ghcr.io/<org>/bulletproof-green:latest`
- [ ] Images: `ghcr.io/<org>/bulletproof-purple:latest`
- [ ] Package visibility: **public** (required for platform access)
- [ ] Semantic version tags (v1.0.0, v1.0.1)
- [ ] GitHub Actions workflow for automated builds on push/tag

**Technical Requirements**:
- GITHUB_TOKEN with packages:write scope
- docker/build-push-action@v5

---

#### Feature 9: AgentBeats Registration

**Description**: Register agents on agentbeats.dev platform.

**Acceptance Criteria**:
- [ ] Green agent registered → `agentbeats_id` obtained
- [ ] Purple agent registered → `agentbeats_id` obtained
- [ ] `scenario.toml` configured with production IDs
- [ ] Platform validates AgentCard endpoints
- [ ] Platform can pull and run Docker images

**Configuration** (scenario.toml):
```toml
[green_agent]
agentbeats_id = "<registered_green_id>"

[[participants]]
agentbeats_id = "<registered_purple_id>"
name = "substantiator"

[config]
difficulty = "medium"
max_iterations = 5
target_risk_score = 20
```

---

#### Feature 10: Enhanced Output Schema [Phase 2]

**Description**: Standardized evaluation output format per Green-Agent-Metrics-Specification.md.

**Acceptance Criteria**:
- [ ] Version and timestamp fields
- [ ] Narrative ID (UUID)
- [ ] Primary metrics object (compliance_classification, confidence, risk_score, risk_category, predicted_audit_outcome)
- [ ] Component scores object (routine_engineering_penalty, vagueness_penalty, business_risk_penalty, experimentation_penalty, specificity_penalty, total_penalty)
- [ ] Diagnostics object (routine_patterns_detected, vague_phrases_detected, business_keywords_detected, experimentation_evidence_score, specificity_score)
- [ ] Redline object with severity counts (total_issues, critical, high, medium, issues array)
- [ ] Metadata object (evaluation_time_ms, rules_version, irs_citations)

**Technical Requirements**:
- JSON schema validation
- Backwards compatibility with legacy fields

---

#### Feature 11: Advanced Pattern Detectors [Phase 2]

**Description**: Additional rule-based detectors for comprehensive IRS Section 41 compliance.

**Acceptance Criteria**:
- [ ] Business risk detector: market, revenue, customers, sales, ROI, profit keywords
- [ ] Specificity detector: failure citations (dates, error codes, metrics), hypothesis-test-failure-iteration patterns
- [ ] Integrated into evaluator scoring pipeline
- [ ] Returns detection counts for diagnostics

**Technical Requirements**:
- Modular detector architecture
- Pattern weight configuration

---

#### Feature 12: ABC Benchmark Rigor [Phase 2]

**Description**: Statistical validation and baseline testing for benchmark credibility.

**Acceptance Criteria**:
- [ ] Trivial agent baseline (empty response → risk_score > 80, random text → risk_score > 70)
- [ ] Statistical measures (Cohen's κ ≥ 0.75, 95% confidence intervals)
- [ ] Held-out test set (separate from training/validation data)
- [ ] Documented limitations and edge cases

**Technical Requirements**:
- scipy or statsmodels for statistical calculations
- Test framework integration

---

#### Feature 13: Difficulty-Based Evaluation [Phase 2]

**Description**: Stratified benchmark testing across difficulty tiers.

**Acceptance Criteria**:
- [ ] Difficulty tags in ground truth (EASY, MEDIUM, HARD)
- [ ] Per-tier accuracy reporting
- [ ] Even distribution across tiers
- [ ] Validation script reports breakdown by difficulty

**Technical Requirements**:
- Updated JSON schema for difficulty field
- Reporting dashboard or CLI output

---

#### Feature 14: Anti-Gaming Measures [Phase 2]

**Description**: Adversarial testing to prevent benchmark exploitation.

**Acceptance Criteria**:
- [ ] Adversarial test narratives (keyword stuffing, template gaming)
- [ ] LLM reward hacking detection
- [ ] Pattern variation resistance
- [ ] Robustness tests (capitalization, whitespace, paraphrasing)

**Technical Requirements**:
- Adversarial test suite
- Gaming detection metrics

---

#### Feature 15: SSE Task Updates [Phase 2]

**Description**: Server-Sent Events for real-time A2A task status streaming.

**Acceptance Criteria**:
- [ ] SSE endpoint for task progress updates
- [ ] Emits events during multi-turn arena evaluations
- [ ] Client-side event handling
- [ ] Graceful degradation if SSE unavailable

**Technical Requirements**:
- SSE protocol implementation
- A2A protocol extension

---

#### Feature 16: ART Fine-tuning Pipeline [Phase 2]

**Description**: Adversarial Reward Training (ART) for Purple Agent improvement.

**Acceptance Criteria**:
- [ ] Trajectory store captures Purple agent generation paths
- [ ] Reward function based on risk score (lower = better)
- [ ] GRPO trainer integration
- [ ] LoRA adapter updates
- [ ] WeightWatcher validation (Alpha 2-6)

**Technical Requirements**:
- Integration with fine-tuning framework (e.g., Hugging Face PEFT)
- Trajectory storage format
- Reward computation logic

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
- [ ] Abstract (300 words) - `ABSTRACT.md`
- [ ] Public GitHub repository with code + README
- [ ] Green agent (benchmark) - A2A compatible
- [ ] Purple agent (baseline) - demonstrates benchmark
- [ ] Docker images on GHCR (public)
- [ ] Agents registered on agentbeats.dev
- [ ] 3-minute demo video
- [ ] Phase 1 submission form completed

**Judging Criteria**:
- Technical Correctness (Docker, A2A, error handling)
- Reproducibility (consistent scores, clean state)
- Benchmark Design (realistic, difficulty levels)
- Evaluation Methodology (clear scoring, IRS citations)
- Innovation & Impact (legal domain gap, practical use)

---

## Out of Scope

1. Non-software R&D claims (manufacturing, biotech)
2. Direct IRS submission (output is for review only)
3. Multi-jurisdiction (US IRS only, no state/international)
4. Fine-tuning on private audit data (Phase 2+)
5. Real-time Git/Jira integration (Phase 2+)

---

## Notes for Ralph Loop

<!-- PARSER REQUIREMENT: Include story count in parentheses -->
<!-- PARSER REQUIREMENT: Use (depends: STORY-XXX, STORY-YYY) for dependencies -->

### Story Breakdown - Phase 1 (14 stories total)

**Core Agents**:
- **Feature 1** → STORY-001: Implement Purple Agent narrative generator
- **Feature 1** → STORY-002: Implement Purple Agent A2A server (depends: STORY-001)
- **Feature 2** → STORY-003: Implement Green Agent rule-based evaluator
- **Feature 2** → STORY-004: Implement Green Agent scorer (depends: STORY-003)
- **Feature 2** → STORY-005: Implement Green Agent A2A server (depends: STORY-003, STORY-004)

**A2A Communication**:
- **Feature 3** → STORY-006: Implement A2A client for inter-agent calls (depends: STORY-002, STORY-005)
- **Feature 3** → STORY-007: Implement AgentCard discovery (depends: STORY-002, STORY-005)

**Data**:
- **Feature 6** → STORY-008: Create ground truth dataset (10 narratives)
- **Feature 6** → STORY-009: Implement benchmark validation script (depends: STORY-008)

**Deployment**:
- **Feature 7** → STORY-010: Create Dockerfiles (depends: STORY-002, STORY-005)
- **Feature 7** → STORY-011: Create docker-compose.yml (depends: STORY-010)
- **Feature 8** → STORY-012: Create GHCR workflow (depends: STORY-010)
- **Feature 9** → STORY-013: Register agents on agentbeats.dev (depends: STORY-012)

**Submission**:
- STORY-014: Write abstract and demo video (depends: STORY-013)

### Story Breakdown - Phase 2 (21 stories total)

- **Feature 4** (Arena Mode orchestration) → STORY-015: Implement Arena Mode orchestration (depends: STORY-006)
- **Feature 5** (Hybrid Evaluation) → STORY-016: Implement LLM-as-Judge (depends: STORY-003)
- **Feature 6** (Expanded Ground Truth) → STORY-017: Expand ground truth to 20+ narratives (depends: STORY-008)
- **Feature 10** (Enhanced Output Schema) → STORY-018: Wire server to accept mode=arena (depends: STORY-020), STORY-019: Integrate hybrid scoring into server (depends: STORY-020), STORY-020: Update output schema per specification, STORY-021: Update tests for new output schema (depends: STORY-020)
- **Feature 11** (Advanced Pattern Detectors) → STORY-022: Create business_risk_detector.py, STORY-023: Create specificity_detector.py, STORY-024: Integrate new detectors into evaluator (depends: STORY-022, STORY-023)
- **Feature 12** (ABC Benchmark Rigor) → STORY-025: Trivial agent baseline tests, STORY-026: Statistical rigor (Cohen's κ, 95% CI), STORY-027: Create held-out test set, STORY-028: Document benchmark limitations
- **Feature 13** (Difficulty-Based Evaluation) → STORY-029: Add difficulty tags to ground truth, STORY-030: Report accuracy by difficulty tier (depends: STORY-029)
- **Feature 14** (Anti-Gaming Measures) → STORY-031: Create adversarial test narratives, STORY-032: LLM reward hacking tests
- **Feature 15** (SSE Task Updates) → STORY-033: A2A task updates (SSE streaming)
- **Feature 16** (ART Fine-tuning Pipeline) → STORY-034: Verify Docker ENTRYPOINT parameters, STORY-035: Task isolation tests, STORY-036: ART trainer integration, STORY-037: Trajectory store, STORY-038: Reward function

**Deferred to Phase 3**:
- Real Git/Jira data ingestion
- Fine-tune on SVT historical data
