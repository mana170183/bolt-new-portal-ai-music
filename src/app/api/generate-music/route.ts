import { NextRequest, NextResponse } from 'next/server';
import { MusicGenerationService } from '@/services/aiMusicService';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { prompt, genre, mood, duration = 30 } = body;

    // Validate input
    if (!prompt || !prompt.trim()) {
      return NextResponse.json(
        { 
          success: false, 
          error: 'Prompt is required' 
        }, 
        { status: 400 }
      );
    }

    // Initialize AI music service
    const musicService = new MusicGenerationService();
    
    // Generate music using AI service
    const result = await musicService.generateMusic({
      prompt,
      genre,
      mood,
      duration
    });

    if (!result.success) {
      return NextResponse.json({
        success: false,
        error: result.error || 'Failed to generate music'
      }, { status: 500 });
    }

    // If generation is immediate (mock provider)
    if (result.status === 'completed' && result.audioUrl) {
      const generatedTrack = {
        id: result.trackId,
        title: `Generated Track - ${prompt.slice(0, 30)}...`,
        prompt: prompt,
        genre: genre || 'Electronic',
        mood: mood || 'Happy',
        duration: duration,
        url: result.audioUrl,
        download_url: result.audioUrl,
        audio_file: `${result.trackId}.wav`,
        waveform: Array.from({ length: 100 }, () => Math.random() * 100),
        created_at: new Date().toISOString(),
        status: 'completed',
        metadata: {
          prompt: prompt,
          genre: genre || 'Electronic',
          mood: mood || 'Happy',
          duration: duration,
          filename: `${result.trackId}.wav`
        }
      };

      return NextResponse.json({
        success: true,
        download_url: generatedTrack.download_url,
        audio_file: generatedTrack.audio_file,
        metadata: generatedTrack.metadata,
        message: 'Music generated successfully!'
      });
    }

    // If generation is async (real AI providers)
    return NextResponse.json({
      success: true,
      trackId: result.trackId,
      status: result.status,
      estimatedTime: result.estimatedTime,
      message: 'Music generation started. Use the polling endpoint to check status.',
      pollUrl: `/api/poll-generation/${result.trackId}`
    });

  } catch (error) {
    console.error('Music generation error:', error);
    return NextResponse.json(
      { 
        success: false, 
        error: 'Internal server error' 
      }, 
      { status: 500 }
    );
  }
}
