# Ground Truth Dataset

This directory contains the ground truth dataset for validating the IRS Section 41 R&D tax credit narrative evaluator (green agent benchmark).

## Dataset Structure

### ground_truth.json

JSON array containing 20 labeled R&D narrative examples for benchmark validation. Each object has the following schema:

```json
{
  "id": "string",           // Unique identifier (Q001-Q010 for qualifying, NQ001-NQ010 for non-qualifying)
  "narrative": "string",    // 300-500 word R&D narrative text
  "label": "string",        // Classification: "QUALIFYING" or "NON_QUALIFYING"
  "irs_rationale": "string" // Explanation citing IRS Section 41 criteria
}
```

### Dataset Composition

- **Total narratives**: 20
- **QUALIFYING**: 10 narratives (IDs: Q001-Q010)
- **NON_QUALIFYING**: 10 narratives (IDs: NQ001-NQ010)

## Labeling Criteria

### QUALIFYING Narratives

Narratives labeled as QUALIFYING meet IRS Section 41(d)(1) requirements for qualified research:

1. **Technical Uncertainty** - Demonstrates that the capability or method was uncertain at the project's outset
2. **Process of Experimentation** - Documents systematic evaluation of alternatives per Section 41(d)(1)(C):
   - Hypothesis formation
   - Multiple approaches tested
   - Documented failures
   - Iterative discovery process
3. **Technological in Nature** - Relies on principles of physical science, biology, computer science, or engineering
4. **Quantifiable Results** - Includes specific metrics and measurements (e.g., "reduced latency by 73%", "achieved 94% detection rate")

**Example indicators**:
- Keywords: "uncertain", "unknown", "unclear", "hypothesis", "experiment", "novel", "investigated", "researched"
- Multiple failed approaches documented
- Systematic comparison of alternatives
- Specific numeric outcomes

### NON_QUALIFYING Narratives

Narratives labeled as NON_QUALIFYING fail to meet Section 41 criteria due to:

1. **Routine Engineering** - Excluded per Section 41(d)(3):
   - Debugging and bug fixes
   - Production issue resolution
   - Maintenance and refactoring
   - Library/framework upgrades
   - Configuration tuning
   - Code cleanup

2. **Vague Language** - Claims lack numeric substantiation:
   - "improve", "enhance", "optimize", "better", "faster"
   - No specific metrics or measurements
   - Subjective assessments ("more intuitive", "user-friendly")

3. **No Technical Uncertainty** - Capability or method was already known:
   - Applying established best practices
   - Using well-known techniques
   - Industry-standard migrations

**Example indicators**:
- Keywords: "debug", "bug fix", "production issue", "maintenance", "refactor", "upgrade", "migration"
- Vague performance claims without numbers
- Standard engineering practices without innovation

## Usage

This dataset is used to:

1. **Validate benchmark accuracy** - Test the green agent's classification performance against known ground truth
2. **Calculate metrics** - Measure accuracy, precision, recall, and F1 score (target: beat IRS AI baseline of 61.2% accuracy)
3. **Benchmark calibration** - Ensure evaluation criteria align with IRS Section 41 statutory requirements

See `src/validate_benchmark.py` for automated validation against this dataset.

## IRS Section 41 Reference

The labeling criteria are based on:

- **Section 41(d)(1)** - Definition of qualified research
- **Section 41(d)(1)(A)** - Discovery requirement
- **Section 41(d)(1)(C)** - Process of experimentation
- **Section 41(d)(3)** - Exclusions for routine engineering

For detailed IRS guidance, see:
- IRS Publication 5784: "Research Credit Claims Audit Techniques Guide"
- Treasury Regulations Section 1.41-4
