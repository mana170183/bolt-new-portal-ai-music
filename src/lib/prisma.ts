import { PrismaClient } from '@prisma/client';

/**
 * PrismaClient is attached to the `global` object in development to prevent
 * exhausting your database connection limit.
 * Learn more: https://pris.ly/d/help/next-js-best-practices
 */

// Define globalThis type for Prisma
const globalForPrisma = globalThis as unknown as {
  prisma: PrismaClient | undefined;
};

// Function to determine if we're in a build environment or if database should be skipped
const shouldSkipDatabase = () => {
  return (
    process.env.SKIP_DATABASE_SETUP === 'true' ||
    process.env.NODE_ENV === 'production' && (
      process.argv.includes('build') || 
      process.env.VERCEL_ENV === 'development' ||
      process.env.NETLIFY === 'true' ||
      process.env.CI === 'true'
    )
  );
};

// Mock client for build time
const mockClient = {
  user: {
    findUnique: () => Promise.resolve(null),
    findMany: () => Promise.resolve([]),
    create: () => Promise.resolve({}),
    update: () => Promise.resolve({}),
    delete: () => Promise.resolve({}),
  },
  track: {
    findMany: () => Promise.resolve([]),
    create: () => Promise.resolve({}),
    findUnique: () => Promise.resolve(null),
  },
  $connect: () => Promise.resolve(),
  $disconnect: () => Promise.resolve(),
  $transaction: () => Promise.resolve([]),
} as unknown as PrismaClient;

// Don't initialize during build (avoids Prisma query engine issues during build)
const createClient = () => {
  if (shouldSkipDatabase()) {
    console.log('Skipping Prisma client initialization (build environment)');
    return mockClient;
  }
  
  // For runtime, create a real client with proper configuration
  console.log('Initializing Prisma client for runtime');
  return new PrismaClient({
    log: process.env.NODE_ENV === 'development' ? ['query', 'error'] : ['error'],
    errorFormat: 'pretty',
  });
};

// Create or reuse the Prisma client
export const prisma = globalForPrisma.prisma || createClient();

// Save the client in development to avoid too many connections
if (process.env.NODE_ENV !== 'production') {
  globalForPrisma.prisma = prisma;
}
