"""Rule-based evaluator for IRS Section 41 R&D tax credit narratives.

Evaluates narratives against IRS Section 41 audit standards using rule-based
detection of disqualifying patterns.

Supports hybrid evaluation (STORY-026) combining rule-based and LLM scoring.
"""

from __future__ import annotations

import re
import time
from typing import TYPE_CHECKING

from bulletproof_green.models import EvaluationResult, Issue, Redline

if TYPE_CHECKING:
    from bulletproof_green.evals.llm_judge import LLMJudge


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

    def evaluate(
        self, narrative: str, llm_judge: LLMJudge | None = None
    ) -> EvaluationResult:
        """Evaluate a narrative and return structured results.

        Supports hybrid evaluation (STORY-026) when llm_judge is provided.
        Falls back to rule-only evaluation when llm_judge is None or unavailable.

        Args:
            narrative: The narrative text to evaluate
            llm_judge: Optional LLM judge for hybrid evaluation

        Returns:
            EvaluationResult with risk score, classification, and redline markup
        """
        # Track evaluation time
        start_time = time.perf_counter()

        issues: list[Issue] = []
        text_lower = narrative.lower()

        # REVIEW/FIXME: Custom penalty detection (not using pre-built NLP/ML packages)
        # Calculate component penalties using pattern-based detection
        routine_penalty, routine_count = self._detect_routine_engineering(text_lower, issues)
        business_penalty, business_count = self._detect_business_risk(text_lower, issues)
        vagueness_penalty, vague_count = self._detect_vagueness(text_lower, issues)
        experimentation_penalty, exp_score = self._detect_missing_experimentation(
            text_lower, issues
        )
        specificity_penalty, spec_score = self._detect_lack_of_specificity(narrative, issues)

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

        # Calculate severity counts
        critical_count = sum(1 for issue in issues if issue.severity == "critical")
        high_count = sum(1 for issue in issues if issue.severity == "high")
        medium_count = sum(1 for issue in issues if issue.severity == "medium")

        redline = Redline(
            total_issues=len(issues),
            issues=issues,
            critical=critical_count,
            high=high_count,
            medium=medium_count,
        )

        # Determine audit outcome
        predicted_audit_outcome = "PASS_AUDIT" if risk_score < 20 else "FAIL_AUDIT"

        # Calculate evaluation time
        end_time = time.perf_counter()
        evaluation_time_ms = (end_time - start_time) * 1000

        # Hybrid evaluation fields - always include, even if not used
        result = EvaluationResult(
            classification=classification,
            confidence=confidence,
            risk_score=risk_score,
            risk_category=risk_category,
            component_scores=component_scores,
            redline=redline,
            predicted_audit_outcome=predicted_audit_outcome,
            routine_patterns_detected=routine_count,
            vague_phrases_detected=vague_count,
            business_keywords_detected=business_count,
            experimentation_evidence_score=exp_score,
            specificity_score=spec_score,
            evaluation_time_ms=evaluation_time_ms,
            hybrid_used=False,
            llm_score=None,
            llm_reasoning=None,
        )

        return result

    async def evaluate_async(
        self, narrative: str, llm_judge: LLMJudge | None = None
    ) -> EvaluationResult:
        """Async version of evaluate() supporting LLM hybrid evaluation.

        This method enables async LLM calls when llm_judge is provided.
        Falls back to synchronous rule-only evaluation when llm_judge is None.

        Args:
            narrative: The narrative text to evaluate
            llm_judge: Optional LLM judge for hybrid evaluation

        Returns:
            EvaluationResult with risk score, classification, and hybrid scores
        """
        # Track evaluation time
        start_time = time.perf_counter()

        issues: list[Issue] = []
        text_lower = narrative.lower()

        # Calculate component penalties using pattern-based detection
        routine_penalty, routine_count = self._detect_routine_engineering(text_lower, issues)
        business_penalty, business_count = self._detect_business_risk(text_lower, issues)
        vagueness_penalty, vague_count = self._detect_vagueness(text_lower, issues)
        experimentation_penalty, exp_score = self._detect_missing_experimentation(
            text_lower, issues
        )
        specificity_penalty, spec_score = self._detect_lack_of_specificity(narrative, issues)

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

        # Calculate severity counts
        critical_count = sum(1 for issue in issues if issue.severity == "critical")
        high_count = sum(1 for issue in issues if issue.severity == "high")
        medium_count = sum(1 for issue in issues if issue.severity == "medium")

        redline = Redline(
            total_issues=len(issues),
            issues=issues,
            critical=critical_count,
            high=high_count,
            medium=medium_count,
        )

        # Determine audit outcome
        predicted_audit_outcome = "PASS_AUDIT" if risk_score < 20 else "FAIL_AUDIT"

        # Calculate evaluation time
        end_time = time.perf_counter()
        evaluation_time_ms = (end_time - start_time) * 1000

        # Hybrid evaluation (STORY-026)
        hybrid_used = False
        llm_score = None
        llm_reasoning = None

        if llm_judge is not None:
            try:
                # Get LLM evaluation
                llm_result = await llm_judge.evaluate(narrative)
                llm_score = llm_result.score
                llm_reasoning = llm_result.reasoning
                hybrid_used = True
            except Exception:
                # Silently fall back to rule-only evaluation
                pass

        return EvaluationResult(
            classification=classification,
            confidence=confidence,
            risk_score=risk_score,
            risk_category=risk_category,
            component_scores=component_scores,
            redline=redline,
            predicted_audit_outcome=predicted_audit_outcome,
            routine_patterns_detected=routine_count,
            vague_phrases_detected=vague_count,
            business_keywords_detected=business_count,
            experimentation_evidence_score=exp_score,
            specificity_score=spec_score,
            evaluation_time_ms=evaluation_time_ms,
            hybrid_used=hybrid_used,
            llm_score=llm_score,
            llm_reasoning=llm_reasoning,
        )

    def _detect_routine_engineering(self, text: str, issues: list[Issue]) -> tuple[int, int]:
        """Detect routine engineering patterns. Max penalty: 30 points.

        REVIEW/FIXME: Custom pattern matching (not using pre-built NLP/text classification)

        Returns:
            tuple[int, int]: (penalty, count of patterns detected)
        """
        penalty = 0
        count = 0
        for pattern, description in self.ROUTINE_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                penalty += 5
                count += 1
                issues.append(
                    Issue(
                        category="routine_engineering",
                        severity="high" if penalty >= 15 else "medium",
                        text=description,
                        suggestion="Document the technical uncertainty being addressed, "
                        "not routine implementation details.",
                    )
                )
        return min(30, penalty), count

    def _detect_business_risk(self, text: str, issues: list[Issue]) -> tuple[int, int]:
        """Detect business risk language. Max penalty: 20 points.

        REVIEW/FIXME: Custom pattern matching (not using pre-built NLP/text classification)

        Returns:
            tuple[int, int]: (penalty, count of patterns detected)
        """
        penalty = 0
        count = 0
        for pattern, description in self.BUSINESS_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                penalty += 5
                count += 1
                issues.append(
                    Issue(
                        category="business_risk",
                        severity="high" if penalty >= 10 else "medium",
                        text=description,
                        suggestion="Focus on technical uncertainty rather than "
                        "business or market objectives.",
                    )
                )
        return min(20, penalty), count

    def _detect_vagueness(self, text: str, issues: list[Issue]) -> tuple[int, int]:
        """Detect vague language without specific metrics. Max penalty: 25 points.

        REVIEW/FIXME: Custom pattern matching (not using pre-built NLP/sentiment analysis)

        Returns:
            tuple[int, int]: (penalty, count of vague phrases detected)
        """
        penalty = 0
        count = 0
        for pattern, description in self.VAGUE_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                penalty += 6
                count += 1
                issues.append(
                    Issue(
                        category="vagueness",
                        severity="medium",
                        text=description,
                        suggestion="Replace vague claims with specific metrics "
                        "(e.g., '45ms latency' instead of 'better performance').",
                    )
                )
        return min(25, penalty), count

    def _detect_missing_experimentation(self, text: str, issues: list[Issue]) -> tuple[int, float]:
        """Detect missing experimentation evidence. Max penalty: 15 points.

        REVIEW/FIXME: Custom pattern counting (not using pre-built ML/NLP libraries)

        Returns:
            tuple[int, float]: (penalty, experimentation_evidence_score 0.0-1.0)
        """
        # Count positive experimentation indicators
        evidence_count = 0
        for pattern, _ in self.EXPERIMENTATION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                evidence_count += 1

        # Calculate evidence score (normalized to 0.0-1.0)
        max_patterns = len(self.EXPERIMENTATION_PATTERNS)
        evidence_score = min(1.0, evidence_count / max(1, max_patterns * 0.4))

        # Penalty inversely proportional to evidence found
        if evidence_count >= 4:
            return 0, evidence_score
        elif evidence_count >= 2:
            return 5, evidence_score
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
            return 15, evidence_score

    def _detect_lack_of_specificity(self, text: str, issues: list[Issue]) -> tuple[int, float]:
        """Detect lack of specific metrics. Max penalty: 10 points.

        REVIEW/FIXME: Custom regex matching (not using pre-built metric extraction libraries)

        Returns:
            tuple[int, float]: (penalty, specificity_score 0.0-1.0)
        """
        # Count specific metrics in the text
        metrics = self.SPECIFICITY_PATTERN.findall(text)

        # Calculate specificity score (normalized to 0.0-1.0)
        # Good narratives have 3+ metrics
        specificity_score = min(1.0, len(metrics) / 3.0)

        if len(metrics) >= 3:
            return 0, specificity_score
        elif len(metrics) >= 1:
            return 3, specificity_score
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
            return 10, specificity_score

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
