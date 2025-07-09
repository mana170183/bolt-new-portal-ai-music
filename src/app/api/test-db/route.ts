import { NextResponse } from 'next/server';
import prisma from '@/lib/prisma-serverless';

export const dynamic = 'force-dynamic'; // Makes sure the route is not cached

export async function GET() {
  try {
    // Try to run a simple query with better error handling
    let userCount = 0;
    
    try {
      // Use a more direct query that returns a number
      const result = await prisma.user.count();
      userCount = result;
    } catch (err) {
      console.error('Prisma count error:', err);
      // If count fails, try a raw query but convert BigInt to number
      const rawResult = await prisma.$queryRaw`SELECT COUNT(*) as count FROM users`;
      userCount = Number((rawResult as any)[0]?.count || 0);
    }
    
    // Database connection succeeded
    return NextResponse.json(
      { 
        success: true, 
        message: 'Database connection successful',
        count: userCount,
        db_provider: 'postgres',
        prisma_version: '6.11.1',
        timestamp: new Date().toISOString(),
      }, 
      { status: 200 }
    );
  } catch (error) {
    console.error('Database connection error:', error);
    
    // Provide more helpful error message and debugging info
    return NextResponse.json(
      { 
        success: false, 
        message: 'Database connection failed',
        error: error instanceof Error ? error.message : String(error),
        env_check: {
          has_url: !!process.env.PRISMA_DATABASE_URL || !!process.env.DATABASE_URL,
          has_postgres_url: !!process.env.POSTGRES_URL,
          node_env: process.env.NODE_ENV
        },
        timestamp: new Date().toISOString(),
      }, 
      { status: 500 }
    );
  }
}
