/**
 * This module provides a dynamic import approach for Prisma Client.
 * This avoids initialization during Next.js builds and works better with
 * Vercel serverless functions.
 * 
 * Reference: https://www.prisma.io/docs/guides/other/troubleshooting-orm/help-articles/nextjs-prisma-client-dev-practices
 */

// Create a global type for our Prisma instance
declare global {
  // eslint-disable-next-line no-var
  var prisma: any | undefined;
}

// A mock client for build time to avoid query engine initialization
const createMockClient = () => {
  return {
    $connect: () => Promise.resolve(),
    $disconnect: () => Promise.resolve(),
    user: {
      findMany: () => Promise.resolve([]),
      count: () => Promise.resolve(0),
      create: () => Promise.resolve({}),
    },
    composition: {
      findMany: () => Promise.resolve([]),
      create: () => Promise.resolve({}),
    }
  };
};

/**
 * Get or create a Prisma Client instance.
 * Handles dynamic imports and caching the client in the global scope.
 */
export const getPrisma = async () => {
  // Function to determine if we're in a build environment
  const isBuildPhase = () => {
    return process.env.NODE_ENV === 'production' && 
          (process.argv.includes('build') || process.env.VERCEL_ENV === 'development');
  };

  try {
    // During build time, return a mock client
    if (isBuildPhase()) {
      return createMockClient();
    }

    // If already instantiated in global scope, return the existing instance
    if (global.prisma) {
      return global.prisma;
    }
    
    // Import PrismaClient at runtime
    const { PrismaClient } = await import('@prisma/client');
    
    // Create a new client
    const client = new PrismaClient();
    
    // Save in global to reuse connection across requests
    global.prisma = client;
    
    return client;
  } catch (error) {
    console.error('Error initializing Prisma client:', error);
    // Return mock client as fallback
    return createMockClient();
  }
};
