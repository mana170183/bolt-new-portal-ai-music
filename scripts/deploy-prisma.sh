#!/bin/bash

# This script helps with deploying Prisma to Vercel
# Usage: ./scripts/deploy-prisma.sh

echo "🚀 Starting Prisma Vercel Deployment Helper..."

# Step 1: Generate Prisma Client
echo "📦 Generating Prisma Client..."
npx prisma generate

# Step 2: Deploy to Vercel
echo "🔄 Deploying to Vercel..."
vercel --prod

# Step 3: Test database connection
echo "🔍 Testing database connection (once deployed)..."
echo "Visit your-deployed-url.vercel.app/api/test-db to test the connection"

echo "✅ Deployment process completed!"
