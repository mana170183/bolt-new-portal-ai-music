import { NextResponse } from 'next/server';

const templates = {
  'pop_ballad': {
    name: 'Pop Ballad',
    description: 'Emotional pop song with slow tempo',
    genre: 'pop',
    mood: 'romantic',
    tempo_range: [60, 80],
    instruments: ['piano', 'strings', 'soft_drums'],
    structure: ['intro', 'verse', 'chorus', 'verse', 'chorus', 'bridge', 'chorus', 'outro']
  },
  'rock_anthem': {
    name: 'Rock Anthem',
    description: 'Powerful rock song with driving energy',
    genre: 'rock', 
    mood: 'epic',
    tempo_range: [120, 140],
    instruments: ['electric_guitar', 'bass', 'drums', 'vocals'],
    structure: ['intro', 'verse', 'chorus', 'verse', 'chorus', 'solo', 'chorus', 'outro']
  },
  'jazz_standard': {
    name: 'Jazz Standard',
    description: 'Classic jazz composition with improvisation',
    genre: 'jazz',
    mood: 'relaxed',
    tempo_range: [100, 120],
    instruments: ['piano', 'saxophone', 'bass', 'drums'],
    structure: ['intro', 'theme', 'improvisation', 'theme', 'outro']
  },
  'electronic_dance': {
    name: 'Electronic Dance',
    description: 'High-energy electronic dance track',
    genre: 'electronic',
    mood: 'upbeat',
    tempo_range: [128, 140],
    instruments: ['synthesizer', 'electronic_drums', 'bass', 'lead_synth'],
    structure: ['intro', 'buildup', 'drop', 'verse', 'buildup', 'drop', 'breakdown', 'outro']
  }
};

export async function GET() {
  try {
    return NextResponse.json({
      success: true,
      templates,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error('Error fetching composition templates:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to fetch composition templates' },
      { status: 500 }
    );
  }
}
