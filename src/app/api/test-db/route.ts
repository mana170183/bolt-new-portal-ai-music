import { NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';

export async function GET() {
  try {
    // Try to perform a simple operation to test connection
    const count = await prisma.user.count();
    
    return NextResponse.json(
      { 
        success: true, 
        message: 'Database connection successful',
        count: count,
        timestamp: new Date().toISOString(),
      }, 
      { status: 200 }
    );
  } catch (error) {
    console.error('Database connection error:', error);
    return NextResponse.json(
      { 
        success: false, 
        message: 'Failed to connect to database', 
        error: error instanceof Error ? error.message : String(error),
        timestamp: new Date().toISOString(),
      }, 
      { status: 500 }
    );
  }
}
