---
title: Purple Agent Product Requirements Document
version: 1.0
created: 2026-01-31
updated: 2026-01-31
phase: Phase 2 - Purple Agent Competition
---

# Purple Agent (R&D Substantiator) - Product Requirements

**AgentBeats Competition**: Phase 2 - Purple Agent Competition
**Period**: February 16 - March 31, 2026

> **See also:**
> - [GreenAgent-PRD.md](GreenAgent-PRD.md) - Green Agent (benchmark) requirements
> - [COMPETITION-ALIGNMENT.md](AgentBeats/COMPETITION-ALIGNMENT.md) - Competition vision alignment
> - [TODO.md](TODO.md) - Phase 2 deferrals with rationale

---

## Project Overview

**Purple Agent Role**: Competing agent that generates IRS Section 41 compliant R&D narratives, demonstrating ability to produce audit-proof documentation when evaluated by Green Agent benchmarks.

**Phase 2 Context**: Phase 2 participants build purple agents to tackle select top green agents from Phase 1 and compete on public leaderboards.

**Architecture**: A2A-compatible agent exposing:
- Narrative generation from engineering data
- Four-Part Test structure (Hypothesis, Test, Failure, Iteration)
- Technical vs business risk distinction
- AgentCard discovery endpoint

---

## Phase 1 Baseline (COMPLETE)

> **See**: [GreenAgent-PRD.md](GreenAgent-PRD.md) for Phase 1 implementation details

**Baseline Purple Agent (STORY-001, 002)**:
- ✅ Template-based narrative generation (STORY-001)
- ✅ A2A server (STORY-002)
- ✅ Demonstrates Green Agent benchmark usage

**Purpose**: Reference implementation showing how benchmarks evaluate purple agents.

---

## Phase 2 Functional Requirements

### Feature 1: Purple Agent - Advanced Narrative Generation

**Description**: A2A-compatible agent that generates IRS Section 41 compliant Four-Part Test narratives from real engineering data sources.

**Phase 2 Status**: ⏸️ **DEFERRED** (Real data ingestion - Git/Jira integration)

**Acceptance Criteria**:
- [ ] Accepts real engineering data (Git commits, technical docs, failure logs)
- [x] Generates 500-word narrative focused on Process of Experimentation (template-based in Phase 1)
- [x] Follows Four-Part Test structure (Hypothesis, Test, Failure, Iteration)
- [x] Distinguishes technical risk from business risk
- [x] Outputs structured narrative with technical uncertainty evidence
- [x] Returns A2A DataPart with narrative content

**Phase 2 Enhancements**:
- [ ] Git commit analysis for failure patterns
- [ ] Jira ticket parsing for technical uncertainty indicators
- [ ] Personnel-to-failure mapping
- [ ] Automatic metric extraction (latency, error rates, resource usage)

**Technical Requirements**:
- A2A server on port 8000
- AgentCard at `/.well-known/agent-card.json`
- Python 3.13, a2a-sdk>=0.3.20
- Git/Jira API integrations (Phase 2)

---

### Feature 4: Arena Mode - Adversarial Loop

**Description**: Multi-turn orchestration where Green Agent iteratively refines Purple Agent narratives via real A2A communication.

**Phase 2 Status**: ⏸️ **DEFERRED** (STORY-015)

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
- Critique parsing and narrative refinement logic

**Implementation Files**:
- `src/bulletproof_green/arena/executor.py`
- `src/bulletproof_purple/refiner.py` (receives critique, regenerates)

---

### Feature 5: Hybrid Evaluation

**Description**: Combine rule-based and LLM-based evaluation for reproducible scores with semantic understanding.

**Phase 2 Status**: ⏸️ **DEFERRED** (STORY-016)

**Acceptance Criteria**:
- [ ] Rule-based evaluation remains deterministic (primary)
- [ ] LLM-as-Judge provides semantic analysis (secondary)
- [ ] Combined: final_score = α*rule_score + β*llm_score
- [ ] Fallback to rule-only if LLM unavailable
- [ ] LLM uses temperature=0 for consistency

**Technical Requirements**:
- OpenAI API (GPT-4) or equivalent
- Graceful degradation

**Implementation Files**:
- `src/bulletproof_green/evals/llm_judge.py` (exists, not integrated)
- `src/bulletproof_green/evals/evaluator.py` (integration point)

**Note**: LLM judge is Green Agent enhancement but impacts Purple Agent scoring.

---

### Feature 10: Enhanced Output Schema

**Description**: Standardized evaluation output format per Green-Agent-Metrics-Specification.md.

**Phase 2 Status**: ⏸️ **DEFERRED** (STORY-018, 019, 020, 021)

**Acceptance Criteria**:
- [ ] Version and timestamp fields
- [ ] Narrative ID (UUID)
- [ ] Primary metrics object (compliance_classification, confidence, risk_score, risk_category, predicted_audit_outcome)
- [ ] Component scores object (routine_engineering_penalty, vagueness_penalty, business_risk_penalty, experimentation_penalty, specificity_penalty, total_penalty)
- [ ] Diagnostics object (routine_patterns_detected, vague_phrases_detected, business_keywords_detected, experimentation_evidence_score, specificity_score)
- [ ] Redline object with severity counts (total_issues, critical, high, medium, issues array)
- [ ] Metadata object (evaluation_time_ms, rules_version, irs_citations)
- [ ] JSON schema validation
- [ ] Backwards compatibility with legacy fields

**Technical Requirements**:
- JSON schema validation
- Backwards compatibility

**Implementation Files**:
- `src/bulletproof_green/models.py` (schema definitions)
- `src/bulletproof_green/evals/evaluator.py` (output generation)

---

### Feature 11: Complete Modular Pattern Detectors

**Description**: Complete extraction of all rule-based detectors into standalone modules.

**Phase 2 Status**: ⏸️ **DEFERRED** (Remaining 3 of 5 detectors - STORY-040-045)

**Phase 1 Complete**:
- ✅ Business risk detector - STORY-031
- ✅ Specificity detector - STORY-032

**Phase 2 Remaining**:
- [ ] Routine engineering detector (`routine_engineering_detector.py`) - STORY-040
- [ ] Vagueness detector (`vagueness_detector.py`) - STORY-041
- [ ] Experimentation detector (`experimentation_detector.py`) - STORY-042
- [ ] Extract existing detectors from evaluator - STORY-043
- [ ] Refactor evaluator to orchestrate all detectors - STORY-044
- [ ] Update tests for modular detectors - STORY-045

**Technical Requirements**:
- Directory structure: `src/bulletproof_green/rules/`
- Each detector exposes `detect(text: str) -> tuple[int, float]` interface
- Pattern weight configuration per detector
- Evaluator delegates to detectors via composition pattern

**Implementation Files**:
- `src/bulletproof_green/rules/routine_engineering_detector.py`
- `src/bulletproof_green/rules/vagueness_detector.py`
- `src/bulletproof_green/rules/experimentation_detector.py`
- `src/bulletproof_green/evals/evaluator.py` (refactored)

---

### Feature 14: Anti-Gaming Measures

**Description**: Adversarial testing to prevent benchmark exploitation.

**Phase 2 Status**: ⏸️ **DEFERRED** (Advanced scenarios - STORY-031 basic scenarios complete)

**Acceptance Criteria**:
- [ ] Adversarial test narratives (keyword stuffing, template gaming)
- [x] LLM reward hacking detection (STORY-032 basic tests complete)
- [ ] Pattern variation resistance
- [ ] Robustness tests (capitalization, whitespace, paraphrasing)

**Technical Requirements**:
- Adversarial test suite
- Gaming detection metrics

**Implementation Files**:
- `tests/adversarial/` (new test suite)
- `data/adversarial_narratives.json`

---

### Feature 15: SSE Task Updates

**Description**: Server-Sent Events for real-time A2A task status streaming.

**Phase 2 Status**: ⏸️ **DEFERRED** (STORY-033)

**Acceptance Criteria**:
- [ ] SSE endpoint for task progress updates
- [ ] Emits events during multi-turn arena evaluations
- [ ] Client-side event handling
- [ ] Graceful degradation if SSE unavailable

**Technical Requirements**:
- SSE protocol implementation
- A2A protocol extension

**Implementation Files**:
- New SSE endpoint in `src/bulletproof_green/server.py`
- Client integration in purple agent

---

### Feature 16: ART Fine-tuning Pipeline

**Description**: Adversarial Reward Training (ART) for Purple Agent improvement.

**Phase 2 Status**: ⏸️ **DEFERRED** (STORY-034, 035, 036, 037, 038)

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

**Implementation Files**:
- `src/bulletproof_purple/training/` (new training pipeline)
- `src/bulletproof_purple/trajectory_store.py`
- `src/bulletproof_purple/reward.py`

---

## Story Breakdown - Phase 2

**Implemented Early in Phase 1** (See [GreenAgent-PRD.md](GreenAgent-PRD.md)):
- ✅ STORY-026: Statistical rigor (Cohen's κ, 95% CI)
- ✅ STORY-027: Create held-out test set
- ✅ STORY-028: Document benchmark limitations
- ✅ STORY-029: Add difficulty tags to ground truth
- ✅ STORY-030: Report accuracy by difficulty tier
- ✅ STORY-031: Create business_risk_detector.py
- ✅ STORY-032: Create specificity_detector.py

**Deferred to Phase 2 (Feb-March 2026)**:
- ⏸️ STORY-015: Implement Arena Mode orchestration
- ⏸️ STORY-016: Implement LLM-as-Judge
- ⏸️ STORY-017: Expand ground truth to 100+ narratives
- ⏸️ STORY-018: Wire server to accept mode=arena
- ⏸️ STORY-019: Integrate hybrid scoring into server
- ⏸️ STORY-020: Update output schema per specification
- ⏸️ STORY-021: Update tests for new output schema
- ⏸️ STORY-033: A2A task updates (SSE streaming)
- ⏸️ STORY-034: Verify Docker ENTRYPOINT parameters
- ⏸️ STORY-035: Task isolation tests
- ⏸️ STORY-036: ART trainer integration
- ⏸️ STORY-037: Trajectory store
- ⏸️ STORY-038: Reward function
- ⏸️ STORY-039: Create GreenAgent orchestrator class
- ⏸️ STORY-040: Create routine_engineering_detector.py
- ⏸️ STORY-041: Create vagueness_detector.py
- ⏸️ STORY-042: Create experimentation_detector.py
- ⏸️ STORY-043: Extract existing detectors from evaluator
- ⏸️ STORY-044: Refactor evaluator to orchestrate all detectors
- ⏸️ STORY-045: Update tests for modular detectors
- ⏸️ STORY-046: Add kind field to messenger parts

**Total Phase 2**: 25 deferred stories

---

## Out of Scope (Phase 2)

1. Non-software R&D claims (manufacturing, biotech) - Future
2. Direct IRS submission (output is for review only) - Future
3. Multi-jurisdiction (US IRS only, no state/international) - Future
4. Fine-tuning on private audit data - Phase 3+
5. Real-time Git/Jira integration - Phase 3+ (template-based for Phase 2)

---

## Phase 2 Timeline

**Feb 16 - March 31, 2026**:
- Week 1-2: Arena Mode implementation (STORY-015)
- Week 3-4: Hybrid LLM evaluation (STORY-016) if desired
- Week 5-6: Complete modular detector refactoring (STORY-040-045)
- Week 7-8: Enhanced output schema (STORY-018-021)

---

## Non-Functional Requirements

**Performance**:
- All narrative generation complete in < 30 seconds
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

**A2A Protocol**:
- JSON-RPC 2.0 message format
- AgentCard at `/.well-known/agent-card.json`
- Standard error codes (-32700 to -32001)

---

**Version**: 1.0
**Phase**: Phase 2 - Purple Agent Competition
**Competition Period**: February 16 - March 31, 2026
**Maintained By**: The Bulletproof Protocol Team
