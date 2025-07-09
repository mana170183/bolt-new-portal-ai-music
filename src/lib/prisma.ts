import { PrismaClient } from '@prisma/client';

/**
 * PrismaClient is attached to the `global` object in development to prevent
 * exhausting your database connection limit.
 * Learn more: https://pris.ly/d/help/next-js-best-practices
 */

// Check if we're in a build context (important for Next.js builds)
const isBuild = process.env.NODE_ENV === 'production' && process.argv.includes('build');

// Create a mock client to use during builds
const createMockPrismaClient = () => {
  return {
    $connect: () => Promise.resolve(),
    $disconnect: () => Promise.resolve(),
    user: {
      findMany: () => Promise.resolve([]),
      count: () => Promise.resolve(0),
      create: () => Promise.resolve({}),
    },
    // Add other models as needed
  } as unknown as PrismaClient;
}

const globalForPrisma = globalThis as unknown as {
  prisma: PrismaClient | undefined;
};

export const prisma = globalForPrisma.prisma || 
  (isBuild ? 
    createMockPrismaClient() : 
    new PrismaClient()
  );

// Save the client instance to avoid recreating it
if (process.env.NODE_ENV !== 'production') {
  globalForPrisma.prisma = prisma;
}
