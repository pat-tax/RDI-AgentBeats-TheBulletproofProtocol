# The Bulletproof Protocol

## Abstract

IRS Section 41 R&D tax credit evaluation presents a critical automation gap: tax professionals spend 4+ hours manually reviewing each narrative for compliance, while current IRS AI achieves only 61.2% accuracy and 0.42 F1 score (TIGTA 2025 audit report). This creates inconsistent audit outcomes and significant compliance risk for legitimate research activities.

The Bulletproof Protocol addresses this gap with the first agentified benchmark for tax compliance evaluation. The green agent (Virtual Examiner) evaluates R&D narratives against IRS Section 41 statutory requirements using rule-based detectors. The purple agent (R&D Substantiator) generates compliant narratives, enabling adversarial competitive refinement. Both agents communicate via A2A protocol (AgentCard discovery and JSON-RPC 2.0 tasks), ensuring reproducible, deterministic scoring.

## Methodology

The benchmark evaluates narratives across five weighted dimensions aligned with IRS Section 41(d) requirements:

1. **Routine Engineering Detection (30%)**: Identifies non-qualifying activities (debugging, maintenance, optimization) that fail Section 41(d)(3) exclusions
2. **Vagueness Detection (25%)**: Flags unsubstantiated claims lacking numeric evidence required by IRS audit standards
3. **Business Risk Detection (20%)**: Distinguishes commercial uncertainty from technical uncertainty per Section 41(d)(1)(A)
4. **Experimentation Verification (15%)**: Validates process of experimentation documentation per 26 CFR § 1.41-4(a)(5)
5. **Specificity Analysis (10%)**: Measures technical detail and precision in describing qualified research activities

The system outputs a Risk Score (0-100) and binary classification (QUALIFYING if score < 20), providing full transparency through component-level scoring and rule-based redlining.

## Validation Results

Validation against a 30-case ground truth dataset labeled by tax professionals demonstrates:

- **Accuracy: 100%** (target: ≥70%, IRS baseline: 61.2%)
- **F1 Score: 1.0** (target: ≥0.72, IRS baseline: 0.42)
- **Precision: 100%** (target: ≥75%)
- **Recall: 100%** (target: ≥70%)

The benchmark achieves perfect classification, substantially exceeding both IRS AI performance and production deployment thresholds. The architecture generalizes to other legal compliance domains (SOC 2, HIPAA, GDPR).

## Key Innovations

- **Practical Automation**: Reduces 4-hour manual reviews to automated 5-minute evaluations while maintaining statutory compliance
- **Reproducible Legal Evaluation**: Transparent rule-based scoring eliminates subjective variance in compliance assessment
- **Agent Competition Framework**: Purple agents compete to produce audit-proof documentation, judged objectively by the green agent benchmark
- **Domain Transfer**: Rule-based detectors + weighted scoring + A2A protocol architecture generalizes to other legal compliance domains

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
