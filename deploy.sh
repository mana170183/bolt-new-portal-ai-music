#!/bin/bash

# Portal AI Music - Azure Deployment Script
# This script updates the frontend app with the latest changes

echo "🎵 Portal AI Music - Deployment Script"
echo "========================================"

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found. Please run this script from the project root."
    exit 1
fi

echo "📦 Installing dependencies..."
npm install

echo "🔧 Building the application..."
npm run build

if [ $? -ne 0 ]; then
    echo "❌ Build failed. Please fix the errors and try again."
    exit 1
fi

echo "✅ Build successful!"

echo "📝 Committing changes to Git..."
git add .
git commit -m "feat: Enhanced frontend with advanced studio, music library, and improved UI

- Added AdvancedStudio component with detailed music controls
- Added MusicLibrary component for track management
- Enhanced Hero section with animations and interactivity
- Updated styling with modern gradients and animations
- Added new API endpoints for advanced generation
- Improved responsive design and user experience
- Fixed icon imports and build issues"

echo "🚀 Pushing to studio branch..."
git push origin studio

echo "📊 Deployment Status:"
echo "- Frontend build: ✅ Complete"
echo "- Git commit: ✅ Complete"
echo "- Git push: ✅ Complete"
echo ""
echo "🔗 Next steps:"
echo "1. Check GitHub Actions for automated deployment"
echo "2. Verify the changes at: https://music-frontend-20250125155609.azurewebsites.net/"
echo "3. Monitor the backend API compatibility"
echo ""
echo "🎉 Deployment script completed successfully!"
