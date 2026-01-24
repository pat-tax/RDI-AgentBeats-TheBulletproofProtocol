---
title: User Story
version: 2.0
applies-to: Agents and humans
purpose: Product vision aligned with original pitch
---

# The Bulletproof Protocol (Adversarial R&D Tax Agent)

## The One-Liner

A recursive adversarial agent system where a "Virtual IRS Auditor" ruthlessly critiques and trains a "Generator Agent" to write audit-proof R&D tax credit claims.

## Problem Statement

Tax compliance isn't about creative writing; it's about surviving an audit. Current LLMs are too agreeable to act as effective legal defense. Traditional approaches result in:

- 4-hour manual legal drafting processes
- High audit risk (vague language, business-speak)
- Missed non-dilutive capital for startups

## Value Proposition

The Bulletproof Protocol treats R&D tax credit substantiation as a Generative Adversarial Network (GAN) of text using a Recursive Adversarial Agents (RAA) architecture:

**Agent A (The Substantiator)**: Ingests raw engineering signals (Git commits, Jira tickets, interview transcripts) to draft IRS Section 41 compliant "Technical Narrative"

**Agent B (The Virtual Examiner)**: A fine-tuned "Cynical Auditor" trained on IRS statutes and rejected claims, whose only goal is to find weaknesses

**Result**: Transform 4-hour manual process into 5-minute automated review, unlocking millions in non-dilutive capital.

### AgentBeats Naming Convention

For AgentBeats competition submission:

- **Agent A (The R&D Substantiator)** = **Purple Agent** (generates narratives to be evaluated)
- **Agent B (The Virtual Examiner)** = **Green Agent** (benchmark that evaluates narratives)

## User Stories

### Agent A: The R&D Substantiator (The Generator)

**As a** tax professional,
**I want to** convert raw engineering data into compliant Four-Part Test narratives,
**so that** I reduce drafting time from 4 hours to 5 minutes.

**Acceptance Criteria:**

- Ingests Git commits (identifying "refactor," "failed," "latency" patterns)
- Parses Jira ticket comments for technical uncertainty indicators
- Processes interview transcripts from Pro Bono Patents scripts
- Filters "business risk" (will it sell?) from "technical risk" (can we build it?)
- Maps personnel to specific technical failures (QRE justification)
- Generates 500-word project summary on Process of Experimentation (Hypothesis → Test → Failure → Iteration)

### Agent B: The Virtual Examiner (The Evaluator)

**As an** IRS compliance validator,
**I want to** ruthlessly critique draft claims using IRS Section 41 audit standards,
**so that** only audit-proof narratives are approved.

**Acceptance Criteria:**

- Detects "Routine Engineering" patterns (standard debugging → REJECT)
- Applies "Business Component" test (product improvement vs process improvement)
- Flags vague language ("optimize," "upgrade") unless backed by specific metrics
- Requires citation of specific failure events (No failure = No uncertainty)
- Outputs Risk Score (0-100) and Redline Markup
- Rejects claims until Risk Score < 20 (Low Audit Risk)

### The Recursive Loop (The Workflow)

**As a** system operator,
**I want** Agent A and Agent B to iteratively refine claims through adversarial debate,
**so that** the final output survives real IRS scrutiny.

**Acceptance Criteria:**

- **Draft**: Agent A writes Version 1
- **Audit**: Agent B issues "Notice of Proposed Adjustment" (Rejection)
- **Refine**: Agent A re-queries raw data for stronger evidence (specific metrics, failed experiments)
- **Finalize**: Loop closes when Agent B assigns Risk Score < 20
- Final output delivered to SVT Partner for 5-minute human review

### SVT Integration (The Ground Truth)

**As a** system developer,
**I want to** fine-tune Agent B on anonymized historical audit data from Silicon Valley Tax,
**so that** the Virtual Examiner mirrors real-world IRS behavior.

**Acceptance Criteria:**

- Training data: narratives that passed audit vs narratives that triggered inquiries
- All data anonymized and redacted (client confidentiality)
- Agent B evaluation matches actual IRS Section 41 enforcement patterns
- Human-in-the-loop validation with SVT Partner before production deployment
- **Phase 2**: Ground truth dataset with 20 labeled narratives, LLM-as-Judge with general IRS knowledge, fine-tuning on SVT data (future enhancement)

## Success Criteria

1. **90% time reduction**: 4 hours → 5 minutes (90%+ efficiency gain)
2. **Low audit risk score (<20)**: Agent B consistently assigns Risk Score < 20 for production-ready narratives
3. **High precision detection**: Accurately distinguish business risk from technical risk
4. **Successful AgentBeats demo**: Working end-to-end demonstration with real anonymized SVT data

## Constraints

1. **IRS Section 41 compliance**: Strictly adhere to IRS Section 41 statutes and Form 6765 requirements
2. **Data privacy/anonymization**: SVT training data must be anonymized and redacted
3. **AgentBeats competition timeline**: Demo-ready for AgentBeats submission deadline
4. **Python 3.13 tech stack**: Implementation constrained to Python 3.13 environment
5. **Domain focus**: LegalTech / FinTech / RegTech - tax compliance and R&D substantiation

## Tech Stack / Keywords

- **Architecture**: Recursive Adversarial Agents (RAA)
- **Domain**: LegalTech / FinTech / RegTech
- **Compliance Standard**: IRS Section 41 (Form 6765)
- **Input Data (Future)**: Unstructured Engineering Logs (Git/Jira) + Interview Transcripts

## Out of Scope

1. **Non-software R&D claims**: Focus only on software/high-tech R&D (exclude manufacturing, biotech)
2. **Direct IRS submission**: System generates claims for review but doesn't directly file with IRS
3. **Multi-jurisdiction support**: US-only (IRS Section 41), exclude state-level or international R&D credits
4. **Git/Jira/transcript ingestion**: Purple agent uses template-based generation (future: data extraction)
5. **Personnel-to-failure mapping**: Manual input only (future: payroll integration)
