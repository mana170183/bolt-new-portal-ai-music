#!/bin/bash

echo "🚀 Portal AI Music - Azure Integrated Deployment"

# Configuration
RESOURCE_GROUP="rg-portal-ai-music-dev"
ACR_NAME="acrportalaimusic508"
BACKEND_APP_NAME="portal-ai-music-backend"
IMAGE_NAME="portal-ai-music-backend-azure"
IMAGE_TAG="latest"

# Step 1: Build and push the Docker image
echo "📦 Building Docker image with Azure integration..."
cd backend
docker build -t $ACR_NAME.azurecr.io/$IMAGE_NAME:$IMAGE_TAG -f Dockerfile .

# Step 2: Login to ACR and push image
echo "🔐 Logging into Azure Container Registry..."
az acr login --name $ACR_NAME

echo "⬆️ Pushing image to ACR..."
docker push $ACR_NAME.azurecr.io/$IMAGE_NAME:$IMAGE_TAG

# Step 3: Get connection strings and secrets
echo "🔗 Retrieving connection strings..."

# Get SQL connection string (you may need to set this manually)
SQL_SERVER="sql-portal-ai-music-dev.database.windows.net"
SQL_DATABASE="portal-ai-music-db"

# Get storage account key
STORAGE_KEY=$(az storage account keys list --resource-group $RESOURCE_GROUP --account-name stportalaimusic439 --query "[0].value" -o tsv)
STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=stportalaimusic439;AccountKey=$STORAGE_KEY;EndpointSuffix=core.windows.net"

# Get OpenAI key (from Key Vault or manual)
OPENAI_KEY=$(az keyvault secret show --vault-name kv-portal-ai-music-dev --name openai-api-key --query "value" -o tsv 2>/dev/null || echo "MANUAL_SET_REQUIRED")

# Step 4: Update Container App with new image and environment variables
echo "🔄 Updating Container App with Azure integration..."

# Update the container app with environment variables
az containerapp update \
  --name $BACKEND_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --image $ACR_NAME.azurecr.io/$IMAGE_NAME:$IMAGE_TAG \
  --set-env-vars \
    AZURE_SQL_SERVER="$SQL_SERVER" \
    AZURE_SQL_DATABASE="$SQL_DATABASE" \
    AZURE_STORAGE_ACCOUNT="stportalaimusic439" \
    AZURE_STORAGE_ENDPOINT="https://stportalaimusic439.blob.core.windows.net/" \
    AZURE_OPENAI_ENDPOINT="https://eastus.api.cognitive.microsoft.com/" \
    AZURE_KEY_VAULT_URI="https://kv-portal-ai-music-dev.vault.azure.net/" \
    AZURE_STORAGE_CONNECTION_STRING="$STORAGE_CONNECTION_STRING" \
    OPENAI_API_KEY="$OPENAI_KEY" \
    PORT="8000" \
    FLASK_ENV="production"

# Step 5: Restart the container app
echo "🔄 Restarting container app..."
az containerapp restart --name $BACKEND_APP_NAME --resource-group $RESOURCE_GROUP

# Step 6: Get the app URL
BACKEND_URL=$(az containerapp show --name $BACKEND_APP_NAME --resource-group $RESOURCE_GROUP --query "properties.configuration.ingress.fqdn" -o tsv)

echo "✅ Deployment complete!"
echo "🌐 Backend URL: https://$BACKEND_URL"
echo "🏥 Health Check: https://$BACKEND_URL/health"

# Step 7: Test the deployment
echo "🧪 Testing deployment..."
sleep 10
curl -s "https://$BACKEND_URL/health" | jq '.' || echo "Health check failed - container may still be starting"

echo "📋 Manual Steps Required:"
echo "1. Set SQL Server authentication in Azure Portal or update AZURE_SQL_CONNECTION_STRING"
echo "2. Verify OpenAI API key in Key Vault: kv-portal-ai-music-dev"
echo "3. Run SQL schema: create_schema.sql on the database"
echo "4. Test all endpoints: /api/music, /api/templates, /api/generate"

# Cleanup
echo "🎵 Portal AI Music Backend with Azure Integration is now deployed!"
