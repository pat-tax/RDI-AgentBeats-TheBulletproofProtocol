"""Tests for benchmark limitations documentation (STORY-028).

This test module validates that benchmark limitations are properly documented:
- LIMITATIONS.md exists and contains required sections
- Documents statistical rigor limitations
- Documents known edge cases
- Documents reproducibility constraints
"""

from pathlib import Path

import pytest


class TestLimitationsDocumentation:
    """Test that benchmark limitations are properly documented."""

    @pytest.fixture
    def limitations_file(self) -> Path:
        """Return path to LIMITATIONS.md."""
        return Path(__file__).parent.parent / "docs" / "AgentBeats" / "LIMITATIONS.md"

    def test_limitations_file_exists(self, limitations_file: Path):
        """Test that LIMITATIONS.md exists."""
        assert limitations_file.exists(), "docs/LIMITATIONS.md must exist"

    def test_limitations_file_not_empty(self, limitations_file: Path):
        """Test that LIMITATIONS.md has content."""
        content = limitations_file.read_text()
        assert len(content) > 100, "LIMITATIONS.md must have substantial content"

    def test_documents_statistical_limitations(self, limitations_file: Path):
        """Test that statistical limitations are documented."""
        content = limitations_file.read_text().lower()

        # Should mention Cohen's kappa or inter-rater reliability
        assert any(
            keyword in content for keyword in ["cohen", "kappa", "κ", "inter-rater", "reliability"]
        ), "Must document Cohen's κ limitations"

        # Should mention confidence intervals
        assert "confidence interval" in content, "Must document CI limitations"

    def test_documents_sample_size_limitations(self, limitations_file: Path):
        """Test that sample size limitations are documented."""
        content = limitations_file.read_text().lower()

        # Should discuss sample size, dataset size, or ground truth limitations
        assert any(
            keyword in content
            for keyword in ["sample size", "dataset size", "ground truth", "test set"]
        ), "Must document sample size limitations"

    def test_documents_rule_based_limitations(self, limitations_file: Path):
        """Test that rule-based evaluation limitations are documented."""
        content = limitations_file.read_text().lower()

        # Should mention rule-based, pattern matching, or keyword detection limitations
        assert any(
            keyword in content
            for keyword in ["rule-based", "pattern", "keyword", "false positive", "false negative"]
        ), "Must document rule-based evaluation limitations"

    def test_documents_edge_cases(self, limitations_file: Path):
        """Test that known edge cases are documented."""
        content = limitations_file.read_text().lower()

        # Should mention edge cases, corner cases, or known failures
        assert any(
            keyword in content
            for keyword in ["edge case", "corner case", "limitation", "known issue"]
        ), "Must document known edge cases"

    def test_has_proper_markdown_structure(self, limitations_file: Path):
        """Test that LIMITATIONS.md follows proper markdown structure."""
        content = limitations_file.read_text()

        # Should have a main heading
        assert content.startswith("#"), "Must start with a markdown heading"

        # Should have multiple sections (at least 3 headings)
        heading_count = content.count("\n##")
        assert heading_count >= 3, f"Must have at least 3 sections, got {heading_count}"

    def test_documents_reproducibility_constraints(self, limitations_file: Path):
        """Test that reproducibility constraints are documented."""
        content = limitations_file.read_text().lower()

        # Should discuss reproducibility, determinism, or variability
        assert any(
            keyword in content
            for keyword in ["reproducib", "deterministic", "variability", "consistency"]
        ), "Must document reproducibility constraints"

    def test_documents_mitigation_strategies(self, limitations_file: Path):
        """Test that mitigation strategies are documented."""
        content = limitations_file.read_text().lower()

        # Should provide guidance on addressing limitations
        assert any(
            keyword in content
            for keyword in ["mitigate", "address", "improve", "recommendation", "future work"]
        ), "Must document mitigation strategies"
