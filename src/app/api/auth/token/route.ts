import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { user_id, plan } = body;
    
    // For now, return a mock token
    // In production, this would integrate with your authentication system
    const mockToken = `demo_token_${user_id}_${Date.now()}`;
    
    return NextResponse.json({
      success: true,
      token: mockToken,
      user_id,
      plan,
      expires_in: 3600,
    });
  } catch (error) {
    console.error('Error generating token:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to generate token' },
      { status: 500 }
    );
  }
}
