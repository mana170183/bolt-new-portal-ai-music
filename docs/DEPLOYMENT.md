# Azure Deployment Guide for AI Music Portal

## Overview

This guide provides step-by-step instructions for deploying the AI Music Portal to Azure using Infrastructure as Code (Terraform) and CI/CD pipelines (GitHub Actions).

## Architecture Overview

The deployment creates a comprehensive Azure infrastructure including:

- **Container Apps**: Scalable application hosting with automatic HTTPS
- **Azure Container Registry**: Private container image storage
- **Azure SQL Database**: Business Critical tier with geo-replication
- **Azure Storage**: Hot tier with lifecycle management
- **Azure Cache for Redis**: Premium tier with persistence
- **Azure OpenAI**: GPT-4, GPT-3.5, and embeddings
- **Azure Cognitive Services**: Speech synthesis and analysis
- **Azure AD B2C**: Identity management with MFA
- **Azure Monitor**: Comprehensive monitoring and alerting
- **Azure Key Vault**: Secure secrets management

## Prerequisites

### Required Tools
- Azure CLI (latest version)
- Terraform (>= 1.0)
- Git
- Docker
- Node.js 18+ (for local development)

### Azure Requirements
- Azure subscription with Owner or Contributor permissions
- Azure AD permissions to create applications and service principals
- Access to Azure OpenAI service (may require approval)

### GitHub Requirements
- GitHub repository with Actions enabled
- Secrets configured for Azure authentication

## Initial Setup

### 1. Azure Service Principal Setup

Create a service principal for GitHub Actions:

```bash
# Login to Azure
az login

# Set subscription
az account set --subscription "<your-subscription-id>"

# Create service principal
az ad sp create-for-rbac --name "portal-ai-music-github" \
  --role "Owner" \
  --scopes "/subscriptions/<your-subscription-id>" \
  --sdk-auth
```

Save the output JSON - you'll need it for GitHub secrets.

### 2. Azure Storage for Terraform State

Create storage account for Terraform remote state:

```bash
# Create resource group for Terraform state
az group create --name "rg-terraform-state" --location "uksouth"

# Create storage account
az storage account create \
  --name "sttfstate$(date +%s)" \
  --resource-group "rg-terraform-state" \
  --location "uksouth" \
  --sku "Standard_LRS"

# Create container
az storage container create \
  --name "tfstate" \
  --account-name "<storage-account-name>"
```

### 3. GitHub Secrets Configuration

Add the following secrets to your GitHub repository:

| Secret Name | Description | Value Source |
|-------------|-------------|--------------|
| `AZURE_CREDENTIALS` | Service principal JSON | Output from step 1 |
| `AZURE_CLIENT_ID` | Service principal client ID | From JSON output |
| `AZURE_CLIENT_SECRET` | Service principal secret | From JSON output |
| `AZURE_SUBSCRIPTION_ID` | Azure subscription ID | Your subscription |
| `AZURE_TENANT_ID` | Azure tenant ID | From JSON output |
| `TF_STATE_STORAGE_ACCOUNT` | Terraform state storage | Storage account name |
| `TF_STATE_CONTAINER` | Terraform state container | "tfstate" |
| `TF_STATE_KEY` | Terraform state file name | "portal-ai-music.tfstate" |

## Environment Configuration

### 1. Terraform Variables

Create environment-specific `.tfvars` files:

**dev.tfvars:**
```hcl
environment = "dev"
location = "uksouth"
location_short = "uks"
custom_domain = "dev.portal-ai-music.com"
container_app_min_replicas = 1
container_app_max_replicas = 5
performance_tier = "standard"
monitoring_email_receivers = [
  {
    name  = "dev-alerts"
    email = "dev-team@yourcompany.com"
  }
]
```

**prod.tfvars:**
```hcl
environment = "prod"
location = "uksouth"
location_short = "uks"
custom_domain = "portal-ai-music.com"
container_app_min_replicas = 3
container_app_max_replicas = 30
performance_tier = "premium"
enable_azure_defender = true
monitoring_email_receivers = [
  {
    name  = "prod-alerts"
    email = "ops-team@yourcompany.com"
  }
]
```

### 2. Backend Configuration

Create `backend-{env}.hcl` files:

**backend-dev.hcl:**
```hcl
resource_group_name  = "rg-terraform-state"
storage_account_name = "<your-storage-account>"
container_name       = "tfstate"
key                  = "dev/portal-ai-music.tfstate"
```

## Deployment Process

### 1. Automated Deployment (Recommended)

The GitHub Actions workflow handles the complete deployment:

1. **Push to development branch:**
   ```bash
   git checkout -b feature/new-feature
   # Make changes
   git commit -m "Add new feature"
   git push origin feature/new-feature
   ```

2. **Create Pull Request:**
   - GitHub Actions will run Terraform plan
   - Review the plan in PR comments
   - Merge when approved

3. **Deploy to production:**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

### 2. Manual Deployment

For manual deployment or troubleshooting:

```bash
# Initialize Terraform
terraform init -backend-config=backend-dev.hcl

# Plan deployment
terraform plan -var-file=dev.tfvars

# Apply deployment
terraform apply -var-file=dev.tfvars

# View outputs
terraform output
```

## Post-Deployment Configuration

### 1. DNS Configuration

After deployment, configure DNS records:

```bash
# Get the container app FQDN
FQDN=$(terraform output -raw container_app_fqdn)

# Create CNAME record for your custom domain
# Example: portal-ai-music.com -> $FQDN
```

### 2. SSL Certificate

The deployment automatically provisions SSL certificates via Azure Container Apps. For custom domains:

1. Add domain verification TXT record
2. Azure will automatically provision SSL certificate
3. Update DNS CNAME to point to container app FQDN

### 3. Azure AD B2C Configuration

1. **Access B2C tenant:**
   ```bash
   B2C_TENANT=$(terraform output -raw b2c_configuration | jq -r '.tenant_name')
   echo "B2C Tenant: https://portal.azure.com/#view/Microsoft_AAD_B2CAdmin"
   ```

2. **Configure user flows:**
   - Sign-up and sign-in flow
   - Password reset flow
   - Profile editing flow

3. **Custom branding:**
   - Upload logo and customize colors
   - Set privacy policy and terms of service URLs

### 4. Monitoring Setup

1. **Access monitoring dashboard:**
   ```bash
   terraform output monitoring_dashboard_url
   ```

2. **Configure additional alerts:**
   - Business metric alerts
   - Custom KPI monitoring
   - Integration with external tools

## Verification

### 1. Health Checks

Verify all services are healthy:

```bash
# Application health
curl https://$(terraform output -raw container_app_fqdn)/health

# Database connectivity
curl https://$(terraform output -raw container_app_fqdn)/api/health/db

# AI services connectivity
curl https://$(terraform output -raw container_app_fqdn)/api/health/ai
```

### 2. Monitoring Verification

Check monitoring setup:

```bash
# Application Insights
APP_INSIGHTS_KEY=$(terraform output -raw application_insights_instrumentation_key)
echo "Application Insights configured: $APP_INSIGHTS_KEY"

# Log Analytics
LOG_WORKSPACE=$(terraform output -raw log_analytics_workspace_id)
echo "Log Analytics workspace: $LOG_WORKSPACE"
```

### 3. Security Verification

Verify security configurations:

```bash
# Check private endpoints
terraform output | grep "private_endpoint"

# Verify Azure Defender
az security setting list --query "[?name=='MCAS'].enabled"

# Check Key Vault access
az keyvault secret list --vault-name $(terraform output -raw key_vault_name)
```

## Troubleshooting

### Common Issues

1. **Terraform Backend Error:**
   ```bash
   # Re-initialize backend
   terraform init -reconfigure -backend-config=backend-dev.hcl
   ```

2. **Azure OpenAI Access:**
   - Apply for Azure OpenAI access at https://aka.ms/oai/access
   - Update `openai_location` variable to available region

3. **Container App Deployment Issues:**
   ```bash
   # Check container app logs
   az containerapp logs show \
     --name $(terraform output -raw container_app_name) \
     --resource-group $(terraform output -raw resource_group_name)
   ```

4. **Private Endpoint Connectivity:**
   ```bash
   # Verify DNS resolution
   nslookup $(terraform output -raw sql_server_fqdn)
   
   # Test connectivity from container app
   az containerapp exec \
     --name $(terraform output -raw container_app_name) \
     --resource-group $(terraform output -raw resource_group_name) \
     --command "nc -zv <private-endpoint-ip> 1433"
   ```

### Getting Help

1. **Check GitHub Actions logs** for deployment errors
2. **Review Terraform state** for resource status
3. **Monitor Application Insights** for runtime issues
4. **Check Azure Service Health** for platform issues

## Maintenance

### Regular Tasks

1. **Update Terraform modules:**
   ```bash
   terraform init -upgrade
   ```

2. **Rotate secrets:**
   - Regenerate service principal credentials
   - Update database passwords
   - Refresh API keys

3. **Review costs:**
   ```bash
   terraform output estimated_monthly_costs
   ```

4. **Security updates:**
   - Keep base images updated
   - Apply security patches
   - Review access permissions

### Backup Verification

Verify backup configurations:

```bash
# SQL Database backups
az sql db show-backup-retention \
  --server $(terraform output -raw sql_server_name) \
  --database $(terraform output -raw sql_database_name) \
  --resource-group $(terraform output -raw resource_group_name)

# Storage account backup
az storage account show \
  --name $(terraform output -raw storage_account_name) \
  --resource-group $(terraform output -raw resource_group_name) \
  --query "{name:name, backupRetention:backup}"
```

## Cost Optimization

Review estimated costs and optimization opportunities:

```bash
# View cost breakdown
terraform output estimated_monthly_costs

# Estimated total: $2,000-3,500 USD/month for production
# - Container Apps: $300-500
# - SQL Database Business Critical: $500-800
# - Azure OpenAI: $400-800
# - Storage/Redis/Monitoring: $300-500
# - AI Services: $500-900
```

## Security & Compliance

The deployment includes:

- **SOC 2 Type II**: Audit logging, access controls, monitoring
- **GDPR**: Data retention, consent management, right to erasure
- **Security**: Private endpoints, encryption, MFA, conditional access
- **Monitoring**: Real-time alerts, security event tracking

## Next Steps

1. **Configure monitoring dashboards** for business metrics
2. **Set up log aggregation** for centralized logging
3. **Implement feature flags** for controlled rollouts
4. **Configure load testing** for performance validation
5. **Set up disaster recovery** procedures
6. **Implement cost optimization** strategies

## Support

For deployment support:
- Create GitHub issue for code-related problems
- Contact Azure support for platform issues
- Review documentation for configuration questions

The deployment workflow is already configured in `.github/workflows/azure-deploy.yml`. 

Add these secrets to your GitHub repository:
- `AZURE_STATIC_WEB_APPS_API_TOKEN`: Get from Azure Portal > Static Web App > Manage deployment token
- `VITE_API_URL`: Your backend API URL

## Backend Deployment (Azure App Service)

### 1. Create App Service

```bash
# Create App Service plan
az appservice plan create \
  --name portal-ai-music-plan \
  --resource-group portal-ai-music-rg \
  --sku B1 \
  --is-linux

# Create web app
az webapp create \
  --resource-group portal-ai-music-rg \
  --plan portal-ai-music-plan \
  --name portal-ai-music-backend \
  --runtime "PYTHON|3.11" \
  --deployment-container-image-name python:3.11-slim
```

### 2. Configure App Settings

```bash
# Set Python version
az webapp config set \
  --resource-group portal-ai-music-rg \
  --name portal-ai-music-backend \
  --linux-fx-version "PYTHON|3.11"

# Configure startup command
az webapp config set \
  --resource-group portal-ai-music-rg \
  --name portal-ai-music-backend \
  --startup-file "gunicorn --bind 0.0.0.0:8000 app:app"
```

### 3. Set Environment Variables

```bash
az webapp config appsettings set \
  --resource-group portal-ai-music-rg \
  --name portal-ai-music-backend \
  --settings \
    AZURE_CONNECTION_STRING="your_storage_connection_string" \
    CONTAINER_NAME="music-files" \
    FLASK_ENV="production"
```

### 4. Deploy Backend

Option A: Using Azure CLI
```bash
cd backend
az webapp up \
  --resource-group portal-ai-music-rg \
  --name portal-ai-music-backend \
  --runtime "PYTHON:3.11"
```

Option B: Using GitHub Actions (recommended)
- Configure the workflow in `.github/workflows/backend-deploy.yml`
- Add secrets: `AZURE_APP_SERVICE_NAME`, `AZURE_APP_SERVICE_PUBLISH_PROFILE`

## Storage Setup (Azure Blob Storage)

### 1. Create Storage Account

```bash
# Create storage account
az storage account create \
  --name portalaimusicstore \
  --resource-group portal-ai-music-rg \
  --location "East US" \
  --sku Standard_LRS

# Create container
az storage container create \
  --name music-files \
  --account-name portalaimusicstore \
  --public-access blob
```

### 2. Configure CORS

```bash
az storage cors add \
  --methods GET POST PUT \
  --origins https://your-static-app.azurestaticapps.net \
  --services b \
  --account-name portalaimusicstore
```

### 3. Get Connection String

```bash
az storage account show-connection-string \
  --name portalaimusicstore \
  --resource-group portal-ai-music-rg
```

## Domain and SSL

### 1. Custom Domain (Optional)

```bash
# Add custom domain to static web app
az staticwebapp hostname set \
  --name portal-ai-music-frontend \
  --resource-group portal-ai-music-rg \
  --hostname yourdomain.com
```

### 2. SSL Certificate

Azure automatically provides SSL certificates for both Static Web Apps and App Service.

## Monitoring and Logging

### 1. Enable Application Insights

```bash
# Create Application Insights
az monitor app-insights component create \
  --app portal-ai-music-insights \
  --location "East US" \
  --resource-group portal-ai-music-rg

# Link to App Service
az webapp config appsettings set \
  --resource-group portal-ai-music-rg \
  --name portal-ai-music-backend \
  --settings APPINSIGHTS_INSTRUMENTATIONKEY="your_instrumentation_key"
```

### 2. Configure Alerts

Set up alerts for:
- High error rates
- Response time degradation
- Storage quota limits

## Scaling and Performance

### 1. Auto-scaling

```bash
# Enable auto-scaling for App Service
az monitor autoscale create \
  --resource-group portal-ai-music-rg \
  --resource portal-ai-music-backend \
  --resource-type Microsoft.Web/serverfarms \
  --name portal-ai-music-autoscale \
  --min-count 1 \
  --max-count 5 \
  --count 2
```

### 2. CDN (Optional)

```bash
# Create CDN profile
az cdn profile create \
  --name portal-ai-music-cdn \
  --resource-group portal-ai-music-rg \
  --sku Standard_Microsoft

# Create CDN endpoint
az cdn endpoint create \
  --name portal-ai-music-endpoint \
  --profile-name portal-ai-music-cdn \
  --resource-group portal-ai-music-rg \
  --origin portalaimusicstore.blob.core.windows.net
```

## Security Best Practices

1. **Environment Variables**: Store all secrets in Azure Key Vault
2. **CORS**: Configure restrictive CORS policies
3. **Authentication**: Implement Azure AD B2C for user authentication
4. **Rate Limiting**: Use Azure API Management for rate limiting
5. **Network Security**: Configure Virtual Networks and NSGs

## Cost Optimization

1. **App Service**: Use B1 tier for development, scale up for production
2. **Storage**: Use Cool tier for long-term storage of generated music
3. **Static Web Apps**: Free tier supports up to 100GB bandwidth
4. **Monitoring**: Set up budget alerts to track spending

## Troubleshooting

### Common Issues

1. **CORS Errors**: Ensure frontend domain is added to backend CORS settings
2. **Storage Access**: Verify connection string and container permissions
3. **Build Failures**: Check Node.js/Python versions match requirements
4. **SSL Issues**: Ensure custom domains are properly configured

### Logs and Debugging

```bash
# View App Service logs
az webapp log tail \
  --resource-group portal-ai-music-rg \
  --name portal-ai-music-backend

# Download logs
az webapp log download \
  --resource-group portal-ai-music-rg \
  --name portal-ai-music-backend
```

## Production Checklist

- [ ] Environment variables configured
- [ ] HTTPS enabled on all services
- [ ] CORS properly configured
- [ ] Monitoring and alerts set up
- [ ] Backup strategy implemented
- [ ] Auto-scaling configured
- [ ] Security headers configured
- [ ] Performance testing completed
- [ ] Documentation updated

For additional support, refer to Azure documentation or create an issue in the repository.

## Advanced Features

### 🔍 Comprehensive Testing and Validation

The deployment includes advanced testing and validation scripts:

#### Integration Tests
```bash
# Run comprehensive integration tests
.github/scripts/integration-tests.sh <app_url> <environment> <iterations>

# Example
.github/scripts/integration-tests.sh https://ca-portal-ai-music-dev-uks.azurecontainerapps.io dev 5
```

#### Performance Testing
```bash
# Load testing with k6
k6 run --env BASE_URL=<app_url> load-test.js

# Performance baseline validation
curl -w "@.github/scripts/curl-format.txt" -o /dev/null -s <app_url>
```

#### Security and Compliance Validation
```bash
# Security header checks
curl -sI <app_url> | grep -i security

# SSL/TLS validation
echo | openssl s_client -connect <hostname>:443 -servername <hostname>
```

#### Final Deployment Validation
```bash
# Complete deployment validation
.github/scripts/final-validation.sh <app_url> <environment> <resource_group> <subscription_id>
```

### 📊 Advanced Monitoring and Alerting

#### Setup Advanced Monitoring
```bash
# Configure comprehensive monitoring
.github/scripts/setup-monitoring.sh <resource_group> <environment> <subscription_id> <location>
```

Features included:
- Application performance monitoring
- Infrastructure health checks
- Database performance alerts
- Security monitoring
- AI services monitoring
- SLO/SLI tracking
- Custom dashboards

#### Disaster Recovery Setup
```bash
# Configure disaster recovery (Production only)
.github/scripts/setup-disaster-recovery.sh <resource_group> <environment> <subscription_id> <primary_location> <secondary_location>
```

DR Features:
- Database geo-replication
- Storage geo-redundancy
- Container registry replication
- Traffic Manager failover
- Recovery automation
- RTO: 15-30 minutes
- RPO: 5-15 minutes

### 💰 Cost Analysis and Optimization

#### Cost Analysis
```bash
# Analyze costs and get optimization recommendations
.github/scripts/cost-analysis.sh <resource_group> <environment> <subscription_id> <location>
```

Cost Features:
- Monthly cost estimates by service
- Optimization recommendations
- Budget alerts and monitoring
- Cost anomaly detection
- Resource utilization analysis

#### Estimated Monthly Costs

| Environment | Container Apps | SQL Database | Storage | AI Services | Total Est. |
|-------------|---------------|--------------|---------|-------------|------------|
| Development | $50 | $150 | $25 | $275 | $675 |
| Staging | $150 | $300 | $75 | $650 | $1,525 |
| Production | $500 | $800 | $200 | $1,800 | $4,000 |

*Costs include Container Apps, SQL Database, Storage, Redis, OpenAI, Cognitive Services, and Monitoring*

#### Cost Optimization Potential
- **Development**: 30-40% savings ($200-270/month)
- **Staging**: 20-25% savings ($300-380/month)
- **Production**: 15-30% savings ($600-1,200/month)

### 🔄 CI/CD Pipeline Features

The GitHub Actions workflow includes:

#### Security Scanning
- ESLint code analysis
- Dependency vulnerability checks
- OWASP security scanning
- CodeQL analysis
- Container image scanning

#### Multi-Stage Testing
- Unit tests
- Integration tests
- Performance tests
- Security validation
- Compliance checks
- End-to-end testing

#### Blue-Green Deployment
- Zero-downtime deployments
- Automatic rollback on failure
- Health check validation
- Traffic switching
- Canary release support

#### Compliance Automation
- SOC 2 Type II validation
- GDPR compliance checks
- Security policy enforcement
- Audit trail generation
- Compliance reporting

### 📋 Deployment Validation Checklist

After deployment, the system automatically validates:

#### ✅ Infrastructure Health
- [ ] Container Apps running
- [ ] Database connectivity
- [ ] Storage access
- [ ] Redis cache status
- [ ] Key Vault access
- [ ] AI services availability

#### ✅ Application Health
- [ ] Health endpoints responding
- [ ] API endpoints functional
- [ ] Static assets loading
- [ ] Authentication working
- [ ] Database queries successful

#### ✅ Security Validation
- [ ] HTTPS enforcement
- [ ] Security headers present
- [ ] TLS configuration valid
- [ ] Private endpoints secured
- [ ] RBAC configured

#### ✅ Performance Validation
- [ ] Response time < 2 seconds
- [ ] Concurrent request handling
- [ ] Page size optimization
- [ ] CDN configuration
- [ ] Caching effectiveness

#### ✅ Compliance Validation
- [ ] Backup configuration
- [ ] Encryption at rest
- [ ] Audit logging enabled
- [ ] Data retention policies
- [ ] Privacy controls

#### ✅ Monitoring Validation
- [ ] Application Insights configured
- [ ] Log Analytics working
- [ ] Alert rules active
- [ ] Dashboard accessible
- [ ] Notification channels tested

### 🎯 Service Level Objectives (SLOs)

The deployment targets these SLOs:

#### Availability
- **Target**: 99.9% uptime
- **Measurement**: Health check availability
- **Alert**: < 99.9% over 30-minute window

#### Performance
- **Target**: P95 response time < 2 seconds
- **Measurement**: Application Insights metrics
- **Alert**: P95 > 2 seconds over 10-minute window

#### Reliability
- **Target**: < 0.1% error rate
- **Measurement**: Failed request percentage
- **Alert**: Error rate > 0.5% over 5-minute window

#### Data Durability
- **Target**: 99.999% data durability
- **Implementation**: Geo-redundant storage + backups
- **Validation**: Regular restore testing

### 🔧 Troubleshooting Guide

#### Common Issues and Solutions

**Application Not Responding**
```bash
# Check container app status
az containerapp show --resource-group <rg> --name <app> --query "properties.provisioningState"

# Check logs
az containerapp logs show --resource-group <rg> --name <app> --follow
```

**Database Connection Issues**
```bash
# Test database connectivity
az sql db show-connection-string --server <server> --name <db> --client ado.net

# Check firewall rules
az sql server firewall-rule list --resource-group <rg> --server <server>
```

**Performance Issues**
```bash
# Check Application Insights
az monitor app-insights query --app <app> --analytics-query "requests | summarize avg(duration) by bin(timestamp, 5m)"

# Check auto-scaling
az containerapp show --resource-group <rg> --name <app> --query "properties.template.scale"
```

**Security Alerts**
```bash
# Check Key Vault access
az keyvault show --resource-group <rg> --name <vault> --query "properties.accessPolicies"

# Review security policies
az policy assignment list --resource-group <rg>
```

### 📞 Support and Maintenance

#### Regular Maintenance Tasks

**Daily**
- Monitor application health
- Review performance metrics
- Check error rates
- Validate backup status

**Weekly**
- Review cost reports
- Update dependencies
- Security patch review
- Performance optimization

**Monthly**
- Disaster recovery testing
- Compliance audit
- Cost optimization review
- Capacity planning

**Quarterly**
- Full security assessment
- DR procedure validation
- Technology stack updates
- Architecture review

#### Support Contacts

- **DevOps Team**: [Contact Information]
- **Security Team**: [Contact Information]
- **Azure Support**: [Support Plan Information]
- **On-Call Rotation**: [PagerDuty/On-Call System]

#### Emergency Procedures

**Production Outage**
1. Check Azure Service Health
2. Review Application Insights alerts
3. Validate infrastructure status
4. Initiate incident response
5. Communicate to stakeholders

**Security Incident**
1. Isolate affected resources
2. Preserve evidence
3. Contact security team
4. Follow incident response plan
5. Document and review

**Data Loss/Corruption**
1. Stop write operations
2. Assess damage scope
3. Initiate restore procedure
4. Validate data integrity
5. Resume operations

### 📚 Additional Resources

- [Azure Container Apps Documentation](https://docs.microsoft.com/en-us/azure/container-apps/)
- [Azure SQL Database Best Practices](https://docs.microsoft.com/en-us/azure/azure-sql/database/best-practices)
- [Azure OpenAI Service Documentation](https://docs.microsoft.com/en-us/azure/cognitive-services/openai/)
- [SOC 2 Compliance Guide](https://docs.microsoft.com/en-us/compliance/regulatory/offering-soc-2)
- [GDPR Compliance Resources](https://docs.microsoft.com/en-us/compliance/regulatory/gdpr)

---

For questions or issues with this deployment guide, please contact the DevOps team or create an issue in the repository.