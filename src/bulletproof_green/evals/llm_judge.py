"""LLM-as-Judge for hybrid evaluation of IRS Section 41 narratives.

Combines rule-based evaluation (deterministic, primary) with LLM semantic analysis
(secondary) using the formula: final_score = α*rule_score + β*llm_score.

Gracefully degrades to rule-only scoring when LLM is unavailable.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from bulletproof_green.evals.models import HybridScoreResult, LLMJudgeConfig, LLMScoreResult
from bulletproof_green.settings import settings

logger = logging.getLogger(__name__)


class LLMJudge:
    """LLM-as-Judge for semantic analysis of IRS Section 41 narratives.

    Uses OpenAI GPT-4 (or equivalent) to provide semantic understanding that
    complements the deterministic rule-based evaluation.

    Attributes:
        config: Configuration settings for the judge.
    """

    def __init__(
        self,
        config: LLMJudgeConfig | None = None,
        api_key: str | None = None,
    ) -> None:
        """Initialize the LLM Judge.

        Args:
            config: Optional configuration (uses defaults if not provided).
            api_key: Optional OpenAI API key (falls back to settings.openai_api_key).
        """
        self.config = config if config is not None else LLMJudgeConfig()
        self._api_key = api_key or settings.openai_api_key
        self._client: Any = None

        # Initialize OpenAI client if API key is available
        if self._api_key:
            try:
                from openai import AsyncOpenAI

                self._client = AsyncOpenAI(api_key=self._api_key)
            except ImportError:
                logger.warning("OpenAI package not installed. LLM evaluation disabled.")
                self._client = None

    async def evaluate(self, narrative: str) -> LLMScoreResult:
        """Evaluate a narrative using LLM semantic analysis.

        Args:
            narrative: The narrative text to evaluate.

        Returns:
            LLMScoreResult with score, reasoning, and category breakdown.

        Raises:
            Exception: If LLM call fails.
        """
        response = await self._call_llm(narrative)

        # Validate response - model provides defaults for missing fields
        return LLMScoreResult.model_validate(response)

    async def hybrid_score(
        self,
        narrative: str,
        rule_score: float,
    ) -> HybridScoreResult:
        """Compute hybrid score combining rule and LLM evaluations.

        Formula: final_score = α*rule_score + β*llm_score

        Falls back to rule-only scoring if LLM is unavailable.

        Args:
            narrative: The narrative text to evaluate.
            rule_score: Score from rule-based evaluation (0-1 scale).

        Returns:
            HybridScoreResult with combined and component scores.
        """
        # Check if LLM is available
        if not self._api_key or not self._client:
            logger.warning("LLM unavailable (no API key). Using rule-only scoring.")
            return HybridScoreResult(
                final_score=rule_score,
                rule_score=rule_score,
                llm_score=None,
                alpha=self.config.alpha,
                beta=self.config.beta,
                fallback_used=True,
            )

        try:
            llm_result = await self.evaluate(narrative)
            llm_score = llm_result.score

            # Compute hybrid score: final = α*rule + β*llm
            final_score = self.config.alpha * rule_score + self.config.beta * llm_score

            return HybridScoreResult(
                final_score=final_score,
                rule_score=rule_score,
                llm_score=llm_score,
                alpha=self.config.alpha,
                beta=self.config.beta,
                fallback_used=False,
                llm_reasoning=llm_result.reasoning,
            )

        except Exception as e:
            logger.warning(f"LLM evaluation failed: {e}. Falling back to rule-only scoring.")
            return HybridScoreResult(
                final_score=rule_score,
                rule_score=rule_score,
                llm_score=None,
                alpha=self.config.alpha,
                beta=self.config.beta,
                fallback_used=True,
            )

    async def _call_llm(self, narrative: str) -> dict[str, Any]:
        """Call the LLM to evaluate a narrative.

        Args:
            narrative: The narrative text to evaluate.

        Returns:
            Dictionary with score, reasoning, and categories.

        Raises:
            Exception: If LLM call fails.
        """
        if not self._client:
            raise RuntimeError("OpenAI client not initialized")

        system_prompt = self._get_system_prompt()
        user_prompt = self._get_user_prompt(narrative)

        response = await self._client.chat.completions.create(
            model=self.config.model,
            temperature=self.config.temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content
        return json.loads(content)

    def _get_system_prompt(self) -> str:
        """Get the system prompt for LLM evaluation.

        Returns:
            System prompt string with IRS Section 41 evaluation criteria.
        """
        return """You are an expert IRS Section 41 R&D tax credit evaluator.
Your task is to evaluate narratives for compliance with the Four-Part Test:

1. **Technical Uncertainty**: Does the narrative document genuine technical uncertainty
   about capability, methodology, or design that couldn't be resolved without experimentation?

2. **Process of Experimentation**: Does it show systematic evaluation of alternatives,
   including hypothesis formulation, testing, and analysis of results?

3. **Technological in Nature**: Does it rely on hard sciences (engineering, physics,
   computer science) rather than business, market, or aesthetic considerations?

4. **Business Component**: Does it describe development of a new or improved product,
   process, software, technique, formula, or invention?

Evaluate the narrative and respond with a JSON object:
{
  "score": <float 0.0-1.0>,
  "reasoning": "<brief explanation>",
  "categories": {
    "technical_uncertainty": <float 0.0-1.0>,
    "experimentation": <float 0.0-1.0>,
    "technological_nature": <float 0.0-1.0>,
    "business_component": <float 0.0-1.0>
  }
}

Scoring guidelines:
- 1.0: Fully meets IRS Section 41 requirements with strong evidence
- 0.8: Mostly compliant with minor gaps
- 0.6: Partial compliance, some significant issues
- 0.4: Below standard, multiple issues
- 0.2: Significant non-compliance
- 0.0: Does not meet requirements

Be rigorous but fair. Look for substance over form."""

    def _get_user_prompt(self, narrative: str) -> str:
        """Get the user prompt with the narrative to evaluate.

        Args:
            narrative: The narrative text to evaluate.

        Returns:
            User prompt string.
        """
        return f"""Please evaluate this IRS Section 41 R&D tax credit narrative:

---
{narrative}
---

Respond with a JSON object containing your evaluation."""
