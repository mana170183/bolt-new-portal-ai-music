#!/bin/bash

echo "🔧 Portal AI Music - Manual Vercel Deployment Script"
echo "==============================================="

echo "📦 Step 1: Installing dependencies..."
npm install

echo "🔄 Step 2: Generating Prisma client..."
npx prisma generate

echo "🏗️ Step 3: Building the Next.js application..."
npm run build

echo "🚀 Step 4: Deploying to Vercel..."
echo "Deploying with environment variables from .env file..."

# Extract environment variables from .env file
if [ -f .env ]; then
  echo "Found .env file, extracting variables..."
  
  # Create a temporary array of environment variables
  ENV_VARS=""
  
  # Read the .env file line by line
  while IFS= read -r line; do
    # Skip comments and empty lines
    if [[ $line =~ ^\#.*$ || -z $line ]]; then
      continue
    fi
    
    # Extract variable name and value
    if [[ $line =~ ^([A-Za-z0-9_]+)=(.*)$ ]]; then
      NAME=${BASH_REMATCH[1]}
      VALUE=${BASH_REMATCH[2]}
      
      # Add to environment variables string (properly quoted)
      ENV_VARS="$ENV_VARS --env $NAME=\"$VALUE\""
    fi
  done < .env
  
  # Deploy with the extracted environment variables
  echo "Deploying with environment variables..."
  eval "vercel --prod $ENV_VARS"
else
  echo "No .env file found, deploying without environment variables..."
  vercel --prod
fi

echo "✅ Deployment process completed!"
echo "Check your Vercel dashboard for deployment status."
