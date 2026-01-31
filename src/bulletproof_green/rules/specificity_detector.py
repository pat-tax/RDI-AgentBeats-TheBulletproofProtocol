"""Specificity detector for IRS Section 41 R&D narratives (STORY-032).

Detects specific metrics, timestamps, error codes, and failure citations.
Resists gaming attempts like metric stuffing and superficial metric listing.

Interface: detect(text: str) -> tuple[int, float]
- penalty: 0-10 points (higher = less specific)
- score: 0.0-1.0 (higher = more specific)
"""

from __future__ import annotations

import re


class SpecificityDetector:
    """Detects specificity in narratives through metrics, dates, and measurements.

    Implements detect(text: str) -> tuple[int, float] interface for modular
    detector architecture (STORY-032).
    """

    # Metrics pattern: numbers with units (ms, %, GB, req/s, etc.)
    # Note: No trailing \b after % to match "95%" correctly
    METRIC_PATTERN = re.compile(
        r"\b\d+(?:\.\d+)?(?:\s*(?:ms|s|seconds?|minutes?|hours?|%|GB|MB|KB|req/s|requests?))",
        re.IGNORECASE,
    )

    # Date/timestamp pattern (YYYY-MM-DD, MM/DD/YYYY, etc.)
    DATE_PATTERN = re.compile(
        r"\b\d{4}[-/]\d{2}[-/]\d{2}\b|" r"\b\d{2}[-/]\d{2}[-/]\d{4}\b", re.IGNORECASE
    )

    # Error code pattern (ERROR-XXX, ERR-XXX, E-XXX, etc.)
    ERROR_CODE_PATTERN = re.compile(r"\b(?:ERROR|ERR|E)-\d+\b", re.IGNORECASE)

    # Bare numbers (for fallback detection when units are missing)
    BARE_NUMBER_PATTERN = re.compile(r"\b\d+(?:\.\d+)?\b")

    # Experimentation keywords (to detect context for metrics)
    EXPERIMENTATION_KEYWORDS = [
        r"\bhypothes",
        r"\bexperiment",
        r"\bfail",
        r"\biterat",
        r"\btest",
        r"\battempt",
        r"\btrial",
        r"\buncertain",
        r"\bobserv",
        r"\bretry",
        r"\bimprov",
        r"\breduc",
        r"\bfinal",
    ]

    def _calculate_penalty(
        self,
        total_indicators: int,
        exp_evidence: int,
        bare_numbers_count: int,
        is_metric_stuffing: bool,
    ) -> int:
        """Calculate penalty based on specificity indicators and gaming detection.

        Args:
            total_indicators: Count of metrics + dates + error codes
            exp_evidence: Count of experimentation keywords found
            bare_numbers_count: Count of bare numbers found
            is_metric_stuffing: Whether gaming/stuffing was detected

        Returns:
            int: Penalty score (0-15, evaluator may cap at 10 for risk calculation)
        """
        if is_metric_stuffing:
            return 15  # Penalize gaming heavily (STORY-032 adversarial detection)
        elif total_indicators >= 3:
            return 0  # High specificity
        elif total_indicators == 2:
            return 0  # Reasonable specificity
        elif total_indicators == 1:
            # Error codes and other single indicators acceptable with context
            if exp_evidence >= 2:
                return 0  # Good context
            elif exp_evidence >= 1:
                return 3  # Some context
            else:
                return 5  # Standalone metric
        else:
            # Check if bare numbers provide some specificity
            if bare_numbers_count >= 3:
                return 5  # Some numbers present
            else:
                return 10  # No specificity at all

    def detect(self, text: str) -> tuple[int, float]:
        """Detect specificity in narrative text.

        Checks for:
        - Quantitative metrics with units (45ms, 95%, 1000 req/s)
        - Timestamps and dates (2024-01-15)
        - Error codes (ERROR-503)
        - Failure citations with specific data
        - Context (experimentation narrative vs. metric stuffing)

        Args:
            text: Narrative text to analyze

        Returns:
            tuple[int, float]: (penalty, specificity_score)
                - penalty: 0-10 points (0 = highly specific, 10 = vague)
                - specificity_score: 0.0-1.0 (normalized specificity level)
        """
        # Handle edge cases
        stripped = text.strip()
        if not stripped:
            return (10, 0.0)

        # Count specificity indicators
        metrics = self.METRIC_PATTERN.findall(text)
        dates = self.DATE_PATTERN.findall(text)
        error_codes = self.ERROR_CODE_PATTERN.findall(text)
        bare_numbers = self.BARE_NUMBER_PATTERN.findall(text)

        # Total specificity indicators
        total_indicators = len(metrics) + len(dates) + len(error_codes)

        # Check for experimentation context (use regex for word boundaries)
        text_lower = text.lower()
        exp_evidence = sum(
            1 for pattern in self.EXPERIMENTATION_KEYWORDS if re.search(pattern, text_lower)
        )

        # Detect metric stuffing (STORY-032 adversarial gaming)
        word_count = len(text.split())
        metric_density = (len(metrics) / max(1, word_count)) * 100

        # Detect repeated metrics (e.g., "95% 95% 95%")
        # Allow some repetition (like "from 120ms to 45ms"), but flag excessive
        unique_metrics = set(metrics)
        if len(metrics) > 0:
            repetition_ratio = len(metrics) / len(unique_metrics)
            has_metric_repetition = repetition_ratio >= 2.5  # e.g., 3 metrics, only 1 unique
        else:
            has_metric_repetition = False

        # Check for comparison patterns (legitimate before/after metrics)
        # Patterns like "from X to Y", "reduced from X", "decreased from X to Y"
        comparison_patterns = [
            r"from\s+\d+[\w.%]+\s+to\s+\d+[\w.%]+",  # "from 200ms to 45ms"
            r"reduced?\s+(?:from\s+)?\d+[\w.%]+\s+to\s+\d+[\w.%]+",  # "reduced from 200ms to 45ms"
            r"decreased?\s+(?:from\s+)?\d+[\w.%]+\s+to\s+\d+[\w.%]+",  # "decreased 1.2GB to 800MB"
            r"improved?\s+(?:from\s+)?\d+[\w.%]+\s+to\s+\d+[\w.%]+",  # "improved from 5% to 1%"
            r"dropped?\s+(?:from\s+)?\d+[\w.%]+\s+to\s+\d+[\w.%]+",  # "dropped from 5% to 0.2%"
        ]
        has_comparison_metrics = any(
            re.search(pattern, text.lower()) for pattern in comparison_patterns
        )

        # Gaming detection rules:
        # 1. Metric repetition (same metric repeated 2.5+ times)
        # 2. High density (>30%) with no/weak exp evidence AND no comparisons
        # 3. Very high density (>50%) regardless of evidence (unless comparisons)
        # 4. Many metrics (>=5) with weak context: no error codes/dates/comparisons AND weak exp
        has_technical_context = len(error_codes) > 0 or len(dates) > 0 or has_comparison_metrics
        is_metric_stuffing = (
            has_metric_repetition
            or (metric_density > 30 and exp_evidence <= 1 and not has_comparison_metrics)
            or (metric_density > 50 and not has_comparison_metrics)
            or (len(metrics) >= 5 and exp_evidence <= 2 and not has_technical_context)
        )

        # Calculate base specificity score (0.0-1.0)
        # Good narratives have 3+ specific indicators
        base_score = min(1.0, total_indicators / 3.0)

        # Adjust for bare numbers (some specificity even without units)
        if total_indicators < 3 and len(bare_numbers) >= 2:
            base_score = min(1.0, base_score + (len(bare_numbers) * 0.15))

        # Penalize metric stuffing (reduce score for gaming attempts)
        if is_metric_stuffing:
            specificity_score = max(0.0, base_score * 0.4)  # Reduce score by 60%
        else:
            specificity_score = base_score

        # Calculate penalty based on indicators and gaming detection
        penalty = self._calculate_penalty(
            total_indicators, exp_evidence, len(bare_numbers), is_metric_stuffing
        )

        return (penalty, specificity_score)
