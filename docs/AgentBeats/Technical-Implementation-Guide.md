# Technical Implementation Guide: Bulletproof Protocol for AgentBeats

**Status**: Implementation Phase
**Timeline**: 9 days until Phase 1 deadline (Jan 31, 2026)
**Approach**: Minimal Viable Benchmark (KISS principle)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                   AgentBeats Platform                    │
└─────────────────────────────────────────────────────────┘
                            │
                            │ A2A Protocol
                            │
        ┌───────────────────┴───────────────────┐
        │                                       │
┌───────▼────────┐                    ┌────────▼────────┐
│  Agent B       │◄──Assessment────►  │   Agent A       │
│  (Green Agent) │    Request         │ (Purple Agent)  │
│  Examiner      │                    │ Substantiator   │
└───────┬────────┘                    └────────┬────────┘
        │                                      │
        │ Evaluates                            │ Generates
        │ Risk Score (0-100)                   │ Narrative
        │ Redline Markup                       │ (Mock Data)
        │                                      │
        └──────────────────┬───────────────────┘
                           │
                           │ Iterative Loop
                           │
                    ┌──────▼──────┐
                    │  Artifact   │
                    │  (JSON)     │
                    │  Results    │
                    └─────────────┘
```

---

## Official Template Structure

The [green-agent-template](https://github.com/RDI-Foundation/green-agent-template) provides the reference structure.

**Example implementation**: [debate_judge branch](https://github.com/RDI-Foundation/green-agent-template/tree/example/debate_judge)

```
src/
├── server.py      # Server + agent card (HTTP entrypoint)
├── executor.py    # A2A request handling (AgentExecutor)
├── agent.py       # Core agent logic (business logic)
└── messenger.py   # A2A messaging utilities (client helpers)
tests/
└── test_agent.py  # A2A conformance tests
Dockerfile         # Container configuration (exposes port 9009)
pyproject.toml     # Dependencies (a2a-sdk, pydantic, uvicorn)
```

### File Responsibilities

| File | Role |
|------|------|
| `server.py` | Agent card metadata, server startup, port config (default 9009) |
| `executor.py` | A2A request validation, task state management, agent dispatch |
| `agent.py` | Core orchestration logic, evaluation rubrics, scoring |
| `messenger.py` | A2A client helpers for calling purple agents |

### Dependencies (pyproject.toml)

```toml
[project]
requires-python = ">=3.13"

dependencies = [
    "a2a-sdk[http-server]>=0.3.20",
    "pydantic>=2.12.5",
    "uvicorn>=0.38.0",
    "python-dotenv>=1.2.1",
]

[project.optional-dependencies]
test = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.24.0",
    "httpx>=0.28.1",
]
```

---

## Running the Agent

### Local Execution

```bash
# Install dependencies
uv sync

# Run agent server (default port 9009)
uv run src/server.py

# Custom port and host
uv run src/server.py --host 0.0.0.0 --port 8001

# Verify running
curl http://localhost:9009/.well-known/agent-card.json
```

### Docker Execution

```bash
# Build
docker build -t my-agent .

# Run (port 9009 exposed by Dockerfile)
docker run -p 9009:9009 my-agent
```

---

## A2A Conformance Testing

The official template includes a conformance test suite to validate A2A protocol compliance.

**Running Conformance Tests**:

```bash
# Install test dependencies
uv sync --extra test

# Start agent in background
uv run src/server.py &

# Run conformance tests against running agent
uv run pytest --agent-url http://localhost:9009
```

**What Conformance Tests Validate**:

- AgentCard discovery at `/.well-known/agent-card.json`
- Task creation and execution
- Status updates and artifact generation
- Error handling and timeout behavior

---

## Leaderboard Submission Workflow

Submit via the [agentbeats-leaderboard-template](https://github.com/RDI-Foundation/agentbeats-leaderboard-template).

### Steps

1. **Fork** the leaderboard repo
2. **Fill** `[[participants]]` in `scenario.toml` with agent credentials
3. **Push** to your fork
4. **GitHub Actions** auto-executes assessment
5. **Submit PR** to main leaderboard repo for review

### Example scenario.toml

```toml
[green_agent]
agentbeats_id = "agent_your_green_id"
env = { API_KEY = "${GITHUB_SECRET_NAME}" }

[[participants]]
agentbeats_id = "agent_your_purple_id"
name = "substantiator"
env = { OPENAI_API_KEY = "${OPENAI_API_KEY}" }

[config]
max_iterations = 3
timeout_seconds = 300
```

---

## Responsibility Division

Per the official templates ([green-agent-template](https://github.com/RDI-Foundation/green-agent-template), [agent-template](https://github.com/RDI-Foundation/agent-template)):

| Agent Type | Responsibility | Examples |
|------------|----------------|----------|
| **Green (Assessor)** | Lightweight orchestration, verification, scoring | Task dispatch, rubric evaluation, result aggregation |
| **Purple (Assessee)** | Complex computation, tool execution, heavy lifting | LLM calls, data processing, code generation |

**Key Principle**: Green agents should be fast and deterministic. Purple agents handle the uncertain, compute-intensive work.

---

## Example: debate_judge Implementation Pattern

The [debate_judge example](https://github.com/RDI-Foundation/green-agent-template/tree/example/debate_judge) demonstrates a three-phase architecture:

### Phase 1: Request Validation

```python
# agent.py - Validate incoming assessment request
class EvalRequest(BaseModel):
    participants: dict[str, str]  # {"debater_a": "http://...", "debater_b": "http://..."}
    config: DebateConfig          # topic, round_count, etc.

async def run(self, msg: Message, updater: TaskUpdater):
    request = EvalRequest.model_validate(msg.parts[0].data)
    # Validate all required roles are present
```

### Phase 2: Orchestration

```python
# agent.py - Coordinate turn-based exchanges
async def orchestrate_debate(self, participants: dict, config: DebateConfig):
    debate_log = []

    # Opening arguments
    opening_a = await self.call_agent(participants["debater_a"], config.topic)
    opening_b = await self.call_agent(participants["debater_b"], config.topic)

    # Sequential rounds
    for round_num in range(config.round_count):
        response_a = await self.call_agent(participants["debater_a"], opening_b)
        response_b = await self.call_agent(participants["debater_b"], response_a)
        debate_log.append({"round": round_num, "a": response_a, "b": response_b})

    return debate_log
```

### Phase 3: Evaluation & Scoring

```python
# agent.py - Judge with structured rubric
class DebateEval(BaseModel):
    emotional_resonance: float  # 0-1
    argument_clarity: float     # 0-1
    logical_flow: float         # 0-1
    topic_relevance: float      # 0-1
    total_score_a: float
    total_score_b: float
    winner: str
    reasoning: str

async def judge_debate(self, debate_log: list) -> DebateEval:
    # Use LLM with structured output
    result = await self.llm.generate(
        prompt=self.rubric_prompt(debate_log),
        response_model=DebateEval
    )
    return result
```

### Key Pattern Elements

| Element | Purpose |
|---------|---------|
| `TaskUpdater` | Stream status updates to platform |
| `Pydantic models` | Type-safe request/response validation |
| `async/await` | Non-blocking multi-agent communication |
| `Artifacts` | Preserve results in human-readable + structured formats |

---

## Network Efficiency Guidelines

Optimize agent communication for assessment performance.

### Best Practices

1. **Minimize inter-agent "chattiness"** - Batch requests where possible
2. **Compute near data sources** - Process data in the agent that has it
3. **Configure appropriate timeouts** - A2A SDK default may be too short

### Timeout Configuration

```python
from a2a.client import A2AClient

client = A2AClient(
    agent_url="http://purple-agent:8000",
    timeout=300  # 5 minutes for long-running tasks
)
```

---

## A2A Protocol Implementation

**Reference**: [A2A Protocol Specification (Python)](https://a2aprotocol.ai/docs/guide/a2a-protocol-specification-python)

### Core Concepts

The A2A protocol uses **JSON-RPC 2.0** for agent-to-agent communication.

| Concept | Description |
|---------|-------------|
| **Agent** | Autonomous entity that can act as server or client |
| **Task** | Unit of work with lifecycle states |
| **Message** | Communication payload with typed parts |
| **AgentCard** | Discovery metadata at `/.well-known/agent-card.json` |

### JSON-RPC 2.0 Message Format

**Request**:

```json
{
  "jsonrpc": "2.0",
  "id": "task_123",
  "method": "tasks/send",
  "params": {
    "task_id": "task_123",
    "message": { "parts": [...] }
  }
}
```

**Success Response**:

```json
{
  "jsonrpc": "2.0",
  "id": "task_123",
  "result": { "status": "completed", "artifacts": [...] }
}
```

**Error Response**:

```json
{
  "jsonrpc": "2.0",
  "id": "task_123",
  "error": { "code": -32600, "message": "Invalid Request" }
}
```

### Message Parts (Union Type)

Messages contain typed parts for flexible content exchange:

| Part Type | Use Case | Example |
|-----------|----------|---------|
| **TextPart** | Plain text, prompts, responses | `{"type": "text", "text": "Evaluate this narrative..."}` |
| **FilePart** | Binary files, documents | `{"type": "file", "name": "report.pdf", "mimeType": "application/pdf", "data": "base64..."}` |
| **DataPart** | Structured JSON data | `{"type": "data", "data": {"risk_score": 45, "issues": [...]}}` |

```python
# Message with multiple parts
message = {
    "role": "user",
    "parts": [
        {"type": "text", "text": "Evaluate this R&D narrative:"},
        {"type": "data", "data": {"project": "ML Pipeline", "narrative": "..."}}
    ]
}
```

### Task States (TaskState)

```
pending → running → completed
              ↓
           failed
              ↓
         cancelled
```

| State | Description |
|-------|-------------|
| `pending` | Task created, not yet started |
| `running` | Task in progress |
| `completed` | Task finished successfully |
| `failed` | Task encountered error |
| `cancelled` | Task was cancelled |

### AgentCard Structure

```json
{
  "name": "bulletproof-green",
  "description": "IRS Section 41 R&D narrative evaluator",
  "version": "1.0.0",
  "url": "http://localhost:8001",
  "skills": [
    {
      "name": "evaluate_narrative",
      "description": "Evaluate R&D tax credit narrative",
      "inputSchema": { "type": "object", "properties": {...} }
    }
  ],
  "capabilities": {
    "streaming": false,
    "pushNotifications": false
  },
  "provider": {
    "name": "Bulletproof Protocol",
    "url": "https://github.com/..."
  }
}
```

### Error Code Mapping

| Code | Name | Description |
|------|------|-------------|
| -32700 | Parse Error | Invalid JSON |
| -32600 | Invalid Request | Missing required fields |
| -32601 | Method Not Found | Unknown method |
| -32602 | Invalid Params | Invalid method parameters |
| -32603 | Internal Error | Server error |
| -32000 | Task Not Found | Task ID doesn't exist |
| -32001 | Task Failed | Task execution failed |

### Communication Patterns

**1. Synchronous (Default)**:

```python
# Client sends, waits for response
response = await client.send_task(task_id, message)
```

**2. Multi-turn with Input**:

```python
# Task requires additional input
while task.status == "input_required":
    user_input = await get_user_input(task.input_request)
    response = await client.send_task(task_id, user_input)
```

**3. Server-Sent Events (SSE)**:

```python
# Stream task updates
async for event in client.stream_task(task_id):
    print(f"Status: {event.status}, Message: {event.message}")
```

**4. Push Notifications**:

```python
# Register webhook for task updates
await client.subscribe(task_id, webhook_url="https://...")
```

### Supported Methods

| Method | Description |
|--------|-------------|
| `tasks/send` | Send message to task |
| `tasks/get` | Get task status |
| `tasks/cancel` | Cancel running task |
| `tasks/subscribe` | Subscribe to task updates |
| `agent/card` | Get agent card (also at `/.well-known/agent-card.json`) |

### A2A Best Practices

**Error Handling**:

```python
try:
    result = await client.send_task(task_id, message)
except A2AError as e:
    if e.code == -32000:  # Task not found
        task_id = await client.create_task()
    elif e.code == -32001:  # Task failed
        logger.error(f"Task failed: {e.message}")
        raise
```

**Task Management**:

- Use unique task IDs (UUIDs recommended)
- Clean up completed tasks
- Set appropriate timeouts
- Handle partial results gracefully

**Security**:

- Validate all input data
- Use HTTPS in production
- Implement authentication (API keys, OAuth)
- Rate limit requests

### Python SDK Setup

**Installation**:

```bash
pip install "a2a-sdk[http-server]"
```

**Dependencies**:

- Python 3.13 (project standard)
- a2a-sdk
- FastAPI/Starlette (HTTP server)
- uvicorn (ASGI server)

### Server Pattern

```python
from a2a.server import AgentExecutor, DefaultRequestHandler
from a2a.server.starlette import create_app
import uvicorn

class MyAgentExecutor(AgentExecutor):
    async def execute(self, task_id: str, input_data: dict) -> dict:
        # Core agent logic here
        return {"result": "..."}

def main():
    executor = MyAgentExecutor()
    handler = DefaultRequestHandler(agent_executor=executor)
    app = create_app(
        agent_card={
            "name": "agent-name",
            "description": "...",
            "version": "1.0.0"
        },
        http_handler=handler
    )
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Docker ENTRYPOINT Pattern

```python
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--card-url", default="http://localhost:8000")
    args = parser.parse_args()

    uvicorn.run(app, host=args.host, port=args.port)
```

---

## IRS Section 41 Evaluation Rules

### Four-Part Test (All Required)

| Test | Criteria | Agent B Check |
|------|----------|---------------|
| **1. Section 174** | R&D costs in experimental/laboratory sense | Verifies technical nature, not business process |
| **2. Technical Info** | Relies on hard sciences, engineering, computer science | Detects absence of technical foundation |
| **3. Business Component** | Applies to identifiable product/system | Requires discrete component identification |
| **4. Process of Experimentation** | ≥80% activities evaluate alternatives | Counts evidence of alternative evaluation |

### Red Flags (Non-Qualifying Patterns)

**Agent B detects these patterns and penalizes Risk Score:**

1. **Routine Engineering Keywords**:
   - "debugging production issues"
   - "porting to new platform"
   - "rewriting in new language"
   - "ERP implementation"
   - "quality assurance testing"
   - "vendor configuration"

2. **Vague Language (Unsubstantiated)**:
   - "optimized performance" (no metrics)
   - "improved user experience" (no measurement)
   - "upgraded system" (no technical detail)
   - "enhanced reliability" (no failure data)

3. **Business Risk vs Technical Risk**:
   - Market validation concerns
   - User preference testing
   - Sales/marketing activities
   - Training program development

4. **Missing Experimentation Evidence**:
   - No documented alternatives
   - No uncertainty description
   - No evaluation methodology
   - No failure citations

5. **Post-Commercial Production**:
   - "after release" timeline mentions
   - "maintenance work"
   - "bug fixes in production"

### Green Flags (Qualifying Patterns)

**Agent B rewards these patterns (lower Risk Score):**

1. **Technical Uncertainty Keywords**:
   - "algorithm design uncertain"
   - "architectural approach unknown"
   - "performance characteristics unclear"
   - "integration method undefined"

2. **Experimentation Evidence**:
   - "evaluated N alternatives"
   - "tested approaches A, B, C"
   - "benchmarked performance"
   - "failed attempt: [specific]"

3. **Specific Metrics**:
   - "reduced latency by 40ms"
   - "achieved 99.9% uptime"
   - "10x throughput improvement"
   - "decreased memory usage from X to Y"

4. **Hypothesis-Test-Failure Pattern**:
   - "hypothesized that..."
   - "tested by implementing..."
   - "failed due to [technical reason]"
   - "iterated with approach..."

5. **Hard Science Foundation**:
   - "applied algorithm X from CS theory"
   - "leveraged principles of distributed systems"
   - "utilized cryptographic protocol Y"
   - "implemented based on engineering model Z"

---

## Risk Scoring Algorithm

### Weighted Calculation (0-100 scale)

```python
risk_score = (
    routine_engineering_penalty * 0.30 +
    vagueness_penalty * 0.25 +
    business_risk_penalty * 0.20 +
    missing_experimentation_penalty * 0.15 +
    lack_of_specificity_penalty * 0.10
)

# Lower score = lower audit risk
# Target: < 20 for "audit-proof"
```

### Penalty Breakdown

| Component | Weight | Max Penalty | Triggers |
|-----------|--------|-------------|----------|
| **Routine Engineering** | 30% | 30 pts | Keywords: debugging, porting, maintenance |
| **Vagueness** | 25% | 25 pts | No metrics, generic claims, buzzwords |
| **Business Risk** | 20% | 20 pts | Market concerns, not technical |
| **No Experimentation** | 15% | 15 pts | Missing alternatives, no evaluation |
| **Lack of Specificity** | 10% | 10 pts | No numbers, no concrete details |

### Redline Markup Format

```json
{
  "risk_score": 65,
  "issues": [
    {
      "line": 12,
      "pattern": "optimized performance",
      "severity": "high",
      "reason": "Vague claim without metrics (IRS Red Flag: unsubstantiated improvement)",
      "suggestion": "Specify metric: 'reduced response time from 200ms to 40ms'"
    }
  ],
  "summary": "Narrative contains 3 high-severity issues typical of rejected claims"
}
```

---

## Implementation Plan (9 Days)

### Days 1-2: Agent B (Green Agent) - MVP

**Goal**: Basic A2A server with 5 core IRS rules

**Files to Create**:

```
src/bulletproof_green/
├── __init__.py
├── server.py              # A2A server entrypoint
├── examiner.py            # AgentExecutor implementation
├── rules/
│   ├── __init__.py
│   ├── routine_engineering.py
│   ├── vagueness_detector.py
│   └── experimentation_checker.py
├── scorer.py              # Risk score calculation
└── redline.py             # Markup generation

Dockerfile.green
agent-card-green.json
```

**Core Rules (Minimal Set)**:

1. Routine engineering keyword detection (10 keywords)
2. Vagueness detection (lack of metrics)
3. Experimentation evidence check (alternatives mentioned?)
4. Specificity scoring (numbers present?)
5. Business vs technical risk (market/sales keywords)

### Days 3-4: Agent A (Purple Agent) - Baseline

**Goal**: Template-based narrative generator with mock data

**Files to Create**:

```
src/bulletproof_purple/
├── __init__.py
├── server.py              # A2A server entrypoint
├── substantiator.py       # AgentExecutor implementation
├── templates/
│   ├── __init__.py
│   └── four_part_test.py  # IRS Section 41 template
├── mock_data.py           # Simulated engineering data
└── generator.py           # Narrative construction

Dockerfile.purple
agent-card-purple.json
```

**Mock Data Sources**:

- 5 sample "projects" with commit messages
- 3-5 technical uncertainties per project
- 2-3 alternatives evaluated
- Specific metrics (latency, throughput, error rates)

### Days 5-6: Assessment Flow + Docker

**Goal**: End-to-end A2A assessment working locally

**Files to Create**:

```
scenario.toml
docker-compose.yml
.dockerignore
```

**Testing**:

```bash
# Build and start containers
docker-compose build
docker-compose up -d

# Verify A2A handshake
curl http://localhost:8001/.well-known/agent-card.json
curl http://localhost:8002/.well-known/agent-card.json

# Run e2e assessment test
pytest tests/integration/test_e2e_assessment.py

# Check results output
cat results/local_benchmark.json
# Verify structure: {participant_id, pass_rate, traffic_light_green_pct, n_tasks, risk_scores[]}

# Query results with DuckDB (optional)
duckdb -c "SELECT participant_id, ROUND(pass_rate, 2) AS pass_rate, ROUND(traffic_light_green_pct, 2) AS green_pct, n_tasks FROM read_json_auto('results/local_benchmark.json')"
```

### Days 7-8: Demo + Documentation

**Goal**: Submission package ready

**Deliverables**:

- README.md with setup instructions
- Abstract (300 words) describing benchmark
- Record 3-minute demo video
- Test on clean machine

### Day 9: Submit

**Actions**:

1. Register agents on agentbeats.dev
2. Push Docker images to GHCR
3. Submit Phase 1 form
4. Buffer for last-minute issues

---

## File Structure (Minimal)

```
bulletproof-protocol/
├── src/
│   ├── bulletproof_green/         # Agent B (Green)
│   │   ├── server.py
│   │   ├── examiner.py
│   │   ├── rules/
│   │   ├── scorer.py
│   │   └── redline.py
│   └── bulletproof_purple/        # Agent A (Purple)
│       ├── server.py
│       ├── substantiator.py
│       ├── templates/
│       └── mock_data.py
├── Dockerfile.green
├── Dockerfile.purple
├── agent-card-green.json
├── agent-card-purple.json
├── scenario.toml
├── docker-compose.yml
├── README.md
├── ABSTRACT.md
└── pyproject.toml
```

---

## Key Sources & References

**Platform, Repos & A2A Protocol**: See [RESOURCES.md](RESOURCES.md)

### A2A Implementation Guides

- [A2A Protocol Specification (Python)](https://a2aprotocol.ai/docs/guide/a2a-protocol-specification-python)
- [Python A2A Tutorial](https://a2aprotocol.ai/blog/python-a2a-tutorial-with-source-code)
- [A2A Sample Methods](https://a2aprotocol.ai/blog/a2a-sample-methods-and-json-responses)

### IRS Section 41

- [IRS Audit Techniques Guide - Qualified Research Activities](https://www.irs.gov/businesses/audit-techniques-guide-credit-for-increasing-research-activities-ie-research-tax-credit-irc-ss-41-qualified-research-activities)
- [IRS Software Development Guidelines](https://www.irs.gov/businesses/audit-guidelines-on-the-application-of-the-process-of-experimentation-for-all-software)
- [26 USC 41 - Credit for Increasing Research Activities](https://uscode.house.gov/view.xhtml?req=(title:26+section:41+edition:prelim))
- [26 CFR § 1.41-4 - Qualified Research Regulations](https://www.law.cornell.edu/cfr/text/26/1.41-4)

---

## Success Criteria

**Phase 1 Submission Requirements Met**:

- [ ] A2A-compatible green agent (Docker image)
- [ ] A2A-compatible baseline purple agent (Docker image)
- [ ] End-to-end assessment flow works
- [ ] Abstract written (300 words)
- [ ] README with clear setup instructions
- [ ] 3-minute demo video recorded
- [ ] Registered on agentbeats.dev
- [ ] Submitted via Phase 1 form

**Technical Quality**:

- [ ] Docker builds on linux/amd64
- [ ] Accepts --host, --port, --card-url arguments
- [ ] Returns valid JSON artifacts
- [ ] Risk score calculation consistent
- [ ] Redline markup actionable

**Benchmark Validity**:

- [ ] Evaluates real legal domain criteria (IRS Section 41)
- [ ] Clear scoring methodology (0-100 scale)
- [ ] Reproducible results (same input → same score)
- [ ] Addresses gap (no existing R&D tax benchmark)
- [ ] Practical use case (startups, tax professionals)
