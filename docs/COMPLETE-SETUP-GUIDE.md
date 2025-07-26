# AI Music Portal - Complete Setup and Deployment Guide

## Overview

This document provides a complete guide for deploying the AI Music Portal on Azure using Static Web Apps, with full integration of Azure OpenAI, SQL Database, Blob Storage, and external music APIs.

## Architecture

The deployed solution follows this architecture:
- **Frontend**: React app deployed on Azure Static Web Apps
- **Backend API**: Azure Functions (Python) co-located with frontend
- **AI Services**: Azure OpenAI for lyrics generation
- **Database**: Azure SQL Database for metadata storage
- **Storage**: Azure Blob Storage for audio files
- **External APIs**: Spotify, MusicBrainz, Freesound, Jamendo integration

## Prerequisites

1. **Azure CLI** installed and configured
2. **Node.js** (v16 or higher)
3. **Python** (v3.9 or higher)
4. **Git** repository with the project
5. **SQL Server tools** (optional, for database management)

## Azure Resources

The following Azure resources are already configured in resource group `rg-portal-ai-music-dev`:

### Existing Resources:
- **Azure OpenAI**: `openai-portal-ai-music-dev`
- **SQL Database**: `sql-portal-ai-music-dev/portal-ai-music-db`
- **Storage Account**: `stportalaimusic439`

### Service Principal:
```bash
App ID: 6a069624-67ed-4bfe-b4e6-301f6e02a853
Tenant: bca013b2-c163-4a0d-ad43-e6f1d3cda34b
Subscription: f165aa7d-ea02-4be9-aa0c-fad453084a9f
```

## Deployment Steps

### 1. Prepare the Environment

```bash
# Clone the repository
git clone <your-repo-url>
cd portal-ai-music

# Install dependencies
npm install

# Build the frontend
npm run build
```

### 2. Deploy to Azure Static Web Apps

```bash
# Make the deployment script executable
chmod +x deploy-complete-azure-solution.sh

# Run the deployment
./deploy-complete-azure-solution.sh
```

This script will:
- Create a new Azure Static Web App
- Deploy frontend and backend together
- Set up database schema
- Configure application settings
- Create blob storage containers

### 3. Configure External Music APIs

After deployment, configure these optional external music APIs:

#### Spotify API (Paid - Required for production)
1. Go to https://developer.spotify.com/dashboard/
2. Create a new app
3. In Azure Static Web App settings, add:
   - `SPOTIFY_CLIENT_ID`
   - `SPOTIFY_CLIENT_SECRET`

#### Freesound API (Free)
1. Go to https://freesound.org/
2. Create account and apply for API access
3. Add `FREESOUND_API_KEY` to app settings

#### Jamendo API (Free)
1. Go to https://developer.jamendo.com/
2. Register your app
3. Add `JAMENDO_CLIENT_ID` to app settings

**Note**: MusicBrainz API works without additional configuration.

## API Endpoints

After deployment, the following endpoints will be available:

### Core Endpoints:
- `GET /api/health` - Health check
- `GET /api/` - API information
- `POST /api/generate-music` - Basic music generation
- `POST /api/advanced-generate` - Advanced music generation with detailed controls

### Music Library:
- `GET /api/music-library` - Get user's saved tracks
- `POST /api/music-library` - Save track to library
- `DELETE /api/music-library` - Remove track from library

### Metadata:
- `GET /api/genres` - Available music genres
- `GET /api/moods` - Available music moods

### Authentication & Usage:
- `POST /api/auth-token` - Generate authentication token
- `GET /api/user-quota` - Check user's API quota

### External Music APIs:
- `GET /api/music-apis/spotify` - Spotify integration
- `GET /api/music-apis/musicbrainz` - MusicBrainz integration
- `GET /api/music-apis/freesound` - Freesound integration
- `GET /api/music-apis/jamendo` - Jamendo integration

## Database Schema

The deployment automatically creates these tables:

### `tracks` table:
- Stores all generated music metadata
- Includes lyrics, prompts, audio URLs, and generation parameters

### `user_library` table:
- Maps users to their saved tracks
- Supports user-specific music collections

### `user_quotas` table:
- Manages API usage limits
- Supports free/premium/enterprise plans

## Testing the Deployment

### 1. Health Check
```bash
curl https://your-app.azurestaticapps.net/api/health
```

### 2. Generate Music
```bash
curl -X POST https://your-app.azurestaticapps.net/api/generate-music \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Happy birthday song", "genre": "pop", "mood": "happy", "duration": 30}'
```

### 3. Get Available Genres
```bash
curl https://your-app.azurestaticapps.net/api/genres
```

### 4. Check User Quota
```bash
curl https://your-app.azurestaticapps.net/api/user-quota?user_id=demo_user
```

## Frontend Integration

The frontend automatically connects to the co-located backend API. Key features:

### Music Generation:
- Simple and advanced music generation forms
- Real-time progress tracking
- Audio playback and download

### Music Library:
- Personal music collection
- Filter by genre and mood
- Save/remove tracks

### External API Integration:
- Search Spotify for inspiration
- Browse MusicBrainz database
- Access free music from Freesound and Jamendo

## Production Configuration

### Environment Variables:
All required environment variables are automatically configured:
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_SQL_CONNECTION_STRING`
- `AZURE_STORAGE_ACCOUNT_NAME`
- `AZURE_STORAGE_ACCOUNT_KEY`

### Security:
- CORS is properly configured
- Authentication tokens for API access
- Encrypted database connections
- Secure blob storage access

### Performance:
- CDN-backed static web app
- Optimized API responses
- Efficient database queries
- Blob storage for fast audio delivery

## Monitoring and Maintenance

### Application Insights:
- Automatic logging for all API calls
- Performance monitoring
- Error tracking and alerts

### Database Maintenance:
- Regular cleanup of old tracks
- Quota reset automation
- Performance optimization

### Storage Management:
- Audio file lifecycle management
- Automatic cleanup of unused files
- Storage cost optimization

## Troubleshooting

### Common Issues:

1. **API not responding**:
   - Check Static Web App deployment status
   - Verify environment variables are set
   - Check function app logs

2. **Database connection errors**:
   - Verify SQL connection string
   - Check firewall rules
   - Ensure service principal has access

3. **Blob storage issues**:
   - Verify storage account credentials
   - Check container permissions
   - Ensure proper CORS settings

4. **OpenAI integration failures**:
   - Verify API key and endpoint
   - Check quota limits
   - Ensure model deployment

### Logs and Diagnostics:
- Azure Functions logs in Application Insights
- Static Web App deployment logs
- SQL Database query performance
- Storage account access logs

## Cost Optimization

### Free Tier Usage:
- Static Web App: Free tier (100GB bandwidth)
- Azure Functions: Consumption plan (free execution time)
- Azure SQL: Basic tier for development
- Blob Storage: Standard tier with lifecycle management

### Production Scaling:
- Upgrade to Standard Static Web App tier for SLA
- Consider Premium Functions for better performance
- Scale SQL Database based on usage
- Implement storage tiering for cost efficiency

## Next Steps

1. **Custom Domain**: Configure custom domain for production
2. **CI/CD Pipeline**: Set up GitHub Actions for automated deployments
3. **API Versioning**: Implement API versioning for future updates
4. **Advanced Features**: Add more AI models and music generation options
5. **Analytics**: Implement user analytics and usage tracking

## Support and Documentation

- **API Documentation**: `/docs/API-DOCUMENTATION.md`
- **Architecture Diagram**: Included in repository
- **Sample Code**: Frontend integration examples provided
- **External API Documentation**: Links provided for each service

This setup provides a production-ready AI music generation platform with comprehensive Azure integration and external API support.
