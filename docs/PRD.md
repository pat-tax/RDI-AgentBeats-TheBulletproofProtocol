---
title: Product Requirements Document
version: 2.0
---

# Product Requirements Document: The Bulletproof Protocol

## Project Overview

The Bulletproof Protocol is an adversarial agent benchmark for IRS Section 41 R&D tax credit evaluation. It deploys two opposing agents in a recursive loop: a Purple Agent (R&D Substantiator) that generates compliant narratives, and a Green Agent (Virtual Examiner) that critiques them against IRS audit standards. The system transforms 4-hour manual legal drafting into 5-minute automated review.

For AgentBeats competition: Purple Agent generates narratives to be evaluated, Green Agent is the benchmark that evaluates them.

---

## Functional Requirements

<!-- PARSER REQUIREMENT: Use exactly "#### Feature N:" format -->

#### Feature 1: Purple Agent - Narrative Generation

**Description**: Generate IRS Section 41 compliant Four-Part Test narratives from engineering signals.

**Acceptance Criteria**:
- [ ] Generates 500-word project summary focused on Process of Experimentation
- [ ] Follows Four-Part Test structure (Hypothesis, Test, Failure, Iteration)
- [ ] Filters business risk from technical risk
- [ ] Outputs structured narrative with technical uncertainty evidence

**Technical Requirements**:
- Template-based generation (data ingestion out of scope)
- Python 3.13 compatible

**Files**:
- `src/bulletproof_purple/generator.py`
- `src/bulletproof_purple/server.py`

---

#### Feature 2: Green Agent - Evaluation Engine

**Description**: Evaluate narratives against IRS Section 41 audit standards using rule-based detection.

**Acceptance Criteria**:
- [ ] Detects "Routine Engineering" patterns
- [ ] Applies "Business Component" test
- [ ] Flags vague language without specific metrics
- [ ] Requires citation of specific failure events
- [ ] Outputs Risk Score (0-100) and Redline Markup
- [ ] Rejects claims until Risk Score < 20

**Technical Requirements**:
- Deterministic rule-based scoring
- Returns structured evaluation per Green-Agent-Metrics-Specification.md

**Files**:
- `src/bulletproof_green/evaluator.py`
- `src/bulletproof_green/scorer.py`
- `src/bulletproof_green/server.py`

---

#### Feature 3: Arena Mode - Adversarial Loop

**Description**: Multi-turn orchestration where Green Agent iteratively refines Purple Agent narratives via A2A protocol.

**Acceptance Criteria**:
- [ ] Green agent accepts `mode=arena` parameter
- [ ] Calls Purple Agent via A2A protocol for each iteration
- [ ] Loop terminates when risk_score < target OR max_iterations reached
- [ ] Returns ArenaResult with full iteration history
- [ ] Configurable max_iterations (default: 5) and target_risk_score (default: 20)

**Technical Requirements**:
- A2A protocol integration
- Each iteration includes: narrative, evaluation, critique

**Files**:
- `src/bulletproof_green/arena_executor.py`
- `src/bulletproof_green/messenger.py`

---

#### Feature 4: Hybrid Evaluation

**Description**: Combine rule-based and LLM-based evaluation for reproducible scores with semantic understanding.

**Acceptance Criteria**:
- [ ] Rule-based evaluation remains deterministic
- [ ] LLM-as-Judge provides semantic analysis with chain-of-thought reasoning
- [ ] Combined scoring: final_score = alpha*rule_score + beta*llm_score
- [ ] Fallback to rule-only if LLM unavailable
- [ ] LLM uses temperature=0 for consistency

**Technical Requirements**:
- OpenAI GPT-4 for LLM judge
- Graceful degradation when LLM unavailable

**Files**:
- `src/bulletproof_green/llm_judge.py`
- `src/bulletproof_green/evaluator.py`

---

#### Feature 5: Ground Truth Dataset

**Description**: Labeled dataset of narratives for benchmark validation and training.

**Acceptance Criteria**:
- [ ] 20+ labeled narratives with expected scores
- [ ] Mix of passing (Risk Score < 20) and failing narratives
- [ ] Covers common failure patterns (vague language, business risk, routine engineering)
- [ ] Anonymized to protect client confidentiality

**Technical Requirements**:
- JSON format for machine readability
- Human-readable annotations

**Files**:
- `data/ground_truth.json`
- `src/validate_benchmark.py`

---

## Non-Functional Requirements

**Performance**: All evaluations complete in < 30 seconds
**Compliance**: Strictly adheres to IRS Section 41 statutes and Form 6765 requirements
**Privacy**: All training data anonymized and redacted
**Platform**: Python 3.13, existing project dependencies
**Domain**: LegalTech / FinTech / RegTech - tax compliance

## Out of Scope

1. Non-software R&D claims (manufacturing, biotech)
2. Direct IRS submission
3. Multi-jurisdiction support (state-level, international)
4. Git/Jira/transcript ingestion (future enhancement)
5. Personnel-to-failure mapping (future enhancement)

---

## Notes for Ralph Loop

<!-- PARSER REQUIREMENT: Include story count in parentheses -->
<!-- PARSER REQUIREMENT: Use (depends: STORY-XXX, STORY-YYY) for dependencies -->
Story Breakdown - Phase 1 (8 stories total):
- **Feature 1 (Purple Agent)** → STORY-001: Implement narrative generator, STORY-002: Create Purple Agent server (depends: STORY-001)
- **Feature 2 (Green Agent)** → STORY-003: Implement rule-based evaluator, STORY-004: Implement scorer, STORY-005: Create Green Agent server (depends: STORY-003, STORY-004)
- **Feature 3 (Arena Mode)** → STORY-006: Create A2A messenger (depends: STORY-002, STORY-005), STORY-007: Implement arena executor (depends: STORY-006)
- **Feature 4 (Hybrid Evaluation)** → STORY-008: Implement LLM judge (depends: STORY-003)
- **Feature 5 (Ground Truth)** → STORY-009: Create ground truth dataset, STORY-010: Implement benchmark validator (depends: STORY-009)
