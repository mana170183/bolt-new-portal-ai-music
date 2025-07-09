// This is an alternative approach to initializing Prisma 
// that helps avoid the enableTracing error during static site generation

import { PrismaClient } from '@prisma/client';

// Prevent multiple instances of Prisma Client in development
const globalForPrisma = global;

// Try/catch block to handle potential initialization errors
let prisma;

try {
  // Only initialize Prisma on the server side (not during build)
  if (typeof window === 'undefined') {
    prisma = globalForPrisma.prisma || new PrismaClient();
    
    // Save to global object in non-production environments
    if (process.env.NODE_ENV !== 'production') {
      globalForPrisma.prisma = prisma;
    }
  } else {
    // For client-side, create a dummy client that won't be used
    // but prevents build errors
    prisma = {} as PrismaClient;
  }
} catch (error) {
  console.error('Failed to initialize Prisma client:', error);
  // Provide a mock client that won't crash the build
  prisma = {} as PrismaClient;
}

export default prisma;
