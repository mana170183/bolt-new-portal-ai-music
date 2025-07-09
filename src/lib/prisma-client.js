/**
 * This file ensures Prisma Client is correctly initialized in a Next.js serverless environment.
 * It should be imported by all API routes that need database access.
 */

import { PrismaClient } from '@prisma/client';

/**
 * PrismaClient is attached to the `globalThis` object to prevent
 * exhausting database connections during development due to hot-reloading.
 * 
 * Learn more: 
 * https://pris.ly/d/help/next-js-best-practices
 */

// Add prisma to the globalThis type
const globalForPrisma = globalThis;

// Prevent multiple instances of Prisma Client in development
export const prisma = globalForPrisma.prisma || new PrismaClient({
  log: process.env.NODE_ENV === 'development' ? ['query', 'error', 'warn'] : ['error'],
});

// If not in production, attach to global object for reuse
if (process.env.NODE_ENV !== 'production') {
  globalForPrisma.prisma = prisma;
}

export default prisma;
