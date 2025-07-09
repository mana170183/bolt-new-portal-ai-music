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

// Function to determine if we're in a build environment
const isBuildPhase = () => {
  return process.env.NODE_ENV === 'production' && 
         (process.argv.includes('build') || 
          process.env.VERCEL_ENV === 'development' ||
          process.env.NETLIFY === 'true');
};

// Don't initialize during build (avoids Prisma query engine issues during build)
const createClient = () => {
  if (isBuildPhase()) {
    // Return minimal mock client during build
    return {
      $connect: () => Promise.resolve(),
      $disconnect: () => Promise.resolve(),
    } as unknown as PrismaClient;
  }
  
  // For runtime, create a real client with proper configuration
  return new PrismaClient({
    log: process.env.NODE_ENV === 'development' ? ['query', 'error'] : ['error'],
    errorFormat: 'pretty',
  });
  return new PrismaClient();
};

// Create or reuse the Prisma client
export const prisma = globalForPrisma.prisma || createClient();

// Save the client in development to avoid too many connections
if (process.env.NODE_ENV !== 'production') {
  globalForPrisma.prisma = prisma;
}
