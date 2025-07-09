#!/bin/bash

echo "Starting Netlify Vite build process..."

# Ensure we're using Vite, not Next.js
echo "Setting environment to skip Next.js detection..."
export NETLIFY_NEXT_PLUGIN_SKIP=true
export NETLIFY_USE_NEXTJS=false

# Generate Prisma client
echo "Generating Prisma client..."
npx prisma generate

# Build with Vite
echo "Building with Vite..."
npm run legacy:build

# Create Netlify redirects file
echo "Creating _redirects file in dist directory..."
cat > dist/_redirects << EOL
# Map API routes to Netlify Functions
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
/*                         /index.html                               200
EOL

# Create a Netlify config file in the dist folder
echo "Creating netlify.json in dist directory..."
cat > dist/netlify.json << EOL
{
  "plugins": [],
  "build": {
    "framework": "#vite"
  }
}
EOL

# Create an empty next.config.js.bak to avoid detection
echo "Renaming next.config.js to next.config.js.bak if it exists..."
if [ -f "next.config.js" ]; then
  mv next.config.js next.config.js.bak
fi

echo "Build complete!"
