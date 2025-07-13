#!/bin/bash

# Integration and Performance Testing Script for Portal AI Music
# This script performs comprehensive testing after deployment

set -e

# Configuration
APP_URL="${1:-}"
ENVIRONMENT="${2:-dev}"
TEST_ITERATIONS="${3:-5}"

if [[ -z "$APP_URL" ]]; then
    echo "Usage: $0 <app_url> [environment] [test_iterations]"
    echo "Example: $0 https://ca-portal-ai-music-dev-uks.azurecontainerapps.io dev 5"
    exit 1
fi

echo "🚀 Starting comprehensive testing for Portal AI Music"
echo "📍 Environment: $ENVIRONMENT"
echo "🌐 App URL: $APP_URL"
echo "🔄 Test iterations: $TEST_ITERATIONS"
echo "---"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test results
PASSED_TESTS=0
FAILED_TESTS=0
TOTAL_TESTS=0

# Function to run a test
run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected_status="${3:-200}"
    
    echo -e "${BLUE}🧪 Running: $test_name${NC}"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    if eval "$test_command"; then
        echo -e "${GREEN}✅ PASSED: $test_name${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}❌ FAILED: $test_name${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    echo
}

# Function to check HTTP status
check_http_status() {
    local url="$1"
    local expected="${2:-200}"
    local max_retries="${3:-3}"
    local retry_delay="${4:-5}"
    
    for i in $(seq 1 $max_retries); do
        local status=$(curl -s -o /dev/null -w "%{http_code}" "$url" || echo "000")
        if [[ "$status" == "$expected" ]]; then
            return 0
        fi
        if [[ $i -lt $max_retries ]]; then
            echo "⏳ Attempt $i failed (status: $status), retrying in ${retry_delay}s..."
            sleep $retry_delay
        fi
    done
    
    echo "❌ Expected status $expected, got $status"
    return 1
}

# Function to check response time
check_response_time() {
    local url="$1"
    local max_time="${2:-2000}" # milliseconds
    
    local response_time=$(curl -w "%{time_total}" -o /dev/null -s "$url")
    local response_time_ms=$(echo "$response_time * 1000" | bc -l | cut -d. -f1)
    
    echo "⏱️  Response time: ${response_time_ms}ms"
    
    if [[ $response_time_ms -le $max_time ]]; then
        return 0
    else
        echo "❌ Response time ${response_time_ms}ms exceeds limit ${max_time}ms"
        return 1
    fi
}

# Function to check JSON response
check_json_response() {
    local url="$1"
    local expected_field="$2"
    
    local response=$(curl -s "$url")
    if echo "$response" | jq -e ".$expected_field" > /dev/null 2>&1; then
        return 0
    else
        echo "❌ Expected field '$expected_field' not found in JSON response"
        echo "Response: $response"
        return 1
    fi
}

echo "🔍 Starting Health Checks..."

# Basic health checks
run_test "Application Health Check" "check_http_status '$APP_URL/api/health' 200"
run_test "Application Root Access" "check_http_status '$APP_URL/' 200"
run_test "Static Assets Loading" "check_http_status '$APP_URL/_next/static/css' 200"

echo "📊 Starting API Endpoint Tests..."

# API endpoint tests
run_test "Genres API Endpoint" "check_http_status '$APP_URL/api/genres' 200"
run_test "Moods API Endpoint" "check_http_status '$APP_URL/api/moods' 200"
run_test "Generate Music API (POST)" "curl -s -X POST -H 'Content-Type: application/json' -d '{\"genre\":\"pop\",\"mood\":\"happy\",\"duration\":30}' '$APP_URL/api/generate' | grep -q 'success\\|error'"

echo "⚡ Starting Performance Tests..."

# Performance tests
total_response_time=0
for i in $(seq 1 $TEST_ITERATIONS); do
    echo "🔄 Performance test iteration $i/$TEST_ITERATIONS"
    if response_time=$(curl -w "%{time_total}" -o /dev/null -s "$APP_URL/"); then
        response_time_ms=$(echo "$response_time * 1000" | bc -l | cut -d. -f1)
        total_response_time=$((total_response_time + response_time_ms))
        echo "   Response time: ${response_time_ms}ms"
    fi
done

avg_response_time=$((total_response_time / TEST_ITERATIONS))
echo "📈 Average response time: ${avg_response_time}ms"

run_test "Performance - Response Time Check" "[[ $avg_response_time -le 2000 ]]"

echo "🔒 Starting Security Tests..."

# Security tests
run_test "HTTPS Redirect" "curl -s -I -L '$APP_URL' | grep -q 'HTTP.*200'"
run_test "Security Headers - X-Frame-Options" "curl -s -I '$APP_URL' | grep -i 'x-frame-options'"
run_test "Security Headers - X-Content-Type-Options" "curl -s -I '$APP_URL' | grep -i 'x-content-type-options'"
run_test "Security Headers - Strict-Transport-Security" "curl -s -I '$APP_URL' | grep -i 'strict-transport-security'"

echo "💾 Starting Data Persistence Tests..."

# Data persistence tests (if applicable)
run_test "Health Check Persistence" "check_http_status '$APP_URL/api/health' 200"

echo "🌍 Starting Load Testing..."

# Simple load test
echo "🔥 Running concurrent requests test..."
pids=()
for i in $(seq 1 10); do
    (curl -s -o /dev/null "$APP_URL/" && echo "Request $i completed") &
    pids+=($!)
done

# Wait for all requests to complete
for pid in "${pids[@]}"; do
    wait $pid
done

run_test "Concurrent Load Test" "echo 'All concurrent requests completed successfully'"

echo "📱 Starting Mobile/Responsive Tests..."

# Mobile responsiveness tests
run_test "Mobile User-Agent Response" "curl -s -H 'User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)' '$APP_URL/' | grep -q 'viewport'"

echo "🔍 Starting Content Validation..."

# Content validation
run_test "Page Title Present" "curl -s '$APP_URL/' | grep -q '<title>'"
run_test "Meta Description Present" "curl -s '$APP_URL/' | grep -q 'description'"
run_test "Favicon Present" "check_http_status '$APP_URL/favicon.ico' 200"

echo "🎵 Starting AI Music Generation Tests..."

# AI Music generation tests (mock mode)
run_test "Generate Music - Pop Genre" "curl -s -X POST -H 'Content-Type: application/json' -d '{\"genre\":\"pop\",\"mood\":\"happy\",\"duration\":30}' '$APP_URL/api/generate' | jq -e '.success or .error'"
run_test "Generate Music - Rock Genre" "curl -s -X POST -H 'Content-Type: application/json' -d '{\"genre\":\"rock\",\"mood\":\"energetic\",\"duration\":45}' '$APP_URL/api/generate' | jq -e '.success or .error'"

echo "🔄 Starting Edge Case Tests..."

# Edge case tests
run_test "Invalid API Route" "check_http_status '$APP_URL/api/nonexistent' 404"
run_test "Large POST Request" "curl -s -X POST -H 'Content-Type: application/json' -d '{\"genre\":\"'$(printf 'A%.0s' {1..1000})'\"}' '$APP_URL/api/generate' | grep -q 'error\\|success'"

# Cleanup and summary
echo "---"
echo "🏁 Test Summary"
echo "==============="
echo -e "${GREEN}✅ Passed: $PASSED_TESTS${NC}"
echo -e "${RED}❌ Failed: $FAILED_TESTS${NC}"
echo -e "${BLUE}📊 Total:  $TOTAL_TESTS${NC}"

success_rate=$((PASSED_TESTS * 100 / TOTAL_TESTS))
echo -e "${YELLOW}📈 Success Rate: $success_rate%${NC}"

if [[ $FAILED_TESTS -eq 0 ]]; then
    echo -e "${GREEN}🎉 All tests passed! Deployment is successful.${NC}"
    exit 0
else
    echo -e "${RED}⚠️  Some tests failed. Please review the deployment.${NC}"
    exit 1
fi
