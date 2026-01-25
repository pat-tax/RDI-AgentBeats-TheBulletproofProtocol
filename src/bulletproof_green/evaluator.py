"""Rule-based evaluator for IRS Section 41 R&D tax credit narratives.

Evaluates narratives against IRS Section 41 audit standards using rule-based
detection of disqualifying patterns.
"""

import re
from dataclasses import dataclass, field


@dataclass
class Issue:
    """Represents a detected issue in the narrative."""

    category: str
    severity: str
    text: str
    suggestion: str


@dataclass
class Redline:
    """Redline markup containing detected issues."""

    total_issues: int = 0
    issues: list[Issue] = field(default_factory=list)


@dataclass
class EvaluationResult:
    """Structured evaluation result per Green-Agent-Metrics-Specification.md."""

    classification: str = "NON_QUALIFYING"
    confidence: float = 0.0
    risk_score: int = 100
    risk_category: str = "CRITICAL"
    component_scores: dict[str, int] = field(default_factory=dict)
    redline: Redline = field(default_factory=Redline)


class RuleBasedEvaluator:
    """Evaluates narratives against IRS Section 41 using rule-based detection.

    REVIEW/FIXME: Custom rule-based evaluation (intentionally not using pre-built
    packages like scikit-learn, spaCy, or other ML/NLP libraries). All pattern
    detection is implemented from first principles for domain-specific IRS compliance.
    """

    # REVIEW/FIXME: Custom-crafted patterns (not using pre-built pattern libraries)
    # Routine engineering patterns (IRS considers these non-qualifying)
    ROUTINE_PATTERNS: list[tuple[str, str]] = [
        (r"\broutine\s+maintenance\b", "routine maintenance"),
        (r"\bdebug(?:ging)?\b", "debugging existing code"),
        (r"\bfix(?:ed|ing)?\s+bugs?\b", "fixing bugs"),
        (r"\bpatch(?:es|ing)?\b", "applying patches"),
        (r"\boff-the-shelf\b", "off-the-shelf components"),
        (r"\bvendor\s+software\b", "adapting vendor software"),
        (r"\bstandard\s+(?:integration|procedures?|engineering)\b", "standard procedures"),
        (r"\bmigrat(?:ed|ion|ing)\b", "migration work"),
        (r"\bport(?:ed|ing)?\b", "porting activities"),
        (r"\bminor\s+customization\b", "minor customization"),
        (r"\bpredictable\s+outcomes?\b", "predictable outcomes"),
        (r"\bdocumented\s+procedures?\b", "documented procedures"),
        (r"\bexisting\s+(?:code|solutions?)\b", "adapting existing solutions"),
    ]

    # REVIEW/FIXME: Custom-crafted patterns (not using pre-built pattern libraries)
    # Business risk patterns (should focus on technical risk instead)
    BUSINESS_PATTERNS: list[tuple[str, str]] = [
        (r"\bmarket\s+share\b", "market share focus"),
        (r"\brevenue\b", "revenue focus"),
        (r"\bprofit(?:s|ability)?\b", "profit focus"),
        (r"\bcustomer\s+satisfaction\b", "customer satisfaction"),
        (r"\bcompetitive\s+position(?:ing)?\b", "competitive positioning"),
        (r"\bsales\s+(?:growth|target)\b", "sales targets"),
        (r"\bbusiness\s+(?:growth|objectives?)\b", "business objectives"),
        (r"\bmarket\s+segments?\b", "market segments"),
        (r"\bstay\s+competitive\b", "competitive pressure"),
    ]

    # REVIEW/FIXME: Custom-crafted patterns (not using pre-built pattern libraries)
    # Vague language patterns (need specific metrics instead)
    VAGUE_PATTERNS: list[tuple[str, str]] = [
        (r"\bsignificant(?:ly)?\s+improv(?:ed|ements?)\b", "significant improvements"),
        (r"\bgreat(?:ly)?\s+(?:enhanced|improved)\b", "greatly enhanced"),
        (r"\bsubstantial\s+gains?\b", "substantial gains"),
        (r"\bbetter\s+performance\b", "better performance"),
        (r"\bvery\s+successful\b", "very successful"),
        (r"\bgreat\s+(?:success|improvements?)\b", "great success"),
        (r"\bmuch\s+(?:faster|better|improved)\b", "much better"),
        (r"\bthings\s+work\s+(?:faster|better)\b", "vague improvement claim"),
    ]

    # REVIEW/FIXME: Custom-crafted patterns (not using pre-built pattern libraries)
    # Experimentation evidence patterns (positive indicators)
    EXPERIMENTATION_PATTERNS: list[tuple[str, str]] = [
        (r"\bfail(?:ed|ure)?\b", "failure documentation"),
        (r"\bhypothes(?:is|es)\b", "hypothesis formulation"),
        (r"\bexperiment(?:s|ation|ed|ing)?\b", "experimentation"),
        (r"\biteration(?:s)?\b", "iterative process"),
        (r"\balternative(?:s)?\s+(?:approach|solution|algorithm)?\b", "alternative approaches"),
        (r"\bunsuccessful\b", "unsuccessful attempts"),
        (r"\bdidn'?t\s+work\b", "documented failures"),
        (r"\btechnical\s+uncertainty\b", "technical uncertainty"),
        (r"\bunknown\b", "unknown outcomes"),
        (r"\buncertain\b", "uncertainty"),
    ]

    # REVIEW/FIXME: Custom-crafted regex pattern (not using pre-built metric libraries)
    # Specificity patterns (numbers and metrics)
    SPECIFICITY_PATTERN = re.compile(
        r"\b\d+(?:\.\d+)?(?:\s*(?:ms|s|seconds?|minutes?|hours?|%|GB|MB|KB|req/s|requests?))\b",
        re.IGNORECASE,
    )

    def evaluate(self, narrative: str) -> EvaluationResult:
        """Evaluate a narrative and return structured results.

        Args:
            narrative: The narrative text to evaluate

        Returns:
            EvaluationResult with risk score, classification, and redline markup
        """
        issues: list[Issue] = []
        text_lower = narrative.lower()

        # REVIEW/FIXME: Custom penalty detection (not using pre-built NLP/ML packages)
        # Calculate component penalties using pattern-based detection
        routine_penalty = self._detect_routine_engineering(text_lower, issues)
        business_penalty = self._detect_business_risk(text_lower, issues)
        vagueness_penalty = self._detect_vagueness(text_lower, issues)
        experimentation_penalty = self._detect_missing_experimentation(text_lower, issues)
        specificity_penalty = self._detect_lack_of_specificity(narrative, issues)

        # REVIEW/FIXME: Custom risk aggregation (intentionally hand-crafted, not ML-based)
        # Calculate total risk score (sum of penalties, capped at 100)
        risk_score = min(
            100,
            routine_penalty
            + business_penalty
            + vagueness_penalty
            + experimentation_penalty
            + specificity_penalty,
        )

        # Determine classification and category
        classification = "QUALIFYING" if risk_score < 20 else "NON_QUALIFYING"
        risk_category = self._get_risk_category(risk_score)

        # Calculate confidence based on pattern matches
        total_patterns = len(issues)
        confidence = min(0.95, 0.5 + (total_patterns * 0.05))

        component_scores = {
            "routine_engineering_penalty": routine_penalty,
            "business_risk_penalty": business_penalty,
            "vagueness_penalty": vagueness_penalty,
            "experimentation_penalty": experimentation_penalty,
            "specificity_penalty": specificity_penalty,
        }

        redline = Redline(total_issues=len(issues), issues=issues)

        return EvaluationResult(
            classification=classification,
            confidence=confidence,
            risk_score=risk_score,
            risk_category=risk_category,
            component_scores=component_scores,
            redline=redline,
        )

    def _detect_routine_engineering(self, text: str, issues: list[Issue]) -> int:
        """Detect routine engineering patterns. Max penalty: 30 points.

        REVIEW/FIXME: Custom pattern matching (not using pre-built NLP/text classification)
        """
        penalty = 0
        for pattern, description in self.ROUTINE_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                penalty += 5
                issues.append(
                    Issue(
                        category="routine_engineering",
                        severity="high" if penalty >= 15 else "medium",
                        text=description,
                        suggestion="Document the technical uncertainty being addressed, "
                        "not routine implementation details.",
                    )
                )
        return min(30, penalty)

    def _detect_business_risk(self, text: str, issues: list[Issue]) -> int:
        """Detect business risk language. Max penalty: 20 points.

        REVIEW/FIXME: Custom pattern matching (not using pre-built NLP/text classification)
        """
        penalty = 0
        for pattern, description in self.BUSINESS_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                penalty += 5
                issues.append(
                    Issue(
                        category="business_risk",
                        severity="high" if penalty >= 10 else "medium",
                        text=description,
                        suggestion="Focus on technical uncertainty rather than "
                        "business or market objectives.",
                    )
                )
        return min(20, penalty)

    def _detect_vagueness(self, text: str, issues: list[Issue]) -> int:
        """Detect vague language without specific metrics. Max penalty: 25 points.

        REVIEW/FIXME: Custom pattern matching (not using pre-built NLP/sentiment analysis)
        """
        penalty = 0
        for pattern, description in self.VAGUE_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                penalty += 6
                issues.append(
                    Issue(
                        category="vagueness",
                        severity="medium",
                        text=description,
                        suggestion="Replace vague claims with specific metrics "
                        "(e.g., '45ms latency' instead of 'better performance').",
                    )
                )
        return min(25, penalty)

    def _detect_missing_experimentation(self, text: str, issues: list[Issue]) -> int:
        """Detect missing experimentation evidence. Max penalty: 15 points.

        REVIEW/FIXME: Custom pattern counting (not using pre-built ML/NLP libraries)
        """
        # Count positive experimentation indicators
        evidence_count = 0
        for pattern, _ in self.EXPERIMENTATION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                evidence_count += 1

        # Penalty inversely proportional to evidence found
        if evidence_count >= 4:
            return 0
        elif evidence_count >= 2:
            return 5
        else:
            # Add issue for missing experimentation
            issues.append(
                Issue(
                    category="experimentation",
                    severity="high",
                    text="missing experimentation evidence",
                    suggestion="Document specific hypotheses, experiments conducted, "
                    "failures encountered, and iterative refinements.",
                )
            )
            return 15

    def _detect_lack_of_specificity(self, text: str, issues: list[Issue]) -> int:
        """Detect lack of specific metrics. Max penalty: 10 points.

        REVIEW/FIXME: Custom regex matching (not using pre-built metric extraction libraries)
        """
        # Count specific metrics in the text
        metrics = self.SPECIFICITY_PATTERN.findall(text)

        if len(metrics) >= 3:
            return 0
        elif len(metrics) >= 1:
            return 3
        else:
            issues.append(
                Issue(
                    category="specificity",
                    severity="low",
                    text="lack of specific metrics",
                    suggestion="Include quantitative metrics (e.g., latency, "
                    "throughput, memory usage, error rates).",
                )
            )
            return 10

    def _get_risk_category(self, risk_score: int) -> str:
        """Map risk score to risk category."""
        if risk_score <= 20:
            return "LOW"
        elif risk_score <= 40:
            return "MODERATE"
        elif risk_score <= 60:
            return "HIGH"
        elif risk_score <= 80:
            return "VERY_HIGH"
        else:
            return "CRITICAL"
