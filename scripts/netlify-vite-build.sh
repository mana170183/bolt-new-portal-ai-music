#!/bin/bash

echo "Starting Netlify Vite build process..."

# Generate Prisma client
echo "Generating Prisma client..."
npx prisma generate

# Build with Vite
echo "Building with Vite..."
npm run legacy:build

# Create Netlify redirects file if it doesn't exist in dist
if [ ! -f "dist/_redirects" ]; then
  echo "Creating _redirects file in dist directory..."
  cp public/_redirects dist/ || echo "# Map API routes to Netlify Functions
/api/health                /.netlify/functions/health                200
/api/genres                /.netlify/functions/genres                200
/api/moods                 /.netlify/functions/moods                 200
/api/user/quota            /.netlify/functions/user-quota            200
/api/auth/token            /.netlify/functions/auth-token            200
/api/instruments           /.netlify/functions/instruments           200
/api/composition-templates /.netlify/functions/composition-templates 200
/api/tracks                /.netlify/functions/tracks                200
/api/generate-music        /.netlify/functions/generate-music        200
/api/generate-enhanced-music /.netlify/functions/generate-enhanced-music 200

# SPA Routing - serve index.html for all routes
/*                         /index.html                               200" > dist/_redirects
fi

echo "Build complete!"
