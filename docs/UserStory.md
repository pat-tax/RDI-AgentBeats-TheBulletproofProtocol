---
title: User Story
version: 2.0
applies-to: Agents and humans
purpose: Product vision, value proposition, and success metrics
---

# User Story: The Bulletproof Protocol

## Problem Statement

Current LLMs are too agreeable to act as effective legal defense in tax compliance. Tax compliance isn't about creative writing; it's about surviving an audit. Traditional approaches to R&D tax credit claims lack adversarial validation, leading to:

- 4-hour manual legal drafting processes for each claim
- High audit risk due to vague language and "business speak"
- Inability to distinguish business risk from technical risk
- Missed opportunities for startups to access non-dilutive capital through R&D tax credits

## Target Users

1. **Tax professionals at Silicon Valley Tax**: SVT partners who review R&D tax credit claims and need to reduce 4-hour manual drafting to 5-minute review
2. **Startup founders/CFOs**: Tech startups seeking to claim R&D tax credits and unlock non-dilutive capital
3. **IP attorneys/technical writers**: Legal professionals who need to substantiate technical uncertainty for compliance

## Value Proposition

The Bulletproof Protocol treats R&D tax credit substantiation as a Generative Adversarial Network (GAN) of text using a Recursive Adversarial Agents (RAA) architecture, deploying two opposing agents in a recursive loop:

- **Agent A (The R&D Substantiator)**: Ingests raw engineering signals (Git commits, Jira tickets, interview transcripts) to draft IRS Section 41 compliant "Technical Narrative"
- **Agent B (The Virtual Examiner)**: A fine-tuned "Cynical Auditor" trained on IRS statutes and rejected claims, whose only goal is to find weaknesses

The system transforms a 4-hour manual legal drafting process into a 5-minute automated review, unlocking millions in non-dilutive capital for startups while ensuring audit-proof claims.

### AgentBeats Naming Convention

For AgentBeats competition submission:
- **Agent A (The R&D Substantiator)** = **Purple Agent** (generates narratives to be evaluated)
- **Agent B (The Virtual Examiner)** = **Green Agent** (benchmark that evaluates narratives)

## User Stories

### Agent A: The R&D Substantiator

**As a** tax professional,
**I want to** automatically convert raw engineering data into a compliant Four-Part Test narrative,
**so that** I can reduce manual drafting time from 4 hours to 5 minutes.

**Acceptance Criteria:**
- Ingests Git commit messages (identifying "refactor," "failed," "latency" patterns)
- Parses Jira ticket comments for technical uncertainty indicators
- Processes interview transcripts from Pro Bono Patents interview scripts
- Filters out "business risk" (will it sell?) and isolates "technical risk" (can we build it?)
- Maps personnel (payroll dollars) to specific technical failures (QRE justification)
- Generates 500-word project summary focused on Process of Experimentation (Hypothesis → Test → Failure → Iteration)

### Agent B: The Virtual Examiner

**As an** IRS compliance validator,
**I want to** ruthlessly critique draft claims using IRS Section 41 audit standards,
**so that** only audit-proof narratives are approved.

**Acceptance Criteria:**
- Detects "Routine Engineering" patterns (standard debugging language → REJECT)
- Applies "Business Component" test (product improvement vs. process improvement)
- Flags vague language ("optimize," "upgrade," "user experience") unless backed by specific metrics
- Requires citation of specific failure events (No failure = No uncertainty)
- Outputs Risk Score (0-100) and Redline Markup
- Rejects claims until Risk Score < 20 (Low Audit Risk)
- **[Phase 2]** Provides LLM-as-Judge semantic evaluation alongside rule-based checks
- **[Phase 2]** Detects business-speak indicators (market, revenue, customers, ROI)
- **[Phase 2]** Verifies specific failure citations (dates, error codes, metrics)
- **[Phase 2]** Returns structured output per Green-Agent-Metrics-Specification.md

### Recursive Adversarial Loop

**As a** system operator,
**I want** Agent A and Agent B to iteratively refine claims through adversarial debate,
**so that** the final output survives real IRS scrutiny.

**Acceptance Criteria:**
- Agent A drafts Version 1
- Agent B issues "Notice of Proposed Adjustment" (Rejection)
- Agent A re-queries raw data for stronger evidence (specific metrics, failed experiments)
- Agent A submits Version 2
- Loop continues until Agent B assigns Risk Score < 20
- Final output delivered to SVT Partner for 5-minute human review
- **[Phase 2 - Arena Mode]** Green agent orchestrates multi-turn loop via A2A protocol
- **[Phase 2]** Configurable max_iterations (default: 5) and target_risk_score (default: 20)
- **[Phase 2]** Each iteration includes: narrative, evaluation, critique
- **[Phase 2]** Returns ArenaResult with full iteration history

### SVT Integration & Training

**As a** system developer,
**I want to** fine-tune Agent B on anonymized historical audit data from Silicon Valley Tax,
**so that** the Virtual Examiner mirrors real-world IRS behavior.

**Acceptance Criteria:**
- Training data includes narratives that passed audit vs. narratives that triggered inquiries
- All data is anonymized and redacted to protect client confidentiality
- Agent B evaluation criteria matches actual IRS Section 41 enforcement patterns
- Human-in-the-loop validation with SVT Partner before production deployment

**Phase 2 Scope** (partial implementation):
- Ground truth dataset with 20 labeled narratives
- LLM-as-Judge uses general IRS Section 41 knowledge
- Fine-tune Agent B on anonymized historical audit data from SVT (future enhancement)

### Arena Mode Benchmark (Phase 2)

**As a** benchmark operator,
**I want to** run the green agent in arena mode to iteratively improve purple agent narratives,
**so that** I can evaluate purple agents' ability to respond to critique and improve.

**Acceptance Criteria:**
- Green agent accepts `mode=arena` parameter
- Green agent calls purple agent via A2A protocol for each iteration
- Loop terminates when risk_score < target OR max_iterations reached
- Returns structured ArenaResult with iteration history
- Supports configurable parameters via environment variables

### Hybrid Evaluation (Phase 2)

**As a** benchmark user,
**I want** both rule-based and LLM-based evaluation of narratives,
**so that** I get reproducible scores AND semantic understanding.

**Acceptance Criteria:**
- Rule-based evaluation remains deterministic
- LLM-as-Judge provides semantic analysis with chain-of-thought reasoning
- Combined scoring: final_score = α*rule_score + β*llm_score
- Fallback to rule-only if LLM unavailable
- LLM uses temperature=0 for consistency

## Success Criteria

1. **90% time reduction**: Reduce human drafting time from 4 hours to 5 minutes (90%+ efficiency gain)
2. **Low audit risk score (<20)**: Agent B consistently assigns Risk Score < 20 for production-ready narratives
3. **High precision detection**: Accurately distinguish business risk from technical risk, catch vague language without false positives
4. **Successful demo at AgentBeats**: Working end-to-end demonstration with real anonymized data from SVT

## Constraints

1. **IRS Section 41 compliance**: Must strictly adhere to IRS Section 41 statutes and Form 6765 requirements
2. **Data privacy/anonymization**: Training data from SVT must be anonymized and redacted to protect client confidentiality
3. **AgentBeats competition timeline**: Must be completed and demo-ready for AgentBeats submission deadline
4. **Python 3.13 tech stack**: Implementation constrained to Python 3.13 environment with existing project dependencies
5. **Domain focus**: LegalTech / FinTech / RegTech - tax compliance and R&D substantiation

## Out of Scope

1. **Non-software R&D claims**: Focus only on software/high-tech R&D, exclude manufacturing, biotech, or other industries
2. **Direct IRS submission**: System generates claims for review but doesn't directly file with IRS
3. **Multi-jurisdiction support**: Initially US-only (IRS Section 41), exclude state-level or international R&D credits
4. **Git/Jira/transcript ingestion**: Purple agent uses template-based generation (future: data extraction)
5. **Personnel-to-failure mapping**: Manual input only (future: payroll integration)
