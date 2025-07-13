import { NextResponse } from 'next/server';

export async function GET() {
  try {
    const templates = [
      {
        id: '1',
        name: 'Pop Song Structure',
        description: 'Classic verse-chorus-verse-chorus-bridge-chorus structure',
        sections: ['Intro', 'Verse 1', 'Chorus', 'Verse 2', 'Chorus', 'Bridge', 'Chorus', 'Outro'],
        duration: 180,
        bpm: 120
      },
      {
        id: '2',
        name: 'Electronic Dance',
        description: 'High-energy electronic music template',
        sections: ['Intro', 'Build-up', 'Drop', 'Breakdown', 'Build-up', 'Drop', 'Outro'],
        duration: 240,
        bpm: 128
      },
      {
        id: '3',
        name: 'Jazz Standard',
        description: 'Traditional jazz composition structure',
        sections: ['Head', 'Solo Section', 'Trading Fours', 'Head Out'],
        duration: 300,
        bpm: 140
      },
      {
        id: '4',
        name: 'Ambient Soundscape',
        description: 'Atmospheric and evolving ambient composition',
        sections: ['Emergence', 'Development', 'Climax', 'Resolution'],
        duration: 360,
        bpm: 80
      },
      {
        id: '5',
        name: 'Rock Anthem',
        description: 'Power-driven rock composition structure',
        sections: ['Intro Riff', 'Verse', 'Pre-Chorus', 'Chorus', 'Verse', 'Chorus', 'Guitar Solo', 'Chorus', 'Outro'],
        duration: 220,
        bpm: 130
      },
      {
        id: '6',
        name: 'Classical Sonata',
        description: 'Traditional sonata form structure',
        sections: ['Exposition', 'Development', 'Recapitulation'],
        duration: 480,
        bpm: 100
      },
      {
        id: '7',
        name: 'Hip Hop Track',
        description: 'Modern hip hop composition structure',
        sections: ['Intro', 'Verse 1', 'Hook', 'Verse 2', 'Hook', 'Bridge', 'Hook', 'Outro'],
        duration: 200,
        bpm: 85
      },
      {
        id: '8',
        name: 'Cinematic Score',
        description: 'Dramatic film score structure',
        sections: ['Opening Theme', 'Development', 'Tension Build', 'Climax', 'Resolution'],
        duration: 400,
        bpm: 110
      }
    ];

    return NextResponse.json({
      success: true,
      templates
    });
  } catch (error) {
    console.error('Error in composition-templates API:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to fetch composition templates' },
      { status: 500 }
    );
  }
}
