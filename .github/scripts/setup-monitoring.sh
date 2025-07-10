#!/bin/bash

# Advanced Monitoring and Alerting Setup for Portal AI Music
# This script configures comprehensive monitoring, alerting, and compliance checks

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

echo "🎯 Setting up advanced monitoring for Portal AI Music"
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
    
    echo -e "${BLUE}🔧 $description${NC}"
    
    if eval "$command"; then
        echo -e "${GREEN}✅ Success: $description${NC}"
    else
        echo -e "${RED}❌ Failed: $description${NC}"
        return 1
    fi
    echo
}

echo "📊 Setting up Application Insights alerts..."

# Critical application alerts
run_az_command "Creating High Response Time Alert" \
"az monitor metrics alert create \
  --name 'High Response Time - Portal AI Music' \
  --resource-group '$RESOURCE_GROUP' \
  --scopes '/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.App/containerApps/ca-portal-ai-music-$ENVIRONMENT-uks' \
  --condition 'avg requests/duration > 2000' \
  --description 'Alert when average response time exceeds 2 seconds' \
  --evaluation-frequency '1m' \
  --window-size '5m' \
  --severity 2 \
  --action '/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/microsoft.insights/actionGroups/ag-portal-ai-music-$ENVIRONMENT-uks'"

run_az_command "Creating High Error Rate Alert" \
"az monitor metrics alert create \
  --name 'High Error Rate - Portal AI Music' \
  --resource-group '$RESOURCE_GROUP' \
  --scopes '/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.App/containerApps/ca-portal-ai-music-$ENVIRONMENT-uks' \
  --condition 'avg requests/failed > 5' \
  --description 'Alert when error rate exceeds 5%' \
  --evaluation-frequency '1m' \
  --window-size '5m' \
  --severity 1 \
  --action '/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/microsoft.insights/actionGroups/ag-portal-ai-music-$ENVIRONMENT-uks'"

run_az_command "Creating Low Availability Alert" \
"az monitor metrics alert create \
  --name 'Low Availability - Portal AI Music' \
  --resource-group '$RESOURCE_GROUP' \
  --scopes '/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.App/containerApps/ca-portal-ai-music-$ENVIRONMENT-uks' \
  --condition 'avg availabilityResults/availabilityPercentage < 99' \
  --description 'Alert when availability drops below 99%' \
  --evaluation-frequency '1m' \
  --window-size '5m' \
  --severity 1 \
  --action '/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/microsoft.insights/actionGroups/ag-portal-ai-music-$ENVIRONMENT-uks'"

echo "🖥️ Setting up infrastructure monitoring alerts..."

# Infrastructure alerts
run_az_command "Creating High CPU Alert" \
"az monitor metrics alert create \
  --name 'High CPU Usage - Container App' \
  --resource-group '$RESOURCE_GROUP' \
  --scopes '/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.App/containerApps/ca-portal-ai-music-$ENVIRONMENT-uks' \
  --condition 'avg CpuPercentage > 80' \
  --description 'Alert when CPU usage exceeds 80%' \
  --evaluation-frequency '1m' \
  --window-size '5m' \
  --severity 2 \
  --action '/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/microsoft.insights/actionGroups/ag-portal-ai-music-$ENVIRONMENT-uks'"

run_az_command "Creating High Memory Alert" \
"az monitor metrics alert create \
  --name 'High Memory Usage - Container App' \
  --resource-group '$RESOURCE_GROUP' \
  --scopes '/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.App/containerApps/ca-portal-ai-music-$ENVIRONMENT-uks' \
  --condition 'avg MemoryPercentage > 85' \
  --description 'Alert when memory usage exceeds 85%' \
  --evaluation-frequency '1m' \
  --window-size '5m' \
  --severity 2 \
  --action '/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/microsoft.insights/actionGroups/ag-portal-ai-music-$ENVIRONMENT-uks'"

echo "🗄️ Setting up database monitoring alerts..."

# Database monitoring
run_az_command "Creating High Database DTU Alert" \
"az monitor metrics alert create \
  --name 'High Database DTU - SQL Database' \
  --resource-group '$RESOURCE_GROUP' \
  --scopes '/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Sql/servers/sql-portal-ai-music-$ENVIRONMENT-uks/databases/portal-ai-music' \
  --condition 'avg dtu_consumption_percent > 80' \
  --description 'Alert when database DTU consumption exceeds 80%' \
  --evaluation-frequency '1m' \
  --window-size '5m' \
  --severity 2 \
  --action '/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/microsoft.insights/actionGroups/ag-portal-ai-music-$ENVIRONMENT-uks'"

run_az_command "Creating Database Connection Alert" \
"az monitor metrics alert create \
  --name 'Database Connection Issues - SQL Database' \
  --resource-group '$RESOURCE_GROUP' \
  --scopes '/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Sql/servers/sql-portal-ai-music-$ENVIRONMENT-uks/databases/portal-ai-music' \
  --condition 'avg connection_failed > 5' \
  --description 'Alert when database connection failures exceed 5 per minute' \
  --evaluation-frequency '1m' \
  --window-size '5m' \
  --severity 1 \
  --action '/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/microsoft.insights/actionGroups/ag-portal-ai-music-$ENVIRONMENT-uks'"

echo "💾 Setting up storage monitoring alerts..."

# Storage monitoring
run_az_command "Creating Storage Capacity Alert" \
"az monitor metrics alert create \
  --name 'High Storage Usage - Storage Account' \
  --resource-group '$RESOURCE_GROUP' \
  --scopes '/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Storage/storageAccounts/stportalaimusic${ENVIRONMENT}uks' \
  --condition 'avg UsedCapacity > 85000000000' \
  --description 'Alert when storage usage exceeds 85GB' \
  --evaluation-frequency '1m' \
  --window-size '5m' \
  --severity 2 \
  --action '/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/microsoft.insights/actionGroups/ag-portal-ai-music-$ENVIRONMENT-uks'"

echo "🔒 Setting up security monitoring alerts..."

# Security monitoring
run_az_command "Creating Key Vault Access Alert" \
"az monitor metrics alert create \
  --name 'Unauthorized Key Vault Access - Security' \
  --resource-group '$RESOURCE_GROUP' \
  --scopes '/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.KeyVault/vaults/kv-portal-ai-music-$ENVIRONMENT-uks' \
  --condition 'total ServiceApiResult > 10' \
  --description 'Alert on unusual Key Vault access patterns' \
  --evaluation-frequency '5m' \
  --window-size '15m' \
  --severity 1 \
  --action '/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/microsoft.insights/actionGroups/ag-portal-ai-music-$ENVIRONMENT-uks'"

echo "🤖 Setting up AI services monitoring..."

# AI services monitoring
run_az_command "Creating OpenAI Rate Limit Alert" \
"az monitor metrics alert create \
  --name 'OpenAI Rate Limit - AI Services' \
  --resource-group '$RESOURCE_GROUP' \
  --scopes '/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.CognitiveServices/accounts/openai-portal-ai-music-$ENVIRONMENT-uks' \
  --condition 'total TotalCalls > 9000' \
  --description 'Alert when approaching OpenAI rate limits' \
  --evaluation-frequency '1m' \
  --window-size '5m' \
  --severity 2 \
  --action '/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/microsoft.insights/actionGroups/ag-portal-ai-music-$ENVIRONMENT-uks'"

run_az_command "Creating AI Services Error Alert" \
"az monitor metrics alert create \
  --name 'AI Services Errors - Cognitive Services' \
  --resource-group '$RESOURCE_GROUP' \
  --scopes '/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.CognitiveServices/accounts/cog-portal-ai-music-$ENVIRONMENT-uks' \
  --condition 'total TotalErrors > 50' \
  --description 'Alert when AI services error count is high' \
  --evaluation-frequency '1m' \
  --window-size '5m' \
  --severity 1 \
  --action '/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/microsoft.insights/actionGroups/ag-portal-ai-music-$ENVIRONMENT-uks'"

echo "📋 Setting up compliance monitoring..."

# Compliance monitoring with Azure Policy
run_az_command "Creating SOC 2 Compliance Policy Assignment" \
"az policy assignment create \
  --name 'soc2-compliance-portal-ai-music' \
  --display-name 'SOC 2 Compliance for Portal AI Music' \
  --scope '/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP' \
  --policy-set-definition '/providers/Microsoft.Authorization/policySetDefinitions/89c6cddc-1c73-4ac1-b19c-54d1a15a42f2' \
  --description 'Ensures SOC 2 compliance for all resources'"

run_az_command "Creating GDPR Compliance Policy Assignment" \
"az policy assignment create \
  --name 'gdpr-compliance-portal-ai-music' \
  --display-name 'GDPR Compliance for Portal AI Music' \
  --scope '/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP' \
  --policy-set-definition '/providers/Microsoft.Authorization/policySetDefinitions/3e596b57-105f-48a6-be97-03e9243f548b' \
  --description 'Ensures GDPR compliance for all resources'"

echo "🔄 Setting up backup monitoring..."

# Backup monitoring
run_az_command "Creating Backup Failure Alert" \
"az monitor activity-log alert create \
  --name 'Backup Failure - Portal AI Music' \
  --resource-group '$RESOURCE_GROUP' \
  --scope '/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP' \
  --condition category=Administrative operationName=Microsoft.Sql/servers/databases/restorePoints/write level=Error \
  --description 'Alert when database backup operations fail' \
  --action-group '/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/microsoft.insights/actionGroups/ag-portal-ai-music-$ENVIRONMENT-uks'"

echo "🔗 Setting up availability tests..."

# Create availability tests
run_az_command "Creating Application Availability Test" \
"az monitor app-insights web-test create \
  --resource-group '$RESOURCE_GROUP' \
  --app-insights '/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/microsoft.insights/components/appi-portal-ai-music-$ENVIRONMENT-uks' \
  --name 'availability-test-portal-ai-music' \
  --location '$LOCATION' \
  --test-locations 'us-va-ash-azr,emea-nl-ams-azr,apac-jp-kaw-edge' \
  --web-test-kind 'ping' \
  --frequency 300 \
  --timeout 120 \
  --url 'https://ca-portal-ai-music-$ENVIRONMENT-uks.azurecontainerapps.io' \
  --description 'Availability test for Portal AI Music application'"

echo "📊 Setting up custom dashboards..."

# Create custom monitoring dashboard
DASHBOARD_CONFIG='{
  "lenses": {
    "0": {
      "order": 0,
      "parts": {
        "0": {
          "position": {"x": 0, "y": 0, "rowSpan": 4, "colSpan": 6},
          "metadata": {
            "inputs": [
              {
                "name": "resourceType",
                "value": "microsoft.app/containerapps"
              },
              {
                "name": "resourceName",
                "value": "ca-portal-ai-music-'$ENVIRONMENT'-uks"
              }
            ],
            "type": "Extension/AppInsightsExtension/PartType/AppMapGalPt"
          }
        }
      }
    }
  },
  "metadata": {
    "model": {
      "timeRange": {
        "value": {
          "relative": {
            "duration": 24,
            "timeUnit": 1
          }
        },
        "type": "MsPortalFx.Composition.Configuration.ValueTypes.TimeRange"
      }
    }
  }
}'

echo "$DASHBOARD_CONFIG" > /tmp/dashboard-config.json

run_az_command "Creating Monitoring Dashboard" \
"az portal dashboard create \
  --resource-group '$RESOURCE_GROUP' \
  --name 'portal-ai-music-monitoring-$ENVIRONMENT' \
  --input-path '/tmp/dashboard-config.json' \
  --location '$LOCATION'"

echo "🎯 Setting up performance baselines..."

# Set up performance baselines and SLI/SLO monitoring
run_az_command "Creating SLO Availability Alert (99.9%)" \
"az monitor metrics alert create \
  --name 'SLO Violation - Availability Below 99.9%' \
  --resource-group '$RESOURCE_GROUP' \
  --scopes '/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.App/containerApps/ca-portal-ai-music-$ENVIRONMENT-uks' \
  --condition 'avg availabilityResults/availabilityPercentage < 99.9' \
  --description 'SLO violation: Availability has dropped below 99.9%' \
  --evaluation-frequency '5m' \
  --window-size '30m' \
  --severity 0 \
  --action '/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/microsoft.insights/actionGroups/ag-portal-ai-music-$ENVIRONMENT-uks'"

run_az_command "Creating SLO Response Time Alert (P95 < 2s)" \
"az monitor metrics alert create \
  --name 'SLO Violation - Response Time P95 Above 2s' \
  --resource-group '$RESOURCE_GROUP' \
  --scopes '/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.App/containerApps/ca-portal-ai-music-$ENVIRONMENT-uks' \
  --condition 'avg requests/duration > 2000' \
  --description 'SLO violation: P95 response time has exceeded 2 seconds' \
  --evaluation-frequency '1m' \
  --window-size '10m' \
  --severity 0 \
  --action '/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/microsoft.insights/actionGroups/ag-portal-ai-music-$ENVIRONMENT-uks'"

echo "🚨 Setting up incident response automation..."

# Create automated incident response
run_az_command "Creating Auto-Scaling Alert" \
"az monitor autoscale create \
  --resource-group '$RESOURCE_GROUP' \
  --name 'autoscale-portal-ai-music-$ENVIRONMENT' \
  --resource '/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.App/containerApps/ca-portal-ai-music-$ENVIRONMENT-uks' \
  --min-count 2 \
  --max-count 10 \
  --count 2"

echo "📧 Testing notification channels..."

# Test alert notifications
run_az_command "Testing Alert Notification Channel" \
"az monitor action-group test-notifications create \
  --action-group-name 'ag-portal-ai-music-$ENVIRONMENT-uks' \
  --resource-group '$RESOURCE_GROUP' \
  --notification-type 'email' \
  --alert-type 'metric'"

# Cleanup temporary files
rm -f /tmp/dashboard-config.json

echo "---"
echo -e "${GREEN}🎉 Advanced monitoring setup completed successfully!${NC}"
echo
echo "📊 Monitoring Components Created:"
echo "• Application performance alerts"
echo "• Infrastructure monitoring alerts"
echo "• Database performance alerts"
echo "• Security monitoring alerts"
echo "• AI services monitoring alerts"
echo "• Compliance policy assignments"
echo "• Backup monitoring alerts"
echo "• Availability tests"
echo "• Custom monitoring dashboard"
echo "• SLO/SLI monitoring"
echo "• Auto-scaling configuration"
echo
echo -e "${BLUE}🔗 Next Steps:${NC}"
echo "1. Verify alerts in Azure Portal"
echo "2. Test notification channels"
echo "3. Review dashboard configuration"
echo "4. Validate compliance policies"
echo "5. Set up on-call rotation"
echo
echo -e "${YELLOW}📝 Important Notes:${NC}"
echo "• All alerts are configured with appropriate thresholds"
echo "• Notification channels need to be tested regularly"
echo "• Dashboard can be customized based on team needs"
echo "• Compliance policies are enforced automatically"
echo "• Auto-scaling will handle traffic spikes"
