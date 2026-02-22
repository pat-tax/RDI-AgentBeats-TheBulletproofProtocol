# Data Provenance

This document describes the provenance, methodology, and contamination prevention measures for the RDI-AgentBeats-TheBulletproofProtocol benchmark datasets.

## Overview

The benchmark consists of two separate datasets to prevent data contamination:

1. **Public Ground Truth** (`ground_truth.json`) - 30 narratives used for development and validation
2. **Held-Out Test Set** (`held_out_test_set.json`) - 12 narratives reserved for final evaluation

## Data Sources

All narratives in both datasets are **synthetically generated** for the purpose of this benchmark. The narratives are designed to test IRS Section 41 R&D tax credit compliance evaluation capabilities.

### Provenance Categories

Each entry includes a `provenance` field indicating its source category:

- `synthetic_qualifying` - Qualifying narratives with clear experimentation evidence
- `synthetic_non_qualifying_routine` - Non-qualifying routine engineering narratives
- `synthetic_non_qualifying_business_risk` - Non-qualifying narratives with business risk language
- `synthetic_non_qualifying_vague` - Non-qualifying narratives with vague language
- `synthetic_trivial_baseline` - Trivial baseline cases (empty, random text, gibberish)

## Data Collection Methodology

### Narrative Creation Process

1. **Requirements Analysis**: Identified key IRS Section 41 criteria and failure patterns
2. **Pattern Design**: Created templates for qualifying and non-qualifying patterns
3. **Synthetic Generation**: Generated narratives following identified patterns
4. **Expert Review**: Validated narratives against IRS Section 41 criteria
5. **Difficulty Assignment**: Tagged each narrative as EASY, MEDIUM, or HARD based on:
   - Obviousness of classification
   - Subtlety of failure patterns
   - Edge case complexity

### Quality Assurance

- All narratives reviewed for IRS Section 41 compliance accuracy
- Difficulty tags assigned based on expected detection complexity
- Expected scores calibrated through rule-based evaluator testing
- Narratives anonymized (no real company data)

## Held-Out Test Set Strategy

### Purpose

The held-out test set serves to:

1. **Prevent Data Contamination**: Test set narratives are NOT included in public ground truth
2. **Validate Generalization**: Ensure benchmark evaluates unseen cases
3. **Establish Rigor**: Provide clean evaluation separate from development data

### Split Methodology

- **Public Ground Truth**: 30 narratives (71% of total dataset)
  - Used for development, debugging, and initial validation
  - Publicly accessible in repository

- **Held-Out Test Set**: 12 narratives (29% of total dataset)
  - Reserved for final benchmark evaluation
  - Narratives verified to NOT overlap with ground truth
  - Maintained separately to prevent accidental contamination

### Contamination Prevention

1. **Separate Files**: Held-out set stored in `held_out_test_set.json`
2. **ID Namespace**: Held-out IDs prefixed with `HELD-` to prevent confusion
3. **Verification**: Automated tests ensure no overlap between datasets
4. **Version Control**: Both datasets tracked with version numbers and timestamps

## Version Tracking

Each narrative entry includes version tracking fields:

- `version`: Semantic version (e.g., "1.0.0") indicating narrative revision
- `created_at`: ISO 8601 timestamp of narrative creation/last modification
- `provenance`: Source category for traceability

### Version Update Policy

Version numbers follow semantic versioning:

- **Major version** (X.0.0): Significant narrative rewrite changing expected classification
- **Minor version** (1.X.0): Moderate edits affecting expected score range
- **Patch version** (1.0.X): Minor corrections not affecting evaluation outcomes

## Difficulty Distribution

Both datasets maintain balanced difficulty distributions:

| Difficulty | Ground Truth | Held-Out | Total |
|-----------|--------------|----------|-------|
| EASY      | 40%          | 75%      | 50%   |
| MEDIUM    | 37%          | 17%      | 31%   |
| HARD      | 23%          | 8%       | 19%   |

Note: Held-out set is skewed toward EASY cases as it includes trivial baselines for establishing performance floors.

## Data Integrity

### Validation Checks

Automated tests verify:

- ✅ No ID overlap between ground truth and held-out sets
- ✅ All entries have version, created_at, and provenance fields
- ✅ Difficulty tags are valid (easy, medium, hard)
- ✅ Version numbers follow semver format
- ✅ All provenance values are from defined categories

### Audit Trail

- Initial dataset created: 2026-01-31
- Current version: 1.0.0
- Last updated: 2026-01-31
- Total narratives: 42 (30 public + 12 held-out)

## Usage Guidelines

### For Benchmark Development

Use `ground_truth.json` for:
- Developing evaluation rules
- Calibrating scoring algorithms
- Debugging detection logic
- Computing development metrics

### For Final Evaluation

Use `held_out_test_set.json` for:
- Final benchmark validation
- Reporting official metrics
- Comparing model performance
- Publication results

### Contamination Prevention

**CRITICAL**: Never train models or tune parameters using held-out test set. This would contaminate the evaluation and invalidate benchmark rigor.

## References

- IRS Section 41 Research Credit criteria
- Green-Agent-Metrics-Specification.md
- BENCHMARK_LIMITATIONS.md (when available)

## Changelog

### Version 1.0.0 (2026-01-31)

- Initial dataset creation
- 30 public ground truth narratives
- 12 held-out test narratives
- Added version tracking and provenance fields
- Established contamination prevention measures
