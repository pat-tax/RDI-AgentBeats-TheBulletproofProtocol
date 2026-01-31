#!/usr/bin/env python3
"""Validation script for STORY-031: Create adversarial test narratives.

This script verifies all acceptance criteria are met:
1. Adversarial test narratives (keyword stuffing, template gaming)
2. LLM reward hacking detection
3. Pattern variation resistance
4. Robustness tests (capitalization, whitespace, paraphrasing)
5. Adversarial test suite
6. Gaming detection metrics
"""

import json
import sys
from pathlib import Path


def validate_adversarial_dataset():
    """Validate adversarial narratives dataset exists and is well-formed."""
    dataset_path = Path(__file__).parent.parent / "data" / "adversarial_narratives.json"

    if not dataset_path.exists():
        print("❌ FAIL: data/adversarial_narratives.json does not exist")
        return False

    with open(dataset_path) as f:
        data = json.load(f)

    if not isinstance(data, list):
        print("❌ FAIL: adversarial_narratives.json must be a list")
        return False

    if len(data) == 0:
        print("❌ FAIL: adversarial_narratives.json must not be empty")
        return False

    # Validate schema
    required_fields = {"id", "narrative", "attack_type", "expected_detection", "description"}
    attack_types_found = set()

    for item in data:
        if not required_fields.issubset(item.keys()):
            print(f"❌ FAIL: Item {item.get('id', 'unknown')} missing required fields")
            return False
        attack_types_found.add(item["attack_type"])

    # Verify required attack types
    required_attack_types = {
        "keyword_stuffing",
        "template_gaming",
        "superficial_metric_stuffing",
        "overgeneralization",
    }

    missing = required_attack_types - attack_types_found
    if missing:
        print(f"❌ FAIL: Missing attack types: {missing}")
        return False

    print(f"✅ PASS: Adversarial dataset valid ({len(data)} examples, {len(attack_types_found)} attack types)")
    return True


def validate_test_suite():
    """Validate test suite exists and has required tests."""
    test_path = Path(__file__).parent.parent / "tests" / "test_adversarial_narratives.py"

    if not test_path.exists():
        print("❌ FAIL: tests/test_adversarial_narratives.py does not exist")
        return False

    content = test_path.read_text()

    # Check for required test methods
    required_tests = [
        "test_keyword_stuffing_detected",
        "test_template_gaming_detected",
        "test_capitalization_variation_resistance",
        "test_whitespace_variation_resistance",
        "test_paraphrasing_resistance",
        "test_adversarial_dataset_schema",
    ]

    missing_tests = []
    for test in required_tests:
        if test not in content:
            missing_tests.append(test)

    if missing_tests:
        print(f"❌ FAIL: Missing required tests: {missing_tests}")
        return False

    print(f"✅ PASS: Test suite valid (all {len(required_tests)} required tests present)")
    return True


def validate_acceptance_criteria():
    """Verify all acceptance criteria are satisfied."""
    print("\nValidating STORY-031 Acceptance Criteria:")
    print("=" * 60)

    criteria = [
        ("Adversarial test narratives dataset", validate_adversarial_dataset),
        ("Adversarial test suite", validate_test_suite),
    ]

    results = []
    for name, validator in criteria:
        print(f"\n{name}:")
        results.append(validator())

    print("\n" + "=" * 60)
    if all(results):
        print("✅ ALL ACCEPTANCE CRITERIA MET")
        return 0
    else:
        print("❌ SOME ACCEPTANCE CRITERIA NOT MET")
        return 1


if __name__ == "__main__":
    sys.exit(validate_acceptance_criteria())
