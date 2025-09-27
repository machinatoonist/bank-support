#!/bin/bash

# Smoke test script for bank support API
# Tests health endpoint and support endpoint with expected risk levels

API_BASE="http://localhost:8001"

echo "🧪 Running Bank Support API Smoke Tests"
echo "=================================================="

# Test 1: Health check
echo "Testing health endpoint..."
health_response=$(curl -s "$API_BASE/health")
if echo "$health_response" | grep -q '"status":"ok"'; then
    echo "✅ Health check passed"
else
    echo "❌ Health check failed: $health_response"
    exit 1
fi

echo

# Test 2: Balance inquiry (should be low risk)
echo "Testing balance inquiry (expecting low risk < 3)..."
balance_response=$(curl -s -X POST "$API_BASE/support" \
    -H "Content-Type: application/json" \
    -d '{"question":"What is my balance?","customer_name":"Alice","customer_id":123}')

echo "Response: $balance_response"
risk1=$(echo "$balance_response" | grep -o '"risk":[0-9]*' | cut -d':' -f2)
if [ "$risk1" -lt 3 ]; then
    echo "✅ Low risk test passed: risk=$risk1 (expected < 3)"
else
    echo "❌ Low risk test failed: risk=$risk1 (expected < 3)"
fi

echo

# Test 3: Lost card (should be high risk)
echo "Testing lost card report (expecting high risk > 7)..."
card_response=$(curl -s -X POST "$API_BASE/support" \
    -H "Content-Type: application/json" \
    -d '{"question":"I just lost my card!","customer_name":"Bob","customer_id":456}')

echo "Response: $card_response"
risk2=$(echo "$card_response" | grep -o '"risk":[0-9]*' | cut -d':' -f2)
if [ "$risk2" -gt 7 ]; then
    echo "✅ High risk test passed: risk=$risk2 (expected > 7)"
else
    echo "❌ High risk test failed: risk=$risk2 (expected > 7)"
fi

echo
echo "=================================================="
echo "🎉 Smoke tests completed!"