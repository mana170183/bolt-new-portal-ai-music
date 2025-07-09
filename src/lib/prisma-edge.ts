/**
 * Edge-compatible Prisma client setup for Vercel
 * Helps prevent query engine issues during Vercel deployment
 */

import { PrismaClient } from '@prisma/client';

// We handle connection pooling by keeping one instance per Node.js process
let prisma: PrismaClient;

// We check first if we're in a production environment
if (process.env.NODE_ENV === 'production') {
  prisma = new PrismaClient();
} else {
  // For development, we use a global variable to avoid multiple connections
  if (!(global as any).prisma) {
    (global as any).prisma = new PrismaClient({
      log: ['query', 'info', 'warn', 'error'],
    });
  }
  prisma = (global as any).prisma;
}

export default prisma;
