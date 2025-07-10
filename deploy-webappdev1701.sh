#!/bin/bash

# Portal AI Music - webappdev1701 Quick Deployment Script
# Automated deployment for restrovision@gmail.com setup

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🎵 Portal AI Music - webappdev1701 Deployment${NC}"
echo "=============================================="
echo "Account: webappdev1701 (restrovision@gmail.com)"
echo "Branch: stage (free deployment)"
echo ""

# Check if we're on the right branch
current_branch=$(git branch --show-current)
if [ "$current_branch" != "stage" ]; then
    echo -e "${YELLOW}⚠️ Switching to stage branch...${NC}"
    git checkout stage
fi

# Check for required tools
check_tools() {
    echo -e "${BLUE}📋 Checking required tools...${NC}"
    
    if ! command -v node &> /dev/null; then
        echo -e "${RED}❌ Node.js not found. Please install Node.js 18+${NC}"
        exit 1
    fi
    
    if ! command -v npm &> /dev/null; then
        echo -e "${RED}❌ npm not found. Please install npm${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Tools check passed${NC}"
}

# Install CLI tools
install_clis() {
    echo -e "${BLUE}🔧 Installing deployment CLIs...${NC}"
    
    # Railway CLI
    if ! command -v railway &> /dev/null; then
        echo "Installing Railway CLI..."
        npm install -g @railway/cli
    fi
    
    # Vercel CLI
    if ! command -v vercel &> /dev/null; then
        echo "Installing Vercel CLI..."
        npm install -g vercel
    fi
    
    echo -e "${GREEN}✅ CLI tools installed${NC}"
}

# Setup environment files
setup_env() {
    echo -e "${BLUE}📝 Setting up environment files...${NC}"
    
    # Frontend environment
    if [ ! -f ".env.local" ]; then
        cp .env.local.example .env.local
        echo -e "${YELLOW}⚠️ Please edit .env.local with your actual API keys${NC}"
    fi
    
    # Backend environment
    if [ ! -f "backend-free/.env" ]; then
        cp backend-free/.env.example backend-free/.env
        echo -e "${YELLOW}⚠️ Please edit backend-free/.env with your actual API keys${NC}"
    fi
    
    echo -e "${GREEN}✅ Environment files ready${NC}"
}

# Deploy backend to Railway
deploy_backend() {
    echo -e "${BLUE}🚂 Deploying backend to Railway...${NC}"
    
    cd backend-free
    
    # Check if Railway is configured
    if [ ! -f "railway.json" ]; then
        echo -e "${RED}❌ Railway configuration missing${NC}"
        exit 1
    fi
    
    # Login to Railway (this will open browser)
    echo -e "${YELLOW}🔐 Please login to Railway with your GitHub account (webappdev1701)${NC}"
    railway login
    
    # Initialize or deploy
    if [ ! -f ".railway" ]; then
        echo "Initializing Railway project..."
        railway init
    fi
    
    echo "Deploying to Railway..."
    railway up
    
    # Get the deployment URL
    railway_url=$(railway status | grep "Deployment URL" | awk '{print $3}' || echo "")
    if [ -n "$railway_url" ]; then
        echo -e "${GREEN}✅ Backend deployed to: $railway_url${NC}"
        echo "REACT_APP_API_URL=$railway_url" >> ../.env.local
    fi
    
    cd ..
}

# Deploy frontend to Vercel
deploy_frontend() {
    echo -e "${BLUE}⚡ Deploying frontend to Vercel...${NC}"
    
    # Login to Vercel
    echo -e "${YELLOW}🔐 Please login to Vercel with: restrovision@gmail.com${NC}"
    vercel login
    
    # Deploy
    echo "Deploying to Vercel..."
    vercel --prod
    
    echo -e "${GREEN}✅ Frontend deployed successfully${NC}"
}

# Test deployment
test_deployment() {
    echo -e "${BLUE}🧪 Testing deployment...${NC}"
    
    # Get Railway URL from environment
    if [ -f ".env.local" ]; then
        api_url=$(grep REACT_APP_API_URL .env.local | cut -d'=' -f2)
        if [ -n "$api_url" ]; then
            echo "Testing API at: $api_url"
            curl -f "$api_url/health" && echo -e "${GREEN}✅ API health check passed${NC}" || echo -e "${RED}❌ API health check failed${NC}"
        fi
    fi
}

# Show final instructions
show_instructions() {
    echo ""
    echo -e "${GREEN}🎉 Deployment completed!${NC}"
    echo ""
    echo -e "${YELLOW}📋 Important next steps:${NC}"
    echo "1. Set up Supabase:"
    echo "   - Go to https://supabase.com"
    echo "   - Create project: portal-ai-music"
    echo "   - Run SQL schema from DEPLOYMENT-WEBAPPDEV1701.md"
    echo "   - Update .env files with Supabase keys"
    echo ""
    echo "2. Get Hugging Face API key:"
    echo "   - Go to https://huggingface.co/settings/tokens"
    echo "   - Create token with 'Read' permissions"
    echo "   - Add to backend-free/.env"
    echo ""
    echo "3. Update environment variables:"
    echo "   - Railway: railway variables set KEY=value"
    echo "   - Vercel: vercel env add KEY"
    echo ""
    echo "4. Test your app:"
    echo "   - ./test-free-deployment.sh [your-api-url]"
    echo ""
    echo -e "${BLUE}📖 See DEPLOYMENT-WEBAPPDEV1701.md for detailed instructions${NC}"
}

# Main deployment process
main() {
    check_tools
    echo ""
    
    install_clis
    echo ""
    
    setup_env
    echo ""
    
    echo -e "${YELLOW}📋 Ready to deploy? This will:${NC}"
    echo "1. Deploy backend to Railway"
    echo "2. Deploy frontend to Vercel"
    echo "3. Configure basic settings"
    echo ""
    read -p "Continue? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Deployment cancelled."
        exit 1
    fi
    
    deploy_backend
    echo ""
    
    deploy_frontend
    echo ""
    
    test_deployment
    echo ""
    
    show_instructions
}

# Run deployment
main "$@"
