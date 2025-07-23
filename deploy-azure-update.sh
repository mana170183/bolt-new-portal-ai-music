#!/bin/bash

# Azure Deployment Script - Update Resources with Latest Changes
# This script deploys all recent changes to existing Azure resources

set -e

echo "🚀 Azure Deployment - Updating Existing Resources"
echo "=================================================="

# Azure Configuration
SUBSCRIPTION_ID="f165aa7d-ea02-4be9-aa0c-fad453084a9f"
RESOURCE_GROUP="rg-portal-ai-music-dev"
SERVICE_PRINCIPAL_NAME="portalaimusic"
CLIENT_ID="6a069624-67ed-4bfe-b4e6-301f6e02a853"
TENANT_ID="bca013b2-c163-4a0d-ad43-e6f1d3cda34b"
CLIENT_SECRET="Q9a8Q~XRiQ3hKIHKUCFn6ka.jZ3udfNwyI.s2aC5"

# Resource Names
CONTAINER_REGISTRY="acrportalaimusic508"
CONTAINER_APP_ENV="cae-portal-ai-music-dev"
BACKEND_CONTAINER_APP="portal-music-backend-new"
FRONTEND_CONTAINER_APP="frontend-containerapp-dev"
BACKEND_IMAGE_NAME="portal-ai-music-backend"
FRONTEND_IMAGE_NAME="portal-ai-music-frontend"
TAG="latest"

echo "📋 Configuration:"
echo "   Subscription: $SUBSCRIPTION_ID"
echo "   Resource Group: $RESOURCE_GROUP"
echo "   Container Registry: $CONTAINER_REGISTRY"
echo "   Backend Container App: $BACKEND_CONTAINER_APP"
echo "   Frontend Container App: $FRONTEND_CONTAINER_APP"
echo ""

# Step 1: Login to Azure using Service Principal
echo "🔑 Logging in to Azure with Service Principal..."
az login --service-principal \
    --username "$CLIENT_ID" \
    --password "$CLIENT_SECRET" \
    --tenant "$TENANT_ID"

if [ $? -eq 0 ]; then
    echo "✅ Successfully logged in to Azure"
else
    echo "❌ Failed to login to Azure"
    exit 1
fi

# Step 2: Set subscription
echo "📦 Setting subscription..."
az account set --subscription "$SUBSCRIPTION_ID"

if [ $? -eq 0 ]; then
    echo "✅ Subscription set successfully"
else
    echo "❌ Failed to set subscription"
    exit 1
fi

# Step 3: Login to Container Registry
echo "🐳 Logging in to Container Registry..."
az acr login --name "$CONTAINER_REGISTRY"

if [ $? -eq 0 ]; then
    echo "✅ Successfully logged in to Container Registry"
else
    echo "❌ Failed to login to Container Registry"
    exit 1
fi

# Step 4: Build and Push Updated Docker Images
echo "🔨 Building updated Docker images..."

# Create optimized Dockerfile for backend
cat > Dockerfile.backend << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libffi-dev \
    libssl-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY backend/ .

# Create necessary directories
RUN mkdir -p generated_audio/stems logs

# Set environment variables
ENV PYTHONPATH=/app
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PORT=8000

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/check || exit 1

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120", "app:app"]
EOF

# Create optimized Dockerfile for frontend
cat > Dockerfile.frontend << 'EOF'
# Build stage
FROM node:18-alpine as builder

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci --only=production

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM node:18-alpine as runner

WORKDIR /app

# Create a non-root user
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy built application
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

# Set correct permissions
RUN chown -R nextjs:nodejs /app
USER nextjs

# Expose port
EXPOSE 3000

ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000 || exit 1

# Start the application
CMD ["node", "server.js"]
EOF

# Build backend image
echo "🔨 Building backend image..."
docker build -f Dockerfile.backend -t "$CONTAINER_REGISTRY.azurecr.io/$BACKEND_IMAGE_NAME:$TAG" .

if [ $? -eq 0 ]; then
    echo "✅ Backend Docker image built successfully"
else
    echo "❌ Failed to build backend Docker image"
    exit 1
fi

# Build frontend image
echo "🔨 Building frontend image..."
docker build -f Dockerfile.frontend -t "$CONTAINER_REGISTRY.azurecr.io/$FRONTEND_IMAGE_NAME:$TAG" .

if [ $? -eq 0 ]; then
    echo "✅ Frontend Docker image built successfully"
else
    echo "❌ Failed to build frontend Docker image"
    exit 1
fi

# Step 5: Push images to registry
echo "📤 Pushing images to Azure Container Registry..."

# Push backend image
echo "📤 Pushing backend image..."
docker push "$CONTAINER_REGISTRY.azurecr.io/$BACKEND_IMAGE_NAME:$TAG"

if [ $? -eq 0 ]; then
    echo "✅ Backend image pushed successfully"
else
    echo "❌ Failed to push backend image"
    exit 1
fi

# Push frontend image
echo "📤 Pushing frontend image..."
docker push "$CONTAINER_REGISTRY.azurecr.io/$FRONTEND_IMAGE_NAME:$TAG"

if [ $? -eq 0 ]; then
    echo "✅ Frontend image pushed successfully"
else
    echo "❌ Failed to push frontend image"
    exit 1
fi

# Step 6: Update Container Apps with latest images
echo "🔄 Updating Container Apps with latest images..."

# Update backend container app
echo "🔄 Updating backend container app..."
az containerapp update \
    --name "$BACKEND_CONTAINER_APP" \
    --resource-group "$RESOURCE_GROUP" \
    --image "$CONTAINER_REGISTRY.azurecr.io/$BACKEND_IMAGE_NAME:$TAG" \
    --cpu 1.0 \
    --memory 2Gi \
    --min-replicas 1 \
    --max-replicas 3 \
    --env-vars \
        "FLASK_ENV=production" \
        "PYTHONPATH=/app" \
        "PORT=8000"

if [ $? -eq 0 ]; then
    echo "✅ Backend Container App updated successfully"
else
    echo "❌ Failed to update Backend Container App"
    exit 1
fi

# Update frontend container app
echo "🔄 Updating frontend container app..."
az containerapp update \
    --name "$FRONTEND_CONTAINER_APP" \
    --resource-group "$RESOURCE_GROUP" \
    --image "$CONTAINER_REGISTRY.azurecr.io/$FRONTEND_IMAGE_NAME:$TAG" \
    --cpu 0.5 \
    --memory 1Gi \
    --min-replicas 1 \
    --max-replicas 2 \
    --env-vars \
        "NEXT_PUBLIC_API_URL=https://portal-music-backend-new.ambitiousmeadow-4c2dba6f.uksouth.azurecontainerapps.io" \
        "PORT=3000" \
        "HOSTNAME=0.0.0.0"

if [ $? -eq 0 ]; then
    echo "✅ Frontend Container App updated successfully"
else
    echo "❌ Failed to update Frontend Container App"
    exit 1
fi

# Step 7: Verify deployment
echo "🔍 Verifying deployment..."
sleep 45  # Wait for deployment to stabilize

# Get the backend app URL
BACKEND_URL=$(az containerapp show \
    --name "$BACKEND_CONTAINER_APP" \
    --resource-group "$RESOURCE_GROUP" \
    --query "properties.configuration.ingress.fqdn" \
    --output tsv)

# Get the frontend app URL
FRONTEND_URL=$(az containerapp show \
    --name "$FRONTEND_CONTAINER_APP" \
    --resource-group "$RESOURCE_GROUP" \
    --query "properties.configuration.ingress.fqdn" \
    --output tsv)

if [ -n "$BACKEND_URL" ] && [ -n "$FRONTEND_URL" ]; then
    FULL_BACKEND_URL="https://$BACKEND_URL"
    FULL_FRONTEND_URL="https://$FRONTEND_URL"
    
    echo "📍 Backend URL: $FULL_BACKEND_URL"
    echo "📍 Frontend URL: $FULL_FRONTEND_URL"
    
    # Test the backend health endpoint
    echo "🏥 Testing backend health endpoint..."
    HEALTH_RESPONSE=$(curl -s -w "%{http_code}" "$FULL_BACKEND_URL/api/check")
    HTTP_CODE="${HEALTH_RESPONSE: -3}"
    
    # Test the frontend
    echo "🌐 Testing frontend endpoint..."
    FRONTEND_RESPONSE=$(curl -s -w "%{http_code}" "$FULL_FRONTEND_URL")
    FRONTEND_HTTP_CODE="${FRONTEND_RESPONSE: -3}"
    
    SUCCESS=true
    
    if [ "$HTTP_CODE" = "200" ]; then
        echo "✅ Backend health check passed"
    else
        echo "❌ Backend health check failed (HTTP $HTTP_CODE)"
        SUCCESS=false
    fi
    
    if [ "$FRONTEND_HTTP_CODE" = "200" ]; then
        echo "✅ Frontend health check passed"
    else
        echo "❌ Frontend health check failed (HTTP $FRONTEND_HTTP_CODE)"
        SUCCESS=false
    fi
    
    if [ "$SUCCESS" = true ]; then
        echo "🎉 Deployment completed successfully!"
        echo ""
        echo "📊 Deployment Summary:"
        echo "===================="
        echo "✅ Service Principal Authentication: SUCCESS"
        echo "✅ Docker Images Build: SUCCESS"
        echo "✅ Container Registry Push: SUCCESS"
        echo "✅ Container Apps Update: SUCCESS"
        echo "✅ Health Checks: SUCCESS"
        echo ""
        echo "🔗 Access Points:"
        echo "   Frontend: $FULL_FRONTEND_URL"
        echo "   Backend API: $FULL_BACKEND_URL"
        echo "   Health Check: $FULL_BACKEND_URL/api/check"
        echo "   Music Styles: $FULL_BACKEND_URL/api/music-styles"
        echo "   Instruments: $FULL_BACKEND_URL/api/instruments"
        echo "   Advanced Generation: $FULL_BACKEND_URL/api/advanced-generate"
        echo ""
        echo "🎵 Your AI Music Portal is now fully updated and running!"
    else
        echo "⚠️ Deployment completed but some services may not be healthy"
    fi
else
    echo "❌ Could not retrieve app URLs"
    exit 1
fi

# Cleanup
rm -f Dockerfile.backend Dockerfile.frontend

echo ""
echo "🏁 Deployment script completed!"
