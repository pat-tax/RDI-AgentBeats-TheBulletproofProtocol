---
title: Purple Agent User Story
version: 1.0
created: 2026-01-31
updated: 2026-01-31
phase: Phase 2 - Purple Agent Competition
---

# Purple Agent (R&D Substantiator) - User Story

**AgentBeats Competition**: Phase 2 - Purple Agent Competition
**Period**: February 16 - March 31, 2026

> **See also:**
> - [GreenAgent-UserStory.md](GreenAgent-UserStory.md) - Green Agent (benchmark) user story
> - [PurpleAgent-PRD.md](PurpleAgent-PRD.md) - Purple Agent requirements
> - [AgentBeats/COMPETITION-ALIGNMENT.md](AgentBeats/COMPETITION-ALIGNMENT.md) - Competition alignment

---

## One-Liner

A recursive adversarial agent system where a "Virtual IRS Auditor" ruthlessly critiques a "Generator Agent" to produce audit-proof R&D tax credit claims.

---

## Problem

**See**: [GreenAgent-UserStory.md](GreenAgent-UserStory.md#problem) for complete problem statement.

**Key Phase 2 Challenges:**
- Real engineering data ingestion (Git commits, Jira tickets)
- Multi-turn refinement based on critique
- Semantic understanding beyond pattern matching
- Production-ready narrative quality

---

## Solution (Phase 2)

Advanced purple agent competing to produce audit-proof documentation evaluated by green agent benchmarks:

| Agent | Role | AgentBeats Name |
|-------|------|-----------------|
| **Agent A (Substantiator)** | Generates IRS-compliant narratives from real data | Purple Agent (Competitor) |
| **Agent B (Virtual Examiner)** | Critiques using IRS audit standards | Green Agent (Judge) |

**Result**: 4-hour manual process → 5-minute automated review via adversarial training.

---

## Target Users

1. **Tax professionals (SVT)**: Reduce 4-hour drafting to 5-minute review
2. **Startup founders/CFOs**: Unlock non-dilutive capital via R&D credits
3. **IP attorneys/technical writers**: Substantiate technical uncertainty
4. **AgentBeats competitors**: Build purple agents to top the leaderboard

---

## Purple Agent (Substantiator) - Phase 2

**As a** tax professional, **I want** raw engineering data converted to Four-Part Test narratives **so that** drafting time drops from 4 hours to 5 minutes.

**Phase 1 Baseline (Complete):**
- [x] Template-based narrative generation
- [x] A2A protocol server
- [x] Four-Part Test structure output

**Phase 2 Enhancements (Deferred):**
- [ ] Ingests Git commits (patterns: "refactor", "failed", "latency")
- [ ] Parses Jira tickets for technical uncertainty indicators
- [ ] Filters business risk (will it sell?) from technical risk (can we build it?)
- [ ] Generates 500-word summary: Hypothesis → Test → Failure → Iteration
- [ ] Automatic metric extraction (latency, error rates, resource usage)
- [ ] Personnel-to-failure mapping

---

## Recursive Loop (Arena Mode) - Phase 2

**As a** system operator, **I want** iterative adversarial refinement **so that** output survives IRS scrutiny.

**Workflow:**
1. Purple drafts Version 1
2. Green issues "Notice of Proposed Adjustment" (critique)
3. Purple re-queries for stronger evidence
4. Loop until Risk Score < 20 or max iterations

**Phase 2 Status**: ⏸️ **DEFERRED** (STORY-015)

**Acceptance Criteria:**
- [ ] Green agent accepts `mode=arena` parameter
- [ ] Calls Purple agent via A2A `tasks/send` for each iteration
- [ ] Purple agent receives critique and regenerates narrative
- [ ] Loop terminates when risk_score < target OR max_iterations reached
- [ ] Returns ArenaResult with full iteration history
- [ ] Configurable: max_iterations (default: 5), target_risk_score (default: 20)

**Implementation Files:**
- `src/bulletproof_green/arena/executor.py`
- `src/bulletproof_purple/refiner.py` (receives critique, regenerates)

---

## Hybrid Evaluation - Phase 2

**As a** benchmark user, **I want** rule-based AND LLM-based evaluation **so that** I get reproducible scores with semantic understanding.

**Phase 2 Status**: ⏸️ **DEFERRED** (STORY-016)

**Acceptance Criteria:**
- [ ] Rule-based: deterministic primary scoring
- [ ] LLM-as-Judge: semantic analysis, temperature=0
- [ ] Combined: final_score = α*rule_score + β*llm_score (α=0.7, β=0.3)
- [ ] Fallback to rule-only if LLM unavailable
- [ ] OpenAI API (GPT-4) or equivalent
- [ ] Graceful degradation

**Business-Speak Detection:**
- Flags market, revenue, ROI mentions without technical context
- Distinguishes commercial uncertainty from technical uncertainty

**Specific Failure Verification:**
- Validates dates, error codes, metrics presence
- Confirms narrative specificity beyond vague claims

---

## Success Criteria (Phase 2)

| Metric | Target |
|--------|--------|
| Time reduction | 4h → 5min (90%+) |
| Risk score | < 20 for production narratives |
| Arena convergence | Within 5 iterations |
| Detection precision | Distinguish business vs technical risk |
| Real data ingestion | Git + Jira integration working |
| Leaderboard ranking | Top 10 purple agents |

---

## ART Fine-tuning Pipeline - Phase 2

**As a** purple agent developer, **I want** adversarial reward training **so that** my agent improves from green agent feedback.

**Phase 2 Status**: ⏸️ **DEFERRED** (STORY-034-038)

**Acceptance Criteria:**
- [ ] Trajectory store captures Purple agent generation paths
- [ ] Reward function based on risk score (lower = better)
- [ ] GRPO trainer integration
- [ ] LoRA adapter updates
- [ ] WeightWatcher validation (Alpha 2-6)

**Implementation Files:**
- `src/bulletproof_purple/training/` (new training pipeline)
- `src/bulletproof_purple/trajectory_store.py`
- `src/bulletproof_purple/reward.py`

---

## Constraints

1. **IRS Section 41**: Strict adherence to statutes and Form 6765
2. **Data privacy**: All SVT data anonymized/redacted
3. **AgentBeats deadline**: Purple agent competition March 31, 2026
4. **Tech stack**: Python 3.13, A2A Protocol v0.3+
5. **Domain**: LegalTech / FinTech / RegTech
6. **Competition rules**: Must use public green agent benchmarks

---

## Out of Scope (Phase 2)

1. Non-software R&D (manufacturing, biotech) - Future
2. Direct IRS submission (output is for review only) - Future
3. Multi-jurisdiction (US IRS only, no state/international) - Future
4. Fine-tuning on private audit data - **Phase 3+**
5. Production deployment at tax firms - **Phase 3+**
6. Multi-agent orchestration (>2 agents) - Future

---

## Phase 2 Timeline

**Feb 16 - March 31, 2026**:
- Week 1-2: Arena Mode implementation (STORY-015)
- Week 3-4: Hybrid LLM evaluation (STORY-016) if desired
- Week 5-6: Real data ingestion (Git/Jira)
- Week 7-8: ART fine-tuning pipeline

---

**Version**: 1.0
**Phase**: Phase 2 - Purple Agent Competition
**Competition Period**: February 16 - March 31, 2026
**Maintained By**: The Bulletproof Protocol Team
