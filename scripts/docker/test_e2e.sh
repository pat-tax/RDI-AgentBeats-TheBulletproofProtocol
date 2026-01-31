#!/bin/bash
################################################################################
# DOCKER-BASED E2E SYSTEM INTEGRATION TESTS
################################################################################
#
# PURPOSE:
#   Full system integration testing using Docker Compose to deploy both
#   Purple (generator) and Green (evaluator) agents. Tests complete A2A
#   workflow, agent communication, and validates against ground truth dataset.
#
#   This is for SYSTEM-WIDE validation (deployment, containers, networking).
#   For ARENA MODE specific pytest tests, use: ./scripts/test_arena_e2e.sh
#
# WHAT THIS TESTS:
#   ✓ Docker deployment of both agents
#   ✓ Agent card discovery via HTTP
#   ✓ Purple agent narrative generation
#   ✓ Green agent evaluation
#   ✓ A2A JSON-RPC protocol
#   ✓ Ground truth dataset validation
#
# WHAT THIS DOES NOT TEST:
#   ✗ Arena mode multi-turn refinement (use test_arena_e2e.sh)
#   ✗ Detailed pytest assertions (use test_arena_e2e.sh)
#   ✗ Python-only integration (use test_arena_e2e.sh)
#
# USAGE:
#   ./scripts/test_e2e.sh [MODE] [OPTIONS]
#
# MODES:
#   quick (default)      Quick smoke test with 2 narratives (30-60s)
#   comprehensive/full   Full ground truth dataset validation (5-10min)
#
# OPTIONS:
#   --build              Rebuild Docker images before starting
#   --help, -h           Show this help message
#
# ENVIRONMENT:
#   E2E_MODE=quick|comprehensive   Set test mode
#   E2E_BUILD=1                    Enable --build flag
#
# FOR ARENA MODE TESTS:
#   Use: ./scripts/test_arena_e2e.sh (separate pytest-based tests)
#
# PREREQUISITES:
#   - Docker and docker-compose installed
#   - Ports 9010 (Purple) and 9009 (Green) available
#   - Ground truth data at: data/ground_truth.json
#
# OUTPUTS:
#   logs/e2e_YYYYMMDD_HHMMSS/
#   ├── summary.log                    Test results summary
#   ├── results.json                   Machine-readable results
#   ├── purple_agent_card.json         Purple agent metadata
#   ├── green_agent_card.json          Green agent metadata
#   ├── *_response.json                Individual test responses
#
# EXAMPLES:
#   # Quick smoke test (recommended for CI)
#   ./scripts/test_e2e.sh quick
#
#   # Full validation (pre-release)
#   ./scripts/test_e2e.sh comprehensive
#
#   # Rebuild containers first
#   ./scripts/test_e2e.sh quick --build
#
#   # For arena mode pytest tests (separate script):
#   ./scripts/test_arena_e2e.sh
#
################################################################################

set -e

# Source common utilities (DRY principle)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/common.sh"

# Defaults from environment
TEST_MODE="${E2E_MODE:-quick}"
BUILD_FLAG=""
[[ "${E2E_BUILD:-0}" == "1" ]] && BUILD_FLAG="--build"

# Docker Compose configuration (aligns with docker-compose-local.yml)
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose-local.yml}"

# Parse command line arguments
for arg in "$@"; do
    case "$arg" in
        quick|--quick)
            TEST_MODE="quick"
            ;;
        comprehensive|--comprehensive|full|--full)
            TEST_MODE="comprehensive"
            ;;
        --build)
            BUILD_FLAG="--build"
            ;;
        --help|-h)
            echo "Usage: $0 [MODE] [OPTIONS]"
            echo ""
            echo "Modes:"
            echo "  quick (default)      Quick smoke test with 2 narratives"
            echo "  comprehensive/full   Full test with ground truth dataset"
            echo ""
            echo "Options:"
            echo "  --build              Rebuild containers before testing"
            echo ""
            echo "Environment variables:"
            echo "  E2E_MODE=quick|comprehensive"
            echo "  E2E_BUILD=1"
            echo ""
            echo "For arena mode pytest tests:"
            echo "  ./scripts/test_arena_e2e.sh"
            exit 0
            ;;
    esac
done

# Setup logging
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_DIR="logs/e2e_${TIMESTAMP}"
mkdir -p "$LOG_DIR"

echo "=========================================="
echo "End-to-End Agent Test"
echo "=========================================="
echo "Mode: $TEST_MODE"
echo "Logs: $LOG_DIR"

# Colors imported from common.sh
# Helper functions for test logging
pass() { success "$1"; echo "PASS: $1" >> "$LOG_DIR/summary.log"; }
fail() { error "$1"; echo "FAIL: $1" >> "$LOG_DIR/summary.log"; exit 1; }
warn() { warning "$1"; echo "WARN: $1" >> "$LOG_DIR/summary.log"; }
# info() already defined in common.sh, just add logging
_info_log() { info "$1"; echo "INFO: $1" >> "$LOG_DIR/summary.log"; }

# Required output fields
REQUIRED_FIELDS="domain score max_score pass_rate task_rewards time_used overall_score correctness safety specificity experimentation classification risk_score risk_category confidence redline"

#
# Start containers
#
start_containers() {
    echo ""
    echo "Step 1: Starting containers..."
    if [ -n "$BUILD_FLAG" ]; then
        echo "(with --build)"
    fi
    docker-compose -f "$COMPOSE_FILE" up -d $BUILD_FLAG

    echo "Waiting for agents to be ready..."
    for i in {1..30}; do
        if curl -s http://localhost:9010/.well-known/agent-card.json > /dev/null 2>&1 && \
           curl -s http://localhost:9009/.well-known/agent-card.json > /dev/null 2>&1; then
            break
        fi
        sleep 1
    done

    echo ""
    echo "Step 2: Checking containers..."
    if docker-compose -f "$COMPOSE_FILE" ps | grep -q "Up"; then
        pass "Containers running"
    else
        fail "Containers not running"
    fi
}

#
# Test agent cards
#
test_agent_cards() {
    echo ""
    echo "Step 3: Testing Purple AgentCard..."
    PURPLE_CARD=$(curl -s http://localhost:9010/.well-known/agent-card.json)
    echo "$PURPLE_CARD" > "$LOG_DIR/purple_agent_card.json"
    if echo "$PURPLE_CARD" | grep -q "Bulletproof Purple Agent"; then
        pass "Purple AgentCard OK"
    else
        fail "Purple AgentCard failed"
    fi

    echo ""
    echo "Step 4: Testing Green AgentCard..."
    GREEN_CARD=$(curl -s http://localhost:9009/.well-known/agent-card.json)
    echo "$GREEN_CARD" > "$LOG_DIR/green_agent_card.json"
    if echo "$GREEN_CARD" | grep -q "Bulletproof Green Agent"; then
        pass "Green AgentCard OK"
    else
        fail "Green AgentCard failed"
    fi
}

#
# Test Purple narrative generation
#
test_purple_agent() {
    echo ""
    echo "Step 5: Testing Purple Agent (narrative generation)..."
    PURPLE_RESPONSE=$(curl -s -X POST http://localhost:9010/ \
        -H "Content-Type: application/json" \
        -d '{"jsonrpc":"2.0","id":"1","method":"message/send","params":{"message":{"messageId":"test-1","role":"user","parts":[{"text":"Generate a qualifying R&D narrative"}]}}}')
    echo "$PURPLE_RESPONSE" > "$LOG_DIR/purple_narrative_response.json"

    if echo "$PURPLE_RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if 'narrative' in str(d) else 1)" 2>/dev/null; then
        pass "Purple Agent generated narrative"
    else
        fail "Purple Agent failed to generate narrative"
    fi
}

#
# Call Green Agent and return response
#
call_green_agent() {
    local narrative="$1"
    local id="$2"
    curl -s -X POST http://localhost:9009/ \
        -H "Content-Type: application/json" \
        -d "{\"jsonrpc\":\"2.0\",\"id\":\"$id\",\"method\":\"message/send\",\"params\":{\"message\":{\"messageId\":\"test-$id\",\"role\":\"user\",\"parts\":[{\"text\":\"$narrative\"}]}}}"
}

#
# Extract field from Green Agent response
#
extract_field() {
    local response="$1"
    local field="$2"
    echo "$response" | python3 -c "import sys,json; print(json.load(sys.stdin)['result']['parts'][0]['data']['$field'])" 2>/dev/null || echo "ERROR"
}

#
# Print metrics from response
#
print_metrics() {
    local response="$1"
    local label="$2"
    echo "$label:"
    echo "$response" | python3 -c "
import sys,json
d=json.load(sys.stdin)['result']['parts'][0]['data']
print(f\"  Classification: {d['classification']}\")
print(f\"  Risk Score: {d['risk_score']}\")
print(f\"  Risk Category: {d['risk_category']}\")
print(f\"  Overall Score: {d['overall_score']:.2f}\")
print(f\"  Pass Rate: {d['pass_rate']:.1f}%\")
print(f\"  Score: {d['score']}/{d['max_score']}\")
" 2>/dev/null || echo "  Could not extract metrics"
}

#
# Quick mode tests
#
run_quick_tests() {
    echo ""
    echo "Step 6: Testing Green Agent (non-qualifying narrative)..."
    GREEN_RESPONSE_BAD=$(call_green_agent "We used standard debugging and routine maintenance to fix bugs and improve market share." "2")
    echo "$GREEN_RESPONSE_BAD" > "$LOG_DIR/green_eval_non_qualifying.json"

    PASS_RATE_BAD=$(extract_field "$GREEN_RESPONSE_BAD" "pass_rate")
    if python3 -c "exit(0 if float('$PASS_RATE_BAD') <= 50 else 1)" 2>/dev/null; then
        pass "Green Agent correctly identified NON_QUALIFYING (pass_rate=$PASS_RATE_BAD%)"
    else
        echo "Got pass_rate: $PASS_RATE_BAD%"
        fail "Green Agent failed to identify NON_QUALIFYING"
    fi

    echo ""
    echo "Step 7: Testing Green Agent (qualifying narrative)..."
    GREEN_RESPONSE_GOOD=$(call_green_agent "Our hypothesis was that a novel architecture could resolve the technical uncertainty. Through experimentation, we tested alternatives. Iterations failed with 50ms latency. The unknown solution emerged from systematic failure analysis." "3")
    echo "$GREEN_RESPONSE_GOOD" > "$LOG_DIR/green_eval_qualifying.json"

    PASS_RATE_GOOD=$(extract_field "$GREEN_RESPONSE_GOOD" "pass_rate")
    if python3 -c "exit(0 if float('$PASS_RATE_GOOD') > 50 else 1)" 2>/dev/null; then
        pass "Green Agent correctly identified QUALIFYING (pass_rate=$PASS_RATE_GOOD%)"
    else
        echo "Got pass_rate: $PASS_RATE_GOOD%"
        fail "Green Agent failed to identify QUALIFYING"
    fi

    echo ""
    echo "Step 8: Validating Green Agent output fields..."
    MISSING_FIELDS=$(echo "$GREEN_RESPONSE_BAD" | python3 -c "
import sys, json
d = json.load(sys.stdin)['result']['parts'][0]['data']
required = '$REQUIRED_FIELDS'.split()
missing = [f for f in required if f not in d]
if missing:
    print(' '.join(missing))
" 2>/dev/null)

    if [ -z "$MISSING_FIELDS" ]; then
        pass "Green Agent outputs all required fields"
    else
        echo "Missing fields: $MISSING_FIELDS"
        fail "Green Agent missing fields"
    fi

    echo ""
    echo "Step 9: Score Summary..."
    echo "----------------------------------------"
    print_metrics "$GREEN_RESPONSE_BAD" "Non-qualifying narrative"
    echo ""
    print_metrics "$GREEN_RESPONSE_GOOD" "Qualifying narrative"

    # Generate results.json
    python3 -c "
import json
from datetime import datetime

bad = json.loads('''$GREEN_RESPONSE_BAD''')['result']['parts'][0]['data']
good = json.loads('''$GREEN_RESPONSE_GOOD''')['result']['parts'][0]['data']

results = {
    'timestamp': datetime.utcnow().isoformat() + 'Z',
    'version': '1.0',
    'mode': 'quick',
    'participants': {'agent': 'green-agent-local'},
    'results': [
        {k: bad[k] for k in ['domain', 'score', 'max_score', 'pass_rate', 'task_rewards', 'time_used', 'classification', 'risk_score', 'overall_score']},
        {k: good[k] for k in ['domain', 'score', 'max_score', 'pass_rate', 'task_rewards', 'time_used', 'classification', 'risk_score', 'overall_score']}
    ]
}
results['results'][0]['test_case'] = 'non_qualifying'
results['results'][1]['test_case'] = 'qualifying'

print(json.dumps(results, indent=2))
" > "$LOG_DIR/results.json" 2>/dev/null
}

#
# Comprehensive mode tests
#
run_comprehensive_tests() {
    echo ""
    echo "Step 6: Testing all narratives from ground truth..."
    echo "Dataset size: $(jq 'length' data/ground_truth.json)"
    echo "=========================================="

    # Initialize counters
    local total=0
    local correct=0

    # Process each narrative
    jq -c '.[]' data/ground_truth.json | while read -r test_case; do
        INDEX=$(echo "$test_case" | jq -r '.id')
        EXPECTED_CLASS=$(echo "$test_case" | jq -r '.classification')
        NARRATIVE=$(echo "$test_case" | jq -r '.narrative' | sed 's/"/\\"/g')

        echo ""
        echo "Testing $INDEX ($EXPECTED_CLASS)..."

        RESPONSE=$(call_green_agent "$NARRATIVE" "$INDEX")
        echo "$RESPONSE" > "$LOG_DIR/${INDEX}_response.json"

        ACTUAL_CLASS=$(extract_field "$RESPONSE" "classification")
        ACTUAL_SCORE=$(extract_field "$RESPONSE" "overall_score")

        if [ "$ACTUAL_CLASS" = "$EXPECTED_CLASS" ]; then
            pass "$INDEX: $ACTUAL_CLASS (score: $ACTUAL_SCORE)"
        else
            warn "$INDEX: Expected $EXPECTED_CLASS, got $ACTUAL_CLASS (score: $ACTUAL_SCORE)"
        fi
    done

    echo ""
    echo "Step 7: Generating comprehensive report..."

    # Generate comprehensive report
    python3 << 'PYTHON_EOF'
import json
from datetime import datetime
import glob
import os

log_dir = os.environ.get('LOG_DIR', 'logs')

# Load ground truth
with open("data/ground_truth.json") as f:
    ground_truth = {item["id"]: item for item in json.load(f)}

results = {
    "timestamp": datetime.utcnow().isoformat() + "Z",
    "version": "1.0",
    "mode": "comprehensive",
    "total_tests": 0,
    "correct": 0,
    "incorrect": 0,
    "accuracy": 0.0,
    "tests": []
}

# Process each response
for response_file in sorted(glob.glob(f"{log_dir}/*_response.json")):
    test_id = os.path.basename(response_file).split("_")[0]
    if test_id in ["purple", "green"]:
        continue

    try:
        with open(response_file) as f:
            response = json.load(f)

        data = response.get("result", {}).get("parts", [{}])[0].get("data", {})
        actual_class = data.get("classification", "ERROR")
        expected = ground_truth.get(test_id, {})
        expected_class = expected.get("classification", "UNKNOWN")

        results["total_tests"] += 1
        match = actual_class == expected_class
        if match:
            results["correct"] += 1
        else:
            results["incorrect"] += 1

        results["tests"].append({
            "id": test_id,
            "expected": expected_class,
            "actual": actual_class,
            "match": match,
            "score": data.get("overall_score"),
            "pass_rate": data.get("pass_rate")
        })
    except Exception as e:
        print(f"Error processing {response_file}: {e}")

if results["total_tests"] > 0:
    results["accuracy"] = round((results["correct"] / results["total_tests"]) * 100, 2)

with open(f"{log_dir}/results.json", "w") as f:
    json.dump(results, f, indent=2)

print(f"\nAccuracy: {results['accuracy']}% ({results['correct']}/{results['total_tests']})")
PYTHON_EOF
}

#
# Main execution
#
start_containers
test_agent_cards
test_purple_agent

if [ "$TEST_MODE" = "comprehensive" ]; then
    export LOG_DIR
    run_comprehensive_tests
else
    run_quick_tests
fi

echo ""
echo "=========================================="
echo -e "${GREEN}All tests completed!${NC}"
echo "=========================================="
echo ""
echo "Logs saved to: $LOG_DIR"
ls -la "$LOG_DIR"

# Optional: Stop containers
echo ""
read -p "Stop containers? (y/N): " STOP
if [ "$STOP" = "y" ] || [ "$STOP" = "Y" ]; then
    docker-compose -f "$COMPOSE_FILE" down
    echo "Containers stopped."
fi
