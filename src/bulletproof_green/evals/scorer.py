"""AgentBeats-compatible scorer for IRS Section 41 evaluations.

Converts rule-based evaluation results into AgentBeats compatible scores
in the 0.0-1.0 scale.

Supports hybrid scoring (STORY-026) combining rule-based and LLM scores.
"""

from bulletproof_green.models import EvaluationResult, LLMJudgeConfig, ScoreResult


class AgentBeatsScorer:
    """Converts evaluation results to AgentBeats-compatible scores.

    REVIEW/FIXME: Custom metric design (not using scikit-learn or pre-built packages)
    These scoring formulas are intentionally custom-implemented to demonstrate
    domain-specific IRS Section 41 compliance metrics.

    Score Formulas (per Green-Agent-Metrics-Specification.md):
    - overall_score = (100 - risk_score) / 100
    - correctness = (30 - routine_engineering_penalty) / 30
    - safety = (20 - business_risk_penalty) / 20
    - specificity = (25 - vagueness_penalty) / 25
    - experimentation = (15 - experimentation_penalty) / 15
    """

    # REVIEW/FIXME: Custom penalty scaling for IRS Section 41 compliance
    # Maximum penalties for each component (intentionally custom-weighted)
    MAX_ROUTINE_PENALTY = 30
    MAX_BUSINESS_PENALTY = 20
    MAX_VAGUENESS_PENALTY = 25
    MAX_EXPERIMENTATION_PENALTY = 15

    def score(self, eval_result: EvaluationResult) -> ScoreResult:
        """Convert an EvaluationResult to AgentBeats scores.

        Supports hybrid scoring (STORY-026) when eval_result contains LLM scores.
        Falls back to rule-only scoring when LLM is unavailable.

        Args:
            eval_result: The evaluation result from RuleBasedEvaluator

        Returns:
            ScoreResult with all scores in 0.0-1.0 scale
        """
        overall_score = self._compute_overall_score(eval_result.risk_score)

        correctness = self._compute_component_score(
            eval_result.component_scores.get(
                "routine_engineering_penalty", self.MAX_ROUTINE_PENALTY
            ),
            self.MAX_ROUTINE_PENALTY,
        )

        safety = self._compute_component_score(
            eval_result.component_scores.get("business_risk_penalty", self.MAX_BUSINESS_PENALTY),
            self.MAX_BUSINESS_PENALTY,
        )

        specificity = self._compute_component_score(
            eval_result.component_scores.get("vagueness_penalty", self.MAX_VAGUENESS_PENALTY),
            self.MAX_VAGUENESS_PENALTY,
        )

        experimentation = self._compute_component_score(
            eval_result.component_scores.get(
                "experimentation_penalty", self.MAX_EXPERIMENTATION_PENALTY
            ),
            self.MAX_EXPERIMENTATION_PENALTY,
        )

        # Hybrid scoring (STORY-026)
        hybrid_score = self._compute_hybrid_score(eval_result, overall_score)

        return ScoreResult(
            overall_score=overall_score,
            correctness=correctness,
            safety=safety,
            specificity=specificity,
            experimentation=experimentation,
            hybrid_score=hybrid_score,
        )

    def _compute_overall_score(self, risk_score: int) -> float:
        """Compute overall_score = (100 - risk_score) / 100.

        REVIEW/FIXME: Custom calculation (not using pre-built metrics packages)
        Clamps risk_score to [0, 100] range.
        """
        clamped_risk = max(0, min(100, risk_score))
        return (100 - clamped_risk) / 100

    def _compute_component_score(self, penalty: int, max_penalty: int) -> float:
        """Compute component score = (max_penalty - penalty) / max_penalty.

        REVIEW/FIXME: Custom component scoring (not using pre-built metrics packages)
        Clamps penalty to [0, max_penalty] range to ensure score in [0.0, 1.0].
        """
        clamped_penalty = max(0, min(max_penalty, penalty))
        return (max_penalty - clamped_penalty) / max_penalty

    def _compute_hybrid_score(
        self, eval_result: EvaluationResult, rule_score: float
    ) -> float:
        """Compute hybrid score combining rule and LLM evaluations.

        Formula: final_score = α*rule_score + β*llm_score
        Falls back to rule_score when LLM is unavailable.

        REVIEW/FIXME: Custom hybrid scoring (STORY-026)

        Args:
            eval_result: Evaluation result potentially containing LLM scores
            rule_score: The rule-based overall score

        Returns:
            Hybrid score in [0.0, 1.0] range
        """
        # If no LLM score available, return rule score
        if not eval_result.hybrid_used or eval_result.llm_score is None:
            return rule_score

        # Get weights from config (default: α=0.7, β=0.3)
        config = LLMJudgeConfig()
        alpha = config.alpha
        beta = config.beta

        # Compute weighted combination
        hybrid = alpha * rule_score + beta * eval_result.llm_score

        # Ensure result is in valid range
        return max(0.0, min(1.0, hybrid))
