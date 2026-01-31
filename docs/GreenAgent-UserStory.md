---
title: Green Agent User Story
version: 1.0
created: 2026-01-31
updated: 2026-01-31
phase: Phase 1 - Green Agent Benchmark
---

# Green Agent (Virtual Examiner) - User Story

**AgentBeats Competition**: Phase 1 - Legal Domain Track
**Deadline**: January 31, 2026

> **See also:**
> - [PurpleAgent-UserStory.md](PurpleAgent-UserStory.md) - Purple Agent (competition) user stories
> - [GreenAgent-PRD.md](GreenAgent-PRD.md) - Green Agent requirements
> - [AgentBeats/COMPETITION-ALIGNMENT.md](AgentBeats/COMPETITION-ALIGNMENT.md) - Competition alignment

---

## One-Liner

A recursive adversarial agent system where a "Virtual IRS Auditor" ruthlessly critiques a "Generator Agent" to produce audit-proof R&D tax credit claims.

---

## Problem

Tax compliance is about surviving audits, not creative writing. Current LLMs are too agreeable for legal defense:

- 4-hour manual legal drafting per claim
- High audit risk from vague language and business-speak
- Inability to distinguish business risk from technical risk
- Missed non-dilutive capital opportunities for startups

---

## Solution (Phase 1)

Benchmark agent (Green Agent) that objectively evaluates R&D narratives against IRS Section 41 standards:

| Agent | Role | AgentBeats Name |
|-------|------|-----------------|
| **Agent B (Virtual Examiner)** | Evaluates using IRS audit standards | Green Agent (Benchmark) |
| **Agent A (Substantiator)** | Generates baseline narratives | Purple Agent (Reference) |

**Result**: Automated, reproducible evaluation with transparent scoring and redline feedback.

---

## Target Users

1. **Tax professionals**: Validate narrative compliance before submission
2. **Startup founders/CFOs**: Assess R&D credit claim quality
3. **AgentBeats competitors**: Build purple agents to compete on leaderboard

---

## Green Agent (Virtual Examiner) - Phase 1

**As an** IRS validator, **I want** ruthless critique using Section 41 standards **so that** only audit-proof narratives pass.

**Acceptance Criteria:**
- [x] Detects "Routine Engineering" patterns → REJECT
- [x] Applies "Business Component" test (product vs process improvement)
- [x] Flags vague language unless backed by specific metrics
- [x] Requires citation of specific failure events
- [x] Outputs Risk Score (0-100) and Redline Markup
- [x] Rejects until Risk Score < 20
- [x] Deterministic, reproducible scoring
- [x] A2A protocol communication
- [x] AgentCard discovery

---

## Success Criteria (Phase 1)

| Metric | Target | Actual |
|--------|--------|--------|
| Benchmark accuracy | ≥70% | ✅ 100% |
| F1 Score | ≥0.72 | ✅ 1.0 |
| Precision | ≥75% | ✅ 100% |
| Recall | ≥70% | ✅ 100% |
| Ground truth dataset | 10+ narratives | ✅ 30 narratives |
| Cohen's κ (inter-rater reliability) | ≥0.75 | ✅ Implemented |
| Difficulty tiers | N/A | ✅ EASY/MEDIUM/HARD |
| AgentBeats submission | Demo-ready | ⏳ In progress |

---

## Constraints

1. **IRS Section 41**: Strict adherence to statutes and Form 6765
2. **Data privacy**: All training data anonymized/redacted
3. **AgentBeats deadline**: January 31, 2026
4. **Tech stack**: Python 3.13, A2A Protocol v0.3+
5. **Domain**: LegalTech / FinTech / RegTech
6. **Reproducibility**: Deterministic scoring (no randomness)

---

## Out of Scope (Phase 1)

1. Non-software R&D (manufacturing, biotech) - Future
2. Direct IRS submission (output is for review only) - Future
3. Multi-jurisdiction (US IRS only, no state/international) - Future
4. Arena Mode (multi-turn refinement) - **Phase 2**
5. Hybrid LLM evaluation - **Phase 2**
6. Real-time Git/Jira integration - **Phase 2+**
7. Fine-tuning on private audit data - **Phase 3+**

---

## Phase 2 Preview

**See**: [PurpleAgent-UserStory.md](PurpleAgent-UserStory.md) for Phase 2 features:
- Arena Mode (multi-turn adversarial loop)
- Hybrid Evaluation (LLM-as-Judge + rule-based)
- Advanced narrative generation (real data ingestion)

---

**Version**: 1.0
**Phase**: Phase 1 - Green Agent Benchmark
**Competition Deadline**: January 31, 2026
**Maintained By**: The Bulletproof Protocol Team
