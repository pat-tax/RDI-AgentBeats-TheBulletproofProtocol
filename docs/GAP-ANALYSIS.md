# Gap Analysis: Current Implementation vs AgentBeats Green Agent Requirements

**Date**: 2026-01-25
**Status**: Pre-submission review
**Verdict**: Not ready — critical integration gap

---

## Summary

The implementation has solid foundations (A2A infrastructure, rule-based evaluation, ground truth dataset) but contains a **critical integration bug** that prevents the evaluator from being used. After fixing this, two missing detectors need implementation to achieve full scoring coverage.

---

## Working Correctly

| Component | Status | Evidence |
|-----------|--------|----------|
| A2A Server Infrastructure | ✓ | Both agents implement `RequestHandler` correctly |
| Agent Cards | ✓ | Proper `AgentCard` with metadata in `server.py` |
| Docker Configuration | ✓ | `linux/amd64` platform, proper port exposure |
| CLI Arguments | ✓ | Supports `--host`, `--port`, `--card-url` |
| Ground Truth Dataset | ✓ | 20 labeled cases (10 QUALIFYING, 10 NON_QUALIFYING) in `data/ground_truth.json` |
| Rule-based Evaluation | ✓ | 3 of 5 detectors implemented with IRS citations |
| Validation Script | ✓ | Uses sklearn metrics (accuracy, F1, precision, recall) |
| Docker Compose | ✓ | Proper networking for local testing |

---

## Critical Gap (Showstopper)

### Green Agent Server Returns Hardcoded Response

**Location**: `src/bulletproof_green/server.py:52-56`

```python
# Current (BROKEN):
evaluation_result = (
    "Evaluation: Risk score 15, Classification: QUALIFYING. "
    "Narrative demonstrates technical uncertainty and process of experimentation."
)
```

**Problem**: The `GreenAgentHandler.on_message_send()` method returns a hardcoded string instead of using the `GreenAgentExecutor` which properly integrates with `NarrativeEvaluator`.

**Impact**: Agent always returns the same fake result regardless of input narrative.

**Fix Required**:
1. Import and instantiate `GreenAgentExecutor` in `server.py`
2. Call `executor.execute(narrative)` in `on_message_send()`
3. Return the actual evaluation result

---

## Functional Gaps

### Missing Detectors (30% of scoring weight)

| Detector | Weight | Current State | Required |
|----------|--------|---------------|----------|
| Business Risk | 20% | `score = 0` always | Detect market/sales/customer keywords vs technical risk |
| Specificity | 10% | `score = 0` always | Check for numeric metrics and concrete details |

**Location**: `src/bulletproof_green/evaluator.py:63-65`

```python
component_scores = {
    ...
    "business_risk": 0,  # Placeholder for future implementation
    "specificity": 0,    # Placeholder for future implementation
}
```

### Purple Agent Static Response

**Location**: `src/bulletproof_purple/server.py:54-59`

The purple agent returns the same hardcoded narrative every time, preventing testing of:
- Varying difficulty levels
- QUALIFYING vs NON_QUALIFYING generation
- Edge cases

---

## Output Format Mismatch

### Current Output

```json
{
  "risk_score": 65,
  "classification": "NON_QUALIFYING",
  "component_scores": {
    "routine_engineering": 12,
    "vagueness": 16,
    "business_risk": 0,
    "experimentation": 10,
    "specificity": 0
  },
  "redline": {...}
}
```

### AgentBeats Expected Format

Per `Green-Agent-Metrics-Specification.md:163-210`:

```json
{
  "version": "1.0",
  "timestamp": "2026-01-22T10:00:00Z",
  "narrative_id": "uuid",
  "primary_metrics": {
    "compliance_classification": "NON_QUALIFYING",
    "confidence": 0.89,
    "risk_score": 65,
    "risk_category": "HIGH",
    "predicted_audit_outcome": "FAIL_AUDIT"
  },
  "component_scores": {...},
  "diagnostics": {...},
  "redline": {...},
  "metadata": {
    "evaluation_time_ms": 245,
    "rules_version": "1.0.0",
    "irs_citations": ["IRS Section 41(d)(1)", "26 CFR § 1.41-4"]
  }
}
```

### Missing Fields

| Field | Purpose |
|-------|---------|
| `confidence` | Evaluation certainty (0-1) |
| `risk_category` | LOW/MODERATE/HIGH/VERY HIGH/CRITICAL |
| `predicted_audit_outcome` | PASS_AUDIT/FAIL_AUDIT |
| `diagnostics` | Pattern counts and evidence scores |
| `metadata.evaluation_time_ms` | Performance tracking |
| `metadata.rules_version` | Reproducibility |
| `metadata.irs_citations` | Legal grounding |

---

## Minor Issues

### Port Configuration

| Specification | Current |
|---------------|---------|
| Template recommends `9009` | Using `8000` |

Not blocking, but may cause confusion during AgentBeats platform integration.

---

## Remediation Priority

### P0 — Critical (Blocks Submission)

1. **Wire evaluator into server** — `server.py` must use `GreenAgentExecutor`

### P1 — High (Affects Accuracy)

2. **Add business risk detector** — Keywords: "market", "sales", "customer preference", "user adoption"
3. **Add specificity detector** — Check for metrics, numbers, concrete technical details

### P2 — Medium (Format Compliance)

4. **Align output format** — Add missing fields (`confidence`, `risk_category`, `metadata`, etc.)

### P3 — Low (Testing Quality)

5. **Purple agent variability** — Template system for generating varied narratives

---

## Validation Targets

From `Green-Agent-Metrics-Specification.md`:

| Metric | IRS Baseline | Target | Status |
|--------|--------------|--------|--------|
| Accuracy | 61.2% | ≥ 70% | Unknown (evaluator not wired) |
| F1 Score | 0.42 | ≥ 0.72 | Unknown |
| Precision | — | ≥ 75% | Unknown |
| Recall | — | ≥ 70% | Unknown |

Run `python src/validate_benchmark.py` after fixing P0 to measure actual performance.

---

## Verdict

| Question | Answer |
|----------|--------|
| Would it work as a Green Agent? | **No** — returns hardcoded responses |
| After fixing critical gap? | **Partially** — 70% scoring coverage |
| After all P0+P1 fixes? | **Yes** — full rule coverage, proper integration |

The rule-based approach (not LLM-as-judge) aligns with AgentBeats design principles. The existing detectors have proper IRS Section 41 citations, which satisfies the "rigorous rubric" requirement.
