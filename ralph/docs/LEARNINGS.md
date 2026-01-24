# Lessons Learned: Agent-Driven Development with Ralph Loop

**Project**: The Bulletproof Protocol (AgentBeats Legal Track)
**Date**: 2026-01-23
**Context**: Analysis of integration gap discovered after STORY-001 through STORY-012 implementation

## Executive Summary

After completing 12 stories (STORY-001 through STORY-012) using the Ralph Loop autonomous development system, we discovered a critical integration gap: sophisticated evaluation detectors (STORY-006 through STORY-009) were implemented and tested individually but never wired into the main evaluation flow (STORY-005). All 145 unit tests passed, but the system didn't work as specified.

**Root Cause**: Missing integration story between component implementation and orchestrator.

**Impact**: Green agent benchmark used simple keyword heuristics instead of the sophisticated IRS Section 41 rule engine.

---

## Top 5 Lessons

### 1. Explicit Integration Stories

**Problem**: Components built in isolation never get wired together.

**Solution**: Add explicit integration stories after completing component groups.

**Pattern**:
```
STORY-005: Build orchestrator (skeleton with placeholders)
STORY-006-009: Build components (detectors, with full logic)
STORY-010: Integration (wire components into orchestrator)
```

**Why It Matters**: Without an explicit integration story, agents assume components will wire themselves automatically. They don't.

**Action Items**:
- Add integration stories to PRD for every group of 3+ components
- Mark integration stories with `type: "integration"` in prd.json
- Require integration stories to have `depends_on` all component stories

---

### 2. Behavior-Focused Acceptance Criteria

**Problem**: Tests validated interface shape, not behavior quality.

**Solution**: Add criteria that verify implementation logic, not just API contracts.

**Example**:
- ❌ Bad: "Returns risk_score between 0-100"
- ✅ Good: "Routine narrative (maintenance keywords) scores >20 on routine_engineering component"

**Why It Matters**: Interface-only criteria let placeholder implementations pass. STORY-005 passed all tests with simple keyword matching instead of using the sophisticated detectors.

**Action Items**:
- Add behavioral acceptance criteria: "Uses RoutineEngineeringDetector.analyze()"
- Add property-based criteria: "risk_score is monotonic - more detections → higher score"
- Add integration criteria: "Mocking detector to return score=30 results in evaluator returning risk_score≥30"

---

### 3. Dependency Tracking in prd.json

**Problem**: Linear story numbering suggested sequential execution when some could be parallel.

**Solution**: Add `depends_on` and `blocks` fields to enable:
- Parallel execution of independent stories
- Validation that dependencies are met
- Detection of missing integration stories

**Enhanced Schema**:
```json
{
  "id": "STORY-010",
  "type": "integration",
  "depends_on": ["STORY-006", "STORY-007", "STORY-008", "STORY-009"],
  "blocks": ["STORY-015"],
  "critical_path": true
}
```

**Why It Matters**: Ralph Loop executed stories sequentially even though STORY-006, 007, 008, 009 could run in parallel. Also, it couldn't detect that STORY-010 (integration) was missing from the plan.

**Action Items**:
- Update prd.json.template with `depends_on`, `blocks`, `type` fields
- Update generating-prd skill to validate dependency graph
- Update ralph.sh to respect dependencies and enable parallel execution

---

### 4. Integration Checkpoints

**Problem**: Ralph Loop ran 11 iterations autonomously without human verification.

**Solution**: Add mandatory checkpoints after completing component groups:

```json
{
  "checkpoints": [
    {
      "after_story": "STORY-009",
      "type": "integration_review",
      "required": true,
      "checklist": [
        "Verify all detectors are imported in evaluator.py",
        "Run E2E test: purple generates narrative → green evaluates",
        "Check evaluator returns non-empty component_scores",
        "Validate risk_score calculation matches weighted algorithm"
      ]
    }
  ]
}
```

**Why It Matters**: Without checkpoints, the loop kept running even though the core evaluation logic was never integrated. By the time we noticed, 11 stories were complete.

**Action Items**:
- Add checkpoint definitions to prd.json
- Update ralph.sh to pause at checkpoints
- Require smoke tests at checkpoints
- Block progress if checkpoint validation fails

---

### 5. Test the Integration, Not Just the Units

**Problem**: 145 unit tests passed, but system didn't work.

**Solution**: Add integration test requirements to every critical story.

**Test Pyramid**:
```python
# Unit Tests (60%): Test individual modules
tests/test_routine_engineering.py       # ✓ Detector works
tests/test_vagueness_detector.py        # ✓ Detector works
tests/test_experimentation_checker.py   # ✓ Detector works
tests/test_scorer.py                    # ✓ Scorer works

# Integration Tests (30%): Test wiring ← THIS WAS MISSING
tests/test_evaluator_integration.py     # ✗ Evaluator uses detectors
tests/test_detector_to_scorer_flow.py   # ✗ Detectors → Scorer pipeline

# E2E Tests (10%): Test full system
tests/integration/test_e2e_assessment.py  # Purple → Green flow
```

**Why It Matters**: Unit tests proved each detector worked correctly in isolation. But no test verified that the evaluator actually called the detectors. The system "worked" in parts but not as a whole.

**Action Items**:
- Add `test_requirements` field to prd.json with unit/integration/e2e paths
- Require integration tests for all skeleton and integration story types
- Add smoke tests that verify components are wired (not just that they exist)
- Use mocking in integration tests: "If detector returns X, does evaluator output Y?"

---

## Case Study: The Missing Integration Story

### Timeline

- **Jan 23, 12:52**: STORY-005 completed - evaluator with placeholder logic ✓
- **Jan 23, 12:56**: STORY-006 completed - routine engineering detector ✓
- **Jan 23, 13:00**: STORY-007 completed - vagueness detector ✓
- **Jan 23, 13:04**: STORY-008 completed - experimentation checker ✓
- **Jan 23, 13:08**: STORY-009 completed - risk scorer ✓
- **Jan 23, 13:11**: STORY-011 completed - Dockerfile.green ✓ (skipped integration!)
- **Jan 23, 13:17**: STORY-012 completed - docker-compose ✓
- **Jan 23, 14:28**: **Integration gap discovered** ❌

### What Should Have Happened

After STORY-009 completed:
1. **Checkpoint triggered**: "All detectors complete. Ready to integrate?"
2. **Smoke test**: Run evaluator against purple agent narratives
3. **Result**: component_scores are empty → integration missing
4. **Action**: Create STORY-010 "Integrate detectors into evaluator"
5. **After STORY-010**: Re-run smoke tests → component_scores populated ✓

### The Fix

Added STORY-010 to prd.json:
```json
{
  "id": "STORY-010",
  "title": "Integrate detectors into evaluator",
  "type": "integration",
  "depends_on": ["STORY-006", "STORY-007", "STORY-008", "STORY-009"],
  "blocks": ["STORY-015"],
  "acceptance": [
    "NarrativeEvaluator imports and instantiates all detectors",
    "evaluate() calls each detector's analyze() method",
    "Component scores aggregated using RiskScorer.calculate_risk()",
    "Returns structured dict with populated component_scores",
    "Integration tests verify detectors are actually called"
  ]
}
```

All subsequent stories renumbered: old STORY-010 → new STORY-011, etc.

---

## Quick Reference Card

**Before Starting a Project:**
- [ ] Add integration stories to PRD (1 per 3-5 component stories)
- [ ] Add dependency fields to prd.json schema
- [ ] Define checkpoints after component groups
- [ ] Set up smoke test suite

**During Story Implementation:**
- [ ] Check story type: skeleton / component / integration
- [ ] If integration: look for components to wire, remove placeholders
- [ ] Write integration tests, not just unit tests
- [ ] Verify behavior, not just interface shape

**Before Marking Story Complete:**
- [ ] All acceptance criteria met (including behavioral ones)
- [ ] All tests pass (unit + integration + E2E)
- [ ] No TODOs/FIXMEs in changed files
- [ ] Smoke tests pass
- [ ] If integration story: verify components are wired, no placeholders remain

**After Completing Story Group:**
- [ ] Run checkpoint: manual review required
- [ ] Run smoke tests: does the system actually work?
- [ ] Check for orphaned modules: are all components used?

---

## References

- **Original PRD**: `docs/PRD.md`
- **Updated prd.json**: `docs/ralph/prd.json` (now includes STORY-010)
- **Ralph Loop Scripts**: `scripts/ralph/`
- **Integration Gap Code Review**: 2026-01-23

---

**Document Version**: 1.0
**Last Updated**: 2026-01-23
**Status**: Living Document
