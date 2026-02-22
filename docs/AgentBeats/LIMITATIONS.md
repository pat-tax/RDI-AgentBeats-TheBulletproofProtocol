# Benchmark Limitations

This document outlines known limitations, edge cases, and constraints of The Bulletproof Protocol benchmark for IRS Section 41 R&D tax credit narrative evaluation.

## Statistical Rigor Limitations

### Cohen's Kappa (κ) Inter-Rater Reliability

**Current Status**: Cohen's κ calculation implemented in `src/bulletproof_green/statistics.py` (STORY-027).

**Limitations**:

- **Binary Classification Only**: Current implementation assumes binary classification (qualifying vs. non-qualifying). Does not support multi-class agreements or ordinal ratings.
- **Two Raters**: Limited to pairwise comparisons. Cannot measure agreement across 3+ raters without extension to Fleiss' κ.
- **Sample Size Sensitivity**: With small datasets (n < 30), κ values can be unstable. Current ground truth has ~30 narratives, approaching the minimum threshold.
- **Paradox of High Agreement, Low Kappa**: In skewed datasets (e.g., 90% qualifying narratives), κ can be artificially low even with high observed agreement due to high chance agreement.
- **No Weighted Disagreements**: Treats all disagreements equally. A near-miss (risk_score=19 vs. 21) is penalized the same as a complete mismatch.

**Recommendations**:
- Expand ground truth dataset to n ≥ 100 for stable κ estimates
- Report both κ and observed agreement percentage
- Consider weighted κ if using ordinal risk score bands (0-20, 21-40, etc.)

### Confidence Intervals

**Current Status**: 95% confidence interval calculation using z-scores (STORY-027).

**Limitations**:

- **Normal Distribution Assumption**: Uses z-scores (1.96 for 95% CI) which assumes scores are normally distributed. May not hold for small samples or skewed distributions.
- **Small Sample Sizes**: With n < 30 samples, t-distribution is more appropriate than normal distribution. Current implementation uses simplified z-scores.
- **Fixed Confidence Levels**: Only supports 95% and 99% confidence levels with hardcoded z-scores. Other levels default to 95%.
- **Independence Assumption**: Assumes benchmark runs are independent. If the same narratives are evaluated repeatedly, CI may be narrower than true population variability.

**Recommendations**:
- Use scipy.stats.t.interval() for small samples (n < 30) to compute t-based CIs
- Add support for arbitrary confidence levels using inverse CDF
- Document test set composition to ensure independence across runs
- Consider bootstrap confidence intervals for non-normal distributions

## Sample Size and Dataset Limitations

### Ground Truth Dataset Size

**Current Status**: ~30 labeled narratives in `data/ground_truth.json`.

**Limitations**:

- **Limited Coverage**: 30 narratives may not capture the full diversity of real-world IRS Section 41 claims (e.g., industry-specific terminology, emerging technologies like blockchain/quantum computing).
- **Difficulty Distribution**: Dataset may not evenly represent easy, medium, and hard cases. Over-representation of easy cases inflates accuracy metrics.
- **Temporal Bias**: Narratives reflect 2024-2026 technology landscape. May not generalize to historical claims or future tech domains.
- **Synthetic vs. Real**: If narratives are synthetically generated, they may lack the linguistic complexity, ambiguity, or edge cases present in actual IRS filings.

**Recommendations**:
- Expand to 100+ narratives (Phase 2 requirement: 20+ narratives is still insufficient)
- Stratify by difficulty tier (33% easy, 33% medium, 33% hard)
- Include real-world anonymized narratives from tax professionals
- Add narratives from diverse industries (biotech, manufacturing, energy) beyond software

### Held-Out Test Set

**Current Status**: Held-out test set created in STORY-027.

**Limitations**:

- **Static Test Set**: Once created, held-out set becomes known. Risk of overfitting if development decisions are repeatedly validated against it.
- **No Out-of-Distribution Testing**: Test set likely drawn from same distribution as training/validation data. May not reveal failure modes on truly novel narratives.
- **Single Validation Split**: A single train/test split may be unrepresentative. Results could vary significantly with different random seeds.

**Recommendations**:
- Use k-fold cross-validation (k=5 or k=10) to average performance across multiple splits
- Create separate "challenge set" with intentionally adversarial or out-of-distribution examples
- Periodically refresh test set with new narratives to prevent overfitting
- Document test set creation date and methodology

## Rule-Based Evaluation Limitations

### Pattern Matching Approach

**Current Status**: Regex-based pattern detection in `src/bulletproof_green/evals/evaluator.py`.

**Limitations**:

- **Keyword Stuffing Vulnerability**: Agents can game scores by inserting keywords like "hypothesis", "failed", "experimentation" without genuine technical uncertainty.
- **Context Insensitivity**: Patterns match text without understanding semantic meaning. "We debugged the hypothesis testing framework" triggers false positive for "debugging" despite being legitimate R&D.
- **Negation Blindness**: Cannot detect negations. "This was NOT routine maintenance" still matches `routine_patterns`.
- **Synonym Gaps**: Limited coverage of synonyms. "investigation" ≠ "experimentation", "unsuccessful" ≠ "did not work", etc.
- **False Positives**:
  - "We developed a novel debugging algorithm" (matches "debugging" but is qualifying research)
  - "The migration algorithm reduced data transfer time" (matches "migration" but describes technical work)
- **False Negatives**:
  - Narratives using technical jargon without explicit "hypothesis/failure" keywords
  - Domain-specific uncertainty indicators (e.g., "cache coherency bottleneck", "race condition")

**Recommendations**:
- Add negation detection using dependency parsing (spaCy)
- Expand synonym coverage using word embeddings or domain-specific thesauri
- Combine with LLM-based semantic understanding (STORY-016 hybrid evaluation)
- Track false positive/negative rates on annotated edge cases
- Implement adversarial testing (STORY-031, STORY-032)

### Weighting and Scoring Arbitrariness

**Current Status**: Fixed penalty weights in `evaluator.py` (e.g., 30 points for routine engineering, 25 for vagueness).

**Limitations**:

- **No Empirical Justification**: Weights are manually tuned, not derived from IRS audit data or expert annotations.
- **Brittle Thresholds**: Risk score < 20 = qualifying is a hard cutoff. A narrative scoring 19 vs. 21 may be nearly identical but receives different classifications.
- **Linear Penalty Accumulation**: Assumes penalties are additive and independent. In reality, multiple weak signals (e.g., 3 vague phrases) may be less damaging than 1 strong signal (e.g., "routine debugging").
- **No Confidence Scores**: Outputs deterministic risk_score without uncertainty estimates. A score of 18 could represent high confidence (clear qualifying) or low confidence (borderline case).

**Recommendations**:
- Calibrate weights using logistic regression on labeled dataset
- Replace hard threshold with probabilistic classification (e.g., 0-30% = likely qualifying, 30-70% = uncertain, 70-100% = likely non-qualifying)
- Add confidence intervals to risk_score predictions
- Report feature importance to understand which patterns drive decisions

## Reproducibility Constraints

### Deterministic Evaluation

**Current Status**: Rule-based evaluation is deterministic (same input → same output). Verified in `tests/test_statistical_rigor.py`.

**Limitations**:

- **LLM Non-Determinism**: When using hybrid evaluation (STORY-016), LLM-as-Judge introduces stochasticity even with temperature=0. Results may vary across API calls due to:
  - Model version updates (GPT-4 turbo vs. GPT-4o)
  - Sampling randomness (temperature=0 reduces but doesn't eliminate variance)
  - API rate limits or retries
- **Environment Dependencies**: Reproducibility assumes:
  - Same Python version (currently 3.13)
  - Same dependency versions (pytest, scipy)
  - Same random seeds (if using probabilistic components)
- **Temporal Drift**: Rule patterns may become outdated as IRS guidance evolves or new technologies emerge.

**Recommendations**:
- Pin all dependencies with exact versions in `requirements.txt` (use `pip freeze`)
- Log LLM model IDs, timestamps, and API responses for hybrid evaluation
- Version control rule patterns and document change rationale
- Run multiple replicates (n ≥ 10) when using LLM components and report variance
- Use containerized environments (Docker) to freeze system dependencies

### Task Isolation

**Current Status**: A2A protocol requires fresh state per task (no memory carryover).

**Limitations**:

- **Stateless Constraint**: Cannot learn from previous evaluations or adapt weights based on feedback. Each narrative is evaluated independently.
- **No Active Learning**: Benchmark cannot request human annotations for uncertain cases or update rules based on new examples.
- **Cache Invalidation**: If rule patterns are updated, all previous benchmark results may become incomparable.

**Recommendations**:
- Version benchmark releases (v1.0, v1.1) and tag results with benchmark version
- Archive historical results before rule updates
- Document all pattern changes in CHANGELOG.md
- Consider separate "static benchmark" (frozen rules) vs. "adaptive benchmark" (learning-enabled)

## Edge Cases and Known Failures

### Known Failure Modes

1. **Template Exploitation**: Purple agent or adversarial agents can memorize high-scoring templates:
   ```
   "We hypothesized X. Initial experiments failed. After testing alternatives,
   we discovered Y with Z% improvement."
   ```
   This template scores well despite lacking genuine technical uncertainty.

2. **Industry Jargon Gaps**: Narratives using domain-specific terminology may be misclassified:
   - Biotech: "expression vector optimization" might not match software patterns
   - Hardware: "ASIC synthesis" or "FPGA routing" lacks software keywords
   - Finance: "latency arbitrage" or "tick-to-trade" may be flagged as business risk

3. **Multilingual Limitations**: Benchmark assumes English text. Non-English narratives or code-switched text (e.g., "Wir haben eine hypothesis...") will fail.

4. **Length Sensitivity**: Very short narratives (< 100 words) may lack sufficient pattern matches. Very long narratives (> 1000 words) may accumulate spurious penalties.

5. **Ambiguous Technical vs. Business Risk**: Narratives describing "customer-facing latency optimization" blend technical (latency) and business (customer) risk. Current rules may over-penalize these legitimate cases.

### Mitigation Strategies

- **Anti-Gaming Tests**: STORY-031 adversarial narratives test template gaming
- **Domain Expansion**: Add industry-specific pattern libraries (biotech, hardware, finance)
- **Length Normalization**: Scale penalties by narrative word count
- **Uncertainty Quantification**: Flag borderline cases (risk_score 15-25) for human review
- **Continuous Validation**: Periodically re-evaluate benchmark against new real-world examples

## Future Work

To address these limitations in Phase 2+:

1. **Larger Datasets**: Expand to 500+ narratives across diverse industries
2. **Semantic Understanding**: Integrate transformer-based embeddings (sentence-BERT) for context-aware pattern matching
3. **Calibrated Weights**: Train logistic regression or XGBoost on human-annotated data
4. **Confidence Intervals**: Add probabilistic predictions with uncertainty estimates
5. **Multi-Rater Validation**: Collect annotations from multiple tax professionals, compute Fleiss' κ
6. **Out-of-Distribution Detection**: Flag narratives that deviate significantly from training distribution
7. **Active Learning**: Allow benchmark to request human annotations for uncertain cases
8. **Temporal Versioning**: Maintain versioned benchmarks (v1.0, v2.0) with frozen rule sets

## References

- IRS Section 41 Statutes: 26 USC § 41
- Form 6765: Credit for Increasing Research Activities
- Cohen's κ: Cohen, J. (1960). "A coefficient of agreement for nominal scales"
- Confidence Intervals: Efron, B., & Tibshirani, R. (1993). "An Introduction to the Bootstrap"

---

**Last Updated**: 2026-01-31 (STORY-028)
**Benchmark Version**: v0.0.0 (Phase 1)
**Maintainer**: The Bulletproof Protocol Team
