#!/bin/bash

set -e

echo "🚀 Starting Azure deployment..."

# Check if logged in to Azure
if ! az account show &> /dev/null; then
    echo "Please login to Azure first:"
    echo "az login"
    exit 1
fi

# Variables
RESOURCE_GROUP="ai-music-portal-rg"
LOCATION="eastus"
ACR_NAME="aimusicportalacr"
BACKEND_APP_NAME="ai-music-portal-backend"
FRONTEND_APP_NAME="ai-music-portal-frontend"

# Ensure we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Please run this script from the root directory of the project"
    exit 1
fi

echo "📦 Building and pushing Docker images..."

# Build backend image
echo "Building backend image..."
docker build -f Dockerfile.backend -t $ACR_NAME.azurecr.io/$BACKEND_APP_NAME:latest .

# Build frontend image
echo "Building frontend image..."
docker build -f Dockerfile.frontend -t $ACR_NAME.azurecr.io/$FRONTEND_APP_NAME:latest .

# Login to ACR and push images
echo "Logging into Azure Container Registry..."
az acr login --name $ACR_NAME

echo "Pushing backend image..."
docker push $ACR_NAME.azurecr.io/$BACKEND_APP_NAME:latest

echo "Pushing frontend image..."
docker push $ACR_NAME.azurecr.io/$FRONTEND_APP_NAME:latest

echo "🔄 Updating Azure Container Apps..."

# Update backend container app
echo "Updating backend container app..."
az containerapp update \
    --name $BACKEND_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --image $ACR_NAME.azurecr.io/$BACKEND_APP_NAME:latest

# Update frontend container app
echo "Updating frontend container app..."
az containerapp update \
    --name $FRONTEND_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --image $ACR_NAME.azurecr.io/$FRONTEND_APP_NAME:latest

echo "🔍 Getting application URLs..."

# Get backend URL
BACKEND_URL=$(az containerapp show \
    --name $BACKEND_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query "properties.configuration.ingress.fqdn" \
    --output tsv)

# Get frontend URL
FRONTEND_URL=$(az containerapp show \
    --name $FRONTEND_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query "properties.configuration.ingress.fqdn" \
    --output tsv)

echo ""
echo "✅ Deployment completed successfully!"
echo ""
echo "🌐 Application URLs:"
echo "Backend:  https://$BACKEND_URL"
echo "Frontend: https://$FRONTEND_URL"
echo ""
echo "📊 Check deployment status:"
echo "az containerapp show --name $BACKEND_APP_NAME --resource-group $RESOURCE_GROUP --query 'properties.runningStatus'"
echo "az containerapp show --name $FRONTEND_APP_NAME --resource-group $RESOURCE_GROUP --query 'properties.runningStatus'"
echo ""
echo "📝 View logs:"
echo "az containerapp logs show --name $BACKEND_APP_NAME --resource-group $RESOURCE_GROUP --follow"
echo "az containerapp logs show --name $FRONTEND_APP_NAME --resource-group $RESOURCE_GROUP --follow"
