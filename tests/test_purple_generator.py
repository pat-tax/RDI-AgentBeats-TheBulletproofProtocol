"""Tests for Purple Agent narrative generator (STORY-001).

This test module validates the acceptance criteria for STORY-001:
- Generates 500-word project summary focused on Process of Experimentation
- Follows Four-Part Test structure (Hypothesis, Test, Failure, Iteration)
- Filters business risk from technical risk
- Outputs structured narrative with technical uncertainty evidence
- Template-based generation (data ingestion out of scope)
- Python 3.13 compatible
"""

import pytest

from bulletproof_purple.generator import NarrativeGenerator, Narrative


class TestNarrativeWordCount:
    """Test narrative generates approximately 500-word summary."""

    def test_generates_approximately_500_words(self):
        """Test that generator produces ~500 word narrative (450-550 range)."""
        generator = NarrativeGenerator()
        narrative = generator.generate()

        word_count = len(narrative.text.split())
        assert 450 <= word_count <= 550, f"Expected ~500 words, got {word_count}"

    def test_narrative_is_non_empty(self):
        """Test that generated narrative is not empty."""
        generator = NarrativeGenerator()
        narrative = generator.generate()

        assert narrative.text is not None
        assert len(narrative.text.strip()) > 0


class TestFourPartTestStructure:
    """Test narrative follows IRS Four-Part Test structure."""

    def test_includes_hypothesis_section(self):
        """Test narrative contains hypothesis/technical uncertainty section."""
        generator = NarrativeGenerator()
        narrative = generator.generate()

        # Should reference hypothesis or technical uncertainty
        text_lower = narrative.text.lower()
        assert any(
            term in text_lower
            for term in ["hypothesis", "technical uncertainty", "uncertain", "unknown"]
        ), "Narrative should include hypothesis or technical uncertainty"

    def test_includes_test_section(self):
        """Test narrative contains experimentation/testing section."""
        generator = NarrativeGenerator()
        narrative = generator.generate()

        text_lower = narrative.text.lower()
        assert any(
            term in text_lower
            for term in ["experiment", "test", "evaluate", "trial", "prototype"]
        ), "Narrative should include experimentation activities"

    def test_includes_failure_section(self):
        """Test narrative documents failures and iterations."""
        generator = NarrativeGenerator()
        narrative = generator.generate()

        text_lower = narrative.text.lower()
        assert any(
            term in text_lower
            for term in ["fail", "didn't work", "unsuccessful", "iteration", "attempt"]
        ), "Narrative should document failures"

    def test_includes_iteration_section(self):
        """Test narrative documents iterative refinement."""
        generator = NarrativeGenerator()
        narrative = generator.generate()

        text_lower = narrative.text.lower()
        assert any(
            term in text_lower
            for term in ["iteration", "refine", "modify", "adjust", "alternative"]
        ), "Narrative should document iteration process"


class TestProcessOfExperimentation:
    """Test narrative focuses on Process of Experimentation."""

    def test_focuses_on_process_of_experimentation(self):
        """Test that narrative emphasizes experimentation process."""
        generator = NarrativeGenerator()
        narrative = generator.generate()

        text_lower = narrative.text.lower()
        # Should contain experimentation-related language
        experimentation_terms = [
            "experiment",
            "hypothesis",
            "test",
            "trial",
            "evaluate",
            "uncertainty",
            "alternative",
        ]
        found_terms = sum(1 for term in experimentation_terms if term in text_lower)
        assert found_terms >= 3, f"Expected at least 3 experimentation terms, found {found_terms}"


class TestTechnicalVsBusinessRisk:
    """Test that narrative filters business risk from technical risk."""

    def test_emphasizes_technical_risk(self):
        """Test narrative focuses on technical uncertainty."""
        generator = NarrativeGenerator()
        narrative = generator.generate()

        text_lower = narrative.text.lower()
        technical_terms = [
            "technical",
            "algorithm",
            "architecture",
            "performance",
            "implementation",
            "engineering",
        ]
        found = sum(1 for term in technical_terms if term in text_lower)
        assert found >= 2, "Narrative should emphasize technical challenges"

    def test_does_not_emphasize_business_risk(self):
        """Test narrative minimizes business/market language."""
        generator = NarrativeGenerator()
        narrative = generator.generate()

        text_lower = narrative.text.lower()
        # Business risk terms should NOT be prominent
        business_terms = [
            "market share",
            "revenue",
            "profit",
            "customer acquisition",
            "sales target",
            "competitive advantage",
            "business growth",
        ]
        found = sum(1 for term in business_terms if term in text_lower)
        assert found <= 1, f"Narrative should minimize business risk language, found {found} terms"


class TestStructuredOutput:
    """Test narrative outputs structured data."""

    def test_returns_narrative_object(self):
        """Test generator returns Narrative dataclass."""
        generator = NarrativeGenerator()
        result = generator.generate()

        assert isinstance(result, Narrative)

    def test_narrative_has_text_field(self):
        """Test Narrative has text field."""
        generator = NarrativeGenerator()
        result = generator.generate()

        assert hasattr(result, "text")
        assert isinstance(result.text, str)

    def test_narrative_has_metadata_field(self):
        """Test Narrative has metadata with technical uncertainty evidence."""
        generator = NarrativeGenerator()
        result = generator.generate()

        assert hasattr(result, "metadata")
        assert result.metadata is not None

    def test_metadata_contains_technical_uncertainty_evidence(self):
        """Test metadata documents technical uncertainty evidence."""
        generator = NarrativeGenerator()
        result = generator.generate()

        assert "technical_uncertainties" in result.metadata
        assert isinstance(result.metadata["technical_uncertainties"], list)
        assert len(result.metadata["technical_uncertainties"]) > 0


class TestTemplateBasedGeneration:
    """Test template-based narrative generation."""

    def test_supports_qualifying_template(self):
        """Test generator supports qualifying narrative template."""
        generator = NarrativeGenerator()
        narrative = generator.generate(template_type="qualifying")

        assert narrative.text is not None
        assert len(narrative.text.split()) >= 400

    def test_supports_non_qualifying_template(self):
        """Test generator supports non-qualifying narrative template."""
        generator = NarrativeGenerator()
        narrative = generator.generate(template_type="non_qualifying")

        assert narrative.text is not None
        assert len(narrative.text.split()) >= 400

    def test_supports_edge_case_template(self):
        """Test generator supports edge case narrative template."""
        generator = NarrativeGenerator()
        narrative = generator.generate(template_type="edge_case")

        assert narrative.text is not None
        assert len(narrative.text.split()) >= 400

    def test_different_templates_produce_different_content(self):
        """Test different template types produce distinct narratives."""
        generator = NarrativeGenerator()

        qualifying = generator.generate(template_type="qualifying")
        non_qualifying = generator.generate(template_type="non_qualifying")

        # Should be different content
        assert qualifying.text != non_qualifying.text


class TestSignalInput:
    """Test generator accepts engineering signals for context."""

    def test_accepts_signals_parameter(self):
        """Test generator accepts signals dict for customization."""
        generator = NarrativeGenerator()
        signals = {
            "project_name": "Authentication Service",
            "technology": "OAuth 2.0",
            "challenge": "Token refresh race condition",
        }

        narrative = generator.generate(signals=signals)

        assert narrative.text is not None
        assert len(narrative.text.split()) >= 400

    def test_signals_influence_narrative_content(self):
        """Test signals are reflected in generated narrative."""
        generator = NarrativeGenerator()
        signals = {
            "project_name": "Machine Learning Pipeline",
            "technology": "TensorFlow",
            "challenge": "Model convergence issues",
        }

        narrative = generator.generate(signals=signals)

        # At least one signal element should appear in narrative
        text_lower = narrative.text.lower()
        found = any(
            term.lower() in text_lower
            for term in ["machine learning", "tensorflow", "model", "convergence"]
        )
        assert found, "Signals should influence narrative content"
