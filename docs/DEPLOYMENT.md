# Deployment Guide

This guide covers deploying Portal AI Music to Azure cloud services.

## Architecture Overview

- **Frontend**: React SPA deployed on Azure Static Web Apps
- **Backend**: Flask API deployed on Azure App Service
- **Storage**: Azure Blob Storage for generated music files
- **Database**: Optional Azure Cosmos DB for user data

## Prerequisites

1. Azure account with active subscription
2. GitHub account for CI/CD
3. Azure CLI installed locally
4. Node.js 18+ and Python 3.11+

## Frontend Deployment (Azure Static Web Apps)

### 1. Create Static Web App

```bash
# Login to Azure
az login

# Create resource group
az group create --name portal-ai-music-rg --location "East US"

# Create static web app
az staticwebapp create \
  --name portal-ai-music-frontend \
  --resource-group portal-ai-music-rg \
  --source https://github.com/yourusername/portal-ai-music \
  --location "East US2" \
  --branch main \
  --app-location "/" \
  --output-location "dist"
```

### 2. Configure Environment Variables

In Azure Portal, go to your Static Web App > Configuration and add:

```
VITE_API_URL=https://your-backend-app.azurewebsites.net
```

### 3. GitHub Actions Setup

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