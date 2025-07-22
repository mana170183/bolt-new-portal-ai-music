#!/bin/bash
# Rollback script to restore production-ready backend
# Usage: ./rollback-to-production-backend.sh

echo "🔄 Rolling back to production-ready backend..."

# Check if we're in the right directory
if [ ! -d "backend-complete-fix" ]; then
    echo "❌ Error: backend-complete-fix directory not found. Run this from the project root."
    exit 1
fi

# Backup current backend if it exists
if [ -d "backend" ]; then
    echo "📦 Backing up current backend to backend-backup-$(date +%Y%m%d-%H%M%S)..."
    cp -r backend "backend-backup-$(date +%Y%m%d-%H%M%S)"
fi

# Restore production backend
echo "🚀 Restoring production-ready backend from backend-complete-fix..."
cp backend-complete-fix/app.py backend/
cp backend-complete-fix/requirements.txt backend/
cp backend-complete-fix/Dockerfile backend/

echo "✅ Production backend restored successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Build and deploy the backend image:"
echo "   cd backend && docker build -t portal-backend-audio-proxy ."
echo ""
echo "2. If using Azure, push to registry:"
echo "   az acr login --name acrportalaimusic508"
echo "   docker tag portal-backend-audio-proxy acrportalaimusic508.azurecr.io/portal-backend-audio-proxy:rollback"
echo "   docker push acrportalaimusic508.azurecr.io/portal-backend-audio-proxy:rollback"
echo ""
echo "3. Update Azure Container App:"
echo "   az containerapp update --name portal-music-backend-bulletproof --resource-group dev --image acrportalaimusic508.azurecr.io/portal-backend-audio-proxy:rollback"
echo ""
echo "🎯 Backend rollback complete! The production-ready version is now active."
