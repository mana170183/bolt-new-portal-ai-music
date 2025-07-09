#!/bin/bash

echo "🔧 Setting Environment Variables in Vercel Project"
echo "================================================="

# Load environment variables from .env file
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    exit 1
fi

# Extract variables
DATABASE_URL=$(grep "^DATABASE_URL=" .env | cut -d '=' -f2- | sed 's/^"//' | sed 's/"$//')
PRISMA_DATABASE_URL=$(grep "^PRISMA_DATABASE_URL=" .env | cut -d '=' -f2- | sed 's/^"//' | sed 's/"$//')
POSTGRES_URL=$(grep "^POSTGRES_URL=" .env | cut -d '=' -f2- | sed 's/^"//' | sed 's/"$//')

echo "Setting DATABASE_URL..."
vercel env add DATABASE_URL production <<< "$DATABASE_URL"

echo "Setting PRISMA_DATABASE_URL..."
vercel env add PRISMA_DATABASE_URL production <<< "$PRISMA_DATABASE_URL"

echo "Setting POSTGRES_URL..."
vercel env add POSTGRES_URL production <<< "$POSTGRES_URL"

echo "Setting NEXT_PUBLIC_API_URL..."
vercel env add NEXT_PUBLIC_API_URL production <<< "/api"

echo "✅ Environment variables set successfully!"
echo "🔄 Triggering new deployment..."

# Trigger a new deployment
vercel --prod

echo "✅ Deployment complete!"
