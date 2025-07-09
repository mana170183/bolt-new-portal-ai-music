import { PrismaClient } from '@prisma/client';

// Define prisma client for global use (prevents multiple instances in development)
const globalForPrisma = globalThis as unknown as {
  prisma: PrismaClient | undefined;
};

// Initialize Prisma client with minimal settings to avoid compatibility issues
export const prisma =
  globalForPrisma.prisma ??
  new PrismaClient({
    // Use minimal settings to avoid compatibility issues on different platforms
  });

// Save the client in development to avoid multiple instances
if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = prisma;
