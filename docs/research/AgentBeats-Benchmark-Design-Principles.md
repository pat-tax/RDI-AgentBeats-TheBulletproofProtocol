# AgentBeats Benchmark Design Principles

**Critical Context for Bulletproof Protocol Implementation**
**Must Review Before Implementation**

---

## Agentified Agent Assessment (AAA) - The New Paradigm

### Current Problems AgentBeats Solves

| Problem | Current State | AgentBeats Solution |
|---------|---------------|---------------------|
| **Interoperability** | Fragmented evaluation frameworks | A2A protocol standardization |
| **Reproducibility** | Fixed harnesses, test/prod mismatch | Docker + GitHub Actions automation |
| **Fragmentation** | Incompatible agent ecosystems | Universal A2A interface |
| **Discovery** | No centralized benchmark platform | Open platform with leaderboards |
| **LLM-Centric** | Overlooks agentic capabilities | Agent-specific evaluation |

### AgentBeats Goals (Our North Star)

1. **Standardization**: A2A protocol = universal compatibility
2. **Openness**: Public benchmarks, transparent evaluation
3. **Reproducibility**: Same input → same output, always
4. **Easy-to-use**: Low barrier to entry, rich documentation
5. **Rich Integration**: Works with existing frameworks (LangGraph, CrewAI, etc.)

**Core Principle**: **"Only improve what gets measured"**

---

## AAA Architecture: Assessor vs Assessee

```
┌────────────────────────────────────────────────────────┐
│              Assessment Control Protocol (A2A)          │
└────────────────────────────────────────────────────────┘
                         │
        ┌────────────────┴────────────────┐
        │                                 │
┌───────▼────────┐               ┌────────▼───────┐
│  GREEN AGENT   │               │  PURPLE AGENT  │
│  (Assessor)    │───evaluates──►│  (Assessee)    │
│                │               │                │
│ • Defines task │               │ • Performs     │
│ • Provides env │               │   task         │
│ • Scores result│               │ • Submits      │
│ • Issues report│               │   artifact     │
└────────────────┘               └────────────────┘
```

### Two Competition Modes

1. **Benchmark Mode** (Single-Agent)
   - Purple agent performs isolated task
   - Green agent evaluates performance
   - **Bulletproof Protocol uses this mode**

2. **Arena Mode** (Multi-Agent Systems)
   - Multiple purple agents interact
   - Green agent orchestrates and evaluates
   - Examples: Debate, negotiation, collaboration

---

## Phase 1 Strategy: Create NEW Benchmark

### Track Types

| Track | Description | Bulletproof Protocol Choice |
|-------|-------------|----------------------------|
| **Create New Benchmark** | Build from scratch | ✓ **Selected** - No R&D tax benchmark exists |
| **Agentify Existing** | Convert fixed harness to AAA | ✗ Not applicable |

### Why "Create New" is Strategic

- **Gap in Legal Domain**: No existing R&D tax credit benchmark
- **Clear Evaluation Criteria**: IRS Section 41 is well-documented law
- **Real-World Impact**: Unlocks non-dilutive capital for startups
- **Measurable Outcomes**: Risk Score (0-100) is quantitative
- **Human-Solvable**: Tax professionals currently do this manually

---

## What Makes a Great Benchmark (Critical Standards)

### 1. Task Validity

**Question**: Does the task evaluate what we claim to evaluate?

**Bulletproof Protocol Application**:
- ✓ Task: Evaluate IRS Section 41 compliance of R&D narratives
- ✓ Measures: Ability to detect non-qualifying activities (routine engineering)
- ✓ Validates: Legal reasoning, technical vs business risk distinction
- ✓ Real-world: Actual tax professionals perform this task

### 2. Outcome Validity

**Question**: Is the evaluation methodology accurate and rigorous?

**Critical Requirements**:
- **No Substring Matching**: Simple pattern matching is insufficient
- **LLM-as-Judge Must Be Accurate**: If using LLM scoring, validate against ground truth
- **Provide Ground Truth**: We need labeled examples (qualifying vs non-qualifying)
- **Rigorous Rubrics**: Explicit scoring criteria, not subjective judgment

**Bulletproof Protocol Application**:
- ✓ Rule-based scoring (not pure LLM judgment)
- ✓ IRS Section 41 statutes = ground truth
- ✓ Weighted rubric: 30% routine engineering + 25% vagueness + 20% business risk + 15% experimentation + 10% specificity
- ⚠ **Action Required**: Create labeled test set (10-20 narratives with known outcomes)

### 3. Principles for Robust Benchmarks

| Principle | Requirement | Bulletproof Protocol Status |
|-----------|-------------|----------------------------|
| **Real-world** | Realistic scenarios, not toy problems | ✓ Actual IRS compliance use case |
| **Difficulty Levels** | Easy/medium/hard tasks | ⚠ **TODO**: Create 3 difficulty tiers |
| **Contamination-Resistant** | Not easily gamed or saturated | ✓ Legal knowledge + technical understanding required |
| **Not Too Easy** | Requires genuine agentic capabilities | ✓ Must distinguish business vs technical risk |
| **Baseline Provided** | Reference implementation | ✓ Agent A (purple) serves as baseline |

---

## Obstacles We Must Overcome

### AAA Implementation Challenges

1. **Complexity**: A2A protocol, Docker, assessment flow
   - **Mitigation**: Use official a2a-sdk, follow agentbeats-tutorial examples

2. **Observability**: Agents are black boxes, hard to debug
   - **Mitigation**: Emit detailed task updates, log evaluation steps

3. **Infrastructure**: Docker build, GHCR deployment, testing
   - **Mitigation**: Test locally with docker-compose before submitting

4. **Lack of Openness**: Proprietary eval methods reduce trust
   - **Mitigation**: Open-source all rules, document IRS Section 41 citations

5. **Fragmentation**: Different agent frameworks
   - **Mitigation**: A2A protocol ensures framework-agnostic compatibility

---

## Learning from Tau-Bench Example

### Tau-Bench Architecture

**Key Innovation**: Cross-agent tool use evaluation

- Green agent provides tools via MCP
- Purple agent uses tools to complete task
- Evaluation: Did agent achieve goal using tools correctly?

**Challenge**: Tool trace not directly visible to assessor
- **Solution**: Observe side effects (database changes, API calls, file system)

### Tau Papers

- **Tau v1**: [arxiv.org/abs/2406.12045](https://arxiv.org/abs/2406.12045) - Original benchmark design
- **Tau v2**: [arxiv.org/abs/2506.07982](https://arxiv.org/abs/2506.07982) - Improved with A2A

### Application to Bulletproof Protocol

**Bulletproof Protocol Architecture** (Simpler than Tau):

- **No MCP Tools Required**: Artifact-based evaluation
- **Direct Observability**: Purple agent submits narrative as artifact
- **Green Agent Inspects**: Text analysis, no tool tracing needed
- **Advantage**: Simpler implementation, faster development

---

## Benchmark Validation Checklist

### Task Validity

- [ ] Task description clear and unambiguous
- [ ] Evaluation criteria match stated goal
- [ ] Human experts can perform this task
- [ ] Task addresses real-world need

### Outcome Validity

- [ ] Ground truth dataset created (10-20 labeled examples)
- [ ] Scoring rubric documented with IRS Section 41 citations
- [ ] Inter-rater reliability checked (multiple evaluators agree?)
- [ ] No shortcut exploitation (substring matching, keyword stuffing)

### Data Quality

- [ ] Mock data realistic (resembles actual engineering signals)
- [ ] Not biased toward specific programming languages or domains
- [ ] Covers edge cases (barely qualifying, clearly non-qualifying)

### Reproducibility

- [ ] Same narrative → same Risk Score every time
- [ ] Docker image builds consistently on linux/amd64
- [ ] Clear documentation for running assessment

### Difficulty Levels

- [ ] Easy task: Obvious routine engineering (e.g., "fixed production bugs")
- [ ] Medium task: Subtle non-qualifying activity (e.g., "optimized database queries")
- [ ] Hard task: Requires distinguishing technical from business uncertainty

---

## Best Practices from Research

### From "Establishing Best Practices for Building Rigorous Agentic Benchmarks"
[arxiv.org/pdf/2507.02825](https://arxiv.org/pdf/2507.02825)

**Key Takeaways**:
1. Define evaluation criteria BEFORE collecting data
2. Use multiple evaluators to establish ground truth
3. Test for shortcut exploitation (can trivial agents score well?)
4. Document limitations and failure modes

### From "Can We Trust AI Benchmarks?"
[arxiv.org/pdf/2502.06559](https://arxiv.org/pdf/2502.06559)

**Risks to Avoid**:
- Benchmark saturation (agents memorize answers)
- Evaluation shortcuts (pattern matching vs understanding)
- Lack of transparency in scoring methodology
- Mismatch between benchmark and real-world performance

### From CyberGym
[arxiv.org/abs/2506.02548](https://arxiv.org/abs/2506.02548), [cybergym.io](https://cybergym.io)

**Lessons**:
- Provide interactive environments, not just static datasets
- Measure capability progression (novice → expert)
- Include both success metrics and risk assessment

---

## Implementation Priorities (Revised)

### MUST HAVE (Phase 1 Submission)

1. **A2A Compatibility**: Green and purple agents expose A2A servers
2. **Clear Rubric**: Documented IRS Section 41 evaluation criteria
3. **Reproducible**: Docker images build and run consistently
4. **Baseline**: Purple agent demonstrates how evaluation works
5. **Documentation**: README, abstract, demo video

### SHOULD HAVE (Strengthens Submission)

1. **Ground Truth Dataset**: 10 labeled narratives (qualifying vs not)
2. **Difficulty Tiers**: Easy/medium/hard test cases
3. **Evaluation Transparency**: Log every rule match, show work
4. **Inter-Rater Validation**: Multiple tax professionals agree with Risk Score

### NICE TO HAVE (Post-Competition)

1. **Real Git/Jira Integration**: Not mock data
2. **Fine-tuned Models**: Use ART for RL training
3. **SVT Historical Data**: Train on actual audit outcomes
4. **CLI Interface**: `bulletproof evaluate narrative.txt`

---

## Critical Success Factors

### For AgentBeats Judges

1. **Technical Correctness**: A2A protocol correctly implemented
2. **Reproducibility**: Anyone can run assessment and get same results
3. **Benchmark Design**: Addresses real gap (legal domain agent evaluation)
4. **Evaluation Methodology**: Rigorous, documented, based on IRS law
5. **Innovation**: First R&D tax credit compliance benchmark

### For Users (Tax Professionals)

1. **Practical**: Solves actual pain point (4-hour manual review)
2. **Accurate**: Risk Score correlates with real audit outcomes
3. **Actionable**: Redline markup shows how to fix issues
4. **Trustworthy**: Open methodology, cites IRS statutes
5. **Fast**: 5-minute evaluation vs 4-hour manual review

---

## Resources

### AgentBeats Official

- **A2A Protocol Spec**: [a2a-protocol.org/latest/](https://a2a-protocol.org/latest/)
- **Google ADK Docs**: [google.github.io/adk-docs/a2a/intro/](https://google.github.io/adk-docs/a2a/intro/)
- **Agent Programming Exercise**: [ape.agentbeats.org/](http://ape.agentbeats.org/)
- **Agentify Example**: [github.com/agentbeats/agentify-example-tau-bench](https://github.com/agentbeats/agentify-example-tau-bench)

### Research Papers

- **Tau-bench v1**: [arxiv.org/abs/2406.12045](https://arxiv.org/abs/2406.12045)
- **Tau-bench v2**: [arxiv.org/abs/2506.07982](https://arxiv.org/abs/2506.07982)
- **Agentic Benchmark Best Practices**: [arxiv.org/pdf/2507.02825](https://arxiv.org/pdf/2507.02825)
- **AI Benchmark Trust Issues**: [arxiv.org/pdf/2502.06559](https://arxiv.org/pdf/2502.06559)
- **CyberGym**: [arxiv.org/abs/2506.02548](https://arxiv.org/abs/2506.02548)

### Tools

- **Gemini in Browserbase**: [gemini.browserbase.com](https://gemini.browserbase.com) (headless browser agent sponsor)

## Next Steps Before Implementation

1. **Create Ground Truth Dataset**: 10 narratives with known Risk Scores
2. **Define Difficulty Tiers**: Easy/medium/hard test cases
3. **Document Rubric**: Detailed scoring with IRS Section 41 citations
4. **Validate Approach**: Can human tax professional agree with Risk Score?
5. **Start Implementation**: Build A2A servers following this framework
