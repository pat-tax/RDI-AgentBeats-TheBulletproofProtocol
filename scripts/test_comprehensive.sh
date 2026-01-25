#!/bin/bash
#
# Comprehensive end-to-end test with full ground truth dataset
#
# Usage: ./scripts/test_comprehensive.sh
#
# Tests all narratives in data/ground_truth.json against Green Agent
# Validates classifications and scores
#

set -e

# Setup logging
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_DIR="logs/comprehensive_${TIMESTAMP}"
mkdir -p "$LOG_DIR"

echo "=========================================="
echo "Comprehensive E2E Test with Ground Truth"
echo "=========================================="
echo "Logs: $LOG_DIR"
echo "Dataset size: $(jq 'length' data/ground_truth.json)"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

pass() { echo -e "${GREEN}✓ $1${NC}"; echo "PASS: $1" >> "$LOG_DIR/summary.log"; }
fail() { echo -e "${RED}✗ $1${NC}"; echo "FAIL: $1" >> "$LOG_DIR/summary.log"; }
info() { echo -e "${YELLOW}ℹ $1${NC}"; echo "INFO: $1" >> "$LOG_DIR/summary.log"; }

# Initialize counters
TOTAL=0
PASSED=0
FAILED=0
CORRECT_CLASS=0
INCORRECT_CLASS=0

# Step 1: Start containers
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

pass "Containers ready"
echo ""

# Step 2: Test all narratives
echo "Step 2: Testing all narratives..."
echo "========================================"
echo ""

# Create test results file
cat > "$LOG_DIR/test_results.json" << 'EOF'
{
  "timestamp": "",
  "total_tests": 0,
  "passed": 0,
  "failed": 0,
  "accuracy": 0.0,
  "tests": []
}
EOF

# Process each narrative
jq -c '.[] | {index: .id, classification: .classification, expected_score: .expected_score, narrative: .narrative}' data/ground_truth.json | while read -r test_case; do
    INDEX=$(echo "$test_case" | jq -r '.index')
    EXPECTED_CLASS=$(echo "$test_case" | jq -r '.classification')
    EXPECTED_SCORE=$(echo "$test_case" | jq -r '.expected_score')
    NARRATIVE=$(echo "$test_case" | jq -r '.narrative')

    echo "Testing $INDEX: $EXPECTED_CLASS (expected score: $EXPECTED_SCORE)..."

    # Call Green Agent
    RESPONSE=$(curl -s -X POST http://localhost:8002/ \
        -H "Content-Type: application/json" \
        -d "{\"jsonrpc\":\"2.0\",\"id\":\"$INDEX\",\"method\":\"message/send\",\"params\":{\"message\":{\"messageId\":\"test-$INDEX\",\"role\":\"user\",\"parts\":[{\"text\":\"$NARRATIVE\"}]}}}")

    # Save response
    echo "$RESPONSE" > "$LOG_DIR/${INDEX}_response.json"

    # Extract classification
    ACTUAL_CLASS=$(echo "$RESPONSE" | jq -r '.result.parts[0].data.classification' 2>/dev/null || echo "ERROR")
    ACTUAL_SCORE=$(echo "$RESPONSE" | jq -r '.result.parts[0].data.overall_score' 2>/dev/null || echo "ERROR")

    # Check if classification matches
    if [ "$ACTUAL_CLASS" = "$EXPECTED_CLASS" ]; then
        pass "$INDEX: Classification correct ($ACTUAL_CLASS)"
        CORRECT_CLASS=$((CORRECT_CLASS + 1))
    else
        fail "$INDEX: Classification mismatch - expected $EXPECTED_CLASS, got $ACTUAL_CLASS"
        INCORRECT_CLASS=$((INCORRECT_CLASS + 1))
    fi

    TOTAL=$((TOTAL + 1))

    # Show scores
    if [ "$ACTUAL_SCORE" != "ERROR" ]; then
        info "$INDEX: Score $ACTUAL_SCORE (expected ~$EXPECTED_SCORE)"
    fi

    echo ""
done

# Step 3: Summary
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo ""
echo "Total tests: $TOTAL"
echo "Classification accuracy: $CORRECT_CLASS/$TOTAL correct"
ACCURACY=$(echo "scale=2; $CORRECT_CLASS * 100 / $TOTAL" | bc)
echo "Accuracy: ${ACCURACY}%"
echo ""

if [ "$ACCURACY" = "100.00" ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    EXIT_CODE=0
else
    echo -e "${YELLOW}⚠ Some tests failed (${ACCURACY}% accuracy)${NC}"
    EXIT_CODE=1
fi

# Generate comprehensive report
python3 << 'PYTHON_EOF'
import json
from datetime import datetime
import glob

log_dir = "logs/$(ls -td logs/comprehensive_* 2>/dev/null | head -1 | xargs basename)"

# Collect all test results
results = {
    "timestamp": datetime.utcnow().isoformat() + "Z",
    "total_tests": 0,
    "correct_classifications": 0,
    "incorrect_classifications": 0,
    "tests": []
}

# Load ground truth for reference
with open("data/ground_truth.json") as f:
    ground_truth = {item["id"]: item for item in json.load(f)}

# Process each response
for response_file in sorted(glob.glob(f"{log_dir}/*_response.json")):
    test_id = response_file.split("/")[-1].split("_")[0]

    try:
        with open(response_file) as f:
            response = json.load(f)

        actual_class = response.get("result", {}).get("parts", [{}])[0].get("data", {}).get("classification", "ERROR")
        actual_score = response.get("result", {}).get("parts", [{}])[0].get("data", {}).get("overall_score", None)

        expected = ground_truth.get(test_id, {})
        expected_class = expected.get("classification", "UNKNOWN")

        results["total_tests"] += 1
        if actual_class == expected_class:
            results["correct_classifications"] += 1
        else:
            results["incorrect_classifications"] += 1

        results["tests"].append({
            "id": test_id,
            "expected_classification": expected_class,
            "actual_classification": actual_class,
            "match": actual_class == expected_class,
            "actual_score": actual_score,
            "expected_score": expected.get("expected_score")
        })
    except Exception as e:
        print(f"Error processing {response_file}: {e}")

# Calculate accuracy
if results["total_tests"] > 0:
    results["accuracy"] = (results["correct_classifications"] / results["total_tests"]) * 100

# Save report
with open(f"{log_dir}/comprehensive_report.json", "w") as f:
    json.dump(results, f, indent=2)

print(json.dumps(results, indent=2))
PYTHON_EOF

echo ""
echo "Logs saved to: $LOG_DIR"
ls -lh "$LOG_DIR" | tail -10

# Optional: Stop containers
echo ""
read -p "Stop containers? (y/N): " STOP
if [ "$STOP" = "y" ] || [ "$STOP" = "Y" ]; then
    docker-compose down
    echo "Containers stopped."
fi

exit $EXIT_CODE
