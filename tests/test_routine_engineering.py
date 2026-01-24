"""Tests for routine engineering detector (STORY-006).

This test module validates the acceptance criteria for STORY-006:
- Detects 10+ routine engineering keywords: debugging, bug fix, production issue,
  maintenance, refactor, upgrade, migration, optimization, performance tuning, code cleanup
- Each detection includes rejection reason citing IRS guidance
- Returns component score (0-30) based on pattern frequency
- Passes test cases: routine narrative scores >20, research narrative scores <10
"""

import pytest

from bulletproof_green.rules.routine_engineering import RoutineEngineeringDetector


class TestRoutineEngineeringKeywordDetection:
    """Test detection of routine engineering keywords."""

    def test_detects_debugging_keyword(self):
        """Test detection of 'debugging' keyword."""
        detector = RoutineEngineeringDetector()
        narrative = "We spent time debugging the authentication system to fix login issues."

        result = detector.analyze(narrative)

        assert result["score"] > 0
        assert len(result["detections"]) > 0
        assert any("debugging" in d["keyword"].lower() for d in result["detections"])

    def test_detects_bug_fix_keyword(self):
        """Test detection of 'bug fix' keyword."""
        detector = RoutineEngineeringDetector()
        narrative = "The team worked on a bug fix to resolve production errors."

        result = detector.analyze(narrative)

        assert result["score"] > 0
        assert any("bug fix" in d["keyword"].lower() for d in result["detections"])

    def test_detects_production_issue_keyword(self):
        """Test detection of 'production issue' keyword."""
        detector = RoutineEngineeringDetector()
        narrative = "We addressed a production issue that was affecting user login."

        result = detector.analyze(narrative)

        assert result["score"] > 0
        assert any("production issue" in d["keyword"].lower() for d in result["detections"])

    def test_detects_maintenance_keyword(self):
        """Test detection of 'maintenance' keyword."""
        detector = RoutineEngineeringDetector()
        narrative = "Performed routine maintenance on the database servers."

        result = detector.analyze(narrative)

        assert result["score"] > 0
        assert any("maintenance" in d["keyword"].lower() for d in result["detections"])

    def test_detects_refactor_keyword(self):
        """Test detection of 'refactor' keyword."""
        detector = RoutineEngineeringDetector()
        narrative = "We decided to refactor the legacy authentication module."

        result = detector.analyze(narrative)

        assert result["score"] > 0
        assert any("refactor" in d["keyword"].lower() for d in result["detections"])

    def test_detects_upgrade_keyword(self):
        """Test detection of 'upgrade' keyword."""
        detector = RoutineEngineeringDetector()
        narrative = "The project involved an upgrade to the latest version of the framework."

        result = detector.analyze(narrative)

        assert result["score"] > 0
        assert any("upgrade" in d["keyword"].lower() for d in result["detections"])

    def test_detects_migration_keyword(self):
        """Test detection of 'migration' keyword."""
        detector = RoutineEngineeringDetector()
        narrative = "We completed a database migration from MySQL to PostgreSQL."

        result = detector.analyze(narrative)

        assert result["score"] > 0
        assert any("migration" in d["keyword"].lower() for d in result["detections"])

    def test_detects_optimization_keyword(self):
        """Test detection of 'optimization' keyword."""
        detector = RoutineEngineeringDetector()
        narrative = "The team focused on query optimization to improve performance."

        result = detector.analyze(narrative)

        assert result["score"] > 0
        assert any("optimization" in d["keyword"].lower() for d in result["detections"])

    def test_detects_performance_tuning_keyword(self):
        """Test detection of 'performance tuning' keyword."""
        detector = RoutineEngineeringDetector()
        narrative = "We engaged in performance tuning of the API endpoints."

        result = detector.analyze(narrative)

        assert result["score"] > 0
        assert any("performance tuning" in d["keyword"].lower() for d in result["detections"])

    def test_detects_code_cleanup_keyword(self):
        """Test detection of 'code cleanup' keyword."""
        detector = RoutineEngineeringDetector()
        narrative = "The sprint included code cleanup to remove deprecated functions."

        result = detector.analyze(narrative)

        assert result["score"] > 0
        assert any("code cleanup" in d["keyword"].lower() for d in result["detections"])

    def test_detects_at_least_10_keywords(self):
        """Test that detector recognizes at least 10 different routine engineering keywords."""
        detector = RoutineEngineeringDetector()

        # Narrative containing all 10+ keywords
        narrative = """
        Our team worked on debugging, bug fixes, and addressing production issues.
        We performed maintenance, refactored code, and completed upgrades.
        The migration involved optimization and performance tuning.
        We also did code cleanup to improve the codebase.
        """

        result = detector.analyze(narrative)

        # Should detect at least 10 different keywords
        unique_keywords = set(d["keyword"] for d in result["detections"])
        assert len(unique_keywords) >= 10


class TestRejectionReasons:
    """Test that detections include IRS guidance citations."""

    def test_each_detection_includes_rejection_reason(self):
        """Test that each detection includes a rejection reason citing IRS guidance."""
        detector = RoutineEngineeringDetector()
        narrative = "We debugged the system and fixed bugs in production."

        result = detector.analyze(narrative)

        # Each detection should have a reason
        assert all("reason" in d for d in result["detections"])
        assert all(len(d["reason"]) > 0 for d in result["detections"])

    def test_rejection_reasons_cite_irs_guidance(self):
        """Test that rejection reasons reference IRS Section 41 guidance."""
        detector = RoutineEngineeringDetector()
        narrative = "We performed routine maintenance on the application."

        result = detector.analyze(narrative)

        # At least one reason should reference IRS or Section 41
        reasons = [d["reason"] for d in result["detections"]]
        assert any("IRS" in r or "Section 41" in r or "routine" in r.lower()
                   for r in reasons)


class TestComponentScore:
    """Test component score calculation (0-30 range)."""

    def test_returns_score_in_range_0_to_30(self):
        """Test that component score is between 0 and 30."""
        detector = RoutineEngineeringDetector()
        narrative = "We debugged and fixed bugs while performing maintenance."

        result = detector.analyze(narrative)

        assert 0 <= result["score"] <= 30

    def test_score_increases_with_pattern_frequency(self):
        """Test that score increases with more routine engineering patterns."""
        detector = RoutineEngineeringDetector()

        # Narrative with few patterns
        narrative_low = "We developed a novel algorithm."
        result_low = detector.analyze(narrative_low)

        # Narrative with many patterns
        narrative_high = """
        We debugged issues, fixed bugs, resolved production issues,
        performed maintenance, refactored code, completed upgrades,
        ran migrations, optimized queries, did performance tuning,
        and cleaned up code.
        """
        result_high = detector.analyze(narrative_high)

        assert result_high["score"] > result_low["score"]

    def test_zero_score_for_no_patterns(self):
        """Test that score is 0 when no routine engineering patterns found."""
        detector = RoutineEngineeringDetector()
        narrative = "We conducted research on novel machine learning algorithms."

        result = detector.analyze(narrative)

        assert result["score"] == 0
        assert len(result["detections"]) == 0


class TestAcceptanceCriteria:
    """Test the specific acceptance criteria from STORY-006."""

    def test_routine_narrative_scores_above_20(self):
        """Test that routine narrative scores >20."""
        detector = RoutineEngineeringDetector()

        # Heavily routine narrative
        narrative = """
        Our team spent the quarter debugging production issues and fixing bugs.
        We performed regular maintenance on the servers, refactored legacy code,
        and upgraded frameworks. The database migration was completed along with
        query optimization and performance tuning. We also did extensive code cleanup
        to remove deprecated functions.
        """

        result = detector.analyze(narrative)

        assert result["score"] > 20

    def test_research_narrative_scores_below_10(self):
        """Test that research narrative scores <10."""
        detector = RoutineEngineeringDetector()

        # Pure research narrative
        narrative = """
        We conducted fundamental research into novel deep learning architectures
        to address technical uncertainty in multi-modal data fusion. Our experiments
        tested multiple hypotheses about attention mechanisms, and we documented
        several failed approaches before discovering a breakthrough solution.
        The work required developing entirely new mathematical frameworks.
        """

        result = detector.analyze(narrative)

        assert result["score"] < 10


class TestResultStructure:
    """Test the structure of the returned result."""

    def test_result_contains_score_field(self):
        """Test that result contains 'score' field."""
        detector = RoutineEngineeringDetector()
        narrative = "We fixed bugs in the system."

        result = detector.analyze(narrative)

        assert "score" in result
        assert isinstance(result["score"], (int, float))

    def test_result_contains_detections_field(self):
        """Test that result contains 'detections' field."""
        detector = RoutineEngineeringDetector()
        narrative = "We debugged the application."

        result = detector.analyze(narrative)

        assert "detections" in result
        assert isinstance(result["detections"], list)

    def test_detection_contains_required_fields(self):
        """Test that each detection contains keyword and reason fields."""
        detector = RoutineEngineeringDetector()
        narrative = "We performed maintenance on the system."

        result = detector.analyze(narrative)

        if result["detections"]:  # If any detections found
            detection = result["detections"][0]
            assert "keyword" in detection
            assert "reason" in detection
            assert isinstance(detection["keyword"], str)
            assert isinstance(detection["reason"], str)
