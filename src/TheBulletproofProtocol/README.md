# Application

## What

Legal Domain Agent Benchmark for AgentBeats competition - IRS Section 41 R&D tax credit evaluator. Purple agent (reference implementation) generates test narratives, Green agent (benchmark) evaluates them for IRS compliance.

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
├── integration
│   ├── __init__.py
│   ├── __pycache__
│   │   ├── __init__.cpython-314.pyc
│   │   ├── test_e2e_assessment.cpython-314-pytest-9.0.2.pyc
│   │   ├── test_green_agent.cpython-314-pytest-9.0.2.pyc
│   │   └── test_purple_agent.cpython-314-pytest-9.0.2.pyc
│   ├── test_e2e_assessment.py
│   ├── test_green_agent.py
│   └── test_purple_agent.py
├── __pycache__
│   ├── __init__.cpython-314.pyc
│   ├── test_docker_compose.cpython-314-pytest-9.0.2.pyc
│   ├── test_dockerfile_green.cpython-314-pytest-9.0.2.pyc
│   ├── test_dockerfile_purple.cpython-314-pytest-9.0.2.pyc
│   ├── test_experimentation_checker.cpython-314-pytest-9.0.2.pyc
│   ├── test_ghcr_scripts.cpython-314-pytest-9.0.2.pyc
│   ├── test_green_agent_executor.cpython-314-pytest-9.0.2.pyc
│   ├── test_green_agent_integration.cpython-314-pytest-9.0.2.pyc
│   ├── test_green_agent_server.cpython-314-pytest-9.0.2.pyc
│   ├── test_purple_agent_executor.cpython-314-pytest-9.0.2.pyc
│   ├── test_purple_agent_server.cpython-314-pytest-9.0.2.pyc
│   ├── test_routine_engineering.cpython-314-pytest-9.0.2.pyc
│   ├── test_scenario_config.cpython-314-pytest-9.0.2.pyc
│   ├── test_scorer.cpython-314-pytest-9.0.2.pyc
│   └── test_vagueness_detector.cpython-314-pytest-9.0.2.pyc
├── test_docker_compose.py
├── test_dockerfile_green.py
├── test_dockerfile_purple.py
├── test_experimentation_checker.py
├── test_ghcr_scripts.py
├── test_green_agent_executor.py
├── test_green_agent_integration.py
├── test_green_agent_server.py
├── test_purple_agent_executor.py
├── test_purple_agent_server.py
├── test_routine_engineering.py
├── test_scenario_config.py
├── test_scorer.py
└── test_vagueness_detector.py
```

## Development

Built with Ralph Loop autonomous development using TDD.
