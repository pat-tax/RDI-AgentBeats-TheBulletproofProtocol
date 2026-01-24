# AgentBeats Competition Research

**Purpose**: Guide implementation of Bulletproof Protocol for AgentBeats submission
**Deadline**: Phase 1 - January 31, 2026 (9 days remaining)
**Prize Pool**: $1M+

---

## Executive Summary

**AgentBeats** introduces **Agentified Agent Assessment (AAA)** - a new paradigm where assessor agents (green) evaluate assessee agents (purple) via standardized A2A protocol.

### Current Problems

- Interoperability: Fragmented evaluation frameworks
- Reproducibility: Fixed harnesses, test/prod mismatch
- Discovery: No centralized agent benchmark platform
- LLM-centric: Overlooks agentic capabilities

### AgentBeats Goals

- **Standardization**: A2A protocol for universal compatibility
- **Reproducibility**: Docker + GitHub Actions automation
- **Collaboration**: Open platform, leaderboards, agent improvements
- **Focus**: Agent evaluation, capability assessment, risk assessment

**Core Principle**: "Only improve what gets measured"

---

## Competition Structure

### Phase 1: Green Agent (Assessor/Benchmark) - Due Jan 31, 2026

**Track Types**:

1. Create new benchmark from scratch
2. Agentify existing benchmark (e.g., Tau-bench)

**Deliverables**:

- Abstract describing evaluation task
- Public GitHub repository (code + README)
- Baseline purple agent(s) demonstrating benchmark
- Docker image (linux/amd64, end-to-end execution)
- AgentBeats platform registration
- 3-minute demo video

**Judging Criteria**:

- Technical Correctness (Docker, docs, error handling)
- Reproducibility (consistent results, A2A compatibility)
- Benchmark Design (realistic, difficulty levels, agentic capabilities)
- Evaluation Methodology (clear scoring, automated, nuanced metrics)
- Innovation & Impact (originality, addresses gaps, use case)

### Phase 2: Purple Agent (Assessee) - March 31, 2026

Compete on public leaderboard for top 3 Phase 1 benchmarks.

---

## Bulletproof Protocol Implementation Strategy

### Positioning: Legal Domain Agent Benchmark

| Component | AgentBeats Role |
|-----------|-----------------|
| **Agent B (Virtual Examiner)** | Green Agent - IRS Section 41 evaluator |
| **Agent A (R&D Substantiator)** | Baseline Purple Agent - demonstrates benchmark |
| **Risk Score (0-100)** | Scoring metric (< 20 = pass) |
| **Redline Markup** | Task feedback with rejection reasons |
| **Adversarial Loop** | Assessment pattern (iterative refinement) |

**Why this works**:

- Legal Domain is explicit AgentBeats category
- No existing R&D tax credit benchmark
- Clear evaluation criteria (IRS Section 41)
- Quantitative + qualitative metrics
- Real-world impact (unlocks non-dilutive capital for startups)

---

## Technical Requirements

### 1. A2A Protocol (Agent-to-Agent)

**Specification**: [a2a-protocol.org](https://a2a-protocol.org/latest/)
**SDK**: [Google ADK](https://google.github.io/adk-docs/a2a/intro/)

**Communication Pattern**:

```json
{
    "participants": { "<role>": "<endpoint_url>" },
    "config": {}
}
```

**Implementation**:

- Green agent receives assessment request
- Creates A2A task with participants
- Interacts via A2A clients
- Emits task updates (logs)
- Returns final artifact (JSON results)

**Language Flexibility**: Any language exposing A2A server (Python, Node, Go, etc.)

### 2. MCP Protocol (Model Context Protocol)

- For tool/resource access
- Green agent can provide traced environment (MCP, SSH, hosted UI)
- Observes purple agent actions for scoring

### 3. Docker Requirements

**Build Command**:

```bash
docker build --platform linux/amd64 -t ghcr.io/username/agent:v1.0 .
```

**ENTRYPOINT Parameters**:

- `--host`: Bind address
- `--port`: Listen port
- `--card-url`: Advertised URL

**Isolation**: Each assessment starts from clean, stateless initial state. Use task_id for namespacing.

### 4. Assessment Modes

1. **Artifact submission**: Purple produces output, green evaluates
2. **Traced environment**: Green observes purple actions via MCP/SSH
3. **Message-based**: LLM-as-Judge via Q&A/dialogue
4. **Multi-agent games**: Green orchestrates multiple purple agents

**Bulletproof Protocol Mode**: Artifact submission + Message-based (Agent A generates narrative → Agent B evaluates)

---

## Benchmark Design Best Practices

### Task Validity

- **Real-world**: Realistic scenarios, not toy problems
- **Difficulty Levels**: Easy/medium/hard tasks
- **Contamination-resistant**: Not easily gamed or saturated
- **Practical**: Addresses actual user needs

### Outcome Validity

- **Ground Truth**: Provide as much as possible
- **Rigorous Rubrics**: Clear evaluation criteria
- **LLM-as-Judge**: Must provide high accuracy (avoid substring matching shortcuts)

### What Could Go Wrong

- Noisy or biased data
- Not practical benchmark
- Eval can be gamed (shortcuts)
- Not challenging enough
- Saturates quickly

### Implementation Checklist

- [ ] Define goal: What to evaluate?
- [ ] Define task: What is the environment?
- [ ] Build data collection pipeline
- [ ] Create evaluation methodology
- [ ] Provide baseline purple agent
- [ ] Test reproducibility

---

## Repository Structure (Reference Implementations)

```
bulletproof-protocol/
├── green-agent/                    # Agent B - Virtual Examiner
│   ├── src/
│   │   ├── examiner.py            # A2A server (entrypoint)
│   │   ├── risk_scorer.py
│   │   ├── vagueness_detector.py
│   │   └── routine_engineering_detector.py
│   ├── Dockerfile
│   └── agent-card.json            # A2A metadata
├── purple-agent/                   # Agent A - R&D Substantiator
│   ├── src/
│   │   ├── substantiator.py       # A2A server
│   │   ├── narrative_generator.py
│   │   └── data_ingestor.py
│   ├── Dockerfile
│   └── agent-card.json
├── scenario.toml                   # Assessment config
├── docker-compose.yml              # Local testing
└── README.md                       # Submission documentation
```

**Reference Examples**:

- [agentbeats-tutorial](https://github.com/RDI-Foundation/agentbeats-tutorial) - Concepts, debate scenario
- [agentbeats-leaderboard-template](https://github.com/RDI-Foundation/agentbeats-leaderboard-template) - Leaderboard setup
- [agentify-example-tau-bench](https://github.com/agentbeats/agentify-example-tau-bench) - Agentifying existing benchmark

---

## Fine-Tuning & Optimization

### 1. ART (Agent Reinforcement Trainer)

**Use Case**: Train Agent A using Agent B's Risk Score as reward signal

**Workflow**:

1. Execute: Agent A generates narrative
2. Store: Trajectory captured
3. Reward: Agent B Risk Score (lower = better)
4. Train: GRPO updates LoRA adapter
5. Repeat: Until consistent Risk Score < 20

**Installation**: `pip install openpipe-art`
**Resources**: [OpenPipe/ART](https://github.com/OpenPipe/ART)

### 2. WeightWatcher

**Use Case**: Validate model quality before deployment

```python
import weightwatcher as ww
watcher = ww.WeightWatcher(model=model)
details = watcher.analyze()
summary = watcher.get_summary(details)
# Alpha 2-6 = well-trained
```

**Resources**: [weightwatcher.ai](https://weightwatcher.ai)

### 3. PerforatedAI

**Use Case**: Reduce Agent B size for faster Docker deployment

- 90% parameter reduction
- 97% compute savings
- ~1 hour integration

**Resources**: [perforatedai.com](https://www.perforatedai.com/)

---

## Implementation Roadmap

### Week 1 (Jan 22-24): Core A2A Integration

1. Study A2A protocol docs
2. Implement A2A server for Agent B (green)
3. Implement A2A server for Agent A (purple baseline)
4. Create agent-card.json for both

### Week 2 (Jan 25-27): Dockerization & Testing

1. Create Dockerfiles (linux/amd64)
2. Build scenario.toml
3. Test locally with docker-compose
4. Verify end-to-end assessment flow

### Week 3 (Jan 28-30): Demo & Submission

1. Register on agentbeats.dev
2. Push Docker images to GHCR
3. Record 3-minute demo video
4. Write abstract and README
5. Submit by Jan 31, 2026

---

## Key Resources

### AgentBeats

- **Platform**: [agentbeats.dev](https://agentbeats.dev)
- **Tutorial**: [docs.agentbeats.dev](https://docs.agentbeats.dev/tutorial/)
- **Discord**: [discord.gg/uqZUta3MYa](https://discord.gg/uqZUta3MYa)
- **Signup**: [forms.gle/NHE8wYVgS6iJLwRj8](https://forms.gle/NHE8wYVgS6iJLwRj8)
- **Phase 1 Submission**: [forms.gle/1C5d8KXny2JBpZhz7](https://forms.gle/1C5d8KXny2JBpZhz7)

### Protocols

- **A2A Protocol**: [a2a-protocol.org](https://a2a-protocol.org/latest/)
- **Google ADK**: [google.github.io/adk-docs](https://google.github.io/adk-docs/a2a/intro/)
- **A2A GitHub**: [github.com/a2aproject/A2A](https://github.com/a2aproject/A2A)

### Benchmark Research

- **Agent Programming Exercise**: [ape.agentbeats.org](http://ape.agentbeats.org/)
- **Tau-bench**: [arxiv.org/abs/2406.12045](https://arxiv.org/abs/2406.12045)
- **Tau2**: [arxiv.org/abs/2506.07982](https://arxiv.org/abs/2506.07982)
- **Best Practices**: [arxiv.org/pdf/2507.02825](https://arxiv.org/pdf/2507.02825)
- **AI Benchmark Issues**: [arxiv.org/pdf/2502.06559](https://arxiv.org/pdf/2502.06559)
- **CyberGym**: [arxiv.org/abs/2506.02548](https://arxiv.org/abs/2506.02548), [cybergym.io](https://cybergym.io)

### Fine-Tuning

- **ART**: [github.com/OpenPipe/ART](https://github.com/OpenPipe/ART)
- **WeightWatcher**: [weightwatcher.ai](https://weightwatcher.ai)
- **PerforatedAI**: [perforatedai.com](https://www.perforatedai.com/)

---

## Cost Management

**BYOK Model** (Bring Your Own Key):

- Set spending limits on API keys
- Recommended: $10 limit with $5 alert for single agent
- Use smaller models (Qwen 2.5 7B) for development
- Reserve larger models for final demo

---

## Next Actions

1. **Register for competition**: [forms.gle/NHE8wYVgS6iJLwRj8](https://forms.gle/NHE8wYVgS6iJLwRj8)
2. **Clone reference repos**: agentbeats-tutorial, agentbeats-leaderboard-template
3. **Study A2A protocol**: Implement minimal A2A server in Python
4. **Define IRS Section 41 rubric**: Document evaluation criteria for Agent B
5. **Create Docker scaffolding**: Dockerfiles for green/purple agents
