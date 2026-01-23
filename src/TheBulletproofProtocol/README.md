# Application

## What

Application description

## Why

- Create A2A-compatible HTTP server for purple agent (reference implementation) with AgentCard discovery and task execution endpoints
- Create AgentExecutor implementation for purple agent that generates simple R&D narratives for testing the benchmark
- Build Docker container for purple agent targeting linux/amd64 platform with a2a-sdk dependencies
- Create A2A-compatible HTTP server for green agent (benchmark) with AgentCard discovery and task execution endpoints
- Create AgentExecutor implementation for green agent that evaluates narratives and returns structured judgments

## Quick Start

```bash
# Run application
python -m TheBulletproofProtocol

# Run example
python src/TheBulletproofProtocol/example.py

# Run tests
pytest tests/
```

## Architecture

```text
src/TheBulletproofProtocol
├── example.py
├── __init__.py
└── README.md
tests/
├── __init__.py
├── __pycache__
│   ├── __init__.cpython-314.pyc
│   ├── test_dockerfile_purple.cpython-314-pytest-9.0.2.pyc
│   ├── test_green_agent_executor.cpython-314-pytest-9.0.2.pyc
│   ├── test_green_agent_server.cpython-314-pytest-9.0.2.pyc
│   ├── test_purple_agent_executor.cpython-314-pytest-9.0.2.pyc
│   └── test_purple_agent_server.cpython-314-pytest-9.0.2.pyc
├── test_dockerfile_purple.py
├── test_green_agent_executor.py
├── test_green_agent_server.py
├── test_purple_agent_executor.py
└── test_purple_agent_server.py
```

## Development

Built with Ralph Loop autonomous development using TDD.
