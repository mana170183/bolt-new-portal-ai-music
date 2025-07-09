#!/bin/bash

# This script will commit and push all the Prisma deployment fixes

echo "🚀 Committing and pushing Prisma deployment fixes..."

# Add all changes
git add .

# Commit the changes
git commit -m "Fix Prisma deployment issues for Vercel"

# Push to the default branch
git push

echo "✅ Changes pushed! Now you can deploy to Vercel with:"
echo "npm run deploy"
echo ""
echo "Or use Vercel CLI directly:"
echo "vercel --prod"
echo ""
echo "After deploying, test your API endpoints:"
echo "https://your-app.vercel.app/api/test-db"
echo "https://your-app.vercel.app/api/instruments"
echo ""
echo "See docs/PRISMA_DEPLOYMENT_FIX.md and docs/VERCEL_DEPLOYMENT.md for details."
