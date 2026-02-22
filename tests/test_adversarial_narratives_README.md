# Adversarial Narratives Test Suite (STORY-031)

## Overview

This test suite validates that the benchmark evaluator can detect and penalize adversarial gaming attempts.

## Test Coverage

### Attack Types Covered

1. **Keyword Stuffing** (ADV001, ADV002)
   - Repetitive use of experimentation keywords
   - Forced inclusion of all positive indicators

2. **Template Gaming** (ADV003, ADV004)
   - Formulaic structure with labeled sections
   - Numbered step templates mimicking Four-Part Test

3. **Superficial Metric Stuffing** (ADV005, ADV006)
   - Metrics without technical substance
   - Lists of numbers without narrative context

4. **Overgeneralization** (ADV007, ADV008)
   - Vague language without specificity
   - Generic claims without technical depth

5. **Irrelevant Content** (ADV009, ADV010)
   - Buzzword salad with technical terms
   - Technology stack listing without experimentation

6. **Combined Gaming** (ADV011, ADV012)
   - Multiple gaming strategies combined
   - Keyword stuffing + template + metrics

7. **Edge Cases** (ADV013-ADV015)
   - Pure routine engineering
   - Pure business risk focus
   - Zero specificity

## Robustness Tests

The test suite includes robustness checks:

- **Capitalization Resistance**: Evaluator is case-insensitive
- **Whitespace Resistance**: Handles extra whitespace consistently
- **Paraphrasing Resistance**: Detects patterns even when reworded

## Dataset

Adversarial narratives are stored in `data/adversarial_narratives.json`:

```json
{
  "id": "ADV001",
  "narrative": "...",
  "attack_type": "keyword_stuffing",
  "expected_detection": true,
  "description": "..."
}
```

## Expected Behavior

All adversarial narratives should:

- Receive risk scores > 40 (high risk)
- Trigger appropriate component penalties
- Be differentiated from legitimate narratives

## Running Tests

```bash
make test_all  # Run all tests including adversarial suite
pytest tests/test_adversarial_narratives.py -v  # Run only adversarial tests
```

## Acceptance Criteria (STORY-031)

- [x] Adversarial test narratives (keyword stuffing, template gaming)
- [x] LLM reward hacking detection
- [x] Pattern variation resistance
- [x] Robustness tests (capitalization, whitespace, paraphrasing)
- [x] Adversarial test suite
- [x] Gaming detection metrics
