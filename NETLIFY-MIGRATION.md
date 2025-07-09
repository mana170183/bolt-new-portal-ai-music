# Netlify Migration Guide

This document provides an overview of the migration from Vercel to Netlify for the AI Music Generation platform.

## Migration Overview

The platform has been migrated from Vercel to Netlify, with several architectural changes:

1. **API Routes as Netlify Functions**: All API routes have been implemented as Netlify Functions in the `/netlify/functions/` directory.
2. **Database Connection**: Using Neon PostgreSQL with connection pooling for serverless functions.
3. **Frontend Updates**: The frontend now detects Netlify environments and adjusts API base URLs accordingly.

## Deployment Steps

### 1. Set up Netlify Project

1. Connect your GitHub repository to Netlify
2. Configure build settings:
   - Build command: `npm run legacy:build`
   - Publish directory: `dist`

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
```

### 3. Database Setup

1. Ensure your Neon database is properly configured
2. Run database migrations: `npx prisma migrate deploy`

### 4. Verify API Functions

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
