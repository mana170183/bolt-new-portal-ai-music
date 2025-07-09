// test-db-simple.js
require('dotenv').config();
const { PrismaClient } = require('@prisma/client');

const prisma = new PrismaClient({
  datasourceUrl: process.env.DATABASE_URL,
});

async function main() {
  try {
    console.log('Testing database connection...');
    // Try a simple query
    const result = await prisma.$queryRaw`SELECT NOW()`;
    console.log('Database connection successful!');
    console.log('Current database time:', result[0].now);
    return process.exit(0);
  } catch (error) {
    console.error('Database connection test failed:');
    console.error(error);
    return process.exit(1);
  }
}

main();
