# The Bulletproof Protocol - TODO

**Phase 1 Deadline**: January 31, 2026
**Phase 2 Period**: February 16 - March 31, 2026

> **See also:**
> - [Competition Alignment](AgentBeats/COMPETITION-ALIGNMENT.md) - How this project addresses AgentBeats vision
> - [Submission Guide](AgentBeats/SUBMISSION-GUIDE.md) - Complete Phase 1 requirements and checklist
> - [Resources](AgentBeats/RESOURCES.md) - Platform links, official repos, IRS references
> - [Abstract](AgentBeats/ABSTRACT.md) - Benchmark description and demo video script

---

## 🔴 CRITICAL - Phase 1 Submission

### 1. AgentBeats Platform Registration ❌ HIGH PRIORITY

- [ ] Register agents on platform and update `scenario.toml` with production IDs
- [ ] Set Docker images to **PUBLIC** visibility on GHCR

**See**: [SUBMISSION-GUIDE.md](AgentBeats/SUBMISSION-GUIDE.md#register-on-agentbeats) for detailed registration steps

**Files to Update**:
- `scenario.toml` (lines 20, 26) - Replace placeholder `agentbeats_id` values

---

### 2. Demo Video Recording ❌ HIGH PRIORITY

- [ ] Record 3-minute demo video
- [ ] Upload to YouTube/Vimeo (unlisted or public)
- [ ] Add video URL to submission form

**See**: [ABSTRACT.md](AgentBeats/ABSTRACT.md#demo-video-recording-guide) for complete recording script (lines 43-85)

---

### 3. GHCR Deployment ❌ HIGH PRIORITY

- [ ] Push Docker images to GitHub Container Registry
- [ ] Set package visibility to **PUBLIC**
- [ ] Verify public accessibility (test pull without authentication)

**See**: [SUBMISSION-GUIDE.md](AgentBeats/SUBMISSION-GUIDE.md#push-to-ghcr) for deployment commands

---

### 4. Final Submission Form ❌ HIGH PRIORITY

- [ ] Complete Phase 1 submission form before deadline
- [ ] Provide: GitHub repo URL, GHCR images, agent IDs, demo video URL, abstract

**See**: [RESOURCES.md](AgentBeats/RESOURCES.md#submission) for form link

---

### 5. Documentation Path Fix ✅ COMPLETE

- [x] Fix inconsistent path references in `README.md`
  - Fixed: `docs/Abstract.md` → `docs/AgentBeats/ABSTRACT.md` (lines 194, 244)
  - Fixed: `AGENTBEATS_REGISTRATION.md` → `SUBMISSION-GUIDE.md` (lines 143, 196)
  - Added: `COMPETITION-ALIGNMENT.md` reference (line 242)

---

### 6. Integration Tests Verification ⚠️ LOW PRIORITY

- [ ] Verify if integration tests exist in `tests/integration/`
- [ ] Run comprehensive E2E test before submission: `bash scripts/test_comprehensive.sh`

**See**: [SUBMISSION-GUIDE.md](AgentBeats/SUBMISSION-GUIDE.md#local-testing) for testing workflow

---

## 🐛 BUGS - Sprint 3 Candidates

### BUG-001: Qualifying Narrative Misclassified as NON_QUALIFYING

**Severity**: High (E2E test shows incorrect classification)
**Story**: TODO - assign new story ID (STORY-039+)

**Symptom**: E2E Step 7 qualifying narrative gets `classification=NON_QUALIFYING`, `risk_score=55`, `overall_score=0.45` despite `pass_rate=100%` and `score=4/4`.

**Root Cause**: `_detect_keyword_stuffing` in `evals/evaluator.py` (lines 542-608) fires a +55 penalty when 2+ R&D keyword patterns each appear 2+ times. The qualifying narrative triggers it because `experimentation`+`tested` (experiment pattern) and `failed`+`failure` (fail pattern) are natural varied forms of the same root words.

**Architectural Disconnect**: `classification` and `overall_score` use full `risk_score` (includes adversarial penalties), but `pass_rate` and `score` use only the five `component_scores` (which intentionally exclude adversarial penalties). This causes contradictory output: 4/4 score but NON_QUALIFYING.

**Fix Direction**:
1. Tune `_detect_keyword_stuffing` threshold (currently `repeated_keywords >= 2` triggers 55 points — too aggressive for legitimate narratives)
2. Consider including adversarial penalties in component scores, or excluding them from classification
3. Review the `risk_score < 20` classification threshold

**Files**: `src/bulletproof_green/evals/evaluator.py` (lines 236, 542-608), `src/bulletproof_green/evals/scorer.py` (lines 84-91)

---

### BUG-002: Arena Mode "No completed task received" (4/6 E2E failures)

**Severity**: Critical (arena mode completely broken)
**Story**: TODO - assign new story ID (STORY-039+)

**Symptom**: All arena E2E tests that call Purple agent fail with `MessengerError: No completed task received`. Direct Purple calls (E2E Step 5 via curl) work fine.

**Root Cause**: `PurpleRequestHandler.on_message_send()` in `src/bulletproof_purple/server.py` (lines 265-273) iterates `executor.execute()` and returns the *last* yielded item. The executor yields: `working_task` → `completed_task` → `Message`. So `final_result` is a `Message`, not the completed `Task`.

The a2a-sdk `BaseClient.send_message()` (non-streaming path) then yields that `Message` directly. `messenger.py` line 181 skips all `Message` events with `continue`, exhausts the iterator, and raises `"No completed task received"` at line 193.

**Why curl works**: `test_e2e.sh` Step 5 just greps for `"narrative"` in raw HTTP response — present regardless of Task vs Message result type.

**Fix Direction**:
1. Fix `PurpleRequestHandler.on_message_send()` to return the completed `Task` (not the trailing `Message`) — track the last Task with `TaskState.completed` separately from the final yield
2. Alternatively, extend `messenger.py` to extract data from `Message` responses (workaround, not root fix)

**Files**: `src/bulletproof_purple/server.py` (lines 265-273), `src/bulletproof_green/messenger.py` (lines 179-193)

---

## ⏸️ DEFERRED - Phase 2 (Feb-March 2026)

### Feature 4: Arena Mode - Multi-Turn Adversarial Loop
**Story**: STORY-015
**Priority**: High (Purple agent competition feature)

**Scope**: Multi-turn orchestration where Green Agent iteratively refines Purple Agent narratives via A2A protocol.

**Rationale for Deferral**: Complex orchestration not required for Phase 1 benchmark. Better suited for Purple agent competition phase.

**See**: [PurpleAgent-PRD.md](PurpleAgent-PRD.md) Feature 4 for complete specification

---

### Feature 5: Hybrid Evaluation - LLM-as-Judge Integration
**Story**: STORY-016
**Priority**: Medium (Enhancement)

**Scope**: Combine rule-based and LLM-based evaluation with graceful fallback to deterministic scoring.

**Rationale for Deferral**: Phase 1 requires reproducible, deterministic scoring. Rule-based evaluation meets this requirement. LLM integration adds complexity without strengthening Phase 1 submission.

**See**: [PurpleAgent-PRD.md](PurpleAgent-PRD.md) Feature 5 for complete specification

---

### Feature 10: Enhanced Output Schema
**Stories**: STORY-018, STORY-019, STORY-020, STORY-021
**Priority**: Low (Enhancement)

**Scope**: Extend output schema with version/timestamp fields, narrative ID, enhanced diagnostics, and JSON schema validation.

**Rationale for Deferral**: Current output schema meets Phase 1 requirements. Enhanced schema is a polish feature.

**See**: [PurpleAgent-PRD.md](PurpleAgent-PRD.md) Feature 10 for complete specification

---

### Feature 15: SSE Task Updates - Server-Sent Events Streaming
**Story**: TODO - assign new story ID (STORY-039+; STORY-033 reassigned to Sprint 2)
**Priority**: Low (Enhancement)

**Scope**: Real-time task progress updates via Server-Sent Events for multi-turn evaluations.

**Rationale for Deferral**: Not required for Phase 1 A2A protocol compliance. JSON-RPC 2.0 task lifecycle is sufficient.

**See**: [PurpleAgent-PRD.md](PurpleAgent-PRD.md) Feature 15 for complete specification

---

### Feature 16: ART Fine-tuning Pipeline - Adversarial Reward Training
**Stories**: TODO - assign new story IDs (STORY-039+; STORY-034-038 reassigned to Sprint 2)
**Priority**: Medium (Purple agent training)

**Scope**: Fine-tuning pipeline for Purple agent improvement using adversarial reward training.

**Rationale for Deferral**: Belongs in Purple agent competition phase, not green agent benchmark submission.

**See**: [PurpleAgent-PRD.md](PurpleAgent-PRD.md) Feature 16 for complete specification

---

### Feature 6: Expanded Ground Truth Dataset
**Story**: STORY-017
**Priority**: Low (Current: 30 narratives, sufficient for Phase 1)

**Scope**: Expand dataset to 100+ narratives across diverse industries with real-world anonymized examples.

**Rationale for Deferral**: Current dataset meets Phase 1 requirements.

**See**: [GreenAgent-PRD.md](GreenAgent-PRD.md) Feature 6 for complete specification

---

### Feature 14: Anti-Gaming Measures - Advanced Adversarial Testing
**Story**: STORY-031
**Priority**: Medium (Enhancement)

**Scope**: Adversarial test suite for keyword stuffing, template gaming, LLM reward hacking, and pattern variation resistance.

**Rationale for Deferral**: Basic measures already documented in LIMITATIONS.md. Advanced testing is Phase 2 enhancement.

**See**:
- [PurpleAgent-PRD.md](PurpleAgent-PRD.md) Feature 14 for complete specification
- [LIMITATIONS.md](AgentBeats/LIMITATIONS.md) for current edge case documentation

---

### Feature 11: Complete Modular Detector Refactoring
**Stories**: STORY-040, STORY-041, STORY-042, STORY-043, STORY-044, STORY-045
**Status**: Partially complete (business_risk_detector, specificity_detector exist)
**Priority**: Low (Architecture polish)

**Scope**: Extract all detection logic into standalone modules for improved testability and maintainability.

**Rationale for Deferral**: Current hybrid architecture (2 modular detectors + embedded logic) meets Phase 1 requirements. Full refactoring is architecture polish.

**See**: [GreenAgent-PRD.md](GreenAgent-PRD.md) Feature 11 for complete specification

---

## ✅ KEEP - Phase 2 Features Already Implemented

These Phase 2 features are **already complete** and **strengthen Phase 1 submission** by aligning with judging criteria:

### Statistical Rigor (Feature 12)
**Stories**: STORY-026, STORY-027, STORY-028 | **Status**: ✅ Complete

**Implementation**: Cohen's κ calculation, 95% confidence intervals, held-out test set, documented limitations

**Why Keep**: Supports "Reproducibility" and "Documentation" judging criteria

**See**: [LIMITATIONS.md](AgentBeats/LIMITATIONS.md) for complete statistical documentation

---

### Difficulty-Based Evaluation (Feature 13)
**Stories**: STORY-029, STORY-030 | **Status**: ✅ Complete

**Implementation**: Difficulty tags (EASY/MEDIUM/HARD), per-tier accuracy reporting, even distribution (8 per tier)

**Why Keep**: Supports "Benchmark Design Quality" judging criteria (clear difficulty progression)

**See**: `data/ground_truth.json` for difficulty-tagged dataset

---

### Modular Detectors (Feature 11, Partial)
**Stories**: STORY-022, STORY-023 (TODO: STORY-033 reassigned to Sprint 2, needs new ID) | **Status**: ✅ Partial (2 of 5 detectors)

**Implementation**: `business_risk_detector.py`, `specificity_detector.py` integrated into evaluator

**Why Keep**: Supports "Technical Correctness" judging criteria (clean, maintainable code)

**See**: `src/bulletproof_green/rules/` for implemented detectors

---

## 📊 Phase 1 Submission Readiness

### Implementation Complete ✅
- [x] Green agent A2A server with AgentCard
- [x] Purple agent A2A server with AgentCard
- [x] Rule-based evaluation engine
- [x] Ground truth dataset (30 narratives)
- [x] Dockerfiles (green, purple)
- [x] docker-compose.yml
- [x] GHCR deployment scripts
- [x] GitHub Actions workflow
- [x] Abstract and demo video script
- [x] Statistical validation (Cohen's κ, CI)
- [x] Difficulty tiers
- [x] LIMITATIONS.md

### Submission Tasks Remaining 🔴
- [ ] AgentBeats platform registration (update `scenario.toml`)
- [ ] Demo video recording and upload
- [ ] GHCR deployment (push images, set to public)
- [ ] Phase 1 submission form completion

**See**: [SUBMISSION-GUIDE.md](AgentBeats/SUBMISSION-GUIDE.md#pre-submission-checklist) for complete pre-submission checklist

---

## 📅 Timeline

**Phase 1 (Completion by January 31, 2026)**:
- AgentBeats registration + GHCR deployment (2-3 hours)
- Demo video recording (1-2 hours)
- Final submission form (15 minutes)

**Phase 2 (Feb 16 - March 31, 2026)**:
- Week 1-2: Arena Mode implementation (STORY-015)
- Week 3-4: Hybrid LLM evaluation (STORY-016) if desired
- Week 5-6: Complete modular detector refactoring (STORY-040-045)
- Week 7-8: Enhanced output schema (STORY-018-021)

---

## 📚 Related Documentation

- [Competition Alignment](AgentBeats/COMPETITION-ALIGNMENT.md) - How this project addresses AgentBeats vision and premises
- [Submission Guide](AgentBeats/SUBMISSION-GUIDE.md) - Requirements, checklist, deployment steps
- [Resources](AgentBeats/RESOURCES.md) - Platform links, official repos, A2A protocol, IRS references
- [Abstract](AgentBeats/ABSTRACT.md) - Benchmark description and demo video script
- [Green Agent PRD](GreenAgent-PRD.md) - Phase 1 requirements (benchmark)
- [Purple Agent PRD](PurpleAgent-PRD.md) - Phase 2 requirements (competition)
- [LIMITATIONS](AgentBeats/LIMITATIONS.md) - Known limitations and edge cases

---

**Last Updated**: 2026-02-22
**Maintained By**: The Bulletproof Protocol Team
