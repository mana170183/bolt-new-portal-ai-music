const { PrismaClient } = require('@prisma/client');

// Initialize PrismaClient with error logging
const prisma = new PrismaClient({
  log: ['error'],
  datasources: {
    db: {
      url: process.env.NETLIFY_DATABASE_URL || process.env.DATABASE_URL,
    },
  },
});

// Export the prisma client for use in functions
module.exports = prisma;
