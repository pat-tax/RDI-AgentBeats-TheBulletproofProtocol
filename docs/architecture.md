# Architecture

## Code Organization Pattern

**Separation of Concerns (following debate_judge template):**

| File | Responsibility | Description |
|------|----------------|-------------|
| `agent.py` | **"What the agent does"** (domain) | AgentCard definition, GreenAgent class, evaluation logic, domain models |
| `executor.py` | **"How to invoke it"** (protocol adapter) | Thin wrapper: A2A params → Agent.run() → A2A response, task lifecycle only |
| `server.py` | **"How to expose it"** (transport) | HTTP server setup, request routing, entry point |
| `messenger.py` | **"How agents talk"** (communication) | A2A SDK client integration, inter-agent communication via ClientFactory.connect() |

## Project Structure

```
src/bulletproof_green/
├── agent.py           # Domain (what it does)
├── executor.py        # Protocol adapter (how to invoke)
├── server.py          # Transport (how to expose)
├── messenger.py       # Communication (A2A messaging for all agents)
├── models.py          # Pydantic models (all data validation)
├── settings.py        # Configuration
├── arena/             # Arena mode (multi-turn refinement)
│   └── executor.py    #   - Arena orchestration (uses messenger.py)
└── evals/             # Evaluation domain
    ├── evaluator.py   #   - Rule-based evaluation
    ├── scorer.py      #   - AgentBeats scoring
    └── llm_judge.py   #   - LLM hybrid scoring
```

## Benefits

- **KISS**: Clear separation - domain vs protocol vs transport
- **DRY**: Agent class usable standalone without A2A overhead
- **Testable**: Domain logic independent of server
- **Matches Template**: Same structure as debate_judge reference implementation
