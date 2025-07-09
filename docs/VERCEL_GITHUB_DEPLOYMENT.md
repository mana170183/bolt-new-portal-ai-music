# Troubleshooting Vercel Deployments from GitHub

If you're having trouble with automatic deployments from GitHub to Vercel, follow this troubleshooting guide.

## Common Issues and Solutions

### 1. GitHub Integration Issues

**Check if your GitHub repository is properly connected to Vercel:**
1. Go to the Vercel dashboard
2. Select your project
3. Click on "Settings" → "Git"
4. Verify that the correct GitHub repository is connected
5. Check that the correct branch is set for production deployments (typically "main", "master", or "production")

**Solution if not connected:**
- Click "Connect Git Repository" and follow the instructions to connect your GitHub repo

### 2. Build Errors During Deployment

**Prisma-related errors:**
- Vercel might have issues generating the Prisma client during build

**Solution:**
1. Add the correct binary targets in schema.prisma:
   ```prisma
   generator client {
     provider = "prisma-client-js"
     previewFeatures = ["driverAdapters"]
     binaryTargets = ["native", "rhel-openssl-1.0.x"]
   }
   ```

2. Make sure your build script properly handles Prisma generation:
   - Use the `vercel-build` script we've added to package.json

### 3. Environment Variables

**Check if environment variables are set in Vercel:**
1. Go to Vercel dashboard
2. Select your project
3. Click "Settings" → "Environment Variables"
4. Verify that all required variables are set:
   - `DATABASE_URL`
   - `PRISMA_DATABASE_URL`
   - `POSTGRES_URL`

**Solution:**
- Add the missing environment variables manually in Vercel dashboard
- Alternatively, use our `scripts/vercel-deploy-direct.sh` script which passes these variables

### 4. Permissions Issues

**Check GitHub permissions:**
1. Go to your GitHub repository
2. Click on "Settings" → "GitHub Apps"
3. Verify that Vercel has the necessary permissions

**Solution:**
- Re-install the Vercel GitHub App with proper permissions

### 5. Manual Deployment

If automatic deployment still fails, you can deploy manually:

```bash
# Use our helper script
npm run github-deploy

# Or use the Vercel CLI directly
vercel --prod
```

## Verifying Deployment

After deploying, check these endpoints to confirm everything is working:

1. Main app: `https://your-app.vercel.app/`
2. Database connection: `https://your-app.vercel.app/api/test-db`

## Getting Help

If you're still having issues, you can:
1. Check Vercel deployment logs
2. Look at GitHub Actions logs
3. Contact Vercel support
