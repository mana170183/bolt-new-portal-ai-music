import { NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';

export async function GET() {
  try {
    // Connect to the database
    await prisma.$connect();
    
    // Get all users (limited to 10 for safety)
    const users = await prisma.user.findMany({
      take: 10,
      select: {
        id: true,
        email: true,
        firstName: true,
        lastName: true,
        createdAt: true,
      },
    });
    
    return NextResponse.json({
      success: true,
      users,
      count: users.length,
    });
  } catch (error) {
    console.error('Error retrieving users:', error);
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : String(error),
      },
      { status: 500 }
    );
  } finally {
    await prisma.$disconnect();
  }
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { clerkId, email, firstName, lastName, imageUrl } = body;
    
    if (!clerkId || !email) {
      return NextResponse.json(
        { success: false, error: 'clerkId and email are required' },
        { status: 400 }
      );
    }
    
    // Create a new user
    const user = await prisma.user.create({
      data: {
        clerkId,
        email,
        firstName: firstName || null,
        lastName: lastName || null,
        imageUrl: imageUrl || null,
      },
    });
    
    return NextResponse.json({
      success: true,
      user,
    }, { status: 201 });
  } catch (error) {
    console.error('Error creating user:', error);
    
    // Check for unique constraint violation
    if (error instanceof Error && error.message.includes('Unique constraint')) {
      return NextResponse.json(
        { success: false, error: 'User with this clerkId or email already exists' },
        { status: 409 }
      );
    }
    
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : String(error),
      },
      { status: 500 }
    );
  }
}
