import { NextResponse } from 'next/server';

const moods = [
  { id: 'upbeat', name: 'Upbeat', description: 'Energetic and positive vibes' },
  { id: 'relaxed', name: 'Relaxed', description: 'Calm and soothing atmosphere' },
  { id: 'dramatic', name: 'Dramatic', description: 'Intense and powerful emotions' },
  { id: 'melancholic', name: 'Melancholic', description: 'Sad and contemplative mood' },
  { id: 'romantic', name: 'Romantic', description: 'Love and intimate feelings' },
  { id: 'mysterious', name: 'Mysterious', description: 'Dark and enigmatic atmosphere' },
  { id: 'epic', name: 'Epic', description: 'Grand and cinematic feel' },
  { id: 'cheerful', name: 'Cheerful', description: 'Happy and lighthearted vibes' },
  { id: 'aggressive', name: 'Aggressive', description: 'Bold and fierce energy' },
  { id: 'nostalgic', name: 'Nostalgic', description: 'Wistful and reminiscent mood' },
];

export async function GET() {
  try {
    return NextResponse.json({
      success: true,
      moods,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error('Error fetching moods:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to fetch moods' },
      { status: 500 }
    );
  }
}
