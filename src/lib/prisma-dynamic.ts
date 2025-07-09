// This approach uses a dynamic import to avoid initialization during build time
// Implementation inspired by: https://www.prisma.io/docs/guides/other/troubleshooting-orm/help-articles/nextjs-prisma-client-dev-practices

// Type for the global object with prisma property
declare global {
  // eslint-disable-next-line no-var
  var prisma: any | undefined;
}

// Define a function to get or create the Prisma client
export const getPrisma = async () => {
  // If already instantiated, return the existing instance
  if (global.prisma) {
    return global.prisma;
  }
  
  // Import PrismaClient at runtime
  const { PrismaClient } = await import('@prisma/client');
  
  // Create a new client
  const client = new PrismaClient();
  
  // Save in global to reuse connection
  global.prisma = client;
  
  return client;
};

// Export a proxy that will dynamically load Prisma when needed
export const prisma = new Proxy({}, {
  get: (_target, prop) => {
    // Return a function that will load Prisma when called
    return async (...args: any[]) => {
      const client = await getPrisma();
      return client[prop](...args);
    };
  }
}) as any;
