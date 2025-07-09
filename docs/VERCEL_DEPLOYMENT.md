# Deploying AI Music Platform to Vercel

This document provides a complete guide for deploying the AI Music Platform with a Prisma/Postgres backend to Vercel.

## Prerequisites

1. A Vercel account connected to your GitHub repository
2. A PostgreSQL database (we're using Prisma Data with Prisma Accelerate)
3. Environment variables properly configured

## Environment Variables

The following environment variables need to be set in your Vercel project settings:

- `PRISMA_DATABASE_URL`: The Prisma Accelerate connection URL
- `POSTGRES_URL`: Direct connection to PostgreSQL database
- `DATABASE_URL`: Legacy URL (can be same as PRISMA_DATABASE_URL)
- `NEXT_PUBLIC_API_URL`: Set to "/api" in production
- `BACKEND_URL`: URL to your separate backend service (if applicable)

## Deployment Steps

### 1. Prepare Your Code

Ensure your code repository is up to date with all the fixes for Prisma deployment on Vercel:

- Updated Prisma client setup in `src/lib/prisma-dynamic.ts`
- Updated `prisma/schema.prisma` with correct environment variable references
- Added custom build script `vercel-build.js`
- Updated `vercel.json` configuration

### 2. Deploy to Vercel

Option 1: Use Vercel Dashboard
1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Import your GitHub repository
3. Configure environment variables
4. Deploy

Option 2: Use Vercel CLI
```bash
# Install Vercel CLI if you haven't already
npm install -g vercel

# Login to Vercel
vercel login

# Deploy to production
vercel --prod
```

### 3. Verify Database Connection

After deployment, verify that your application is correctly connecting to the database:

1. Visit `https://your-deployed-url.vercel.app/api/test-db`
2. You should see a JSON response with `success: true` and a user count

### 4. Troubleshooting

If you encounter issues with Prisma during deployment:

#### Database Connection Issues

1. Verify environment variables are correctly set
2. Check database credentials and access permissions
3. Ensure database is accessible from Vercel's IP ranges

#### Prisma Client Generation Issues

1. Try rebuilding the deployment with `vercel --force`
2. Verify that the `postinstall` script is running correctly
3. Check Vercel build logs for any errors

#### Serverless Function Timeouts

1. Check memory/timeout settings in `vercel.json`
2. Optimize database queries
3. Consider adding connection pooling

## Maintenance

### Database Migrations

To update your database schema:

```bash
# Generate new migration
npx prisma migrate dev --name description-of-changes

# Apply migrations in production
npx prisma migrate deploy
```

### Monitoring

Monitor your application's performance:

1. Use Vercel Analytics
2. Set up logging with a service like LogDNA or Papertrail
3. Monitor database performance with Prisma Data platform

## References

- [Prisma Documentation](https://www.prisma.io/docs)
- [Next.js on Vercel](https://nextjs.org/docs/deployment)
- [Vercel Environment Variables](https://vercel.com/docs/environment-variables)
