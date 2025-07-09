#!/bin/bash

echo "🚀 Deploying Portal AI Music to Vercel with Prisma Database"
echo "============================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if .env file exists
if [ ! -f .env ]; then
    print_error ".env file not found! Please create it with your database URLs."
    exit 1
fi

print_status "Found .env file"

# Extract environment variables from .env
export $(grep -v '^#' .env | xargs)

# Check required environment variables
if [ -z "$PRISMA_DATABASE_URL" ] || [ -z "$POSTGRES_URL" ]; then
    print_error "Missing required database URLs in .env file"
    print_warning "Required: PRISMA_DATABASE_URL, POSTGRES_URL"
    exit 1
fi

print_status "Environment variables loaded"

# Step 1: Generate Prisma Client
print_status "Generating Prisma client..."
npx prisma generate

if [ $? -ne 0 ]; then
    print_error "Failed to generate Prisma client"
    exit 1
fi

# Step 2: Build the project locally to check for errors
print_status "Building project locally..."
npm run build

if [ $? -ne 0 ]; then
    print_error "Local build failed"
    exit 1
fi

print_status "Local build successful"

# Step 3: Deploy to Vercel with environment variables
print_status "Deploying to Vercel..."

vercel --prod \
    --env DATABASE_URL="$DATABASE_URL" \
    --env PRISMA_DATABASE_URL="$PRISMA_DATABASE_URL" \
    --env POSTGRES_URL="$POSTGRES_URL" \
    --env NEXT_PUBLIC_API_URL="/api"

if [ $? -eq 0 ]; then
    print_status "Deployment successful!"
    echo ""
    print_status "Next steps:"
    echo "1. Check your Vercel dashboard for the deployment URL"
    echo "2. Test the database connection: https://your-app.vercel.app/api/test-db"
    echo "3. Test the instruments API: https://your-app.vercel.app/api/instruments"
else
    print_error "Deployment failed"
    exit 1
fi
