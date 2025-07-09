# Prisma Database Setup

This document outlines the steps taken to configure Prisma with PostgreSQL on Vercel for the AI Music Generation platform.

## Database Configuration

The project is set up with Prisma ORM connecting to a PostgreSQL database via Prisma Accelerate for improved performance and connection pooling.

### Environment Variables

The following environment variables have been configured:

- `DATABASE_URL`: The Prisma Accelerate connection URL with API key
- `POSTGRES_URL`: The direct PostgreSQL connection URL
- `PRISMA_DATABASE_URL`: Alias for the Prisma Accelerate URL (used by some tools)

### Schema Configuration

The Prisma schema in `prisma/schema.prisma` has been configured to use both Prisma Accelerate and direct PostgreSQL connections:

```prisma
datasource db {
  provider  = "postgresql"
  url       = env("DATABASE_URL")
  directUrl = env("POSTGRES_URL")
}
```

### Database Schema

The database schema includes the following models:

- `User`: User account information
- `Subscription`: User subscription details
- `UserPreferences`: User preferences for music generation
- `Composition`: Music compositions created by users
- `CompositionVariant`: Variations of a composition
- `Collaboration`: Collaborative editing of compositions
- `Export`: Exported compositions in various formats
- `Feedback`: User feedback on compositions
- `StyleTransfer`: Style transfer information for compositions

### API Routes

The following API routes have been implemented to test the database connection:

- `/api/test-db`: Tests the Prisma database connection
- `/api/instruments`: Returns a list of available instruments (with database connection verification)

## Deployment on Vercel

### Vercel Configuration

The `vercel.json` file has been updated to include the database environment variables:

```json
{
  "env": {
    "DATABASE_URL": "${DATABASE_URL}",
    "PRISMA_DATABASE_URL": "${PRISMA_DATABASE_URL}",
    "POSTGRES_URL": "${POSTGRES_URL}"
  }
}
```

### Deployment Steps

1. Push your code to GitHub
2. Create a new project on Vercel linked to your GitHub repository
3. Configure the environment variables in Vercel:
   - `DATABASE_URL`
   - `PRISMA_DATABASE_URL`
   - `POSTGRES_URL`
4. Deploy the project

## Local Development

For local development:

1. Make sure `.env.local` contains the database connection URLs
2. Run `npx prisma generate` to generate the Prisma client
3. Run `npm run dev` to start the development server

## Database Migration and Seeding

To update the database schema:

```bash
# Push schema changes to the database
npx prisma db push

# If you need to reset the database during development
npx prisma db reset

# To open Prisma Studio for database management
npx prisma studio
```
