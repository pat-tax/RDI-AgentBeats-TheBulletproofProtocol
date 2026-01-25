#!/bin/bash
#
# End-to-end test script for Purple and Green agents
#
# Usage: ./scripts/test_e2e.sh
#
# Prerequisites:
#   - Docker and docker-compose installed
#   - Ports 8001 and 8002 available
#
# Outputs:
#   - logs/e2e_YYYYMMDD_HHMMSS/ - Full test logs and responses
#

set -e

# Setup logging
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_DIR="logs/e2e_${TIMESTAMP}"
mkdir -p "$LOG_DIR"

echo "=========================================="
echo "End-to-End Agent Test"
echo "=========================================="
echo "Logs: $LOG_DIR"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

pass() { echo -e "${GREEN}✓ $1${NC}"; echo "PASS: $1" >> "$LOG_DIR/summary.log"; }
fail() { echo -e "${RED}✗ $1${NC}"; echo "FAIL: $1" >> "$LOG_DIR/summary.log"; exit 1; }

# Step 1: Start containers
echo ""
echo "Step 1: Starting containers..."
docker-compose up -d --build

# Wait for containers to be healthy
echo "Waiting for agents to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8001/.well-known/agent-card.json > /dev/null 2>&1 && \
       curl -s http://localhost:8002/.well-known/agent-card.json > /dev/null 2>&1; then
        break
    fi
    sleep 1
done

# Step 2: Check containers running
echo ""
echo "Step 2: Checking containers..."
if docker-compose ps | grep -q "Up"; then
    pass "Containers running"
else
    fail "Containers not running"
fi

# Step 3: Test Purple AgentCard
echo ""
echo "Step 3: Testing Purple AgentCard..."
PURPLE_CARD=$(curl -s http://localhost:8001/.well-known/agent-card.json)
echo "$PURPLE_CARD" > "$LOG_DIR/purple_agent_card.json"
if echo "$PURPLE_CARD" | grep -q "Bulletproof Purple Agent"; then
    pass "Purple AgentCard OK"
else
    fail "Purple AgentCard failed"
fi

# Step 4: Test Green AgentCard
echo ""
echo "Step 4: Testing Green AgentCard..."
GREEN_CARD=$(curl -s http://localhost:8002/.well-known/agent-card.json)
echo "$GREEN_CARD" > "$LOG_DIR/green_agent_card.json"
if echo "$GREEN_CARD" | grep -q "Bulletproof Green Agent"; then
    pass "Green AgentCard OK"
else
    fail "Green AgentCard failed"
fi

# Step 5: Test Purple narrative generation
echo ""
echo "Step 5: Testing Purple Agent (narrative generation)..."
PURPLE_RESPONSE=$(curl -s -X POST http://localhost:8001/ \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","id":"1","method":"message/send","params":{"message":{"messageId":"test-1","role":"user","parts":[{"text":"Generate a qualifying R&D narrative"}]}}}')
echo "$PURPLE_RESPONSE" > "$LOG_DIR/purple_narrative_response.json"

if echo "$PURPLE_RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if 'narrative' in str(d) else 1)" 2>/dev/null; then
    pass "Purple Agent generated narrative"
else
    fail "Purple Agent failed to generate narrative"
fi

# Step 6: Test Green evaluation (non-qualifying)
echo ""
echo "Step 6: Testing Green Agent (non-qualifying narrative)..."
GREEN_RESPONSE_BAD=$(curl -s -X POST http://localhost:8002/ \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","id":"2","method":"message/send","params":{"message":{"messageId":"test-2","role":"user","parts":[{"text":"We used standard debugging and routine maintenance to fix bugs and improve market share."}]}}}')
echo "$GREEN_RESPONSE_BAD" > "$LOG_DIR/green_eval_non_qualifying.json"

CLASSIFICATION_BAD=$(echo "$GREEN_RESPONSE_BAD" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['result']['parts'][0]['data']['classification'])" 2>/dev/null || echo "ERROR")
if [ "$CLASSIFICATION_BAD" = "NON_QUALIFYING" ]; then
    pass "Green Agent correctly identified NON_QUALIFYING"
else
    echo "Got classification: $CLASSIFICATION_BAD"
    fail "Green Agent failed to identify NON_QUALIFYING"
fi

# Step 7: Test Green evaluation (qualifying)
echo ""
echo "Step 7: Testing Green Agent (qualifying narrative)..."
GREEN_RESPONSE_GOOD=$(curl -s -X POST http://localhost:8002/ \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","id":"3","method":"message/send","params":{"message":{"messageId":"test-3","role":"user","parts":[{"text":"Our hypothesis was that a novel architecture could resolve the technical uncertainty. Through experimentation, we tested alternatives. Iterations failed with 50ms latency. The unknown solution emerged from systematic failure analysis."}]}}}')
echo "$GREEN_RESPONSE_GOOD" > "$LOG_DIR/green_eval_qualifying.json"

CLASSIFICATION_GOOD=$(echo "$GREEN_RESPONSE_GOOD" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['result']['parts'][0]['data']['classification'])" 2>/dev/null || echo "ERROR")
if [ "$CLASSIFICATION_GOOD" = "QUALIFYING" ]; then
    pass "Green Agent correctly identified QUALIFYING"
else
    echo "Got classification: $CLASSIFICATION_GOOD"
    fail "Green Agent failed to identify QUALIFYING"
fi

# Step 8: Validate Green Agent outputs scores
echo ""
echo "Step 8: Validating Green Agent score output..."

REQUIRED_FIELDS="overall_score correctness safety specificity experimentation risk_score risk_category confidence classification redline"
MISSING_FIELDS=$(echo "$GREEN_RESPONSE_BAD" | python3 -c "
import sys, json
d = json.load(sys.stdin)['result']['parts'][0]['data']
required = '$REQUIRED_FIELDS'.split()
missing = [f for f in required if f not in d]
if missing:
    print(' '.join(missing))
" 2>/dev/null)

if [ -z "$MISSING_FIELDS" ]; then
    pass "Green Agent outputs all required score fields"
else
    echo "Missing fields: $MISSING_FIELDS"
    fail "Green Agent missing score fields"
fi

# Step 9: Score Summary
echo ""
echo "Step 9: Score Summary..."
echo "----------------------------------------"

# Extract and log metrics
echo "=== METRICS ===" > "$LOG_DIR/metrics.log"
echo "" >> "$LOG_DIR/metrics.log"

echo "Non-qualifying narrative:"
echo "Non-qualifying narrative:" >> "$LOG_DIR/metrics.log"
METRICS_BAD=$(echo "$GREEN_RESPONSE_BAD" | python3 -c "
import sys,json
d=json.load(sys.stdin)['result']['parts'][0]['data']
print(f\"  Risk Score: {d['risk_score']}\")
print(f\"  Classification: {d['classification']}\")
print(f\"  Risk Category: {d['risk_category']}\")
print(f\"  Confidence: {d['confidence']}\")
print(f\"  Overall Score: {d['overall_score']:.2f}\")
print(f\"  Correctness: {d['correctness']:.2f}\")
print(f\"  Safety: {d['safety']:.2f}\")
print(f\"  Specificity: {d['specificity']:.2f}\")
print(f\"  Experimentation: {d['experimentation']:.2f}\")
" 2>/dev/null || echo "  Could not extract metrics")
echo "$METRICS_BAD"
echo "$METRICS_BAD" >> "$LOG_DIR/metrics.log"

echo ""
echo "" >> "$LOG_DIR/metrics.log"

echo "Qualifying narrative:"
echo "Qualifying narrative:" >> "$LOG_DIR/metrics.log"
METRICS_GOOD=$(echo "$GREEN_RESPONSE_GOOD" | python3 -c "
import sys,json
d=json.load(sys.stdin)['result']['parts'][0]['data']
print(f\"  Risk Score: {d['risk_score']}\")
print(f\"  Classification: {d['classification']}\")
print(f\"  Risk Category: {d['risk_category']}\")
print(f\"  Confidence: {d['confidence']}\")
print(f\"  Overall Score: {d['overall_score']:.2f}\")
print(f\"  Correctness: {d['correctness']:.2f}\")
print(f\"  Safety: {d['safety']:.2f}\")
print(f\"  Specificity: {d['specificity']:.2f}\")
print(f\"  Experimentation: {d['experimentation']:.2f}\")
" 2>/dev/null || echo "  Could not extract metrics")
echo "$METRICS_GOOD"
echo "$METRICS_GOOD" >> "$LOG_DIR/metrics.log"

# Generate AgentBeats-compatible results.json
echo "$GREEN_RESPONSE_BAD" | python3 -c "
import sys, json
from datetime import datetime

bad = json.load(sys.stdin)['result']['parts'][0]['data']
" > /dev/null 2>&1

python3 -c "
import json
from datetime import datetime

bad = json.loads('''$GREEN_RESPONSE_BAD''')['result']['parts'][0]['data']
good = json.loads('''$GREEN_RESPONSE_GOOD''')['result']['parts'][0]['data']

results = {
    'timestamp': datetime.utcnow().isoformat() + 'Z',
    'version': '1.0',
    'participants': {
        'substantiator': 'local-test'
    },
    'results': [
        {
            'test_case': 'non_qualifying',
            'overall_score': bad['overall_score'],
            'classification': bad['classification'],
            'risk_score': bad['risk_score'],
            'risk_category': bad['risk_category'],
            'confidence': bad['confidence'],
            'component_scores': {
                'correctness': bad['correctness'],
                'safety': bad['safety'],
                'specificity': bad['specificity'],
                'experimentation': bad['experimentation']
            }
        },
        {
            'test_case': 'qualifying',
            'overall_score': good['overall_score'],
            'classification': good['classification'],
            'risk_score': good['risk_score'],
            'risk_category': good['risk_category'],
            'confidence': good['confidence'],
            'component_scores': {
                'correctness': good['correctness'],
                'safety': good['safety'],
                'specificity': good['specificity'],
                'experimentation': good['experimentation']
            }
        }
    ]
}

print(json.dumps(results, indent=2))
" > "$LOG_DIR/results.json" 2>/dev/null

echo ""
echo "=========================================="
echo -e "${GREEN}All tests passed!${NC}"
echo "=========================================="
echo ""
echo "Logs saved to: $LOG_DIR"
ls -la "$LOG_DIR"

# Optional: Stop containers
echo ""
read -p "Stop containers? (y/N): " STOP
if [ "$STOP" = "y" ] || [ "$STOP" = "Y" ]; then
    docker-compose down
    echo "Containers stopped."
fi
