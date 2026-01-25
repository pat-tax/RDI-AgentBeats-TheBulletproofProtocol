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

---

## Demo Video Recording Guide

A 3-minute demo video is required for submission. Record the following workflow:

### Setup (30 seconds)

```bash
docker-compose up -d
curl http://localhost:8001/.well-known/agent-card.json  # Green agent
curl http://localhost:8002/.well-known/agent-card.json  # Purple agent
```

### Narrative Generation (60 seconds)

Show the purple agent generating an R&D narrative:
- Explain Four-Part Test structure (Hypothesis, Test, Failure, Iteration)
- Show technical uncertainty documentation
- Display structured narrative output

### Evaluation and Scoring (60 seconds)

Demonstrate green agent evaluation:
- Rule-based detection (routine engineering, vagueness, business risk)
- Component scoring breakdown (correctness, safety, specificity, experimentation)
- Risk Score computation (0-100 scale)
- Binary classification (QUALIFYING/NON_QUALIFYING)

### Agent Communication (30 seconds)

Show A2A protocol interaction:
- AgentCard discovery
- JSON-RPC 2.0 task execution
- Reproducible, deterministic scoring

### Recommended Tools

- Screen recording: OBS Studio, Loom, or macOS built-in
- Terminal: Use clear, readable font (14pt+)
- Resolution: 1080p minimum
