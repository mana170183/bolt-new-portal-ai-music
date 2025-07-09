// Netlify Functions database utility - shared across all functions
import { PrismaClient } from '@prisma/client';

// Create a single instance of Prisma Client to be reused across function invocations
let prisma;

// Initialize the Prisma client with appropriate connection pooling for serverless
if (!prisma) {
  prisma = new PrismaClient({
    log: ['query', 'error', 'warn'],
    // Configure connection pooling - important for serverless functions
    // to avoid connection issues
    datasources: {
      db: {
        url: process.env.DATABASE_URL || process.env.PRISMA_DATABASE_URL,
      },
    },
  });
}

export { prisma };
