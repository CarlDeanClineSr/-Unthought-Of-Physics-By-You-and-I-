#!/bin/bash
# Test script for unthought_of_physics.py error handling
# Tests all error scenarios to ensure the system never crashes

echo "=========================================="
echo "LUFT CME Heartbeat Logger Error Handling Tests"
echo "=========================================="
echo ""

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Helper function to run test and check exit code
run_test() {
    local test_name="$1"
    local expected_exit="$2"
    
    echo "----------------------------------------"
    echo "Test: $test_name"
    echo "----------------------------------------"
    
    python3 unthought_of_physics.py > /tmp/test_output.log 2>&1
    local exit_code=$?
    
    if [ $exit_code -eq $expected_exit ]; then
        echo "✓ PASS - Exit code: $exit_code"
    else
        echo "✗ FAIL - Expected exit code: $expected_exit, Got: $exit_code"
        return 1
    fi
    
    echo ""
}

# Clean up before tests
cleanup() {
    rm -f data/ace_plasma_latest.json data/ace_mag_latest.json
    rm -f raw_csv/cme_heartbeat_log_2025_12.csv
    rm -f data/logs/*.log data/logs/*.json
}

echo "Test 1: Missing all data files"
cleanup
run_test "Missing all data files - should auto-generate and succeed" 0

echo "Test 2: Empty JSON files"
cleanup
echo "" > data/ace_plasma_latest.json
echo "" > data/ace_mag_latest.json
run_test "Empty JSON files - should regenerate and succeed" 0

echo "Test 3: Malformed JSON"
cleanup
echo '{"bad": "json"' > data/ace_plasma_latest.json
echo '{"invalid": json}' > data/ace_mag_latest.json
run_test "Malformed JSON - should regenerate and succeed" 0

echo "Test 4: Empty CSV file"
cleanup
mkdir -p raw_csv
echo "" > raw_csv/cme_heartbeat_log_2025_12.csv
run_test "Empty CSV file - should regenerate and succeed" 0

echo "Test 5: Malformed CSV with bad data types"
cleanup
mkdir -p raw_csv
echo "2025-12-16 01:50:00,not_a_number,bad_float,pre" > raw_csv/cme_heartbeat_log_2025_12.csv
run_test "Malformed CSV data - should regenerate and succeed" 0

echo "Test 6: Valid data files"
cleanup
python3 -c "
import json
from datetime import datetime

# Create valid test data
plasma = {
    'metadata': {'source': 'TEST', 'instrument': 'ACE_SWEPAM'},
    'observations': [{'timestamp': datetime.now().isoformat() + 'Z', 
                     'proton_density': 5.0, 'proton_speed': 400.0, 
                     'proton_temperature': 100000.0}],
    'status': 'TEST_MODE'
}

mag = {
    'metadata': {'source': 'TEST', 'instrument': 'ACE_MAG'},
    'observations': [{'timestamp': datetime.now().isoformat() + 'Z',
                     'bx_gsm': 0.0, 'by_gsm': 0.0, 'bz_gsm': 0.0, 'bt': 5.0}],
    'status': 'TEST_MODE'
}

with open('data/ace_plasma_latest.json', 'w') as f:
    json.dump(plasma, f)
    
with open('data/ace_mag_latest.json', 'w') as f:
    json.dump(mag, f)
"

mkdir -p raw_csv
cat > raw_csv/cme_heartbeat_log_2025_12.csv << 'EOF'
2025-12-16 19:51:00,0.1500,2.50,quiet,5.0,596.0,6.5,0.8,ACE
EOF

run_test "Valid data files - should process successfully" 0

echo "=========================================="
echo "All tests completed!"
echo "=========================================="

# Cleanup after tests
cleanup
