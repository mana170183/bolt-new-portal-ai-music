// Simple database test script
const { PrismaClient } = require('@prisma/client');

// Define the database URLs directly for this test
const DATABASE_URL = "prisma+postgres://accelerate.prisma-data.net/?api_key=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcGlfa2V5IjoiMDFKWlFHVlNLWDc3RFZKMFlLWVlUMTc4S1MiLCJ0ZW5hbnRfaWQiOiIyMWIwMjc4NGE3MThjMWY0YzYxNWJmYTlkNGY3YzUyZGFkNjNlMjRmMWY4ODlmOTljYzQ4NmM0M2JhMjE3ZTQyIiwiaW50ZXJuYWxfc2VjcmV0IjoiNmY0OWQxNjMtZTJjNi00ZTFhLWI0OGItNjdhM2YxN2Q4Mzk1In0.Clt6JfDH0Tundbd43JDZm5DHOGKm-5IrgHIXlSX1EQg";
const POSTGRES_URL = "postgres://21b02784a718c1f4c615bfa9d4f7c52dad63e24f1f889f99cc486c43ba217e42:sk_HAvgGZqr4UYuJUqa9M-h7@db.prisma.io:5432/?sslmode=require";

// Create a new PrismaClient instance
const prisma = new PrismaClient({
  datasources: {
    db: {
      url: DATABASE_URL
    }
  }
});

async function main() {
  try {
    console.log('Testing database connection...');
    
    // Try to query for users
    const userCount = await prisma.user.count();
    console.log(`Database connection successful! Found ${userCount} users.`);
    
    return process.exit(0);
  } catch (error) {
    console.error('Database connection test failed:');
    console.error(error);
    return process.exit(1);
  } finally {
    await prisma.$disconnect();
  }
}

main();
