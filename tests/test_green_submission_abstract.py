"""Tests for ABSTRACT.md submission document.

This test validates that ABSTRACT.md meets AgentBeats submission requirements:
- Length ~300 words (250-350 word range)
- Explains problem: IRS Section 41 evaluation complexity
- Describes solution: adversarial agent benchmark
- Highlights innovation: legal domain gap, practical use
- References demo video (3-minute showcasing agents)
- Video demonstrates: narrative generation, evaluation, scoring
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
ABSTRACT_PATH = PROJECT_ROOT / "ABSTRACT.md"


def test_abstract_exists():
    """Test that ABSTRACT.md exists in the project root."""
    assert ABSTRACT_PATH.exists(), "ABSTRACT.md must exist in project root"


def test_abstract_word_count():
    """Test that abstract section is approximately 300 words (250-350 range)."""
    content = ABSTRACT_PATH.read_text()

    # Extract only the Abstract section (before any "---" separator or other sections)
    # The abstract section ends at first horizontal rule or Demo Video Guide
    abstract_section = content
    if "---" in content:
        abstract_section = content.split("---")[0]

    # Count words (split on whitespace)
    words = abstract_section.split()
    word_count = len(words)

    assert 250 <= word_count <= 350, (
        f"Abstract section must be ~300 words (250-350 range), found {word_count}"
    )


def test_abstract_explains_problem():
    """Test that Abstract explains IRS Section 41 evaluation complexity."""
    content = ABSTRACT_PATH.read_text().lower()

    # Must mention IRS Section 41 and evaluation complexity
    assert "section 41" in content, "Abstract must mention Section 41"
    assert "irs" in content, "Abstract must mention IRS"

    # Must describe complexity/challenge
    complexity_terms = ["complex", "challenge", "difficult", "hours", "manual"]
    found = any(term in content for term in complexity_terms)
    assert found, f"Abstract must describe evaluation complexity using one of: {complexity_terms}"


def test_abstract_describes_solution():
    """Test that Abstract describes adversarial agent benchmark solution."""
    content = ABSTRACT_PATH.read_text().lower()

    # Must mention adversarial agents or benchmark
    assert "benchmark" in content, "Abstract must mention benchmark"

    # Must describe agent-based solution
    agent_terms = ["agent", "green", "purple", "adversarial"]
    found = any(term in content for term in agent_terms)
    assert found, f"Abstract must describe agent solution using one of: {agent_terms}"


def test_abstract_highlights_innovation():
    """Test that Abstract highlights legal domain gap and practical use."""
    content = ABSTRACT_PATH.read_text().lower()

    # Must mention legal domain contribution
    legal_terms = ["legal", "tax", "compliance", "audit"]
    found_legal = sum(1 for term in legal_terms if term in content)
    assert found_legal >= 2, (
        f"Abstract must highlight legal domain (found {found_legal} of: {legal_terms})"
    )

    # Must highlight practical use/impact
    practical_terms = ["practical", "automat", "reduc", "improve", "first"]
    found_practical = any(term in content for term in practical_terms)
    assert found_practical, f"Abstract must highlight practical use with one of: {practical_terms}"


def test_abstract_references_demo_video():
    """Test that Abstract references 3-minute demo video."""
    content = ABSTRACT_PATH.read_text().lower()

    # Must mention demo video
    assert "video" in content or "demo" in content, "Abstract must reference demo video"

    # Should mention duration (3 minutes)
    duration_terms = ["3-minute", "3 minute", "three minute", "3min"]
    found = any(term in content for term in duration_terms)
    assert found, f"Abstract must mention 3-minute duration ({duration_terms})"


def test_abstract_video_demonstrates_functionality():
    """Test that Abstract describes video demonstrating key functionality."""
    content = ABSTRACT_PATH.read_text().lower()

    # Video should demonstrate these capabilities
    demo_terms = ["narrative", "evaluat", "scor", "generat"]
    found = sum(1 for term in demo_terms if term in content)
    assert found >= 2, (
        f"Abstract must describe video demonstrating at least 2 of: {demo_terms} (found {found})"
    )
