# 🚀 Azure Functions v2 Backend Deployment Guide

## Overview
We have successfully migrated from the old folder-based Azure Functions structure to the new v2 programming model using a single `function_app.py` file. This provides better performance, easier maintenance, and more features.

## 🔄 Current Status
- ✅ **Local Backend**: Fully operational (100% test success rate)
- ✅ **15 Endpoints**: All working perfectly locally
- ✅ **New Architecture**: Single `function_app.py` with all endpoints
- ⚠️ **Production**: Currently using old structure (404 errors)

## 🎯 Deployment Options

### Option A: Update Existing Static Web App (Recommended)
Use this if you want to keep your current Static Web App URL and just update the backend.

```bash
# Quick update of existing app
./update-existing-backend.sh
```

**What this does:**
- Backs up old function folders
- Removes old structure 
- Keeps only new `function_app.py` structure
- Updates configurations
- Prepares for GitHub Actions deployment

### Option B: Create New Static Web App
Use this if you want a fresh deployment with a new URL.

```bash
# Full new deployment
./deploy-v2-backend.sh
```

**What this does:**
- Creates a new Static Web App
- Deploys new backend structure
- Sets up GitHub Actions workflow
- Configures everything from scratch

## 📋 Manual Deployment Steps

If you prefer manual control:

### 1. Clean Up API Structure
```bash
# Backup old structure
mkdir api_backup
cp -r api/*/ api_backup/ 2>/dev/null || true

# Remove old function folders (keep function_app.py)
find api -maxdepth 1 -type d ! -name "api" ! -name "." -exec rm -rf {} + 2>/dev/null || true
```

### 2. Verify New Structure
```bash
cd api
ls -la
# Should see:
# - function_app.py (main file)
# - requirements.txt
# - host.json
# - local.settings.json
```

### 3. Test Locally
```bash
cd api
func start
# Test: curl http://localhost:7071/api/health
```

### 4. Deploy via Git
```bash
git add .
git commit -m "Migrate to Azure Functions v2 - single function_app.py"
git push origin main
```

## 🧪 Testing After Deployment

Once deployed, test these key endpoints:

```bash
# Replace with your actual URL
BASE_URL="https://your-app.azurestaticapps.net"

# Health check
curl $BASE_URL/api/health

# Status and architecture
curl $BASE_URL/api/status

# Available endpoints
curl $BASE_URL/api/root

# Generate music
curl -X POST $BASE_URL/api/generate-music \
  -H "Content-Type: application/json" \
  -d '{"prompt": "happy upbeat song", "genre": "pop"}'
```

## 🔧 Environment Variables

Set these in Azure Portal > Static Web Apps > Configuration:

```
AZURE_OPENAI_ENDPOINT=your_openai_endpoint
AZURE_OPENAI_API_KEY=your_openai_key
AZURE_SQL_CONNECTION_STRING=your_sql_connection
AZURE_STORAGE_CONNECTION_STRING=your_storage_connection
SPOTIFY_CLIENT_ID=your_spotify_id
SPOTIFY_CLIENT_SECRET=your_spotify_secret
```

## 📊 Comparison: Old vs New

| Feature | Old Structure | New Structure |
|---------|---------------|---------------|
| Files | 15+ folders | 1 function_app.py |
| Performance | Standard | Optimized |
| CORS | Per-function | Centralized |
| Maintenance | Complex | Simple |
| Features | Basic | Enhanced |
| Testing | Manual | Automated |

## 🎉 Benefits of New Structure

1. **Single File Management**: All endpoints in one place
2. **Better Performance**: Faster cold starts
3. **Centralized CORS**: Consistent across all endpoints
4. **Enhanced Features**: New endpoints like /status, /catalog, /playlists
5. **Better Error Handling**: Consistent error responses
6. **Easier Testing**: Comprehensive test coverage

## 🚨 Important Notes

- The old individual function folders will be removed
- All functionality is preserved and enhanced
- No breaking changes to API interface
- Frontend code requires no changes
- GitHub Actions will handle automatic deployment

## 🔗 Next Steps

1. Choose deployment option (A or B)
2. Run the appropriate script
3. Monitor GitHub Actions deployment
4. Test all endpoints
5. Configure production environment variables

Choose your deployment approach and let's get your new backend live! 🚀
