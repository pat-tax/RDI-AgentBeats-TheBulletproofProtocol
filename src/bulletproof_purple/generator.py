"""Narrative generator for Purple Agent.

Generates R&D tax credit narratives using predefined templates.
"""

from bulletproof_purple.templates import NarrativeTemplates


class NarrativeGenerator:
    """Generates R&D narratives from templates."""

    def __init__(self) -> None:
        """Initialize the narrative generator with templates."""
        self.templates = NarrativeTemplates()

    def generate(self, template_type: str = "qualifying") -> str:
        """Generate a narrative from the specified template.

        Args:
            template_type: Type of template to use (qualifying, non_qualifying, edge_case)

        Returns:
            Generated narrative text

        Raises:
            ValueError: If template_type is not recognized
        """
        if template_type == "qualifying":
            return self.templates.qualifying()
        elif template_type == "non_qualifying":
            return self.templates.non_qualifying()
        elif template_type == "edge_case":
            return self.templates.edge_case()
        else:
            raise ValueError(f"Unknown template type: {template_type}")
