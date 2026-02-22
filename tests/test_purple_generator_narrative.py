"""Tests for Purple Agent narrative generator (STORY-001).

Validates core behavior:
- Generates ~500-word narrative
- Follows Four-Part Test structure
- Filters business risk from technical risk
- Template-based generation with signals support
"""

from bulletproof_purple.generator import NarrativeGenerator


class TestNarrativeGeneration:
    """Test core narrative generation behavior."""

    def test_generates_approximately_500_words(self):
        """Test that generator produces ~500 word narrative."""
        generator = NarrativeGenerator()
        narrative = generator.generate()

        word_count = len(narrative.text.split())
        assert 450 <= word_count <= 550, f"Expected ~500 words, got {word_count}"

    def test_includes_four_part_test_elements(self):
        """Test narrative contains Four-Part Test elements."""
        generator = NarrativeGenerator()
        narrative = generator.generate()

        text_lower = narrative.text.lower()

        # Hypothesis/uncertainty
        has_hypothesis = any(
            t in text_lower for t in ["hypothesis", "technical uncertainty", "uncertain", "unknown"]
        )
        # Experimentation
        has_experiment = any(
            t in text_lower for t in ["experiment", "test", "evaluate", "trial", "prototype"]
        )
        # Failure/iteration
        has_failure = any(
            t in text_lower for t in ["fail", "didn't work", "unsuccessful", "iteration", "attempt"]
        )

        assert has_hypothesis, "Should include hypothesis or technical uncertainty"
        assert has_experiment, "Should include experimentation activities"
        assert has_failure, "Should document failures or iterations"


class TestTechnicalVsBusinessRisk:
    """Test that narrative filters business risk from technical risk."""

    def test_emphasizes_technical_over_business_risk(self):
        """Test narrative focuses on technical uncertainty, not business risk."""
        generator = NarrativeGenerator()
        narrative = generator.generate()

        text_lower = narrative.text.lower()

        technical_terms = [
            "technical",
            "algorithm",
            "architecture",
            "performance",
            "implementation",
        ]
        business_terms = [
            "market share",
            "revenue",
            "profit",
            "customer acquisition",
            "sales target",
        ]

        technical_count = sum(1 for t in technical_terms if t in text_lower)
        business_count = sum(1 for t in business_terms if t in text_lower)

        assert technical_count >= 2, "Should emphasize technical challenges"
        assert business_count <= 1, "Should minimize business risk language"


class TestTemplateBasedGeneration:
    """Test template-based narrative generation."""

    def test_different_templates_produce_different_content(self):
        """Test different template types produce distinct narratives."""
        generator = NarrativeGenerator()

        qualifying = generator.generate(template_type="qualifying")
        non_qualifying = generator.generate(template_type="non_qualifying")

        assert qualifying.text != non_qualifying.text
        assert len(qualifying.text.split()) >= 400
        assert len(non_qualifying.text.split()) >= 400

    def test_signals_influence_narrative_content(self):
        """Test signals are reflected in generated narrative."""
        generator = NarrativeGenerator()
        signals = {
            "project_name": "Machine Learning Pipeline",
            "technology": "TensorFlow",
            "challenge": "Model convergence issues",
        }

        narrative = generator.generate(signals=signals)

        text_lower = narrative.text.lower()
        found = any(
            t.lower() in text_lower
            for t in ["machine learning", "tensorflow", "model", "convergence"]
        )
        assert found, "Signals should influence narrative content"


class TestMetadataOutput:
    """Test metadata in generated narratives."""

    def test_metadata_contains_technical_uncertainties(self):
        """Test metadata documents technical uncertainty evidence."""
        generator = NarrativeGenerator()
        result = generator.generate()

        assert "technical_uncertainties" in result.metadata
        assert len(result.metadata["technical_uncertainties"]) > 0
