"""Tests for Abstract.md submission document.

This test validates that Abstract.md meets all AgentBeats submission requirements:
- Length <= 500 words
- Explains benchmark purpose (IRS Section 41 R&D tax credit evaluator)
- Describes evaluation methodology (rule-based detectors)
- Cites IRS Section 41 statutory basis
- Includes validation metrics (accuracy, F1)
- Explains Legal Track contribution
"""

from pathlib import Path


def test_abstract_exists():
    """Test that Abstract.md exists in the project root."""
    abstract_path = Path(__file__).parent.parent / "Abstract.md"
    assert abstract_path.exists(), "Abstract.md must exist in project root"


def test_abstract_word_count():
    """Test that Abstract.md is <= 500 words."""
    abstract_path = Path(__file__).parent.parent / "Abstract.md"
    content = abstract_path.read_text()

    # Count words (split on whitespace)
    words = content.split()
    word_count = len(words)

    assert word_count <= 500, f"Abstract must be <= 500 words (found {word_count})"


def test_abstract_includes_benchmark_purpose():
    """Test that Abstract explains benchmark purpose."""
    abstract_path = Path(__file__).parent.parent / "Abstract.md"
    content = abstract_path.read_text().lower()

    # Must mention IRS Section 41 and R&D tax credit
    assert "irs section 41" in content or "section 41" in content, \
        "Abstract must mention IRS Section 41"
    assert "r&d" in content or "research" in content, \
        "Abstract must mention R&D or research"
    assert "tax credit" in content or "tax" in content, \
        "Abstract must mention tax credit"


def test_abstract_describes_methodology():
    """Test that Abstract describes evaluation methodology."""
    abstract_path = Path(__file__).parent.parent / "Abstract.md"
    content = abstract_path.read_text().lower()

    # Must mention key evaluation components
    methodology_terms = ["routine engineering", "vagueness", "experimentation"]
    found_terms = [term for term in methodology_terms if term in content]

    assert len(found_terms) >= 2, \
        f"Abstract must describe evaluation methodology (found: {found_terms})"


def test_abstract_cites_statutory_basis():
    """Test that Abstract cites IRS Section 41 statutory basis."""
    abstract_path = Path(__file__).parent.parent / "Abstract.md"
    content = abstract_path.read_text()

    # Must cite IRS Section 41 or related guidance
    assert "Section 41" in content or "26 CFR" in content or "IRS" in content, \
        "Abstract must cite IRS Section 41 statutory basis"


def test_abstract_includes_metrics():
    """Test that Abstract includes validation metrics."""
    abstract_path = Path(__file__).parent.parent / "Abstract.md"
    content = abstract_path.read_text().lower()

    # Must mention accuracy and F1 score with targets
    assert "accuracy" in content, "Abstract must include accuracy metric"
    assert "f1" in content or "f-score" in content, \
        "Abstract must include F1 score metric"
    assert "70%" in content or "0.7" in content, \
        "Abstract must include accuracy target (>= 70%)"
    assert "0.72" in content or "72%" in content, \
        "Abstract must include F1 target (>= 0.72)"


def test_abstract_explains_legal_track_contribution():
    """Test that Abstract explains Legal Track contribution."""
    abstract_path = Path(__file__).parent.parent / "Abstract.md"
    content = abstract_path.read_text().lower()

    # Must explain contribution to Legal Track
    legal_terms = ["legal", "tax compliance", "agentbeats", "benchmark"]
    found_terms = [term for term in legal_terms if term in content]

    assert len(found_terms) >= 2, \
        f"Abstract must explain Legal Track contribution (found: {found_terms})"
