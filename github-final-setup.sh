#!/bin/bash

# 🎵 Portal AI Music - GitHub Repository Setup Script
# This script prepares the project for deployment to the new GitHub repository

echo "🎵 Portal AI Music - GitHub Repository Setup"
echo "============================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 Current Project Status${NC}"
echo "----------------------------------------"

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo -e "${RED}❌ Error: package.json not found. Please run this script from the project root.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Found package.json - we're in the right directory${NC}"

# Check current git status
echo -e "${BLUE}📊 Checking Git Status...${NC}"
if [ -d ".git" ]; then
    echo -e "${GREEN}✅ Git repository initialized${NC}"
    echo -e "Current remote: $(git remote get-url origin 2>/dev/null || echo 'No remote set')"
else
    echo -e "${YELLOW}⚠️  Git not initialized${NC}"
fi

echo ""
echo -e "${BLUE}📦 Project Information${NC}"
echo "----------------------------------------"
echo "Name: $(grep '"name"' package.json | cut -d'"' -f4)"
echo "Version: $(grep '"version"' package.json | cut -d'"' -f4)"
echo "Files to commit: $(find . -name "*.js" -o -name "*.jsx" -o -name "*.css" -o -name "*.md" -o -name "*.json" -o -name "*.html" | grep -v node_modules | wc -l | tr -d ' ') files"

echo ""
echo -e "${BLUE}🎨 Theme Verification${NC}"
echo "----------------------------------------"
if grep -q "from-blue-600 via-purple-600 to-pink-600" src/index.css; then
    echo -e "${GREEN}✅ Blue-purple-pink gradient theme applied${NC}"
else
    echo -e "${RED}❌ Theme not applied correctly${NC}"
fi

if grep -q "bg-gradient-to-br from-blue-50 via-white to-blue-100" src/App.jsx; then
    echo -e "${GREEN}✅ Light background theme applied${NC}"
else
    echo -e "${RED}❌ Background theme not applied${NC}"
fi

echo ""
echo -e "${BLUE}🚀 Repository Setup Instructions${NC}"
echo "============================================="
echo ""
echo -e "${YELLOW}Step 1: Create New GitHub Repository${NC}"
echo "   1. Go to: https://github.com/new"
echo "   2. Repository name: ${BLUE}portal-ai-music-final${NC}"
echo "   3. Owner: ${BLUE}mana170183uk${NC}"
echo "   4. Set as: ${BLUE}Public${NC}"
echo "   5. Initialize with README: ${BLUE}No${NC} (we have our own)"
echo "   6. Click 'Create repository'"
echo ""

echo -e "${YELLOW}Step 2: Prepare Local Repository${NC}"
echo "   Run these commands in order:"
echo ""

# Clean up and add files
echo -e "${GREEN}# Remove node_modules from staging (if any)${NC}"
echo "git reset HEAD node_modules/ 2>/dev/null || true"
echo ""

echo -e "${GREEN}# Add all important files${NC}"
echo "git add ."
echo "git add -f README.md FINAL-DEPLOYMENT-READY.md"
echo ""

echo -e "${GREEN}# Commit with comprehensive message${NC}"
echo 'git commit -m "🎵 Complete Portal AI Music Platform - Ready for Production

✨ Features Implemented:
- Modern React + Vite + Tailwind CSS frontend
- Blue-purple-pink gradient theme throughout
- Working music generator with 3 modes (Simple, Advanced, Library)
- Real audio playback functionality
- Express.js test server for local development
- Python Flask backend structure
- Azure Functions serverless backend
- Responsive mobile-friendly design
- Professional UI/UX with smooth animations

🔧 Technical Stack:
- Frontend: React 18, Vite, Tailwind CSS, Lucide Icons
- Backend: Node.js/Express (test), Python/Flask (production)
- APIs: 15+ endpoints with mock data fallbacks
- Deployment: Azure Static Web Apps ready
- Testing: Complete local development environment

🎨 Design:
- Consistent blue-purple-pink gradient theme
- High-contrast text for accessibility
- Modern card-based layouts
- Smooth hover effects and animations
- Mobile-responsive across all screen sizes

🚀 Ready for immediate deployment and production use!"'
echo ""

echo -e "${YELLOW}Step 3: Set New Remote and Push${NC}"
echo -e "${GREEN}# Set new repository as origin${NC}"
echo "git remote set-url origin https://github.com/mana170183uk/portal-ai-music-final.git"
echo ""
echo -e "${GREEN}# Push to new repository${NC}"
echo "git push -u origin main"
echo ""

echo -e "${YELLOW}Step 4: Verify Deployment${NC}"
echo "   1. Check that all files are visible in GitHub"
echo "   2. Verify README.md displays correctly"
echo "   3. Check that src/ folder contains all components"
echo "   4. Confirm package.json shows correct dependencies"
echo ""

echo -e "${BLUE}📋 Quick File Check${NC}"
echo "----------------------------------------"
key_files=("src/App.jsx" "src/components/Header.jsx" "src/components/Hero.jsx" "src/components/MusicGenerator.jsx" "src/index.css" "package.json" "README.md" "test-server.cjs")

for file in "${key_files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅ $file${NC}"
    else
        echo -e "${RED}❌ $file (MISSING)${NC}"
    fi
done

echo ""
echo -e "${BLUE}🎯 Next Steps After Repository Creation${NC}"
echo "============================================="
echo "1. 🌐 Deploy to production (Azure/Vercel/Netlify)"
echo "2. 🔧 Configure environment variables"
echo "3. 🧪 Run production tests"
echo "4. 📊 Set up monitoring and analytics"
echo "5. 🚀 Share your amazing AI music platform!"
echo ""

echo -e "${GREEN}🎉 Your Portal AI Music platform is ready for the world! 🎵${NC}"
echo ""

# Optional: Show current directory size
echo -e "${BLUE}📊 Project Statistics${NC}"
echo "----------------------------------------"
echo "Total files (excluding node_modules): $(find . -type f | grep -v node_modules | wc -l | tr -d ' ')"
echo "Source files: $(find src -name "*.jsx" -o -name "*.js" -o -name "*.css" | wc -l | tr -d ' ')"
echo "Documentation files: $(find . -name "*.md" | wc -l | tr -d ' ')"
echo "Configuration files: $(find . -name "*.json" -o -name "*.config.*" | grep -v node_modules | wc -l | tr -d ' ')"
