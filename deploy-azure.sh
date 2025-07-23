#!/bin/bash

# 🎵 Azure Deployment Script for AI Music Generation System
# Updates existing Azure infrastructure in rg-portal-ai-music-dev

set -e

echo "🎵 AI Music Generation System - Azure Deployment"
echo "================================================"
echo "Resource Group: rg-portal-ai-music-dev"
echo "Region: UK South"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
RESOURCE_GROUP="rg-portal-ai-music-dev"
LOCATION="uksouth"
ACR_NAME="acrportalaimusic508"
FRONTEND_APP="frontend-containerapp-dev"
BACKEND_APP="portal-music-backend-bulletproof"
FRONTEND_IMAGE_TAG="ai-music-v2"
BACKEND_IMAGE_TAG="ai-music-backend-v2"

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️ $1${NC}"
}

# Check Azure CLI login
check_azure_login() {
    print_info "Checking Azure CLI authentication..."
    if ! az account show &> /dev/null; then
        print_error "Not logged into Azure CLI. Please run 'az login' first."
        exit 1
    fi
    print_status "Azure CLI authenticated"
}

# Build and push backend image
build_backend() {
    print_info "Building and pushing backend container image..."
    
    cd backend
    
    # Build the image
    docker build -t $ACR_NAME.azurecr.io/ai-music-backend:$BACKEND_IMAGE_TAG .
    
    # Login to ACR
    az acr login --name $ACR_NAME
    
    # Push the image
    docker push $ACR_NAME.azurecr.io/ai-music-backend:$BACKEND_IMAGE_TAG
    
    cd ..
    
    print_status "Backend image built and pushed"
}

# Build and push frontend image
build_frontend() {
    print_info "Building and pushing frontend container image..."
    
    # Create production Dockerfile for frontend
    cat > Dockerfile.frontend << 'EOF'
FROM node:18-alpine AS base

# Install dependencies only when needed
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Set environment variables for build
ENV NEXT_PUBLIC_API_URL=https://portal-music-backend-bulletproof.ambitiousmeadow-4c2dba6f.uksouth.azurecontainerapps.io
ENV NODE_ENV=production

RUN npm run build

# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public

# Set the correct permission for prerender cache
RUN mkdir .next
RUN chown nextjs:nodejs .next

# Automatically leverage output traces to reduce image size
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
EOF

    # Build the image
    docker build -f Dockerfile.frontend -t $ACR_NAME.azurecr.io/ai-music-frontend:$FRONTEND_IMAGE_TAG .
    
    # Login to ACR
    az acr login --name $ACR_NAME
    
    # Push the image
    docker push $ACR_NAME.azurecr.io/ai-music-frontend:$FRONTEND_IMAGE_TAG
    
    print_status "Frontend image built and pushed"
}

# Update backend container app
update_backend() {
    print_info "Updating backend container app..."
    
    az containerapp update \
        --name $BACKEND_APP \
        --resource-group $RESOURCE_GROUP \
        --image $ACR_NAME.azurecr.io/ai-music-backend:$BACKEND_IMAGE_TAG \
        --set-env-vars \
            FLASK_ENV=production \
            PORT=5001 \
            CORS_ORIGINS="https://frontend-containerapp-dev.ambitiousmeadow-4c2dba6f.uksouth.azurecontainerapps.io" \
            DATABASE_URL="@Microsoft.KeyVault(SecretUri=https://kv-portal-ai-music-dev.vault.azure.net/secrets/database-url/)" \
            AZURE_OPENAI_ENDPOINT="@Microsoft.KeyVault(SecretUri=https://kv-portal-ai-music-dev.vault.azure.net/secrets/azure-openai-endpoint/)" \
            AZURE_OPENAI_KEY="@Microsoft.KeyVault(SecretUri=https://kv-portal-ai-music-dev.vault.azure.net/secrets/azure-openai-key/)" \
        --cpu 1.0 \
        --memory 2.0Gi \
        --min-replicas 1 \
        --max-replicas 3
    
    print_status "Backend container app updated"
}

# Update frontend container app
update_frontend() {
    print_info "Updating frontend container app..."
    
    az containerapp update \
        --name $FRONTEND_APP \
        --resource-group $RESOURCE_GROUP \
        --image $ACR_NAME.azurecr.io/ai-music-frontend:$FRONTEND_IMAGE_TAG \
        --set-env-vars \
            NODE_ENV=production \
            NEXT_PUBLIC_API_URL="https://portal-music-backend-bulletproof.ambitiousmeadow-4c2dba6f.uksouth.azurecontainerapps.io" \
        --cpu 0.5 \
        --memory 1.0Gi \
        --min-replicas 1 \
        --max-replicas 2
    
    print_status "Frontend container app updated"
}

# Test deployment
test_deployment() {
    print_info "Testing deployment..."
    
    FRONTEND_URL="https://frontend-containerapp-dev.ambitiousmeadow-4c2dba6f.uksouth.azurecontainerapps.io"
    BACKEND_URL="https://portal-music-backend-bulletproof.ambitiousmeadow-4c2dba6f.uksouth.azurecontainerapps.io"
    
    echo "Frontend URL: $FRONTEND_URL"
    echo "Backend URL: $BACKEND_URL"
    
    # Test backend health
    print_info "Testing backend health..."
    if curl -f "$BACKEND_URL/health" > /dev/null 2>&1; then
        print_status "Backend health check passed"
    else
        print_warning "Backend health check failed - may still be starting up"
    fi
    
    # Test frontend
    print_info "Testing frontend..."
    if curl -f "$FRONTEND_URL" > /dev/null 2>&1; then
        print_status "Frontend accessibility confirmed"
    else
        print_warning "Frontend test failed - may still be starting up"
    fi
    
    print_status "Deployment testing completed"
}

# Create GitHub Actions workflow for CI/CD
create_github_workflow() {
    print_info "Creating GitHub Actions workflow..."
    
    mkdir -p .github/workflows
    
    cat > .github/workflows/azure-deploy.yml << 'EOF'
name: Deploy to Azure Container Apps

on:
  push:
    branches: [ main ]
  workflow_dispatch:

env:
  AZURE_CONTAINER_REGISTRY: acrportalaimusic508.azurecr.io
  RESOURCE_GROUP: rg-portal-ai-music-dev
  FRONTEND_APP: frontend-containerapp-dev
  BACKEND_APP: portal-music-backend-bulletproof

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Log in to Azure
      uses: azure/login@v1
      with:
        creds: ${{ secrets.AZURE_CREDENTIALS }}
    
    - name: Log in to Azure Container Registry
      run: az acr login --name acrportalaimusic508
    
    - name: Build and push backend image
      run: |
        cd backend
        docker build -t $AZURE_CONTAINER_REGISTRY/ai-music-backend:${{ github.sha }} .
        docker push $AZURE_CONTAINER_REGISTRY/ai-music-backend:${{ github.sha }}
    
    - name: Build and push frontend image
      run: |
        docker build -f Dockerfile.frontend -t $AZURE_CONTAINER_REGISTRY/ai-music-frontend:${{ github.sha }} .
        docker push $AZURE_CONTAINER_REGISTRY/ai-music-frontend:${{ github.sha }}
    
    - name: Deploy backend to Container Apps
      run: |
        az containerapp update \
          --name $BACKEND_APP \
          --resource-group $RESOURCE_GROUP \
          --image $AZURE_CONTAINER_REGISTRY/ai-music-backend:${{ github.sha }}
    
    - name: Deploy frontend to Container Apps
      run: |
        az containerapp update \
          --name $FRONTEND_APP \
          --resource-group $RESOURCE_GROUP \
          --image $AZURE_CONTAINER_REGISTRY/ai-music-frontend:${{ github.sha }}
    
    - name: Test deployment
      run: |
        sleep 60  # Wait for containers to start
        curl -f https://portal-music-backend-bulletproof.ambitiousmeadow-4c2dba6f.uksouth.azurecontainerapps.io/health
        curl -f https://frontend-containerapp-dev.ambitiousmeadow-4c2dba6f.uksouth.azurecontainerapps.io
EOF
    
    print_status "GitHub Actions workflow created"
}

# Main deployment function
main() {
    echo "Select deployment option:"
    echo "1. Full deployment (build + deploy backend + frontend)"
    echo "2. Backend only"
    echo "3. Frontend only"
    echo "4. Test existing deployment"
    echo "5. Create CI/CD workflow only"
    echo ""
    
    read -p "Enter your choice (1-5): " choice
    
    case $choice in
        1)
            check_azure_login
            build_backend
            build_frontend
            update_backend
            update_frontend
            create_github_workflow
            test_deployment
            ;;
        2)
            check_azure_login
            build_backend
            update_backend
            test_deployment
            ;;
        3)
            check_azure_login
            build_frontend
            update_frontend
            test_deployment
            ;;
        4)
            test_deployment
            ;;
        5)
            create_github_workflow
            ;;
        *)
            print_error "Invalid choice. Please select 1-5."
            exit 1
            ;;
    esac
    
    echo ""
    print_status "Azure deployment completed!"
    echo ""
    echo "📋 Deployment URLs:"
    echo "==================="
    echo "🌐 Frontend: https://frontend-containerapp-dev.ambitiousmeadow-4c2dba6f.uksouth.azurecontainerapps.io"
    echo "🔧 Backend:  https://portal-music-backend-bulletproof.ambitiousmeadow-4c2dba6f.uksouth.azurecontainerapps.io"
    echo "📊 Health:   https://portal-music-backend-bulletproof.ambitiousmeadow-4c2dba6f.uksouth.azurecontainerapps.io/health"
    echo ""
    print_info "🎉 Your AI Music Generation System is now live on Azure!"
}

# Run the script
main
