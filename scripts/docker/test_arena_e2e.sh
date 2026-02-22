#!/bin/bash
################################################################################
# ARENA MODE PYTEST E2E INTEGRATION TESTS
################################################################################
#
# PURPOSE:
#   Arena mode specific E2E testing using pytest and FastAPI TestClient.
#   Tests multi-turn refinement, A2A protocol details, and arena configuration.
#
#   This is for ARENA MODE validation (iterative refinement, critique flow).
#   For SYSTEM-WIDE Docker tests, use: test_e2e.sh
#
# WHAT THIS TESTS:
#   ✓ Arena mode multi-turn iterative refinement
#   ✓ Green → Purple → Green critique loop
#   ✓ ArenaExecutor with real Purple agent
#   ✓ A2A protocol message format validation
#   ✓ Configuration (max_iterations, target_risk_score)
#   ✓ Error handling (Purple agent unavailable)
#   ✓ Risk score improvement across iterations
#
# WHAT THIS DOES NOT TEST:
#   ✗ Docker deployment (use test_e2e.sh)
#   ✗ Full system integration (use test_e2e.sh)
#   ✗ Ground truth dataset (use test_e2e.sh comprehensive)
#
# USAGE:
#   test_arena_e2e.sh
#
# TECHNOLOGY:
#   - pytest for test execution
#   - FastAPI TestClient (no HTTP server needed for Green)
#   - Real Purple agent (auto-started via Docker or manual)
#   - Configuration from settings.py (not hardcoded)
#
# PREREQUISITES:
#   1. Python environment with dependencies:
#      pip install -e .[dev]
#
#   2. Purple agent (auto-started by script):
#      Option A: docker-compose (preferred, automatic)
#      Option B: Manual - cd src && python -m bulletproof_purple.server
#      Option C: External - start before running script
#
#   3. Optional: OpenAI API key (if Purple uses LLMs)
#      export OPENAI_API_KEY=your-key
#
# CONFIGURATION:
#   All settings come from settings.py (not hardcoded):
#   - Purple host/port: bulletproof_purple.settings
#   - Purple URL: bulletproof_green.settings.purple_agent_url
#   - Agent card path: Standard A2A protocol path
#
# ENVIRONMENT:
#   PURPLE_HOST=localhost         Override Purple agent host (from settings.py)
#   PURPLE_PORT=8001              Override Purple agent port (from settings.py)
#   PURPLE_AGENT_URL=http://...   Override full Purple URL (from settings.py)
#
# OUTPUTS:
#   - pytest console output with test results
#   - Arena iteration details (risk scores, termination)
#   - PASSED/FAILED/SKIPPED status for each test
#
# TEST STRUCTURE:
#   tests/test_arena_integration.py
#   ├── TestArenaIntegrationBasicFlow
#   │   ├── test_arena_mode_completes_successfully
#   │   ├── test_arena_mode_respects_max_iterations
#   │   └── test_arena_mode_iteration_improvement
#   ├── TestArenaIntegrationA2AProtocol
#   │   ├── test_purple_agent_a2a_message_format
#   │   └── test_arena_mode_with_different_contexts
#   └── TestArenaIntegrationErrorHandling
#       └── test_arena_mode_with_invalid_purple_agent_url
#
# PERFORMANCE:
#   - Duration: 45-120 seconds (SLOW due to real LLM calls)
#   - Cost: Real OpenAI API calls (charges apply)
#   - Parallelization: Tests run sequentially (pytest -n not recommended)
#
# EXAMPLES:
#   # Standard usage (auto-detects docker-compose)
#   test_arena_e2e.sh
#
#   # Force Docker usage
#   docker-compose -f docker-compose-local.yml up -d purple
#   test_arena_e2e.sh
#
#   # Force manual usage (no Docker)
#   cd src && python -m bulletproof_purple.server &
#   cd .. && test_arena_e2e.sh
#
#   # With custom Purple port
#   PURPLE_PORT=9001 test_arena_e2e.sh
#
#   # Run via pytest directly (requires Purple running)
#   pytest tests/test_arena_integration.py -v
#
#   # Run specific test
#   pytest tests/test_arena_integration.py::TestArenaIntegrationBasicFlow -v
#
################################################################################

set -e  # Exit on error

# Source common utilities (DRY principle)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/common.sh"

# Configuration (gets defaults from settings.py - NOT hardcoded!)
# Override via environment: PURPLE_PORT=9001 test_arena_e2e.sh

# Load settings from Python in ONE call
read -r DEFAULT_PURPLE_HOST DEFAULT_PURPLE_PORT DEFAULT_PURPLE_URL < <(load_purple_agent_settings)

# Use environment overrides or defaults from settings
PURPLE_HOST=${PURPLE_HOST:-${DEFAULT_PURPLE_HOST}}
PURPLE_PORT=${PURPLE_PORT:-${DEFAULT_PURPLE_PORT}}
PURPLE_AGENT_URL=${PURPLE_AGENT_URL:-${DEFAULT_PURPLE_URL}}

TEST_TIMEOUT=300  # 5 minutes total timeout for pytest execution
PURPLE_STARTUP_WAIT=5  # Seconds to wait for Purple agent to start (if started by script)

# Unified cleanup function
cleanup() {
    if [ ! -z "$PURPLE_DOCKER" ]; then
        cleanup_purple_docker "docker-compose-local.yml"
    elif [ ! -z "$PURPLE_PID" ]; then
        cleanup_purple_agent
    fi
}

# Set trap to cleanup on exit
trap cleanup EXIT

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  E2E Integration Test Runner${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Step 1: Check if Purple agent is already running
info "Checking if Purple agent is already running..."
info "Purple agent URL: ${PURPLE_AGENT_URL}"
if check_purple_agent_available "${PURPLE_AGENT_URL}"; then
    success "Purple agent already running at ${PURPLE_AGENT_URL}"
    EXTERNAL_PURPLE=true
else
    warning "Purple agent not running, will start it"
    EXTERNAL_PURPLE=false
fi

# Step 2: Start Purple agent if not already running
if [ "$EXTERNAL_PURPLE" = false ]; then
    echo ""

    # Prefer docker-compose if available (KISS principle)
    if is_docker_available; then
        info "Docker available, using docker-compose..."
        if start_purple_docker "${PURPLE_AGENT_URL}" "docker-compose-local.yml"; then
            PURPLE_DOCKER=true
        else
            error "Failed to start Purple agent via Docker"
            exit 1
        fi
    else
        # Fallback to manual startup
        info "Docker not available, starting Purple agent manually..."

        cd src
        python -m bulletproof_purple.server &
        PURPLE_PID=$!
        cd ..

        success "Purple agent started (PID: $PURPLE_PID)"

        # Wait for Purple agent to be ready
        info "Waiting ${PURPLE_STARTUP_WAIT}s for Purple agent to start..."
        sleep $PURPLE_STARTUP_WAIT

        # Verify Purple agent is responding with retries
        if wait_for_purple_agent "${PURPLE_AGENT_URL}" 10 1; then
            success "Purple agent ready!"
        else
            error "Purple agent failed to start"
            exit 1
        fi
    fi
fi

# Step 3: Run E2E tests
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Running E2E Tests${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

export PURPLE_AGENT_URL="${PURPLE_AGENT_URL}"

# Run integration tests with timeout
timeout $TEST_TIMEOUT pytest tests/test_arena_integration.py -v -s "$@"
TEST_EXIT_CODE=$?

echo ""
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  ✓ All E2E tests passed!${NC}"
    echo -e "${GREEN}========================================${NC}"
else
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}  ✗ Some E2E tests failed${NC}"
    echo -e "${RED}========================================${NC}"
fi

# Cleanup will happen automatically via trap
exit $TEST_EXIT_CODE
