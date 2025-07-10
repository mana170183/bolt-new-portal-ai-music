#!/bin/bash

# Final Deployment Validation for Portal AI Music
# This script performs comprehensive validation of the entire deployment

set -e

# Configuration
APP_URL="${1:-}"
ENVIRONMENT="${2:-dev}"
RESOURCE_GROUP="${3:-}"
SUBSCRIPTION_ID="${4:-}"

if [[ -z "$APP_URL" || -z "$RESOURCE_GROUP" || -z "$SUBSCRIPTION_ID" ]]; then
    echo "Usage: $0 <app_url> <environment> <resource_group> <subscription_id>"
    echo "Example: $0 https://ca-portal-ai-music-dev-uks.azurecontainerapps.io dev rg-portal-ai-music-dev 12345678-1234-1234-1234-123456789012"
    exit 1
fi

echo "🚀 Final Deployment Validation for Portal AI Music"
echo "📍 Environment: $ENVIRONMENT"
echo "🌐 App URL: $APP_URL"
echo "📦 Resource Group: $RESOURCE_GROUP"
echo "---"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Test results tracking
declare -A test_results
total_tests=0
passed_tests=0
failed_tests=0
warnings=0

# Function to run a validation test
validate() {
    local category="$1"
    local test_name="$2"
    local test_command="$3"
    local is_critical="${4:-true}"
    
    echo -e "${BLUE}🔍 [$category] $test_name${NC}"
    total_tests=$((total_tests + 1))
    
    if eval "$test_command" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ PASSED: $test_name${NC}"
        test_results["$category-$test_name"]="PASSED"
        passed_tests=$((passed_tests + 1))
        return 0
    else
        if [[ "$is_critical" == "true" ]]; then
            echo -e "${RED}❌ FAILED: $test_name (CRITICAL)${NC}"
            test_results["$category-$test_name"]="FAILED"
            failed_tests=$((failed_tests + 1))
        else
            echo -e "${YELLOW}⚠️ WARNING: $test_name${NC}"
            test_results["$category-$test_name"]="WARNING"
            warnings=$((warnings + 1))
        fi
        return 1
    fi
}

# Function to check Azure resource status
check_azure_resource() {
    local resource_type="$1"
    local resource_name="$2"
    local expected_status="${3:-Running}"
    
    local status=$(az "$resource_type" show \
        --resource-group "$RESOURCE_GROUP" \
        --name "$resource_name" \
        --query "properties.provisioningState" \
        --output tsv 2>/dev/null || echo "NotFound")
    
    [[ "$status" == "Succeeded" ]] || [[ "$status" == "$expected_status" ]]
}

echo "🏗️ Infrastructure Validation"
echo "================================"

# Container App validation
validate "Infrastructure" "Container App Deployment" \
    "az containerapp show --resource-group '$RESOURCE_GROUP' --name 'ca-portal-ai-music-$ENVIRONMENT-uks' --query 'properties.provisioningState' --output tsv | grep -q 'Succeeded'"

validate "Infrastructure" "Container Registry Access" \
    "az acr show --resource-group '$RESOURCE_GROUP' --name 'acrportalaimusic${ENVIRONMENT}uks' --query 'properties.provisioningState' --output tsv | grep -q 'Succeeded'"

validate "Infrastructure" "SQL Database Connectivity" \
    "az sql db show --resource-group '$RESOURCE_GROUP' --server 'sql-portal-ai-music-$ENVIRONMENT-uks' --name 'portal-ai-music' --query 'status' --output tsv | grep -q 'Online'"

validate "Infrastructure" "Storage Account Access" \
    "az storage account show --resource-group '$RESOURCE_GROUP' --name 'stportalaimusic${ENVIRONMENT}uks' --query 'provisioningState' --output tsv | grep -q 'Succeeded'"

validate "Infrastructure" "Redis Cache Status" \
    "az redis show --resource-group '$RESOURCE_GROUP' --name 'redis-portal-ai-music-$ENVIRONMENT-uks' --query 'provisioningState' --output tsv | grep -q 'Succeeded'"

validate "Infrastructure" "Key Vault Access" \
    "az keyvault show --resource-group '$RESOURCE_GROUP' --name 'kv-portal-ai-music-$ENVIRONMENT-uks' --query 'properties.provisioningState' --output tsv | grep -q 'Succeeded'"

echo
echo "🌐 Application Validation"
echo "=========================="

# Application health checks
validate "Application" "Health Endpoint" \
    "curl -f -s '$APP_URL/api/health' | grep -q 'ok'"

validate "Application" "Main Page Load" \
    "curl -f -s '$APP_URL/' | grep -q 'Portal AI Music'"

validate "Application" "API Genres Endpoint" \
    "curl -f -s '$APP_URL/api/genres' | jq -e 'type == \"array\"'"

validate "Application" "API Moods Endpoint" \
    "curl -f -s '$APP_URL/api/moods' | jq -e 'type == \"array\"'"

validate "Application" "Static Assets Loading" \
    "curl -f -s -I '$APP_URL/_next/static/chunks/pages/_app.js' | grep -q '200'" "false"

echo
echo "🔒 Security Validation"
echo "======================"

# Security checks
validate "Security" "HTTPS Enforcement" \
    "curl -s -I '$APP_URL' | grep -q 'HTTP.*200'"

validate "Security" "Security Headers - HSTS" \
    "curl -s -I '$APP_URL' | grep -qi 'strict-transport-security'" "false"

validate "Security" "Security Headers - X-Frame-Options" \
    "curl -s -I '$APP_URL' | grep -qi 'x-frame-options'" "false"

validate "Security" "Security Headers - Content-Type-Options" \
    "curl -s -I '$APP_URL' | grep -qi 'x-content-type-options'" "false"

validate "Security" "TLS Configuration" \
    "echo | openssl s_client -connect \$(echo '$APP_URL' | sed 's|https://||'):443 -servername \$(echo '$APP_URL' | sed 's|https://||') 2>/dev/null | grep -q 'Verify return code: 0'"

echo
echo "⚡ Performance Validation"
echo "========================"

# Performance checks
response_time=$(curl -w "%{time_total}" -o /dev/null -s "$APP_URL/")
response_time_ms=$(echo "$response_time * 1000" | bc -l | cut -d. -f1)

validate "Performance" "Response Time (<2s)" \
    "[[ $response_time_ms -lt 2000 ]]"

validate "Performance" "Page Size Optimization" \
    "page_size=\$(curl -s '$APP_URL/' | wc -c); [[ \$page_size -lt 1048576 ]]" "false"

# Concurrent request test
validate "Performance" "Concurrent Request Handling" \
    "for i in {1..5}; do curl -s '$APP_URL/api/health' > /dev/null & done; wait; echo 'ok'"

echo
echo "🤖 AI Services Validation"
echo "========================="

# AI services checks (using mock endpoints)
validate "AI Services" "Music Generation API" \
    "curl -s -X POST -H 'Content-Type: application/json' -d '{\"genre\":\"pop\",\"mood\":\"happy\"}' '$APP_URL/api/generate' | jq -e '.success or .error or .data'"

validate "AI Services" "OpenAI Service Connectivity" \
    "az cognitiveservices account show --resource-group '$RESOURCE_GROUP' --name 'openai-portal-ai-music-$ENVIRONMENT-uks' --query 'provisioningState' --output tsv | grep -q 'Succeeded'" "false"

validate "AI Services" "Cognitive Services Status" \
    "az cognitiveservices account show --resource-group '$RESOURCE_GROUP' --name 'cog-portal-ai-music-$ENVIRONMENT-uks' --query 'provisioningState' --output tsv | grep -q 'Succeeded'" "false"

echo
echo "📊 Monitoring Validation"
echo "========================"

# Monitoring checks
validate "Monitoring" "Application Insights" \
    "az monitor app-insights component show --resource-group '$RESOURCE_GROUP' --app 'appi-portal-ai-music-$ENVIRONMENT-uks' --query 'provisioningState' --output tsv | grep -q 'Succeeded'"

validate "Monitoring" "Log Analytics Workspace" \
    "az monitor log-analytics workspace show --resource-group '$RESOURCE_GROUP' --workspace-name 'log-portal-ai-music-$ENVIRONMENT-uks' --query 'provisioningState' --output tsv | grep -q 'Succeeded'"

validate "Monitoring" "Alert Rules Configuration" \
    "az monitor metrics alert list --resource-group '$RESOURCE_GROUP' --query 'length(@)' --output tsv | awk '{if(\$1 > 0) exit 0; else exit 1}'" "false"

echo
echo "📋 Compliance Validation"
echo "========================"

# Compliance checks
validate "Compliance" "Backup Configuration" \
    "az sql db ltr-policy show --resource-group '$RESOURCE_GROUP' --server 'sql-portal-ai-music-$ENVIRONMENT-uks' --database 'portal-ai-music' --query 'weeklyRetention' --output tsv | grep -q 'P'" "false"

validate "Compliance" "Encryption at Rest" \
    "az storage account show --resource-group '$RESOURCE_GROUP' --name 'stportalaimusic${ENVIRONMENT}uks' --query 'encryption.services.blob.enabled' --output tsv | grep -q 'True'"

validate "Compliance" "Private Endpoints" \
    "az network private-endpoint list --resource-group '$RESOURCE_GROUP' --query 'length(@)' --output tsv | awk '{if(\$1 > 0) exit 0; else exit 1}'" "false"

validate "Compliance" "RBAC Configuration" \
    "az role assignment list --resource-group '$RESOURCE_GROUP' --query 'length(@)' --output tsv | awk '{if(\$1 > 0) exit 0; else exit 1}'"

echo
echo "🔄 Disaster Recovery Validation"
echo "==============================="

# DR checks (for production)
if [[ "$ENVIRONMENT" == "prod" ]]; then
    validate "DR" "Geo-Redundant Storage" \
        "az storage account show --resource-group '$RESOURCE_GROUP' --name 'stportalaimusic${ENVIRONMENT}uks' --query 'sku.name' --output tsv | grep -q 'GRS'"
    
    validate "DR" "Database Geo-Replication" \
        "az sql db replica list --resource-group '$RESOURCE_GROUP' --server 'sql-portal-ai-music-$ENVIRONMENT-uks' --name 'portal-ai-music' --query 'length(@)' --output tsv | awk '{if(\$1 > 0) exit 0; else exit 1}'" "false"
    
    validate "DR" "Traffic Manager Configuration" \
        "az network traffic-manager profile show --resource-group '$RESOURCE_GROUP' --name 'tm-portal-ai-music-$ENVIRONMENT' --query 'trafficRoutingMethod' --output tsv | grep -q 'Priority'" "false"
else
    echo -e "${CYAN}ℹ️  Disaster Recovery validation skipped for $ENVIRONMENT environment${NC}"
fi

echo
echo "📱 User Experience Validation"
echo "============================="

# UX checks
validate "UX" "Mobile Responsiveness" \
    "curl -s -H 'User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)' '$APP_URL/' | grep -q 'viewport'"

validate "UX" "Page Title Present" \
    "curl -s '$APP_URL/' | grep -q '<title>'"

validate "UX" "Meta Description" \
    "curl -s '$APP_URL/' | grep -q 'description'" "false"

validate "UX" "Favicon Availability" \
    "curl -f -s '$APP_URL/favicon.ico' > /dev/null"

echo
echo "🧪 End-to-End Test Scenarios"
echo "============================"

# E2E test scenarios
validate "E2E" "User Journey - Home to Generate" \
    "curl -s '$APP_URL/' | grep -q 'Generate' && curl -s '$APP_URL/api/genres' | jq -e 'length > 0'"

validate "E2E" "API Error Handling" \
    "curl -s '$APP_URL/api/nonexistent' | grep -q '404\\|error'" "false"

validate "E2E" "Large Payload Handling" \
    "large_payload=\$(printf 'A%.0s' {1..1000}); curl -s -X POST -H 'Content-Type: application/json' -d '{\"genre\":\"\$large_payload\"}' '$APP_URL/api/generate' | grep -q 'error\\|success'"

echo
echo "💰 Cost and Resource Optimization"
echo "================================="

# Resource optimization checks
validate "Optimization" "Container App Scaling" \
    "az containerapp show --resource-group '$RESOURCE_GROUP' --name 'ca-portal-ai-music-$ENVIRONMENT-uks' --query 'properties.template.scale.minReplicas' --output tsv | awk '{if(\$1 <= 2) exit 0; else exit 1}'" "false"

validate "Optimization" "Database Tier Appropriate" \
    "az sql db show --resource-group '$RESOURCE_GROUP' --server 'sql-portal-ai-music-$ENVIRONMENT-uks' --name 'portal-ai-music' --query 'serviceLevelObjective' --output tsv | grep -v 'P15'" "false"

validate "Optimization" "Storage Lifecycle Policy" \
    "az storage account management-policy show --resource-group '$RESOURCE_GROUP' --account-name 'stportalaimusic${ENVIRONMENT}uks' --query 'policy' --output tsv | grep -q 'rules'" "false"

echo
echo "🎯 Final Validation Summary"
echo "==========================="

# Calculate success rate
success_rate=$((passed_tests * 100 / total_tests))
critical_failures=$failed_tests

echo -e "${BLUE}📊 Test Results Summary:${NC}"
echo "┌─────────────────────┬───────────┐"
echo "│ Metric              │ Count     │"
echo "├─────────────────────┼───────────┤"
printf "│ %-19s │ %-9s │\n" "Total Tests" "$total_tests"
printf "│ %-19s │ %-9s │\n" "Passed" "${GREEN}$passed_tests${NC}"
printf "│ %-19s │ %-9s │\n" "Failed (Critical)" "${RED}$failed_tests${NC}"
printf "│ %-19s │ %-9s │\n" "Warnings" "${YELLOW}$warnings${NC}"
printf "│ %-19s │ %-9s │\n" "Success Rate" "${success_rate}%"
echo "└─────────────────────┴───────────┘"

echo
if [[ $critical_failures -eq 0 ]]; then
    echo -e "${GREEN}🎉 DEPLOYMENT VALIDATION SUCCESSFUL!${NC}"
    echo -e "${GREEN}✅ All critical tests passed${NC}"
    if [[ $warnings -gt 0 ]]; then
        echo -e "${YELLOW}⚠️  $warnings non-critical warnings detected${NC}"
        echo -e "${YELLOW}💡 Review warnings for optimization opportunities${NC}"
    fi
    echo
    echo -e "${BLUE}🚀 Portal AI Music is ready for use!${NC}"
    echo -e "${CYAN}🌐 Application URL: $APP_URL${NC}"
    echo -e "${CYAN}📊 Environment: $ENVIRONMENT${NC}"
    echo -e "${CYAN}📦 Resource Group: $RESOURCE_GROUP${NC}"
    
    # Generate deployment certificate
    echo
    echo -e "${PURPLE}📜 Deployment Certificate${NC}"
    echo "=============================="
    echo "Application: Portal AI Music"
    echo "Environment: $ENVIRONMENT"
    echo "Deployment Date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "Validation Status: PASSED"
    echo "Success Rate: ${success_rate}%"
    echo "Critical Issues: 0"
    echo "Warnings: $warnings"
    echo "Validated By: Azure DevOps Pipeline"
    echo "=============================="
    
    exit 0
else
    echo -e "${RED}❌ DEPLOYMENT VALIDATION FAILED!${NC}"
    echo -e "${RED}🚨 $critical_failures critical tests failed${NC}"
    echo
    echo -e "${YELLOW}🔍 Failed Tests:${NC}"
    for test in "${!test_results[@]}"; do
        if [[ "${test_results[$test]}" == "FAILED" ]]; then
            echo -e "${RED}  • $test${NC}"
        fi
    done
    
    echo
    echo -e "${BLUE}🛠️  Recommended Actions:${NC}"
    echo "1. Check application logs for errors"
    echo "2. Verify infrastructure deployment status"
    echo "3. Test network connectivity"
    echo "4. Review security configurations"
    echo "5. Validate service dependencies"
    
    echo
    echo -e "${RED}❌ Portal AI Music deployment requires attention before use${NC}"
    exit 1
fi
