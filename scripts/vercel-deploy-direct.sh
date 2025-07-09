#!/bin/bash
# This script will directly deploy to Vercel using environment variables from .env
# Run this script from the project root directory

echo "🚀 Deploying to Vercel with environment variables from .env..."

# Function to extract value from .env file
get_env_var() {
  local var_name=$1
  grep -E "^${var_name}=" .env | cut -d '=' -f2-
}

# Extract database URLs
DATABASE_URL=$(get_env_var "DATABASE_URL")
PRISMA_DATABASE_URL=$(get_env_var "PRISMA_DATABASE_URL")
POSTGRES_URL=$(get_env_var "POSTGRES_URL")

# Check if the variables were found
if [ -z "$DATABASE_URL" ] || [ -z "$PRISMA_DATABASE_URL" ] || [ -z "$POSTGRES_URL" ]; then
  echo "❌ Error: Could not find all required database URLs in .env file"
  exit 1
fi

echo "✅ Found database URLs in .env file"

# Deploy using extracted environment variables
vercel --prod \
  --env DATABASE_URL="$DATABASE_URL" \
  --env PRISMA_DATABASE_URL="$PRISMA_DATABASE_URL" \
  --env POSTGRES_URL="$POSTGRES_URL" \
  --build-env NEXT_PUBLIC_API_URL="/api"

echo "✅ Deployment command completed!"
