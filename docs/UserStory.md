---
title: User Story - The Bulletproof Protocol
version: 2.1
applies-to: Agents and humans
purpose: Product vision, value proposition, and success metrics
---

## One-Liner

A recursive adversarial agent system where a "Virtual IRS Auditor" ruthlessly critiques a "Generator Agent" to produce audit-proof R&D tax credit claims.

## Problem

Tax compliance is about surviving audits, not creative writing. Current LLMs are too agreeable for legal defense:

- 4-hour manual legal drafting per claim
- High audit risk from vague language and business-speak
- Inability to distinguish business risk from technical risk
- Missed non-dilutive capital opportunities for startups

## Solution

Recursive Adversarial Agents (RAA) architecture treating R&D substantiation as a GAN of text:

| Agent | Role | AgentBeats Name |
|-------|------|-----------------|
| **Agent A (Substantiator)** | Generates IRS Section 41 compliant narratives | Purple Agent |
| **Agent B (Virtual Examiner)** | Critiques using IRS audit standards | Green Agent |

**Result**: 4-hour manual process → 5-minute automated review.

## Target Users

1. **Tax professionals (SVT)**: Reduce 4-hour drafting to 5-minute review
2. **Startup founders/CFOs**: Unlock non-dilutive capital via R&D credits
3. **IP attorneys/technical writers**: Substantiate technical uncertainty

## User Stories

### Purple Agent (Substantiator)

**As a** tax professional, **I want** raw engineering data converted to Four-Part Test narratives **so that** drafting time drops from 4 hours to 5 minutes.

**Acceptance Criteria:**
- Ingests Git commits (patterns: "refactor", "failed", "latency")
- Parses Jira tickets for technical uncertainty indicators
- Filters business risk (will it sell?) from technical risk (can we build it?)
- Generates 500-word summary: Hypothesis → Test → Failure → Iteration

### Green Agent (Virtual Examiner)

**As an** IRS validator, **I want** ruthless critique using Section 41 standards **so that** only audit-proof narratives pass.

**Acceptance Criteria:**
- Detects "Routine Engineering" patterns → REJECT
- Applies "Business Component" test (product vs process improvement)
- Flags vague language unless backed by specific metrics
- Requires citation of specific failure events
- Outputs Risk Score (0-100) and Redline Markup
- Rejects until Risk Score < 20

**Phase 2 Additions:**
- LLM-as-Judge semantic evaluation
- Business-speak detection (market, revenue, ROI)
- Specific failure verification (dates, error codes, metrics)

### Recursive Loop (Arena Mode)

**As a** system operator, **I want** iterative adversarial refinement **so that** output survives IRS scrutiny.

**Workflow:**
1. Purple drafts Version 1
2. Green issues "Notice of Proposed Adjustment"
3. Purple re-queries for stronger evidence
4. Loop until Risk Score < 20 or max iterations

**Phase 2:** Arena mode via A2A protocol, configurable max_iterations (5) and target_risk_score (20).

### Hybrid Evaluation (Phase 2)

**As a** benchmark user, **I want** rule-based AND LLM-based evaluation **so that** I get reproducible scores with semantic understanding.

- Rule-based: deterministic primary scoring
- LLM-as-Judge: semantic analysis, temperature=0
- Combined: final_score = α*rule_score + β*llm_score
- Fallback to rule-only if LLM unavailable

## Success Criteria

| Metric | Target |
|--------|--------|
| Time reduction | 4h → 5min (90%+) |
| Risk score | < 20 for production narratives |
| Detection precision | Distinguish business vs technical risk |
| AgentBeats demo | Working E2E with anonymized SVT data |

## Constraints

1. **IRS Section 41**: Strict adherence to statutes and Form 6765
2. **Data privacy**: All SVT data anonymized/redacted
3. **AgentBeats deadline**: Demo-ready for submission
4. **Tech stack**: Python 3.13
5. **Domain**: LegalTech / FinTech / RegTech

## Out of Scope

1. Non-software R&D (manufacturing, biotech)
2. Direct IRS submission (review only)
3. Multi-jurisdiction (US IRS only)
4. Git/Jira ingestion (template-based for now)
5. Personnel-to-failure mapping (manual input)
