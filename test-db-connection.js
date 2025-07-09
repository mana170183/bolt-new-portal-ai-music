// test-db-connection.js
import dotenv from 'dotenv';
import { PrismaClient } from '@prisma/client';

// Load environment variables
dotenv.config();

const prisma = new PrismaClient();

async function main() {
  try {
    // Test database connection
    console.log('Connecting to database...');
    await prisma.$connect();
    
    console.log('Database connection successful!');
    
    // Print database URL (with credentials redacted for security)
    const dbUrl = process.env.DATABASE_URL || 'Not set';
    console.log('Database URL:', dbUrl.replace(/:\/\/(.*?)@/, '://*****@'));
    
    // Attempt to query the database (this will fail if the connection is not working)
    console.log('Testing query...');
    const result = await prisma.$queryRaw`SELECT 1 as result`;
    console.log('Query result:', result);
    
    console.log('All tests passed. Your database is configured correctly!');
  } catch (error) {
    console.error('Database connection test failed:');
    console.error(error);
    process.exit(1);
  } finally {
    await prisma.$disconnect();
  }
}

main();
