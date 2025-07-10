#!/bin/bash

# Portal AI Music - Repository Transfer Script
# Transfer all branches to webappdev1701 GitHub account

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🚀 Portal AI Music - Repository Transfer${NC}"
echo "========================================"

# New repository details
NEW_OWNER="webappdev1701"
REPO_NAME="bolt-new-portal-ai-music"
NEW_REPO_URL="https://github.com/${NEW_OWNER}/${REPO_NAME}.git"

echo -e "${YELLOW}📋 Prerequisites:${NC}"
echo "1. ✅ Login to GitHub as webappdev1701 (restrovision@gmail.com)"
echo "2. ✅ Create new repository: ${NEW_REPO_URL}"
echo "3. ✅ Make repository public (for Vercel free tier)"
echo ""

read -p "Have you created the new repository? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Please create the repository first and run this script again."
    exit 1
fi

echo -e "${BLUE}📦 Adding new remote...${NC}"
git remote add new-origin $NEW_REPO_URL

echo -e "${BLUE}📤 Pushing all branches...${NC}"

# Get all local branches
branches=$(git branch | sed 's/\* //' | sed 's/  //')

for branch in $branches; do
    echo -e "${BLUE}Pushing branch: $branch${NC}"
    git push new-origin $branch
done

echo -e "${BLUE}🏷️ Pushing all tags...${NC}"
git push new-origin --tags

echo -e "${GREEN}✅ Repository transfer completed!${NC}"
echo ""
echo -e "${YELLOW}📋 Next steps:${NC}"
echo "1. Update remote origin to new repository:"
echo "   git remote remove origin"
echo "   git remote rename new-origin origin"
echo ""
echo "2. Verify all branches transferred:"
echo "   Visit: ${NEW_REPO_URL}"
echo ""
echo "3. Continue with deployment setup using stage branch"
echo ""

echo -e "${BLUE}🔗 New Repository URL: ${NEW_REPO_URL}${NC}"
