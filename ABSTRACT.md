# The Bulletproof Protocol

## Abstract

IRS Section 41 R&D tax credit evaluation presents a complex challenge: tax professionals spend 4+ hours manually reviewing each narrative for compliance, while current IRS AI achieves only 61.2% accuracy. The lack of automated, reproducible evaluation tools creates inconsistent audit outcomes and significant compliance risk for legitimate research activities.

The Bulletproof Protocol addresses this gap with an adversarial agent benchmark built on the A2A protocol. Our green agent (Virtual Examiner) evaluates R&D narratives against IRS audit standards using rule-based detectors for routine engineering, vague language, business risk, and experimentation evidence. The purple agent (R&D Substantiator) generates compliant narratives, enabling competitive refinement. Both agents communicate via AgentCard discovery and JSON-RPC 2.0 tasks, ensuring reproducible, deterministic scoring.

This benchmark represents the first agentified solution for tax compliance evaluation in the legal domain. Key innovations include:

- **Weighted Risk Scoring**: Five detection dimensions (routine engineering 30%, vagueness 25%, business risk 20%, experimentation 15%, specificity 10%) aligned with IRS Section 41(d) requirements
- **Practical Automation**: Reduces 4-hour manual reviews to automated 5-minute evaluations while maintaining statutory compliance
- **Reproducible Evaluation**: Transparent rule-based scoring eliminates subjective variance in compliance assessment

Validation against a 20-case ground truth dataset demonstrates 100% accuracy and 1.0 F1 score, exceeding target thresholds (70% accuracy, 0.72 F1) and IRS baseline performance. The architecture generalizes to other legal compliance domains (SOC 2, HIPAA, GDPR).

A 3-minute demo video showcases the complete workflow: narrative generation by the purple agent, evaluation and scoring by the green agent, and the adversarial improvement loop. The video demonstrates agent discovery, task execution, and risk score computation.

Docker images are publicly available on GitHub Container Registry for reproducible deployment.
