#!/bin/bash

# Portal AI Music - Free Deployment Testing Script
# Test deployed services on Railway, Vercel, and Supabase

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[FAIL]${NC} $1"
}

# Configuration
API_URL=${1:-"https://your-railway-app.railway.app"}
FRONTEND_URL=${2:-"https://your-vercel-app.vercel.app"}

echo "🧪 Portal AI Music - Free Deployment Tests"
echo "=========================================="
echo "API URL: $API_URL"
echo "Frontend URL: $FRONTEND_URL"
echo ""

test_api_health() {
    print_status "Testing API health endpoint..."
    
    response=$(curl -s -w "%{http_code}" -o /tmp/health_response.json "$API_URL/health" || echo "000")
    
    if [ "$response" = "200" ]; then
        print_success "API health check passed"
        
        # Check response content
        if command -v jq &> /dev/null; then
            status=$(jq -r '.status' /tmp/health_response.json 2>/dev/null || echo "unknown")
            services=$(jq -r '.services' /tmp/health_response.json 2>/dev/null || echo "{}")
            print_status "API Status: $status"
            print_status "Services: $services"
        fi
    else
        print_error "API health check failed (HTTP $response)"
        return 1
    fi
}

test_cors() {
    print_status "Testing CORS configuration..."
    
    response=$(curl -s -w "%{http_code}" \
        -H "Origin: $FRONTEND_URL" \
        -H "Access-Control-Request-Method: POST" \
        -H "Access-Control-Request-Headers: Content-Type" \
        -X OPTIONS \
        "$API_URL/generate-music" -o /dev/null)
    
    if [ "$response" = "200" ] || [ "$response" = "204" ]; then
        print_success "CORS configuration is working"
    else
        print_warning "CORS test returned HTTP $response (may still work)"
    fi
}

test_music_generation() {
    print_status "Testing music generation endpoint..."
    
    test_payload='{
        "prompt": "test upbeat electronic music",
        "style": "electronic",
        "duration": 10,
        "user_id": "test-user-' $(date +%s) '"
    }'
    
    response=$(curl -s -w "%{http_code}" \
        -H "Content-Type: application/json" \
        -H "Origin: $FRONTEND_URL" \
        -X POST \
        -d "$test_payload" \
        "$API_URL/generate-music" \
        -o /tmp/generation_response.json)
    
    if [ "$response" = "200" ] || [ "$response" = "202" ]; then
        print_success "Music generation endpoint is working"
        
        if command -v jq &> /dev/null; then
            generation_id=$(jq -r '.id' /tmp/generation_response.json 2>/dev/null || echo "unknown")
            status=$(jq -r '.status' /tmp/generation_response.json 2>/dev/null || echo "unknown")
            print_status "Generation ID: $generation_id"
            print_status "Status: $status"
        fi
    else
        print_error "Music generation test failed (HTTP $response)"
        if [ -f /tmp/generation_response.json ]; then
            print_error "Response: $(cat /tmp/generation_response.json)"
        fi
    fi
}

test_frontend() {
    print_status "Testing frontend deployment..."
    
    response=$(curl -s -w "%{http_code}" -o /dev/null "$FRONTEND_URL")
    
    if [ "$response" = "200" ]; then
        print_success "Frontend is accessible"
    else
        print_error "Frontend test failed (HTTP $response)"
    fi
}

test_api_endpoints() {
    print_status "Testing additional API endpoints..."
    
    # Test stats endpoint
    response=$(curl -s -w "%{http_code}" -o /tmp/stats_response.json "$API_URL/stats")
    if [ "$response" = "200" ]; then
        print_success "Stats endpoint is working"
    else
        print_warning "Stats endpoint returned HTTP $response"
    fi
    
    # Test 404 handling
    response=$(curl -s -w "%{http_code}" -o /dev/null "$API_URL/nonexistent")
    if [ "$response" = "404" ]; then
        print_success "404 error handling is working"
    else
        print_warning "404 handling may not be configured properly"
    fi
}

load_test() {
    print_status "Running basic load test..."
    
    if command -v ab &> /dev/null; then
        print_status "Using Apache Bench for load testing..."
        ab -n 10 -c 2 "$API_URL/health" > /tmp/load_test.txt 2>&1
        
        if [ $? -eq 0 ]; then
            requests_per_second=$(grep "Requests per second" /tmp/load_test.txt | awk '{print $4}')
            print_success "Load test completed: $requests_per_second requests/second"
        else
            print_warning "Load test failed or ab not available"
        fi
    else
        print_status "Apache Bench not available, skipping load test"
        print_status "To install: brew install apache-bench (macOS) or apt-get install apache2-utils (Ubuntu)"
    fi
}

check_free_tier_limits() {
    print_status "Checking free tier resource usage..."
    
    # This would typically query service APIs for usage
    print_status "Railway: Check dashboard for credit usage"
    print_status "Vercel: Check dashboard for bandwidth usage"
    print_status "Supabase: Check dashboard for database/storage usage"
    print_status "Hugging Face: Monitor API rate limits"
}

show_monitoring_urls() {
    echo ""
    echo "📊 Monitoring & Dashboard URLs:"
    echo "=============================="
    echo "Railway Dashboard: https://railway.app/dashboard"
    echo "Vercel Dashboard: https://vercel.com/dashboard"
    echo "Supabase Dashboard: https://app.supabase.com/"
    echo "Hugging Face Dashboard: https://huggingface.co/settings/tokens"
    echo ""
    echo "API Endpoints to monitor:"
    echo "Health: $API_URL/health"
    echo "Stats: $API_URL/stats"
    echo ""
}

main() {
    echo "Starting comprehensive tests..."
    echo ""
    
    # Core functionality tests
    test_api_health || echo "API health test failed"
    echo ""
    
    test_cors
    echo ""
    
    test_music_generation
    echo ""
    
    test_frontend
    echo ""
    
    test_api_endpoints
    echo ""
    
    # Performance tests
    load_test
    echo ""
    
    # Resource monitoring
    check_free_tier_limits
    echo ""
    
    # Show monitoring info
    show_monitoring_urls
    
    echo "🎉 Testing completed!"
    echo ""
    echo "Next steps:"
    echo "1. Monitor your service dashboards for resource usage"
    echo "2. Set up uptime monitoring (e.g., UptimeRobot)"
    echo "3. Configure alerts for when approaching free tier limits"
    echo "4. Test with real users and gather feedback"
}

# Show usage if no arguments
if [ $# -eq 0 ]; then
    echo "Usage: $0 <api-url> [frontend-url]"
    echo ""
    echo "Examples:"
    echo "  $0 https://my-app.railway.app"
    echo "  $0 https://my-app.railway.app https://my-app.vercel.app"
    echo ""
    exit 1
fi

# Run tests
main "$@"
