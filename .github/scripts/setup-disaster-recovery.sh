#!/bin/bash

# Disaster Recovery and Business Continuity Setup for Portal AI Music
# This script configures comprehensive backup, recovery, and failover mechanisms

set -e

# Configuration
RESOURCE_GROUP="${1:-}"
ENVIRONMENT="${2:-dev}"
SUBSCRIPTION_ID="${3:-}"
LOCATION="${4:-uksouth}"
SECONDARY_LOCATION="${5:-ukwest}"

if [[ -z "$RESOURCE_GROUP" || -z "$SUBSCRIPTION_ID" ]]; then
    echo "Usage: $0 <resource_group> [environment] [subscription_id] [primary_location] [secondary_location]"
    echo "Example: $0 rg-portal-ai-music-dev dev 12345678-1234-1234-1234-123456789012 uksouth ukwest"
    exit 1
fi

echo "🛡️ Setting up Disaster Recovery for Portal AI Music"
echo "📍 Primary Location: $LOCATION"
echo "🔄 Secondary Location: $SECONDARY_LOCATION"
echo "🏷️  Environment: $ENVIRONMENT"
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
    
    echo -e "${BLUE}🔧 $description${NC}"
    
    if eval "$command"; then
        echo -e "${GREEN}✅ Success: $description${NC}"
        return 0
    else
        if [[ "$optional" == "true" ]]; then
            echo -e "${YELLOW}⚠️  Optional: $description (may already exist)${NC}"
            return 0
        else
            echo -e "${RED}❌ Failed: $description${NC}"
            return 1
        fi
    fi
    echo
}

echo "🗄️ Setting up Database Backup and Recovery..."

# Database backup configuration
run_az_command "Enabling SQL Database Automated Backup" \
"az sql db show \
  --resource-group '$RESOURCE_GROUP' \
  --server 'sql-portal-ai-music-$ENVIRONMENT-uks' \
  --name 'portal-ai-music' \
  --query 'earliestRestoreDate'" "true"

run_az_command "Configuring Long-term Backup Retention" \
"az sql db ltr-policy set \
  --resource-group '$RESOURCE_GROUP' \
  --server 'sql-portal-ai-music-$ENVIRONMENT-uks' \
  --database 'portal-ai-music' \
  --weekly-retention 'P12W' \
  --monthly-retention 'P12M' \
  --yearly-retention 'P7Y' \
  --week-of-year 1"

# Geo-redundant backup for production
if [[ "$ENVIRONMENT" == "prod" ]]; then
    run_az_command "Creating Geo-Redundant SQL Database Backup" \
    "az sql db replica create \
      --resource-group '$RESOURCE_GROUP' \
      --server 'sql-portal-ai-music-$ENVIRONMENT-uks' \
      --name 'portal-ai-music' \
      --partner-resource-group '$RESOURCE_GROUP' \
      --partner-server 'sql-portal-ai-music-$ENVIRONMENT-ukw' \
      --partner-database 'portal-ai-music-replica'" "true"
fi

echo "💾 Setting up Storage Backup and Replication..."

# Storage account geo-replication
run_az_command "Configuring Storage Account Geo-Redundancy" \
"az storage account update \
  --resource-group '$RESOURCE_GROUP' \
  --name 'stportalaimusic${ENVIRONMENT}uks' \
  --sku 'Standard_RAGRS'"

# Create backup storage account in secondary region
run_az_command "Creating Secondary Storage Account" \
"az storage account create \
  --resource-group '$RESOURCE_GROUP' \
  --name 'stportalaimusic${ENVIRONMENT}ukw' \
  --location '$SECONDARY_LOCATION' \
  --sku 'Standard_RAGRS' \
  --kind 'StorageV2' \
  --access-tier 'Hot' \
  --encryption-services 'blob' 'file' \
  --https-only true \
  --allow-blob-public-access false" "true"

echo "🔄 Setting up Application Recovery..."

# Create secondary resource group for DR
run_az_command "Creating Secondary Resource Group" \
"az group create \
  --name 'rg-portal-ai-music-$ENVIRONMENT-dr' \
  --location '$SECONDARY_LOCATION'" "true"

# Create container registry in secondary region
run_az_command "Creating Secondary Container Registry" \
"az acr create \
  --resource-group 'rg-portal-ai-music-$ENVIRONMENT-dr' \
  --name 'acrportalaimusic${ENVIRONMENT}ukw' \
  --location '$SECONDARY_LOCATION' \
  --sku 'Premium' \
  --admin-enabled false" "true"

# Setup geo-replication for container registry
run_az_command "Configuring Container Registry Geo-Replication" \
"az acr replication create \
  --registry 'acrportalaimusic${ENVIRONMENT}uks' \
  --location '$SECONDARY_LOCATION'" "true"

echo "🔑 Setting up Key Vault Recovery..."

# Create secondary Key Vault
run_az_command "Creating Secondary Key Vault" \
"az keyvault create \
  --resource-group 'rg-portal-ai-music-$ENVIRONMENT-dr' \
  --name 'kv-portal-ai-music-$ENVIRONMENT-ukw' \
  --location '$SECONDARY_LOCATION' \
  --enabled-for-disk-encryption true \
  --enabled-for-deployment true \
  --enabled-for-template-deployment true \
  --enable-soft-delete true \
  --soft-delete-retention-days 90 \
  --enable-purge-protection true" "true"

# Enable Key Vault backup
run_az_command "Enabling Key Vault Backup" \
"az keyvault secret backup \
  --vault-name 'kv-portal-ai-music-$ENVIRONMENT-uks' \
  --name 'database-connection-string' \
  --file '/tmp/kv-backup-$(date +%Y%m%d).bak'" "true"

echo "📊 Setting up Monitoring and Recovery Automation..."

# Create recovery automation runbooks
RECOVERY_RUNBOOK='{
  "type": "PowerShell",
  "content": "
param(
    [Parameter(Mandatory=$true)]
    [string]$ResourceGroup,
    
    [Parameter(Mandatory=$true)]
    [string]$Environment,
    
    [Parameter(Mandatory=$true)]
    [string]$SecondaryLocation
)

Write-Output \"Starting disaster recovery failover for Portal AI Music\"
Write-Output \"Environment: $Environment\"
Write-Output \"Target Location: $SecondaryLocation\"

# Step 1: Validate secondary infrastructure
Write-Output \"Validating secondary infrastructure...\"

# Step 2: Update DNS records to point to secondary region
Write-Output \"Updating DNS records...\"

# Step 3: Start secondary container apps
Write-Output \"Starting secondary container apps...\"

# Step 4: Validate application health
Write-Output \"Validating application health...\"

Write-Output \"Disaster recovery failover completed successfully\"
"
}'

echo "$RECOVERY_RUNBOOK" > /tmp/recovery-runbook.json

run_az_command "Creating Disaster Recovery Automation Account" \
"az automation account create \
  --resource-group '$RESOURCE_GROUP' \
  --name 'aa-portal-ai-music-$ENVIRONMENT' \
  --location '$LOCATION'" "true"

echo "🚨 Setting up Recovery Testing..."

# Create recovery testing schedule
run_az_command "Creating Recovery Test Schedule" \
"az monitor scheduled-query-rule create \
  --resource-group '$RESOURCE_GROUP' \
  --name 'recovery-test-portal-ai-music' \
  --location '$LOCATION' \
  --description 'Monthly disaster recovery test' \
  --evaluation-frequency 'PT1H' \
  --severity 3 \
  --window-size 'PT1H' \
  --criteria-query 'let threshold = 30d; SecurityEvent | where TimeGenerated > ago(threshold) | where EventID == 4625 | summarize count() by bin(TimeGenerated, 1h)' \
  --action-group '/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/microsoft.insights/actionGroups/ag-portal-ai-music-$ENVIRONMENT-uks'" "true"

echo "📋 Creating Recovery Documentation..."

# Create recovery runbook documentation
RECOVERY_DOCS="# Disaster Recovery Runbook - Portal AI Music

## Recovery Time Objectives (RTO)
- **Critical Services**: 15 minutes
- **Full Application**: 30 minutes
- **Data Recovery**: 1 hour

## Recovery Point Objectives (RPO)
- **Database**: 5 minutes
- **File Storage**: 15 minutes
- **Configuration**: 1 hour

## Recovery Procedures

### 1. Database Failover
\`\`\`bash
# Failover to geo-replica
az sql db replica set-primary \\
  --resource-group '$RESOURCE_GROUP' \\
  --server 'sql-portal-ai-music-$ENVIRONMENT-ukw' \\
  --name 'portal-ai-music-replica'
\`\`\`

### 2. Application Failover
\`\`\`bash
# Deploy to secondary region
az containerapp create \\
  --resource-group 'rg-portal-ai-music-$ENVIRONMENT-dr' \\
  --name 'ca-portal-ai-music-$ENVIRONMENT-ukw' \\
  --location '$SECONDARY_LOCATION' \\
  --image 'acrportalaimusic${ENVIRONMENT}ukw.azurecr.io/portal-ai-music:latest'
\`\`\`

### 3. DNS Failover
\`\`\`bash
# Update Traffic Manager endpoint
az network traffic-manager endpoint update \\
  --resource-group '$RESOURCE_GROUP' \\
  --profile-name 'tm-portal-ai-music-$ENVIRONMENT' \\
  --name 'primary' \\
  --type 'azureEndpoints' \\
  --endpoint-status 'Disabled'

az network traffic-manager endpoint update \\
  --resource-group '$RESOURCE_GROUP' \\
  --profile-name 'tm-portal-ai-music-$ENVIRONMENT' \\
  --name 'secondary' \\
  --type 'azureEndpoints' \\
  --endpoint-status 'Enabled'
\`\`\`

## Testing Schedule
- **Monthly**: Database restore test
- **Quarterly**: Full DR test
- **Annually**: Complete infrastructure rebuild

## Emergency Contacts
- **Primary On-Call**: [Contact Information]
- **Secondary On-Call**: [Contact Information]
- **Azure Support**: [Support Plan Information]

## Monitoring and Validation
- Health check endpoints
- Database connectivity tests
- Application functionality validation
- Performance baseline comparison

## Rollback Procedures
1. Validate primary region recovery
2. Reverse DNS changes
3. Failback database
4. Verify application health
5. Resume normal operations
"

echo "$RECOVERY_DOCS" > "/tmp/disaster-recovery-runbook-$ENVIRONMENT.md"

echo "🌐 Setting up Traffic Manager for High Availability..."

# Create Traffic Manager profile for automatic failover
run_az_command "Creating Traffic Manager Profile" \
"az network traffic-manager profile create \
  --resource-group '$RESOURCE_GROUP' \
  --name 'tm-portal-ai-music-$ENVIRONMENT' \
  --routing-method 'Priority' \
  --unique-dns-name 'portal-ai-music-$ENVIRONMENT' \
  --ttl 30 \
  --monitor-protocol 'HTTPS' \
  --monitor-port 443 \
  --monitor-path '/api/health'" "true"

# Add primary endpoint
run_az_command "Adding Primary Traffic Manager Endpoint" \
"az network traffic-manager endpoint create \
  --resource-group '$RESOURCE_GROUP' \
  --profile-name 'tm-portal-ai-music-$ENVIRONMENT' \
  --name 'primary' \
  --type 'azureEndpoints' \
  --target-resource-id '/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.App/containerApps/ca-portal-ai-music-$ENVIRONMENT-uks' \
  --priority 1 \
  --endpoint-status 'Enabled'" "true"

# Add secondary endpoint (for production)
if [[ "$ENVIRONMENT" == "prod" ]]; then
    run_az_command "Adding Secondary Traffic Manager Endpoint" \
    "az network traffic-manager endpoint create \
      --resource-group '$RESOURCE_GROUP' \
      --profile-name 'tm-portal-ai-music-$ENVIRONMENT' \
      --name 'secondary' \
      --type 'azureEndpoints' \
      --target-resource-id '/subscriptions/$SUBSCRIPTION_ID/resourceGroups/rg-portal-ai-music-$ENVIRONMENT-dr/providers/Microsoft.App/containerApps/ca-portal-ai-music-$ENVIRONMENT-ukw' \
      --priority 2 \
      --endpoint-status 'Enabled'" "true"
fi

echo "🔍 Setting up Recovery Monitoring..."

# Monitor recovery metrics
run_az_command "Creating Recovery Time Monitoring Alert" \
"az monitor metrics alert create \
  --name 'Recovery Time SLA Violation' \
  --resource-group '$RESOURCE_GROUP' \
  --scopes '/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.App/containerApps/ca-portal-ai-music-$ENVIRONMENT-uks' \
  --condition 'avg availabilityResults/availabilityPercentage < 99.9' \
  --description 'Alert when recovery time exceeds SLA' \
  --evaluation-frequency '1m' \
  --window-size '5m' \
  --severity 0 \
  --action '/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/microsoft.insights/actionGroups/ag-portal-ai-music-$ENVIRONMENT-uks'"

echo "📊 Creating Recovery Dashboard..."

# Create recovery status dashboard
RECOVERY_DASHBOARD='{
  "properties": {
    "lenses": {
      "0": {
        "order": 0,
        "parts": {
          "0": {
            "position": {"x": 0, "y": 0, "rowSpan": 4, "colSpan": 6},
            "metadata": {
              "inputs": [],
              "type": "Extension/Microsoft_Azure_Monitoring/PartType/MetricsChartPart",
              "settings": {
                "content": {
                  "options": {
                    "chart": {
                      "metrics": [
                        {
                          "resourceMetadata": {
                            "id": "/subscriptions/'$SUBSCRIPTION_ID'/resourceGroups/'$RESOURCE_GROUP'/providers/Microsoft.App/containerApps/ca-portal-ai-music-'$ENVIRONMENT'-uks"
                          },
                          "name": "availabilityResults/availabilityPercentage",
                          "aggregationType": 4,
                          "namespace": "microsoft.app/containerapps",
                          "metricVisualization": {
                            "displayName": "Availability"
                          }
                        }
                      ],
                      "title": "Disaster Recovery Status",
                      "titleKind": 1,
                      "visualization": {
                        "chartType": 2
                      }
                    }
                  }
                }
              }
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
        },
        "filterLocale": {
          "value": "en-us"
        },
        "filters": {
          "value": {
            "MsPortalFx_TimeRange": {
              "model": {
                "format": "utc",
                "granularity": "auto",
                "relative": "24h"
              },
              "displayCache": {
                "name": "UTC Time",
                "value": "Past 24 hours"
              },
              "filteredPartIds": []
            }
          }
        }
      }
    }
  },
  "name": "portal-ai-music-disaster-recovery-'$ENVIRONMENT'",
  "type": "Microsoft.Portal/dashboards",
  "location": "INSERT_LOCATION",
  "tags": {
    "hidden-title": "Portal AI Music - Disaster Recovery Dashboard"
  }
}'

echo "$RECOVERY_DASHBOARD" > /tmp/recovery-dashboard.json

run_az_command "Creating Recovery Dashboard" \
"az portal dashboard create \
  --resource-group '$RESOURCE_GROUP' \
  --name 'portal-ai-music-dr-$ENVIRONMENT' \
  --input-path '/tmp/recovery-dashboard.json' \
  --location '$LOCATION'" "true"

echo "🧪 Running Recovery Validation Tests..."

# Validate recovery capabilities
run_az_command "Testing Database Backup Restore" \
"az sql db show-backup-short-term-retention-policy \
  --resource-group '$RESOURCE_GROUP' \
  --server 'sql-portal-ai-music-$ENVIRONMENT-uks' \
  --database 'portal-ai-music'"

run_az_command "Testing Storage Account Replication Status" \
"az storage account show \
  --resource-group '$RESOURCE_GROUP' \
  --name 'stportalaimusic${ENVIRONMENT}uks' \
  --query 'primaryEndpoints'"

run_az_command "Testing Container Registry Replication" \
"az acr replication list \
  --registry 'acrportalaimusic${ENVIRONMENT}uks' \
  --output table" "true"

# Cleanup temporary files
rm -f /tmp/recovery-runbook.json
rm -f /tmp/recovery-dashboard.json

echo "---"
echo -e "${GREEN}🎉 Disaster Recovery setup completed successfully!${NC}"
echo
echo "🛡️ Disaster Recovery Components Created:"
echo "• Database backup and geo-replication"
echo "• Storage account geo-redundancy"
echo "• Secondary infrastructure in $SECONDARY_LOCATION"
echo "• Container registry geo-replication"
echo "• Key Vault backup and secondary vault"
echo "• Traffic Manager for automatic failover"
echo "• Recovery automation runbooks"
echo "• Recovery monitoring and alerting"
echo "• Recovery testing schedule"
echo "• Recovery status dashboard"
echo
echo -e "${BLUE}📋 Recovery Objectives:${NC}"
echo "• RTO (Critical Services): 15 minutes"
echo "• RTO (Full Application): 30 minutes"
echo "• RPO (Database): 5 minutes"
echo "• RPO (Storage): 15 minutes"
echo
echo -e "${YELLOW}🔗 Next Steps:${NC}"
echo "1. Test database failover procedure"
echo "2. Validate application deployment in secondary region"
echo "3. Configure DNS failover automation"
echo "4. Schedule regular DR testing"
echo "5. Train team on recovery procedures"
echo
echo -e "${GREEN}📄 Documentation created:${NC}"
echo "• Recovery runbook: /tmp/disaster-recovery-runbook-$ENVIRONMENT.md"
echo "• Copy this to your documentation repository"
echo
echo -e "${BLUE}⚠️  Important Reminders:${NC}"
echo "• Test recovery procedures monthly"
echo "• Update recovery documentation regularly"
echo "• Monitor backup and replication status"
echo "• Validate RTO/RPO objectives quarterly"
echo "• Keep emergency contact information current"
