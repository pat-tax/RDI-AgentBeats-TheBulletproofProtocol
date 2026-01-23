# Green Agent Metrics Specification

**Purpose**: Define rigorous, validated evaluation metrics for Bulletproof Protocol assessor agent
**Target**: Outperform current IRS AI models (61.2% accuracy baseline)

---

## Primary Metrics (What We Report)

### 1. Compliance Classification (Binary)

**Output**: {QUALIFYING, NON-QUALIFYING}

| Metric | Definition | Target |
|--------|------------|--------|
| **Accuracy** | (TP + TN) / Total | ≥ 70% (beat IRS 61.2% baseline) |
| **Precision** | TP / (TP + FP) | ≥ 75% (minimize false approvals) |
| **Recall** | TP / (TP + FN) | ≥ 70% (catch non-qualifying claims) |
| **F1 Score** | 2 × (Precision × Recall) / (Precision + Recall) | ≥ 0.72 (beat IRS 0.42 baseline) |

**Why These Metrics**:
- [Google ML Guide](https://developers.google.com/machine-learning/crash-course/classification/accuracy-precision-recall): Standard classification metrics
- [TIGTA IRS AI Report](https://www.tigta.gov/reports/audit/irs-could-leverage-examination-results-artificial-intelligence-examination-case): IRS AI achieving 61.2% accuracy, F1=0.42
- **Our Goal**: Demonstrate agent-based evaluation outperforms traditional ML models

### 2. Risk Score (Continuous)

**Output**: 0-100 scale (0 = audit-proof, 100 = guaranteed rejection)

| Range | Classification | Description |
|-------|----------------|-------------|
| **0-20** | LOW RISK | Audit-proof, meets all IRS Section 41 criteria |
| **21-40** | MODERATE | Minor issues, likely to pass with revisions |
| **41-60** | HIGH | Significant compliance gaps, needs major revision |
| **61-80** | VERY HIGH | Multiple disqualifying patterns, likely rejection |
| **81-100** | CRITICAL | Obvious non-qualifying activity, immediate rejection |

**Validation**:
- Correlate with actual SVT audit outcomes (when available)
- Inter-rater reliability: Multiple tax professionals review same narrative
- Test-retest reliability: Same narrative → same score

### 3. Audit Prediction Accuracy

**Output**: {PASS_AUDIT, FAIL_AUDIT}

Predicted vs Actual IRS Audit Outcomes

**Validation Metrics**:
```
Confusion Matrix:
                Predicted PASS    Predicted FAIL
Actual PASS     True Positive    False Negative
Actual FAIL     False Positive   True Negative

Positive Predictive Value (PPV) = TP / (TP + FP) ≥ 0.80
Negative Predictive Value (NPV) = TN / (TN + FN) ≥ 0.75
```

**Data Source**: SVT historical audit data (Phase 2, when available)

---

## Secondary Metrics (Internal Quality)

### 4. Component Breakdown (Diagnostic Metrics)

| Component | Weight | Max Penalty | Detection Rate Target |
|-----------|--------|-------------|----------------------|
| **Routine Engineering** | 30% | 30 pts | ≥ 90% (catch obvious maintenance work) |
| **Vagueness** | 25% | 25 pts | ≥ 80% (flag unsubstantiated claims) |
| **Business Risk** | 20% | 20 pts | ≥ 85% (distinguish market from technical) |
| **Missing Experimentation** | 15% | 15 pts | ≥ 75% (require alternatives documentation) |
| **Lack of Specificity** | 10% | 10 pts | ≥ 70% (require metrics) |

**Why Weighted**:
- [IRS Audit Guide](https://www.irs.gov/businesses/research-credit-claims-audit-techniques-guide-rccatg-credit-for-increasing-research-activities): Most audits fail on routine engineering (30% weight)
- Vagueness second-most common rejection reason (25% weight)

### 5. Redline Quality Metrics

**Output**: JSON with issues, severity, reasons, suggestions

| Metric | Definition | Target |
|--------|------------|--------|
| **Actionability** | % of suggestions that lead to improved score | ≥ 80% |
| **False Positive Rate** | Flagged issues that are actually compliant | ≤ 15% |
| **Coverage** | % of actual issues detected | ≥ 85% |

**User Validation**: Tax professionals rate redline usefulness (1-5 scale, target ≥ 4.0)

---

## Benchmark Validity Metrics

### 6. Task Validity

**Question**: Does our benchmark evaluate what we claim?

| Criterion | Measurement | Target |
|-----------|-------------|--------|
| **Face Validity** | Tax professionals agree task is realistic | 5/5 experts agree |
| **Construct Validity** | Scores correlate with known qualifying/non-qualifying examples | Correlation ≥ 0.85 |
| **Content Validity** | Rules cover all IRS Section 41 four-part test | 100% coverage |

**Validation Method**: Expert panel review (5 tax professionals from SVT)

### 7. Outcome Validity

**Question**: Are evaluation results accurate and rigorous?

| Criterion | Measurement | Target |
|-----------|-------------|--------|
| **Inter-Rater Reliability** | Agreement between Green Agent and human evaluators | Cohen's κ ≥ 0.75 |
| **Test-Retest Reliability** | Same narrative evaluated twice | Intraclass correlation ≥ 0.95 |
| **Ground Truth Accuracy** | Agent score vs labeled dataset | Accuracy ≥ 85% |

**Validation Dataset**: 20 labeled narratives (10 qualifying, 10 non-qualifying)

### 8. Reproducibility Metrics

| Metric | Measurement | Target |
|--------|-------------|--------|
| **Determinism** | Same input → same output (100 trials) | 100% consistency |
| **Cross-Platform** | Same results on Linux/macOS/Windows Docker | 100% match |
| **Robustness** | Minor input variations (whitespace, capitalization) don't change score | Score variance < 2 pts |

---

## AgentBeats-Specific Metrics

### 9. A2A Protocol Compliance

| Requirement | Validation | Status |
|-------------|------------|--------|
| **Server Responds** | HTTP 200 on assessment request | ✓ Pass/Fail |
| **Task Updates** | Emits progress updates during evaluation | ✓ Pass/Fail |
| **Artifact Format** | Returns valid JSON with required fields | ✓ Pass/Fail |
| **Error Handling** | Graceful degradation on malformed input | ✓ Pass/Fail |

### 10. Baseline Comparison

**Purple Agent (Agent A) Baseline Performance**:

| Purple Agent | Risk Score Range | Pass Rate |
|--------------|------------------|-----------|
| **Naive** | 70-90 | 10% (should fail - no experimentation) |
| **Template-Based** | 40-60 | 50% (moderate quality) |
| **Optimized** | 15-25 | 90% (well-crafted narratives) |

**Green Agent Must Differentiate**: Low correlation between naive and optimized (r < 0.3)

---

## Metrics Reporting Format

### Assessment Artifact (JSON)

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

  "component_scores": {
    "routine_engineering_penalty": 20,
    "vagueness_penalty": 16,
    "business_risk_penalty": 10,
    "experimentation_penalty": 12,
    "specificity_penalty": 7,
    "total_penalty": 65
  },

  "diagnostics": {
    "routine_patterns_detected": 2,
    "vague_phrases_detected": 4,
    "business_keywords_detected": 3,
    "experimentation_evidence_score": 0.35,
    "specificity_score": 0.60
  },

  "redline": {
    "total_issues": 9,
    "critical": 2,
    "high": 3,
    "medium": 4,
    "issues": [...]
  },

  "metadata": {
    "evaluation_time_ms": 245,
    "rules_version": "1.0.0",
    "irs_citations": [
      "IRS Section 41(d)(1)",
      "26 CFR § 1.41-4"
    ]
  }
}
```

---

## Validation Plan

### Phase 1: Ground Truth Dataset (Days 1-2)

**Create 20 Test Cases**:
- 5 **Obvious Qualifying**: Novel algorithms, documented experimentation
- 5 **Obvious Non-Qualifying**: Debugging, maintenance, porting
- 5 **Edge Cases - Qualifying**: Subtle technical uncertainty
- 5 **Edge Cases - Non-Qualifying**: Routine engineering disguised as research

**Labeling Process**:
1. Draft narratives based on IRS examples
2. 3 tax professionals independently label (qualifying vs not)
3. Resolve disagreements via discussion
4. Final labels require 2/3 agreement

### Phase 2: Metric Validation (Days 3-4)

**Test Green Agent Performance**:
```python
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

# Run Green Agent on 20 test cases
predictions = [agent_b.evaluate(case) for case in test_cases]
y_true = [case.label for case in test_cases]
y_pred = [p.classification for p in predictions]

accuracy = accuracy_score(y_true, y_pred)
precision, recall, f1, _ = precision_recall_fscore_support(y_true, y_pred)

print(f"Accuracy: {accuracy:.2f} (target: ≥0.70)")
print(f"F1 Score: {f1:.2f} (target: ≥0.72)")
```

**Threshold Tuning**: Adjust Risk Score thresholds if F1 < target

### Phase 3: Inter-Rater Reliability (Days 5-6)

**Compare Agent vs Humans**:
1. Green Agent evaluates 10 narratives
2. 2 tax professionals independently evaluate same 10
3. Calculate Cohen's κ (inter-rater agreement)
4. Target: κ ≥ 0.75 (substantial agreement)

### Phase 4: Robustness Testing (Day 7)

**Adversarial Evaluation**:
- Keyword stuffing: Add "experimentation" 100 times
- Capitalization changes: ALL CAPS vs lowercase
- Whitespace variations: Extra spaces, line breaks
- Paraphrasing: Rephrase same content

**Expected**: Score variance < 5 points for non-adversarial changes

---

## Success Criteria Summary

### Minimum Viable Benchmark (Phase 1 Submission)

- [x] Risk Score (0-100) implemented
- [x] Binary classification (qualifying/non-qualifying)
- [ ] **Accuracy ≥ 70%** on 20-case test set
- [ ] **F1 Score ≥ 0.72** (beat IRS 0.42 baseline)
- [ ] Redline markup generated
- [ ] Inter-rater reliability κ ≥ 0.60 (moderate agreement)

### Stretch Goals (Post-Competition)

- [ ] Audit prediction accuracy ≥ 80% (validated against SVT data)
- [ ] Inter-rater reliability κ ≥ 0.80 (near-perfect agreement)
- [ ] User satisfaction ≥ 4.5/5.0
- [ ] Evaluation time < 250ms per narrative

---

## Key Sources

### Classification Metrics
- [Google ML Crash Course - Classification Metrics](https://developers.google.com/machine-learning/crash-course/classification/accuracy-precision-recall)
- [Understanding F1 Score - Medium](https://medium.com/@piyushkashyap045/understanding-precision-recall-and-f1-score-metrics-ea219b908093)
- [F1 Score in LLM Evaluation - Data Science Dojo](https://datasciencedojo.com/blog/understanding-f1-score/)

### IRS AI Benchmarks
- [TIGTA: IRS AI Audit Selection](https://www.tigta.gov/reports/audit/irs-could-leverage-examination-results-artificial-intelligence-examination-case)
- [IRS AI for Tax Audits 2025](https://www.ryanandwetmore.com/insights/irs-using-ai-for-tax-audits-in-2025-what-businesses-must-know)
- [Tax Audit ML Models - PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC9710839/)

### Legal Compliance Metrics
- [Gartner Compliance Score](https://www.gartner.com/en/legal-compliance/research/compliance-score)
- [Ethisphere 2026 Ethics & Compliance Metrics](https://ethisphere.com/resources/ec-metrics-and-reporting-guide/)
- [Harvard Law - Quality Metrics](https://clp.law.harvard.edu/research/research-projects/quality-metrics/)

### IRS Section 41
- [IRS Audit Techniques Guide](https://www.irs.gov/businesses/research-credit-claims-audit-techniques-guide-rccatg-credit-for-increasing-research-activities)
- [IRS Software Development Guidelines](https://www.irs.gov/businesses/audit-guidelines-on-the-application-of-the-process-of-experimentation-for-all-software)

---

## Next Steps

1. **Create ground truth dataset** (20 labeled narratives)
2. **Implement metrics calculation** in `scorer.py`
3. **Validate on test set** (measure accuracy, F1)
4. **Expert panel review** (5 tax professionals)
5. **Document in README** (report metrics in submission)
