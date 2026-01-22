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

#### Feature 1: Agent A - R&D Substantiator (Data Ingestion & Narrative Generation)

**Description**: Automatically converts raw engineering signals (Git commits, Jira tickets, interview transcripts) into IRS Section 41 compliant "Four-Part Test" narratives focusing on technical uncertainty and the Process of Experimentation.

**User Stories**:
- As a tax professional, I want to automatically convert raw engineering data into a compliant Four-Part Test narrative, so that I can reduce manual drafting time from 4 hours to 5 minutes.

**Acceptance Criteria**:
- [ ] Ingests Git commit messages and identifies patterns: "refactor," "failed," "latency," "bug," "optimization"
- [ ] Parses Jira ticket comments for technical uncertainty indicators
- [ ] Processes interview transcripts from Pro Bono Patents interview scripts
- [ ] Filters out "business risk" (market validation, sales concerns) and isolates "technical risk" (can we build it?)
- [ ] Maps specific personnel (payroll dollars) to specific technical failures (QRE justification)
- [ ] Generates 500-word project summary structured as: Hypothesis → Test → Failure → Iteration

**Technical Requirements**:
- Git API integration (GitPython or similar)
- Jira REST API integration
- Text parsing/NLP for transcript analysis
- Pattern matching for technical uncertainty keywords
- Template-based narrative generation following IRS Section 41 Four-Part Test structure

**Files Expected**:
- `src/TheBulletproofProtocol/agent_a/data_ingestor.py` - Git/Jira/transcript ingestion
- `src/TheBulletproofProtocol/agent_a/uncertainty_extractor.py` - Technical vs. business risk filter
- `src/TheBulletproofProtocol/agent_a/nexus_mapper.py` - Personnel-to-failure mapping
- `src/TheBulletproofProtocol/agent_a/narrative_generator.py` - Four-Part Test narrative construction
- `tests/test_agent_a.py` - Unit tests for Agent A components

---

#### Feature 2: Agent B - Virtual Examiner (Audit Critique & Risk Scoring)

**Description**: A "Cynical Auditor" that ruthlessly critiques draft narratives using IRS Section 41 audit standards. Detects routine engineering, vague language, business-speak, and lack of technical specificity. Outputs Risk Score (0-100) and Redline Markup.

**User Stories**:
- As an IRS compliance validator, I want to ruthlessly critique draft claims using IRS Section 41 audit standards, so that only audit-proof narratives are approved.

**Acceptance Criteria**:
- [ ] Detects "Routine Engineering" patterns (standard debugging language → REJECT)
- [ ] Applies "Business Component" test (product improvement vs. process improvement)
- [ ] Flags vague language: "optimize," "upgrade," "user experience" unless backed by specific metrics (e.g., "reduced latency by 40ms")
- [ ] Requires citation of specific failure events (No failure = No uncertainty)
- [ ] Outputs Risk Score (0-100) based on IRS Section 41 compliance
- [ ] Generates Redline Markup with specific rejection reasons
- [ ] Rejects claims until Risk Score < 20 (Low Audit Risk)

**Technical Requirements**:
- Rule-based evaluation engine aligned with IRS Section 41 statutes
- NLP for vagueness detection and specificity scoring
- Citation/evidence validation logic
- Risk scoring algorithm with configurable thresholds
- Markup generation (diff format or annotated text)

**Files Expected**:
- `src/TheBulletproofProtocol/agent_b/routine_engineering_detector.py` - Detects standard debugging patterns
- `src/TheBulletproofProtocol/agent_b/business_component_test.py` - Validates product vs. process improvements
- `src/TheBulletproofProtocol/agent_b/vagueness_detector.py` - Flags unsubstantiated language
- `src/TheBulletproofProtocol/agent_b/risk_scorer.py` - Computes 0-100 Risk Score
- `src/TheBulletproofProtocol/agent_b/redline_generator.py` - Produces rejection markup
- `tests/test_agent_b.py` - Unit tests for Agent B components

---

#### Feature 3: Recursive Adversarial Loop (Iterative Refinement)

**Description**: Orchestrates the recursive debate between Agent A and Agent B. Agent A drafts, Agent B rejects, Agent A refines with stronger evidence. Loop terminates when Agent B assigns Risk Score < 20.

**User Stories**:
- As a system operator, I want Agent A and Agent B to iteratively refine claims through adversarial debate, so that the final output survives real IRS scrutiny.

**Acceptance Criteria**:
- [ ] Agent A drafts Version 1 narrative
- [ ] Agent B evaluates and issues "Notice of Proposed Adjustment" (Rejection) with Risk Score and Redline Markup
- [ ] Agent A re-queries raw data for more specific evidence (metrics, failed experiments)
- [ ] Agent A submits revised Version 2
- [ ] Loop continues with version tracking (V1, V2, V3, ...)
- [ ] Loop terminates when Agent B assigns Risk Score < 20
- [ ] Final output delivered with full audit trail (all versions + critiques)
- [ ] Maximum iteration limit (e.g., 10 loops) to prevent infinite loops

**Technical Requirements**:
- Orchestration engine managing Agent A/B interaction
- Version control for narrative drafts
- Convergence detection (Risk Score < 20)
- Iteration limit safeguard
- Audit trail logging (all drafts, critiques, scores)

**Files Expected**:
- `src/TheBulletproofProtocol/orchestrator/adversarial_loop.py` - Main loop controller
- `src/TheBulletproofProtocol/orchestrator/version_manager.py` - Tracks narrative versions
- `src/TheBulletproofProtocol/orchestrator/convergence_checker.py` - Validates termination condition
- `tests/test_orchestrator.py` - Integration tests for loop behavior

---

#### Feature 4: SVT Integration & Training Data Pipeline

**Description**: Integrates with Silicon Valley Tax (SVT) historical audit data for fine-tuning Agent B. Includes anonymization, data preprocessing, and human-in-the-loop validation.

**User Stories**:
- As a system developer, I want to fine-tune Agent B on anonymized historical audit data from Silicon Valley Tax, so that the Virtual Examiner mirrors real-world IRS behavior.

**Acceptance Criteria**:
- [ ] Training data pipeline ingests SVT historical claims (passed vs. failed audits)
- [ ] All data anonymized and redacted to protect client confidentiality
- [ ] Agent B evaluation criteria matches actual IRS Section 41 enforcement patterns
- [ ] Fine-tuning process for Agent B rules/weights based on historical outcomes
- [ ] Human-in-the-loop validation: SVT Partner reviews final output (5-minute review)
- [ ] Feedback mechanism to improve Agent B accuracy over time

**Technical Requirements**:
- Data anonymization utilities (PII redaction)
- Training data format specification (JSON/CSV with labels: passed/failed)
- Fine-tuning pipeline for Agent B rule weights or LLM prompts
- Human review interface (CLI or web form)
- Feedback loop to update Agent B parameters

**Files Expected**:
- `src/TheBulletproofProtocol/svt_integration/data_anonymizer.py` - PII redaction
- `src/TheBulletproofProtocol/svt_integration/training_pipeline.py` - Fine-tuning workflow
- `src/TheBulletproofProtocol/svt_integration/human_review.py` - SVT Partner validation interface
- `data/training/` - Directory for anonymized training data (gitignored)
- `tests/test_svt_integration.py` - Unit tests for SVT components

---

#### Feature 5: CLI Interface & Workflow Management

**Description**: Command-line interface for end-to-end workflow execution. Supports data ingestion, adversarial loop execution, output generation, and human review.

**User Stories**:
- As a tax professional, I want a simple CLI to run the full workflow, so that I can generate audit-proof claims in 5 minutes.

**Acceptance Criteria**:
- [ ] `bulletproof init` - Initialize project and configure data sources (Git repo URL, Jira API, transcript file)
- [ ] `bulletproof ingest` - Run Agent A data ingestion
- [ ] `bulletproof generate` - Execute adversarial loop (Agent A + Agent B)
- [ ] `bulletproof review` - Display final narrative, Risk Score, and audit trail
- [ ] `bulletproof export` - Export to IRS Form 6765 compatible format
- [ ] Progress indicators for long-running operations
- [ ] Error handling and user-friendly messages

**Technical Requirements**:
- CLI framework (Click or Typer)
- Configuration management (YAML/TOML config file)
- Progress bars (rich or tqdm)
- Logging (structured logs for debugging)

**Files Expected**:
- `src/TheBulletproofProtocol/cli/main.py` - CLI entry point
- `src/TheBulletproofProtocol/cli/commands.py` - Command implementations
- `src/TheBulletproofProtocol/config.py` - Configuration schema
- `tests/test_cli.py` - CLI integration tests

---

## Non-Functional Requirements

### Performance
- **Efficiency**: Reduce human drafting time from 4 hours to 5 minutes (90%+ efficiency gain)
- **Convergence**: Adversarial loop completes in ≤ 10 iterations for typical projects
- **Responsiveness**: CLI operations provide feedback within 2 seconds (except long-running tasks which show progress)

### Compliance & Accuracy
- **IRS Section 41 Adherence**: All generated narratives must align with IRS Section 41 statutes and Form 6765 requirements
- **Risk Score Validity**: Agent B Risk Score < 20 must correlate with real-world low audit risk (validated against SVT historical data)
- **Precision**: ≥ 90% accuracy in distinguishing business risk from technical risk (measured against labeled test set)

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

## Out of Scope

1. **Non-software R&D claims**: Focus only on software/high-tech R&D. Manufacturing, biotech, pharmaceutical, or other industries are excluded.
2. **Direct IRS submission**: System generates claims for human review but does NOT directly file with IRS. Tax professionals retain final approval and submission control.
3. **Multi-jurisdiction support**: Initially US-only (IRS Section 41). State-level R&D credits (California, New York, etc.) and international R&D tax programs are excluded.
4. **Real-time collaboration**: Single-user workflow initially. Multi-user editing, approval chains, or team collaboration features are not included.
5. **Graphical UI**: CLI-only interface for initial version. Web-based or desktop GUI is out of scope.
6. **Automated payroll integration**: Manual input of personnel/payroll data. Automatic integration with payroll systems (Gusto, ADP) is excluded.

---

## Notes for Ralph Loop

When using the `generating-prd` skill to convert this PRD to `docs/ralph/prd.json`:

1. **Atomic Stories**: Each feature should be broken into atomic stories implementable in a single context window (100-300 lines)
2. **Story Breakdown Example**:
   - Feature 1 → STORY-001: Implement Git ingestion, STORY-002: Implement Jira ingestion, STORY-003: Implement uncertainty extractor, STORY-004: Add Agent A tests
   - Feature 2 → STORY-005: Implement routine engineering detector, STORY-006: Implement vagueness detector, STORY-007: Implement risk scorer, STORY-008: Add Agent B tests
   - Feature 3 → STORY-009: Implement adversarial loop orchestrator, STORY-010: Add orchestrator tests
   - Feature 4 → STORY-011: Implement data anonymizer, STORY-012: Implement training pipeline, STORY-013: Add SVT integration tests
   - Feature 5 → STORY-014: Implement CLI commands, STORY-015: Add CLI tests
3. **Acceptance Criteria**: Each checkbox becomes testable acceptance criteria in prd.json
4. **Files Expected**: List of files becomes the `files` field in prd.json
5. **Dependencies**: Consider story dependencies (e.g., orchestrator depends on Agent A and Agent B being implemented first)

Keep stories atomic, specific, and testable. Prioritize core adversarial loop (Features 1-3) before SVT integration and CLI polish.
