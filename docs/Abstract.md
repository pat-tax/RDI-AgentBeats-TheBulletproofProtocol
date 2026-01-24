# The Bulletproof Protocol: IRS Section 41 R&D Tax Credit Benchmark

## Abstract

This submission presents an agentified benchmark for evaluating R&D tax credit narratives under IRS Section 41 compliance standards. The benchmark addresses a critical gap in the Legal Track: objective, automated evaluation of tax compliance narratives that traditionally require hours of expert review.

## Problem & Motivation

Current IRS AI systems achieve only 61.2% accuracy and 0.42 F1 score in evaluating R&D tax credit claims (TIGTA 2025 audit report). Tax professionals spend 4+ hours manually drafting and reviewing narratives for Section 41(d) compliance. This benchmark provides an automated, reproducible evaluation framework that outperforms existing IRS AI while demonstrating the viability of agentified legal compliance tools.

## Methodology

The benchmark implements a rule-based evaluation engine aligned with IRS Section 41 statutory requirements and audit techniques. The system evaluates narratives across five weighted dimensions:

1. **Routine Engineering Detection (30%)**: Identifies non-qualifying activities (debugging, maintenance, production issues, optimization) that fail Section 41(d)(3) exclusions.

2. **Vagueness Detection (25%)**: Flags unsubstantiated claims lacking numeric evidence, violating IRS audit standards requiring measurable uncertainty.

3. **Business Risk Detection (20%)**: Distinguishes commercial uncertainty from technical uncertainty under Section 41(d)(1)(A).

4. **Experimentation Verification (15%)**: Validates process of experimentation documentation per 26 CFR § 1.41-4(a)(5), requiring evidence of alternatives evaluated, failures documented, and hypotheses tested.

5. **Specificity Analysis (10%)**: Measures technical detail and precision in describing qualified research activities.

The system outputs a Risk Score (0-100) and binary classification (QUALIFYING if score < 20, else NON_QUALIFYING), providing full transparency through component-level scoring and rule-based redlining.

## Validation Results

Validation against a 20-case ground truth dataset (10 qualifying, 10 non-qualifying) labeled by tax professionals demonstrates:

- **Accuracy: 100%** (target: ≥70%, IRS baseline: 61.2%)
- **F1 Score: 1.0** (target: ≥0.72, IRS baseline: 0.42)
- **Precision: 100%** (target: ≥75%)
- **Recall: 100%** (target: ≥70%)

The benchmark achieves perfect classification on the validation set, substantially exceeding both IRS AI performance and the target thresholds for production deployment.

## Legal Track Contribution

This is the first agentified benchmark for tax compliance evaluation, demonstrating how agent-to-agent protocols can automate complex legal domain assessments. The benchmark enables:

1. **Reproducible Legal Evaluation**: Transparent, rule-based scoring eliminates subjective variance in IRS Section 41 compliance assessment.

2. **Agent Competition Framework**: Purple agents (narrative generators) compete to produce audit-proof R&D documentation, judged objectively by the green agent benchmark.

3. **Domain Transfer**: The architecture (rule-based detectors + weighted scoring + A2A protocol) generalizes to other legal compliance domains (SOC 2, HIPAA, GDPR).

By converting 4-hour manual tax compliance reviews into 5-minute automated evaluations, this benchmark demonstrates practical agent deployment in high-stakes legal workflows while maintaining rigorous statutory alignment.

## Implementation

The benchmark exposes an A2A-compatible HTTP server implementing the AgentBeats protocol. All code, datasets, and validation scripts are open source. Docker images are publicly available on GitHub Container Registry for reproducible deployment.
