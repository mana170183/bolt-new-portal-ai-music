// This is a fallback implementation of the /api/moods endpoint
// to prevent 404 errors during initialization

import { NextResponse } from 'next/server';

export async function GET() {
  // Default moods data
  const moods = [
    {id: 'upbeat', name: 'Upbeat', description: 'Happy, energetic feeling'},
    {id: 'calm', name: 'Calm', description: 'Peaceful, relaxing'},
    {id: 'energetic', name: 'Energetic', description: 'High-energy, motivating'},
    {id: 'melancholic', name: 'Melancholic', description: 'Sad, reflective'},
    {id: 'romantic', name: 'Romantic', description: 'Loving, passionate'},
    {id: 'dark', name: 'Dark', description: 'Ominous, mysterious'},
    {id: 'epic', name: 'Epic', description: 'Grand, powerful'}
  ];

  return NextResponse.json({ 
    success: true, 
    moods
  });
}
