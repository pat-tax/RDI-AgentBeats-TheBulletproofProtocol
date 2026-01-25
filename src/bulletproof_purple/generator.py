"""Purple Agent narrative generator for IRS Section 41 R&D tax credits.

Generates Four-Part Test narratives from engineering signals with focus on
Process of Experimentation and technical uncertainty evidence.
"""

from dataclasses import dataclass, field


@dataclass
class Narrative:
    """Structured narrative output with metadata."""

    text: str
    metadata: dict = field(default_factory=dict)


class NarrativeGenerator:
    """Generates IRS Section 41 compliant Four-Part Test narratives."""

    TEMPLATES = {
        "qualifying": {
            "intro": """The {project_name} project faced significant technical uncertainty
regarding {challenge}. At the project's inception, it was unknown whether the proposed
approach using {technology} would achieve the required performance characteristics.
The engineering team identified that existing solutions in the industry did not address
our specific technical requirements, necessitating original research and development
activities to discover a viable approach.""",
            "hypothesis": """Our engineering team formulated a hypothesis that a novel
{technology} architecture could resolve the technical challenges. This hypothesis was
based on preliminary analysis, but the outcome remained uncertain due to the lack of
existing solutions for our specific requirements. We theorized that by systematically
exploring the design space and evaluating multiple architectural patterns, we could
identify an approach that would meet the demanding performance specifications while
maintaining system reliability and scalability.""",
            "experimentation": """To evaluate our hypothesis, we designed and executed
a systematic experimentation process. Multiple alternative approaches were tested,
including different algorithm implementations and architectural patterns. Each experiment
was carefully documented to capture performance metrics and identify failure modes.
The experimentation methodology involved controlled testing environments, systematic
variation of parameters, and rigorous measurement protocols to ensure reproducible results.
We evaluated both established techniques and novel approaches that we developed
specifically to address the unique technical challenges of this project.""",
            "failures": """During the experimentation phase, several attempts failed to
meet the technical requirements. Initial iterations using conventional approaches didn't
work as expected, revealing unexpected performance bottlenecks. These unsuccessful trials
provided valuable insights that informed subsequent modifications to our approach.
Specific failure modes included inadequate throughput under load conditions, memory
consumption exceeding acceptable limits, and latency spikes during peak processing periods.
Each failure was documented with detailed analysis of root causes and potential mitigations.""",
            "iteration": """Through iterative refinement, we systematically modified our
implementation based on experimental results. Each iteration addressed specific technical
issues identified in previous trials. Alternative solutions were evaluated and compared
against established benchmarks to determine optimal configurations. The iterative process
involved multiple cycles of hypothesis refinement, implementation modification, testing,
and analysis. We maintained detailed records of each iteration to track the evolution
of our approach and the rationale for design decisions.""",
            "conclusion": """The process of experimentation ultimately led to a technical
solution that resolved the initial uncertainties. The systematic approach of hypothesis
formulation, controlled testing, failure documentation, and iterative refinement
demonstrates the qualified research activities undertaken in this project. The final
implementation incorporates novel technical approaches that emerged from our research
efforts and represents a meaningful advancement in addressing the original technical
uncertainty.""",
        },
        "non_qualifying": {
            "intro": """The {project_name} initiative was launched to improve business
operations using {technology}. The project aimed to increase market share and enhance
customer satisfaction through improved product features. Management determined that
implementing standard industry solutions would help the company achieve its business
objectives and maintain competitive positioning in the marketplace.""",
            "hypothesis": """We believed that implementing {technology} would help the
company stay competitive in the marketplace. Our goal was to match features offered
by competitors and improve our market position. The team reviewed available commercial
solutions and selected an approach based on vendor recommendations and industry best
practices. The expected outcome was predictable based on documented case studies from
similar implementations at other organizations.""",
            "experimentation": """The team followed standard industry practices and
applied well-known patterns to implement the solution. Development proceeded according
to established guidelines with minimal deviation from conventional approaches. We used
documented implementation patterns from vendor documentation and industry guides.
The configuration and deployment followed established procedures with predictable outcomes
based on extensive prior experience with similar systems.""",
            "failures": """The project encountered some schedule delays and budget
concerns, but the technical implementation followed expected patterns. Some features
required additional time to complete according to business requirements. The challenges
faced were primarily related to resource allocation, stakeholder alignment, and project
management rather than technical uncertainty. Implementation issues were resolved using
standard troubleshooting procedures and vendor support channels.""",
            "iteration": """We adjusted project timelines and resources to meet
business deadlines. The team worked to deliver features that would improve customer
retention and drive revenue growth. Schedule modifications were made to accommodate
business priorities and resource availability. The implementation approach remained
consistent throughout the project with adjustments limited to scheduling and scope
rather than technical methodology.""",
            "conclusion": """The project successfully delivered the planned features
on schedule. The implementation followed standard engineering practices and achieved
the business objectives of improving competitive positioning. The solution performs
as expected based on industry benchmarks and vendor specifications. Customer feedback
has been positive, contributing to improved market presence and revenue performance.""",
        },
        "edge_case": {
            "intro": """The {project_name} project addressed {challenge} using
{technology}. While some aspects of the work involved standard implementation,
certain technical elements required investigation into uncertain outcomes. The project
scope included both routine engineering tasks and research activities to resolve
specific technical questions that could not be answered through conventional means.""",
            "hypothesis": """Our team hypothesized that existing solutions could be
adapted for our use case, though it was unclear whether the performance requirements
could be met. The technical uncertainty centered on specific integration challenges
and the interaction between components under real-world operating conditions. We
formulated testable hypotheses about system behavior and designed experiments to
validate our assumptions before committing to a particular implementation approach.""",
            "experimentation": """We conducted experiments to validate whether the
approach would work for our specific requirements. Testing included both standard
configurations and novel parameter combinations to explore the solution space. The
experimentation process revealed both expected behaviors consistent with documentation
and unexpected interactions that required further investigation. We documented all
experimental results to support decision-making about the final implementation approach.""",
            "failures": """Some experimental configurations failed to produce acceptable
results. Several iterations were required to identify configurations that met the
technical specifications, with unsuccessful attempts documented along the way. The
failure analysis revealed specific technical limitations that were not apparent from
available documentation. These findings informed modifications to our approach that
ultimately enabled successful implementation.""",
            "iteration": """Through iterative testing and adjustment, we refined the
implementation to address identified issues. The process involved evaluating alternatives
and selecting approaches based on experimental evidence. Each iteration incorporated
lessons learned from previous attempts and moved the project closer to meeting the
technical requirements. The iterative approach allowed us to systematically resolve
uncertainties while maintaining project momentum.""",
            "conclusion": """The project achieved its technical objectives through
a combination of applied research and engineering implementation. Documentation
of the process demonstrates elements of qualified research activity where technical
uncertainty existed. The final solution addresses the original technical challenges
and provides a foundation for future development efforts in this area.""",
        },
    }

    DEFAULT_SIGNALS = {
        "project_name": "Data Processing Pipeline",
        "technology": "distributed computing architecture",
        "challenge": "achieving sub-millisecond latency at scale",
    }

    def generate(
        self,
        template_type: str = "qualifying",
        signals: dict | None = None,
    ) -> Narrative:
        """Generate an IRS Section 41 compliant narrative.

        Args:
            template_type: Type of narrative template (qualifying, non_qualifying, edge_case)
            signals: Engineering signals dict with project_name, technology, challenge

        Returns:
            Narrative with text and metadata
        """
        effective_signals = {**self.DEFAULT_SIGNALS, **(signals or {})}
        template = self.TEMPLATES.get(template_type, self.TEMPLATES["qualifying"])

        sections = []
        for key in ["intro", "hypothesis", "experimentation", "failures", "iteration", "conclusion"]:
            section_text = template[key].format(**effective_signals)
            sections.append(section_text)

        narrative_text = "\n\n".join(sections)

        # Pad to reach ~500 words if needed
        word_count = len(narrative_text.split())
        if word_count < 450:
            padding = self._generate_padding(effective_signals, 500 - word_count)
            narrative_text += "\n\n" + padding

        # Extract technical uncertainties for metadata
        technical_uncertainties = self._extract_technical_uncertainties(
            effective_signals, template_type
        )

        return Narrative(
            text=narrative_text.strip(),
            metadata={
                "template_type": template_type,
                "technical_uncertainties": technical_uncertainties,
                "signals": effective_signals,
            },
        )

    def _generate_padding(self, signals: dict, target_words: int) -> str:
        """Generate additional content to reach target word count."""
        padding_template = """
Additional technical documentation captures the engineering activities performed
during the research phase. The team systematically evaluated {technology}
capabilities and limitations through controlled experiments. Performance testing
revealed areas requiring further investigation, leading to hypothesis refinement
and additional experimentation cycles. The iterative process of testing, failure
analysis, and modification demonstrated the systematic approach characteristic
of qualified research activities under IRS Section 41. Technical metrics were
collected throughout the experimentation process to quantify improvements and
identify remaining uncertainties requiring resolution.
"""
        return padding_template.format(**signals).strip()

    def _extract_technical_uncertainties(
        self, signals: dict, template_type: str
    ) -> list[str]:
        """Extract technical uncertainty evidence from signals and template type."""
        uncertainties = []

        if template_type == "qualifying":
            uncertainties.extend([
                f"Uncertainty in {signals['technology']} performance characteristics",
                f"Unknown solution approach for {signals['challenge']}",
                "Unpredictable interaction between system components",
            ])
        elif template_type == "non_qualifying":
            uncertainties.extend([
                "Standard implementation with predictable outcomes",
            ])
        else:  # edge_case
            uncertainties.extend([
                f"Partial uncertainty in {signals['technology']} adaptation",
                "Integration challenges with existing systems",
            ])

        return uncertainties
