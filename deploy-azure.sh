#!/bin/bash

# Azure Configuration
export SUBSCRIPTION_ID="f165aa7d-ea02-4be9-aa0c-fad453084a9f"
export RESOURCE_GROUP="rg-portal-ai-music-dev"
export LOCATION="uksouth"

# Service Principal
export SP_APP_ID="6a069624-67ed-4bfe-b4e6-301f6e02a853"
export SP_PASSWORD="Q9a8Q~XRiQ3hKIHKUCFn6ka.jZ3udfNwyI.s2aC5"
export SP_TENANT="bca013b2-c163-4a0d-ad43-e6f1d3cda34b"

# App Configuration
export APP_NAME="portal-ai-music-frontend"
export STORAGE_ACCOUNT_NAME="portalaimusicstatic"

echo "🚀 Starting Azure deployment for Portal AI Music Frontend..."

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI is not installed. Please install it first:"
    echo "   brew install azure-cli"
    exit 1
fi

# Login with service principal
echo "🔐 Logging in to Azure with service principal..."
az login --service-principal \
    --username $SP_APP_ID \
    --password $SP_PASSWORD \
    --tenant $SP_TENANT

if [ $? -ne 0 ]; then
    echo "❌ Failed to login to Azure"
    exit 1
fi

# Set subscription
echo "📋 Setting subscription..."
az account set --subscription $SUBSCRIPTION_ID

# Check if resource group exists, create if not
echo "🏗️  Checking resource group..."
RG_EXISTS=$(az group exists --name $RESOURCE_GROUP)
if [ "$RG_EXISTS" = "false" ]; then
    echo "📦 Creating resource group: $RESOURCE_GROUP"
    az group create --name $RESOURCE_GROUP --location $LOCATION
else
    echo "✅ Resource group already exists: $RESOURCE_GROUP"
fi

# Create storage account for static website hosting
echo "💾 Creating storage account for static website..."
az storage account create \
    --name $STORAGE_ACCOUNT_NAME \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --sku Standard_LRS \
    --kind StorageV2 \
    --allow-blob-public-access true

if [ $? -ne 0 ]; then
    echo "⚠️  Storage account might already exist, continuing..."
fi

# Enable static website hosting
echo "🌐 Enabling static website hosting..."
az storage blob service-properties update \
    --account-name $STORAGE_ACCOUNT_NAME \
    --static-website \
    --404-document 404.html \
    --index-document index.html

# Get storage account key
echo "🔑 Getting storage account key..."
STORAGE_KEY=$(az storage account keys list \
    --account-name $STORAGE_ACCOUNT_NAME \
    --resource-group $RESOURCE_GROUP \
    --query '[0].value' -o tsv)

# Upload build files to blob storage
echo "📤 Uploading build files to Azure Blob Storage..."
az storage blob upload-batch \
    --account-name $STORAGE_ACCOUNT_NAME \
    --account-key $STORAGE_KEY \
    --destination '$web' \
    --source ./dist \
    --overwrite

# Get the static website URL
echo "🔗 Getting static website URL..."
WEBSITE_URL=$(az storage account show \
    --name $STORAGE_ACCOUNT_NAME \
    --resource-group $RESOURCE_GROUP \
    --query "primaryEndpoints.web" -o tsv)

echo ""
echo "🎉 Deployment completed successfully!"
echo "📱 Your Portal AI Music Frontend is now live at:"
echo "   $WEBSITE_URL"
echo ""
echo "📊 Azure Resources Created:"
echo "   • Resource Group: $RESOURCE_GROUP"
echo "   • Storage Account: $STORAGE_ACCOUNT_NAME"
echo "   • Static Website: Enabled"
echo ""
echo "💡 To update the site, just run this script again after building your changes."
