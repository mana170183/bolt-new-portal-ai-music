import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const page = parseInt(searchParams.get('page') || '1');
    const limit = parseInt(searchParams.get('limit') || '10');

    // Mock data for now - replace with actual database queries
    const compositions = [
      {
        id: '1',
        title: 'Sample Composition 1',
        description: 'A beautiful orchestral piece',
        createdAt: new Date().toISOString(),
        userId: 'mock-user',
        tracks: []
      }
    ];

    return NextResponse.json({
      success: true,
      compositions,
      pagination: {
        page,
        limit,
        total: compositions.length,
        pages: Math.ceil(compositions.length / limit),
      },
    });
  } catch (error) {
    console.error('Error fetching compositions:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { title, description, tracks } = body;

    // Mock creation - replace with actual database creation
    const composition = {
      id: Date.now().toString(),
      title,
      description,
      tracks: tracks || [],
      createdAt: new Date().toISOString(),
      userId: 'mock-user'
    };

    return NextResponse.json({
      success: true,
      composition,
    });
  } catch (error) {
    console.error('Error creating composition:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
