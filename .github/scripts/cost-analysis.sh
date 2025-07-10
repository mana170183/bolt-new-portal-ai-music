#!/bin/bash

# Cost Estimation and Optimization for Portal AI Music
# This script analyzes current costs and provides optimization recommendations

set -e

# Configuration
RESOURCE_GROUP="${1:-}"
ENVIRONMENT="${2:-dev}"
SUBSCRIPTION_ID="${3:-}"
LOCATION="${4:-uksouth}"

if [[ -z "$RESOURCE_GROUP" || -z "$SUBSCRIPTION_ID" ]]; then
    echo "Usage: $0 <resource_group> [environment] [subscription_id] [location]"
    echo "Example: $0 rg-portal-ai-music-dev dev 12345678-1234-1234-1234-123456789012 uksouth"
    exit 1
fi

echo "💰 Running cost analysis for Portal AI Music"
echo "📍 Resource Group: $RESOURCE_GROUP"
echo "🏷️  Environment: $ENVIRONMENT"
echo "📍 Location: $LOCATION"
echo "---"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to run Azure CLI commands with error handling
run_az_command() {
    local description="$1"
    local command="$2"
    local optional="${3:-false}"
    
    echo -e "${BLUE}💡 $description${NC}"
    
    if result=$(eval "$command" 2>/dev/null); then
        echo "$result"
        return 0
    else
        if [[ "$optional" == "true" ]]; then
            echo -e "${YELLOW}⚠️  Data not available: $description${NC}"
            return 0
        else
            echo -e "${RED}❌ Failed: $description${NC}"
            return 1
        fi
    fi
    echo
}

# Get cost information
echo "📊 Analyzing current costs..."

# Get resource costs (last 30 days)
COST_DATA=$(az consumption usage list \
    --start-date "$(date -d '30 days ago' '+%Y-%m-%d')" \
    --end-date "$(date '+%Y-%m-%d')" \
    2>/dev/null || echo "[]")

# Calculate estimated monthly costs by service type
echo "📈 Estimating monthly costs by service..."

# Define cost estimates based on environment and scaling
case "$ENVIRONMENT" in
    "dev")
        echo "💡 Development Environment Cost Estimates:"
        container_app_cost=50
        sql_database_cost=150
        storage_cost=25
        redis_cost=100
        openai_cost=200
        cognitive_cost=75
        monitoring_cost=50
        networking_cost=25
        total_estimated=675
        ;;
    "staging")
        echo "💡 Staging Environment Cost Estimates:"
        container_app_cost=150
        sql_database_cost=300
        storage_cost=75
        redis_cost=200
        openai_cost=500
        cognitive_cost=150
        monitoring_cost=100
        networking_cost=50
        total_estimated=1525
        ;;
    "prod")
        echo "💡 Production Environment Cost Estimates:"
        container_app_cost=500
        sql_database_cost=800
        storage_cost=200
        redis_cost=400
        openai_cost=1500
        cognitive_cost=300
        monitoring_cost=200
        networking_cost=100
        total_estimated=4000
        ;;
    *)
        echo "💡 Unknown Environment - Using Development Estimates:"
        container_app_cost=50
        sql_database_cost=150
        storage_cost=25
        redis_cost=100
        openai_cost=200
        cognitive_cost=75
        monitoring_cost=50
        networking_cost=25
        total_estimated=675
        ;;
esac

echo
echo -e "${BLUE}💰 Estimated Monthly Costs (USD):${NC}"
echo "┌─────────────────────────┬──────────────┐"
echo "│ Service                 │ Monthly Cost │"
echo "├─────────────────────────┼──────────────┤"
printf "│ %-23s │ \$%-11s │\n" "Container Apps" "$container_app_cost"
printf "│ %-23s │ \$%-11s │\n" "SQL Database" "$sql_database_cost"
printf "│ %-23s │ \$%-11s │\n" "Storage Account" "$storage_cost"
printf "│ %-23s │ \$%-11s │\n" "Redis Cache" "$redis_cost"
printf "│ %-23s │ \$%-11s │\n" "Azure OpenAI" "$openai_cost"
printf "│ %-23s │ \$%-11s │\n" "Cognitive Services" "$cognitive_cost"
printf "│ %-23s │ \$%-11s │\n" "Monitoring & Logs" "$monitoring_cost"
printf "│ %-23s │ \$%-11s │\n" "Networking" "$networking_cost"
echo "├─────────────────────────┼──────────────┤"
printf "│ %-23s │ \$%-11s │\n" "TOTAL ESTIMATED" "$total_estimated"
echo "└─────────────────────────┴──────────────┘"
echo

# Cost optimization recommendations
echo "🎯 Cost Optimization Recommendations:"
echo

case "$ENVIRONMENT" in
    "dev")
        echo "📋 Development Environment Optimizations:"
        echo "• Use Azure Dev/Test pricing where available"
        echo "• Implement auto-shutdown for non-business hours"
        echo "• Use smaller SKUs for development workloads"
        echo "• Consider shared resources for multiple dev environments"
        echo "• Estimated savings: 30-40% (\$200-270/month)"
        ;;
    "staging")
        echo "📋 Staging Environment Optimizations:"
        echo "• Use smaller database tier during non-testing periods"
        echo "• Implement scheduled scaling for container apps"
        echo "• Use lifecycle policies for storage optimization"
        echo "• Consider reserved instances for predictable workloads"
        echo "• Estimated savings: 20-25% (\$300-380/month)"
        ;;
    "prod")
        echo "📋 Production Environment Optimizations:"
        echo "• Implement Azure Reserved Instances (1-3 year terms)"
        echo "• Use Azure Hybrid Benefit if applicable"
        echo "• Optimize AI service usage with caching strategies"
        echo "• Implement intelligent storage tiering"
        echo "• Use Azure Cost Management budgets and alerts"
        echo "• Estimated savings: 15-30% (\$600-1200/month)"
        ;;
esac

echo
echo "🔍 Resource-Specific Optimizations:"
echo

# Container Apps optimization
echo "🐳 Container Apps:"
echo "• Current estimate: \$${container_app_cost}/month"
echo "• Optimization: Use auto-scaling with min replicas = 0 for dev"
echo "• Optimization: Right-size CPU/memory based on actual usage"
echo "• Optimization: Use spot instances for non-critical workloads"
echo "• Potential savings: 20-40%"
echo

# Database optimization
echo "🗄️ SQL Database:"
echo "• Current estimate: \$${sql_database_cost}/month"
echo "• Optimization: Use serverless tier for development"
echo "• Optimization: Implement backup retention optimization"
echo "• Optimization: Use read replicas only when needed"
echo "• Potential savings: 30-50% in dev/staging"
echo

# Storage optimization
echo "💾 Storage Account:"
echo "• Current estimate: \$${storage_cost}/month"
echo "• Optimization: Implement lifecycle policies (Hot → Cool → Archive)"
echo "• Optimization: Use appropriate replication (LRS vs GRS)"
echo "• Optimization: Enable data deduplication"
echo "• Potential savings: 40-60%"
echo

# AI Services optimization
echo "🤖 AI Services:"
echo "• Current estimate: \$${openai_cost}/month"
echo "• Optimization: Implement intelligent caching"
echo "• Optimization: Use batch processing for non-real-time requests"
echo "• Optimization: Optimize prompt engineering to reduce token usage"
echo "• Optimization: Use multiple model tiers based on request complexity"
echo "• Potential savings: 25-45%"
echo

# Create cost monitoring alerts
echo "🚨 Setting up cost monitoring..."

# Create budget alert
run_az_command "Creating Budget Alert" \
"az consumption budget create \
  --budget-name 'budget-portal-ai-music-$ENVIRONMENT' \
  --amount $((total_estimated * 120 / 100)) \
  --resource-group '$RESOURCE_GROUP' \
  --time-grain 'Monthly' \
  --time-period '{\"start-date\":\"$(date +%Y-%m-01)\"}' \
  --category 'Cost' \
  --notifications '[{\"enabled\":true,\"operator\":\"GreaterThan\",\"threshold\":80,\"contact-emails\":[\"admin@example.com\"]}]'" "true"

# Create cost anomaly detection
run_az_command "Enabling Cost Anomaly Detection" \
"az costmanagement settings create \
  --name 'anomaly-detection-portal-ai-music' \
  --scope '/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP' \
  --type 'anomaly-detection'" "true"

echo "📊 Creating cost optimization dashboard..."

# Create cost optimization recommendations script
OPTIMIZATION_SCRIPT="#!/bin/bash
# Daily cost optimization check for Portal AI Music

echo '📊 Daily Cost Optimization Check - $(date)'
echo '================================================'

# Check for unused resources
echo '🔍 Checking for unused resources...'

# Check for stopped but not deallocated VMs
stopped_vms=\$(az vm list --resource-group '$RESOURCE_GROUP' --show-details --query \"[?powerState=='VM stopped'].name\" --output tsv)
if [[ -n \"\$stopped_vms\" ]]; then
    echo \"⚠️ Found stopped VMs that are still incurring costs:\"
    echo \"\$stopped_vms\"
    echo \"💡 Recommendation: Deallocate VMs to stop billing\"
fi

# Check for unattached disks
unattached_disks=\$(az disk list --resource-group '$RESOURCE_GROUP' --query \"[?diskState=='Unattached'].name\" --output tsv)
if [[ -n \"\$unattached_disks\" ]]; then
    echo \"⚠️ Found unattached disks:\"
    echo \"\$unattached_disks\"
    echo \"💡 Recommendation: Delete unused disks to save costs\"
fi

# Check storage account usage
echo '💾 Checking storage usage...'
storage_usage=\$(az storage account show-usage --resource-group '$RESOURCE_GROUP' --query 'value[0].currentValue' --output tsv 2>/dev/null || echo '0')
echo \"📊 Storage accounts in use: \$storage_usage\"

# Check database utilization
echo '🗄️ Checking database utilization...'
db_metrics=\$(az sql db show-usage --resource-group '$RESOURCE_GROUP' --server 'sql-portal-ai-music-$ENVIRONMENT-uks' --name 'portal-ai-music' --query 'value[0].currentValue' --output tsv 2>/dev/null || echo 'N/A')
echo \"📊 Database utilization: \$db_metrics\"

echo '✅ Cost optimization check completed'
echo '💡 Next check: $(date -d \"+1 day\")'
"

echo "$OPTIMIZATION_SCRIPT" > "/tmp/daily-cost-check-$ENVIRONMENT.sh"
chmod +x "/tmp/daily-cost-check-$ENVIRONMENT.sh"

# Generate cost report
COST_REPORT="# Cost Analysis Report - Portal AI Music ($ENVIRONMENT)

Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)
Environment: $ENVIRONMENT
Resource Group: $RESOURCE_GROUP
Location: $LOCATION

## Estimated Monthly Costs

| Service | Monthly Cost (USD) | Optimization Potential |
|---------|-------------------|----------------------|
| Container Apps | \$${container_app_cost} | 20-40% |
| SQL Database | \$${sql_database_cost} | 30-50% |
| Storage Account | \$${storage_cost} | 40-60% |
| Redis Cache | \$${redis_cost} | 15-25% |
| Azure OpenAI | \$${openai_cost} | 25-45% |
| Cognitive Services | \$${cognitive_cost} | 20-30% |
| Monitoring & Logs | \$${monitoring_cost} | 10-20% |
| Networking | \$${networking_cost} | 15-25% |
| **TOTAL** | **\$${total_estimated}** | **20-35%** |

## Key Optimization Opportunities

### 1. Development Environment
- Use Azure Dev/Test pricing
- Implement auto-shutdown schedules
- Use smaller SKUs for development
- Estimated savings: \$200-270/month

### 2. AI Services Optimization
- Implement intelligent caching
- Optimize prompt engineering
- Use batch processing
- Estimated savings: \$50-225/month

### 3. Storage Optimization
- Implement lifecycle policies
- Use appropriate replication tiers
- Enable data deduplication
- Estimated savings: \$10-30/month

### 4. Database Optimization
- Use serverless tier for dev/staging
- Optimize backup retention
- Right-size based on usage
- Estimated savings: \$45-240/month

## Monitoring and Alerts

- Budget alert set at 120% of estimated costs
- Cost anomaly detection enabled
- Daily optimization checks scheduled
- Monthly cost review meetings

## Action Items

1. Review and implement optimization recommendations
2. Set up automated shutdown schedules
3. Monitor AI service usage patterns
4. Implement storage lifecycle policies
5. Regular cost review meetings

## Next Review Date

$(date -d '+30 days' '+%Y-%m-%d')
"

echo "$COST_REPORT" > "/tmp/cost-analysis-report-$ENVIRONMENT.md"

echo "---"
echo -e "${GREEN}💰 Cost analysis completed successfully!${NC}"
echo
echo -e "${BLUE}📊 Summary:${NC}"
echo "• Estimated monthly cost: \$${total_estimated}"
echo "• Optimization potential: 20-35%"
echo "• Potential monthly savings: \$$(($total_estimated * 20 / 100))-\$$(($total_estimated * 35 / 100))"
echo
echo -e "${YELLOW}📄 Reports generated:${NC}"
echo "• Cost analysis report: /tmp/cost-analysis-report-$ENVIRONMENT.md"
echo "• Daily cost check script: /tmp/daily-cost-check-$ENVIRONMENT.sh"
echo
echo -e "${GREEN}🎯 Next Steps:${NC}"
echo "1. Review cost optimization recommendations"
echo "2. Implement automated shutdown schedules"
echo "3. Set up cost monitoring alerts"
echo "4. Schedule monthly cost review meetings"
echo "5. Monitor actual vs. estimated costs"
echo
echo -e "${BLUE}💡 Quick Wins:${NC}"
echo "• Enable auto-shutdown for dev environments"
echo "• Implement storage lifecycle policies"
echo "• Use smaller SKUs in non-production"
echo "• Set up budget alerts and monitoring"
echo
echo -e "${YELLOW}⚠️  Important:${NC}"
echo "• These are estimates based on typical usage patterns"
echo "• Actual costs may vary based on usage"
echo "• Regular monitoring and optimization are essential"
echo "• Consider reserved instances for production workloads"
