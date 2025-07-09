# Netlify Migration Guide

This document provides an overview of the migration from Vercel to Netlify for the AI Music Generation platform.

## Migration Overview

The platform has been migrated from Vercel to Netlify, with several architectural changes:

1. **API Routes as Netlify Functions**: All API routes have been implemented as Netlify Functions in the `/netlify/functions/` directory.
2. **Database Connection**: Using Neon PostgreSQL with connection pooling for serverless functions.
3. **Frontend Updates**: The frontend now detects Netlify environments and adjusts API base URLs accordingly.
4. **Vite Build System**: The project now uses Vite for builds instead of Next.js.

## Deployment Steps

### 1. Set up Netlify Project

1. Connect your GitHub repository to Netlify
2. Important: Manually disable the Next.js plugin in the Netlify UI before deploying:
   - Go to Site settings > Build & deploy > Continuous Deployment
   - Under "Build settings", click "Edit settings"
   - Set "Build command" to `npm run netlify:vite-build`
   - Set "Publish directory" to `dist`
   - Save these settings
3. Go to Site settings > Build & deploy > Build plugins
   - Ensure no Next.js plugin is enabled
   - If it is, disable or remove it

### 2. Configure Environment Variables

Set the following environment variables in Netlify:

```
DATABASE_URL=postgresql://neondb_owner:[PASSWORD]@ep-empty-fog-aebnbgb6-pooler.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require
PRISMA_DATABASE_URL=postgresql://neondb_owner:[PASSWORD]@ep-empty-fog-aebnbgb6-pooler.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require
POSTGRES_URL=postgresql://neondb_owner:[PASSWORD]@ep-empty-fog-aebnbgb6.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require
NETLIFY_DATABASE_URL=postgresql://neondb_owner:[PASSWORD]@ep-small-bush-aeholakr-pooler.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require
NETLIFY_DATABASE_URL_UNPOOLED=postgresql://neondb_owner:[PASSWORD]@ep-small-bush-aeholakr.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require
SKIP_DATABASE_SETUP=true
NEXT_PUBLIC_API_URL=
NETLIFY_NEXT_PLUGIN_SKIP=true
NETLIFY_USE_NEXTJS=false
```

### 3. Database Setup

1. Ensure your Neon database is properly configured
2. Run database migrations: `npx prisma migrate deploy`

### 4. Deployment Steps for Netlify CLI

If deploying from the command line:

```bash
# Install Netlify CLI if not installed
npm install -g netlify-cli

# Log in to Netlify
netlify login

# Create a new site (if needed)
netlify sites:create --name bolt-ai-music

# Link to the site
netlify link --name bolt-ai-music

# Deploy to production
netlify deploy --prod
```

### 5. Verify API Functions

After deployment, verify these API endpoints are working:

- `/api/health`
- `/api/genres`
- `/api/moods`
- `/api/user/quota`
- `/api/auth/token`
- `/api/instruments`
- `/api/composition-templates`
- `/api/tracks`
- `/api/generate-music`
- `/api/generate-enhanced-music`

### 6. Troubleshooting

If Netlify keeps detecting this as a Next.js project:

1. **Manual Plugin Disabling**:
   - Go to the Netlify UI > Site settings > Build & deploy > Build plugins
   - Disable any Next.js plugin that appears there

2. **Force Rebuild**:
   - After disabling plugins, trigger a new deploy from the Netlify UI

3. **Check Build Logs**:
   - If issues persist, check the build logs for any mentions of Next.js detection
   - Look for plugins being auto-installed
- `/api/composition-templates`
- `/api/tracks`
- `/api/generate-music`
- `/api/generate-enhanced-music`

## Architecture Details

### API Routes Structure

All backend API endpoints are implemented as Netlify Functions:

```
netlify/
  functions/
    auth-token.js             # Authentication token generation
    composition-templates.js  # Composition templates
    generate-enhanced-music.js # Enhanced music generation
    generate-music.js         # Basic music generation
    genres.js                # Music genres
    health.js                # Health check endpoint
    instruments.js           # Available instruments
    moods.js                 # Available moods
    tracks.js                # User's music tracks
    user-quota.js            # User quota information
    utils/
      prisma.js              # Prisma client utility
      response.js            # API response utility
```

### Redirects Configuration

The `/public/_redirects` file maps API routes to Netlify Functions:

```
/api/health                /.netlify/functions/health
/api/genres                /.netlify/functions/genres
# etc...
```

## Troubleshooting

### Database Connectivity Issues

1. Verify connection strings in Netlify environment variables
2. Check Netlify Function logs for connection errors
3. Ensure IP addresses are allowed in Neon database settings

### API 404 Errors

1. Verify that the API route is properly mapped in `_redirects`
2. Check that the corresponding function exists in the `netlify/functions/` directory
3. Inspect Netlify Function logs for errors

### Frontend/Backend Connection Issues

1. Check browser console for API errors
2. Verify that the API base URL is correctly set to empty string for Netlify deployments
3. Ensure all API endpoints match between frontend and backend

## Fallback Behavior

The frontend has been updated to handle API unavailability during the migration process. If certain API endpoints are not yet available, the application will use fallback data to ensure a smooth user experience.
