# 🚀 Portal AI Music - Complete Azure Deployment Guide

## 📋 Overview
This guide provides step-by-step instructions to deploy the Portal AI Music platform to Azure using Web Apps (not Container Apps) to avoid previous CORS and deployment issues.

## 🏗️ Architecture Overview

```
Portal AI Music Azure Architecture:
┌─────────────────────────────────────────────────────────────┐
│                    Resource Group: rg-portal-ai-music      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Frontend Web App           Backend Web App                 │
│  ┌─────────────────┐       ┌─────────────────┐            │
│  │ React/Vite      │◄──────┤ Node.js/Express │            │
│  │ Tailwind CSS    │       │ REST API        │            │
│  │ Blue-Purple-Pink│       │ CORS Fixed      │            │
│  └─────────────────┘       └─────────────────┘            │
│           │                          │                     │
│           │                          ▼                     │
│           │                 ┌─────────────────┐            │
│           │                 │ Azure SQL DB    │            │
│           │                 │ Metadata Store  │            │
│           │                 └─────────────────┘            │
│           │                          │                     │
│           │                          ▼                     │
│           │                 ┌─────────────────┐            │
│           │                 │ Azure Storage   │            │
│           │                 │ Audio Files     │            │
│           │                 └─────────────────┘            │
│           │                          │                     │
│           │                          ▼                     │
│           │                 ┌─────────────────┐            │
│           │                 │ Azure OpenAI    │            │
│           │                 │ Music Analysis  │            │
│           │                 └─────────────────┘            │
│           │                          │                     │
│           │                          ▼                     │
│           │                 ┌─────────────────┐            │
│           └─────────────────┤ Key Vault       │            │
│                             │ Secrets Store   │            │
│                             └─────────────────┘            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Prerequisites

### 1. Required Tools
```bash
# Install Azure CLI
brew install azure-cli

# Install Node.js
brew install node

# Verify installations
az --version
node --version
npm --version
```

### 2. Azure Configuration
```bash
# Your provided configuration
export SUBSCRIPTION_ID="f165aa7d-ea02-4be9-aa0c-fad453084a9f"
export RESOURCE_GROUP="rg-portal-ai-music"
export LOCATION="uksouth"  # or "westeurope"

# Service Principal
export SP_APP_ID="6a069624-67ed-4bfe-b4e6-301f6e02a853"
export SP_PASSWORD="Q9a8Q~XRiQ3hKIHKUCFn6ka.jZ3udfNwyI.s2aC5"
export SP_TENANT="bca013b2-c163-4a0d-ad43-e6f1d3cda34b"
```

## 🚀 Step-by-Step Deployment

### Step 1: Prepare Local Environment

```bash
# Navigate to your project directory
cd /Users/managobindasethi/bolt-new/https---github.com-mana170183-bolt-new-portal-ai-music-tree-studio

# Ensure all dependencies are installed
npm install

# Build the frontend
npm run build

# Verify build output
ls -la dist/
```

### Step 2: Run the Deployment Script

```bash
# Make the deployment script executable
chmod +x azure-webapp-deploy.sh

# Run the complete deployment
./azure-webapp-deploy.sh
```

This script will automatically:
1. ✅ Login to Azure with your service principal
2. ✅ Create the resource group `rg-portal-ai-music`
3. ✅ Create App Service Plan (Linux, B1 tier)
4. ✅ Create Azure Storage Account with containers
5. ✅ Create Azure SQL Database with firewall rules
6. ✅ Create Azure OpenAI service
7. ✅ Create Key Vault and store secrets
8. ✅ Create Frontend and Backend Web Apps
9. ✅ Deploy the code to both Web Apps
10. ✅ Configure app settings and environment variables

### Step 3: Set Up Database Schema

After deployment, run the SQL schema:

```bash
# Install sqlcmd (if not already installed)
brew install sqlcmd

# Connect to your Azure SQL Database
sqlcmd -S portal-ai-music-sql-server.database.windows.net -d portal-ai-music-db -U portaladmin -P [PASSWORD_FROM_DEPLOYMENT] -i azure-sql-schema.sql
```

Alternative: Use Azure Portal Query Editor:
1. Go to Azure Portal → SQL Database → portal-ai-music-db
2. Click "Query editor"
3. Login with the credentials from deployment
4. Copy and paste the content of `azure-sql-schema.sql`
5. Execute the script

### Step 4: Configure API Keys

#### Get Free API Keys:
```bash
# 1. Jamendo API Key
# Register at: https://devportal.jamendo.com/
# Get your CLIENT_ID

# 2. Last.fm API Key  
# Register at: https://www.last.fm/api/account/create
# Get your API_KEY

# 3. Freesound API Key
# Register at: https://freesound.org/help/developers/
# Get your API_TOKEN
```

#### Configure Backend with API Keys:
```bash
az webapp config appsettings set \
  --name portal-ai-music-backend \
  --resource-group rg-portal-ai-music \
  --settings \
    JAMENDO_CLIENT_ID="your_jamendo_client_id" \
    LASTFM_API_KEY="your_lastfm_api_key" \
    FREESOUND_API_KEY="your_freesound_api_key"
```

### Step 5: Test Deployment

#### 1. Test Backend Health:
```bash
curl https://portal-ai-music-backend.azurewebsites.net/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-07-27T...",
  "environment": "production",
  "version": "1.0.0",
  "services": {
    "database": "connected",
    "storage": "connected", 
    "openai": "connected"
  }
}
```

#### 2. Test API Endpoints:
```bash
# Test genres endpoint
curl https://portal-ai-music-backend.azurewebsites.net/api/genres

# Test music generation
curl -X POST https://portal-ai-music-backend.azurewebsites.net/api/generate-music \
  -H "Content-Type: application/json" \
  -d '{"genre":"electronic","mood":"energetic","duration":30}'

# Test music search
curl "https://portal-ai-music-backend.azurewebsites.net/api/search-all?query=jazz"
```

#### 3. Test Frontend:
Visit: `https://portal-ai-music-frontend.azurewebsites.net`

Expected behavior:
- ✅ Website loads with blue-purple-pink theme
- ✅ No console errors
- ✅ Music player works
- ✅ Generation forms work
- ✅ No CORS errors

## 🔧 Resource Details

### Created Resources:

| Resource | Name | SKU | Cost/Month |
|----------|------|-----|------------|
| Resource Group | rg-portal-ai-music | - | $0 |
| App Service Plan | portal-ai-music-plan | B1 Linux | ~$13 |
| Frontend Web App | portal-ai-music-frontend | - | Included |
| Backend Web App | portal-ai-music-backend | - | Included |
| Storage Account | portalaimusicstore | Standard_LRS | ~$5 |
| SQL Database | portal-ai-music-db | Basic (5 DTU) | ~$5 |
| SQL Server | portal-ai-music-sql-server | - | Included |
| OpenAI Service | portal-ai-music-openai | S0 | ~$10 |
| Key Vault | portal-ai-music-kv | Standard | ~$3 |
| **Total Estimated** | | | **~$36/month** |

### Optimized for Cost:
- ✅ B1 App Service Plan (cheapest with custom domains)
- ✅ Basic SQL Database (5 DTU - perfect for metadata)
- ✅ Standard_LRS Storage (locally redundant)
- ✅ S0 OpenAI (pay-per-use model)

## 🌐 Domain & HTTPS

### Custom Domain (Optional):
```bash
# Add custom domain
az webapp config hostname add \
  --webapp-name portal-ai-music-frontend \
  --resource-group rg-portal-ai-music \
  --hostname yourdomain.com

# Add SSL certificate
az webapp config ssl upload \
  --name portal-ai-music-frontend \
  --resource-group rg-portal-ai-music \
  --certificate-file path/to/certificate.pfx \
  --certificate-password your_password
```

### Free SSL (Recommended):
The Web Apps come with free `*.azurewebsites.net` SSL certificates automatically.

## 📊 Monitoring & Analytics

### Enable Application Insights:
```bash
# Create Application Insights
az extension add --name application-insights
az monitor app-insights component create \
  --app portal-ai-music-insights \
  --location uksouth \
  --resource-group rg-portal-ai-music \
  --application-type web

# Get instrumentation key
INSIGHTS_KEY=$(az monitor app-insights component show \
  --app portal-ai-music-insights \
  --resource-group rg-portal-ai-music \
  --query instrumentationKey -o tsv)

# Configure Web Apps with Application Insights
az webapp config appsettings set \
  --name portal-ai-music-backend \
  --resource-group rg-portal-ai-music \
  --settings APPINSIGHTS_INSTRUMENTATIONKEY="$INSIGHTS_KEY"

az webapp config appsettings set \
  --name portal-ai-music-frontend \
  --resource-group rg-portal-ai-music \
  --settings APPINSIGHTS_INSTRUMENTATIONKEY="$INSIGHTS_KEY"
```

## 🔒 Security Best Practices

### 1. Key Vault References:
All sensitive data is stored in Key Vault:
- SQL connection string
- OpenAI API key
- Storage account key

### 2. Managed Identity:
Both Web Apps use system-assigned managed identities to access Key Vault.

### 3. Network Security:
```bash
# Restrict SQL Database to Azure services only
az sql server firewall-rule create \
  --server portal-ai-music-sql-server \
  --resource-group rg-portal-ai-music \
  --name "AllowAzureServices" \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0
```

## 🐛 Troubleshooting

### Common Issues:

#### 1. CORS Error:
```bash
# Check backend CORS configuration
az webapp config show \
  --name portal-ai-music-backend \
  --resource-group rg-portal-ai-music \
  --query "cors"

# Update CORS if needed
az webapp cors add \
  --name portal-ai-music-backend \
  --resource-group rg-portal-ai-music \
  --allowed-origins "https://portal-ai-music-frontend.azurewebsites.net"
```

#### 2. Backend Not Starting:
```bash
# Check backend logs
az webapp log tail \
  --name portal-ai-music-backend \
  --resource-group rg-portal-ai-music

# Check app settings
az webapp config appsettings list \
  --name portal-ai-music-backend \
  --resource-group rg-portal-ai-music
```

#### 3. Database Connection Issues:
```bash
# Test SQL connection
az sql db show-connection-string \
  --server portal-ai-music-sql-server \
  --name portal-ai-music-db \
  --client sqlcmd

# Check firewall rules
az sql server firewall-rule list \
  --server portal-ai-music-sql-server \
  --resource-group rg-portal-ai-music
```

#### 4. Frontend Build Issues:
```bash
# Rebuild frontend locally
npm run build

# Check dist folder
ls -la dist/

# Redeploy frontend
cd frontend-deploy
zip -r ../frontend-deploy.zip .
cd ..
az webapp deployment source config-zip \
  --name portal-ai-music-frontend \
  --resource-group rg-portal-ai-music \
  --src frontend-deploy.zip
```

## 🔄 Updates & Maintenance

### Update Backend Code:
```bash
# Update production-backend-webapp.js
# Then redeploy:
cp production-backend-webapp.js server.js
zip -r backend-update.zip server.js package.json
az webapp deployment source config-zip \
  --name portal-ai-music-backend \
  --resource-group rg-portal-ai-music \
  --src backend-update.zip
```

### Update Frontend Code:
```bash
# Build new version
npm run build

# Redeploy
# (Follow frontend deployment steps from main script)
```

### Scale Resources:
```bash
# Scale App Service Plan up
az appservice plan update \
  --name portal-ai-music-plan \
  --resource-group rg-portal-ai-music \
  --sku S1

# Scale SQL Database up
az sql db update \
  --server portal-ai-music-sql-server \
  --resource-group rg-portal-ai-music \
  --name portal-ai-music-db \
  --edition Standard \
  --capacity 20
```

## 📈 Performance Optimization

### 1. Enable CDN:
```bash
# Create CDN profile
az cdn profile create \
  --name portal-ai-music-cdn \
  --resource-group rg-portal-ai-music \
  --sku Standard_Microsoft

# Create CDN endpoint
az cdn endpoint create \
  --name portal-ai-music-assets \
  --profile-name portal-ai-music-cdn \
  --resource-group rg-portal-ai-music \
  --origin portalaimusicstore.blob.core.windows.net
```

### 2. Enable Redis Cache:
```bash
# Create Redis Cache
az redis create \
  --name portal-ai-music-cache \
  --resource-group rg-portal-ai-music \
  --location uksouth \
  --sku Basic \
  --vm-size c0
```

## ✅ Deployment Checklist

- [ ] Prerequisites installed (Azure CLI, Node.js)
- [ ] Environment variables exported
- [ ] Local build successful (`npm run build`)
- [ ] Deployment script executed successfully
- [ ] Database schema applied
- [ ] API keys configured
- [ ] Backend health check passes
- [ ] Frontend loads without errors
- [ ] Music generation works
- [ ] Audio playback works
- [ ] No CORS errors in browser console
- [ ] All API endpoints respond correctly
- [ ] Database connections working
- [ ] Storage containers accessible
- [ ] OpenAI service responding

## 🎉 Success Criteria

Your deployment is successful when:

1. **Frontend**: `https://portal-ai-music-frontend.azurewebsites.net`
   - ✅ Loads with blue-purple-pink theme
   - ✅ No console errors
   - ✅ Music player functional
   - ✅ All forms work

2. **Backend**: `https://portal-ai-music-backend.azurewebsites.net`
   - ✅ Health check returns 200
   - ✅ All API endpoints respond
   - ✅ Database connected
   - ✅ Storage connected
   - ✅ OpenAI connected

3. **Integration**:
   - ✅ Frontend can call backend APIs
   - ✅ No CORS errors
   - ✅ Music generation works end-to-end
   - ✅ Audio files play correctly

**Total deployment time**: 15-20 minutes
**Monthly cost**: ~$36 USD
**Ready for production**: ✅ YES

Your Portal AI Music platform is now live and ready for users! 🎵🚀
