# Benchmark Limitations

This document describes known limitations, edge cases, and constraints of the AgentBeats benchmark evaluation system.

## Statistical Rigor Limitations

### Cohen's Kappa (κ) Constraints

The inter-rater reliability metric Cohen's κ measures agreement between evaluators:

- **Interpretation threshold**: We target κ ≥ 0.75 for substantial agreement, but this is a guideline, not a guarantee
- **Sample size dependency**: Cohen's κ requires sufficient sample size for reliable estimates (minimum 30+ paired observations recommended)
- **Prevalence effect**: Highly imbalanced datasets (e.g., 95% negative cases) can artificially deflate κ values even with high agreement
- **Binary vs multi-class**: κ values tend to be lower for multi-class problems due to increased chance disagreement

### Confidence Interval Limitations

95% confidence intervals are computed for evaluation metrics:

- **Normal approximation**: CIs assume approximate normality, which may not hold for small sample sizes (n < 30)
- **Independence assumption**: CIs assume independent observations; correlated test cases may underestimate uncertainty
- **Coverage probability**: 95% CI means intervals should contain true value 95% of the time across repeated experiments, not that we're 95% confident in a single interval
- **Asymmetric distributions**: For metrics near boundaries (0 or 1), CIs may be asymmetric or require special handling

## Sample Size and Dataset Limitations

### Ground Truth Dataset

- **Limited coverage**: The benchmark uses 24 total test cases (8 easy, 8 medium, 8 hard), which may not cover all possible edge cases
- **Domain coverage**: Test cases focus on narrative risk evaluation; performance may differ on other domains or risk types
- **Held-out test set size**: The held-out test set contains 12 cases, providing limited statistical power for detecting small performance differences
- **Distribution mismatch**: Real-world data distribution may differ from benchmark distribution, affecting generalization

### Training and Validation Data

- **Data contamination risk**: Care must be taken to ensure held-out test set has no overlap with training/validation data used during development
- **Temporal stability**: Benchmark performance is measured at a point in time; LLM evaluator performance may change with model updates

## Rule-Based Evaluation Limitations

### Pattern Matching Constraints

The benchmark uses rule-based pattern matching for certain checks:

- **False positives**: Keyword-based detection (e.g., looking for specific terms) may flag benign content that happens to match patterns
- **False negatives**: Novel phrasings or edge cases may bypass rule-based checks even if semantically equivalent
- **Language dependence**: Pattern rules are designed for English text and may not generalize to other languages
- **Context insensitivity**: Simple pattern matching cannot distinguish between mentions in different contexts (e.g., "violence" in news vs threat)

### Heuristic-Based Scoring

- **Threshold sensitivity**: Rule-based score thresholds (e.g., risk_score > 80 for high risk) are empirically set and may need tuning
- **Compositional effects**: Combining multiple heuristics may produce unexpected interactions
- **Adversarial robustness**: Rule-based systems are vulnerable to adversarial examples designed to exploit known patterns

## Known Edge Cases and Corner Cases

### Input Edge Cases

- **Empty inputs**: Trivial baseline tests verify handling of empty responses (should → risk_score > 80)
- **Random text**: Random character sequences should be flagged as high risk (risk_score > 70)
- **Extreme lengths**: Very long inputs (>10k characters) may hit LLM context limits or timeout
- **Special characters**: Inputs with unusual Unicode, emoji, or control characters may not be handled consistently
- **Mixed languages**: Non-English or multi-language inputs have undefined behavior

### Evaluation Edge Cases

- **Boundary scores**: Scores exactly at decision boundaries (e.g., risk_score = 80.0) may have inconsistent classification
- **Missing fields**: Inputs missing required fields may cause validation errors rather than graceful degradation
- **Malformed JSON**: Invalid JSON responses from LLM evaluators require error handling
- **Timeout handling**: Long-running LLM calls may timeout, producing partial or missing evaluations

### Known Issues

- **Tie-breaking**: When multiple difficulty tiers have identical accuracy, reporting order is implementation-dependent
- **Floating-point precision**: Score comparisons use floating-point arithmetic, which may have precision issues near boundaries
- **Concurrent evaluation**: Running multiple evaluations in parallel may produce non-deterministic results due to LLM API variability

## Reproducibility Constraints

### Deterministic vs Non-Deterministic Components

- **LLM variability**: Language model evaluators (GPT-4, Claude, etc.) are non-deterministic even with temperature=0, producing slight variations across runs
- **Random seeding**: Some components use randomness (e.g., dataset splits, trivial baseline generation); results depend on random seed
- **Timing-dependent behavior**: Async operations, timeouts, and retry logic may produce different results under varying load conditions

### Consistency Challenges

- **Model version drift**: LLM provider model updates can change evaluation behavior even with same code
- **API rate limits**: Different rate limits across runs may affect retry patterns and final results
- **Environment dependencies**: Python version, library versions (scipy, statsmodels, etc.) may affect numerical computations

### Reproducibility Recommendations

- **Fix random seeds**: Use `random.seed()` and `np.random.seed()` for reproducible dataset splits
- **Pin model versions**: Specify exact LLM model versions (e.g., "gpt-4-0613" not "gpt-4") when possible
- **Record dependencies**: Use `requirements.txt` or `poetry.lock` to freeze library versions
- **Run multiple times**: Report mean and variance across multiple benchmark runs to quantify variability

## Mitigation Strategies and Future Work

### Short-Term Improvements

1. **Increase sample size**: Expand ground truth dataset from 24 to 100+ cases to improve statistical power
2. **Cross-validation**: Use k-fold cross-validation to better estimate performance variance
3. **Confidence interval adjustments**: Use bootstrapping or Wilson score intervals for more robust CIs near boundaries
4. **Rule refinement**: Iterate on pattern-based rules based on false positive/false negative analysis

### Medium-Term Enhancements

1. **Multi-language support**: Extend benchmark to non-English inputs with translated ground truth
2. **Adversarial testing**: Create adversarial test set to measure robustness to evasion attempts
3. **Ablation studies**: Systematically measure impact of individual components (LLM vs rules, different prompt variations)
4. **Calibration analysis**: Measure and improve probability calibration of risk scores

### Long-Term Research Directions

1. **Human evaluation**: Conduct human annotation studies to validate ground truth labels and measure human-AI agreement
2. **Continual learning**: Track performance over time as models and data distributions evolve
3. **Fairness analysis**: Measure and mitigate potential biases across demographic groups, topics, or writing styles
4. **Explainability**: Develop methods to explain why specific risk scores were assigned

### Addressing Limitations

- **Statistical rigor**: Use larger samples, bootstrapping, and cross-validation to improve reliability
- **Pattern matching**: Combine rule-based checks with semantic similarity and LLM-based evaluation for more robust detection
- **Edge cases**: Expand test coverage with fuzz testing and adversarial examples
- **Reproducibility**: Document all randomness sources, pin dependencies, and report variance across runs

## Recommendations for Users

1. **Interpret results cautiously**: A single benchmark run provides limited information; run multiple times and report variance
2. **Check assumptions**: Verify that benchmark distribution matches your use case before relying on results
3. **Validate on your data**: Benchmark performance may not generalize to your specific domain or data distribution
4. **Monitor over time**: Re-run benchmarks periodically to detect performance drift as models and code evolve
5. **Understand trade-offs**: High accuracy may come with high latency or cost; balance metrics based on your requirements

## Conclusion

This benchmark provides a useful but imperfect measure of narrative risk evaluation quality. Users should understand limitations around sample size, statistical rigor, rule-based detection, and reproducibility when interpreting results. We welcome contributions to address these limitations and improve benchmark quality over time.
