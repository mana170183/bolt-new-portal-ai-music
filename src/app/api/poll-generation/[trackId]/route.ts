import { NextRequest, NextResponse } from 'next/server';
import { MusicGenerationService } from '@/services/aiMusicService';

export async function GET(
  request: NextRequest,
  { params }: { params: { trackId: string } }
) {
  try {
    const { trackId } = params;

    if (!trackId) {
      return NextResponse.json(
        { 
          success: false, 
          error: 'Track ID is required' 
        }, 
        { status: 400 }
      );
    }

    // Initialize AI music service
    const musicService = new MusicGenerationService();
    
    // Poll generation status
    const result = await musicService.pollGeneration(trackId);

    if (!result.success) {
      return NextResponse.json({
        success: false,
        error: result.error || 'Failed to check generation status'
      }, { status: 500 });
    }

    // If still processing
    if (result.status === 'processing') {
      return NextResponse.json({
        success: true,
        status: 'processing',
        progress: result.progress || 0,
        message: 'Music generation in progress...',
        retryAfter: 5 // seconds
      });
    }

    // If completed
    if (result.status === 'completed' && result.audioUrl) {
      const generatedTrack = {
        id: trackId,
        title: `Generated Track`,
        url: result.audioUrl,
        download_url: result.audioUrl,
        audio_file: `${trackId}.wav`,
        waveform: Array.from({ length: 100 }, () => Math.random() * 100),
        created_at: new Date().toISOString(),
        status: 'completed'
      };

      return NextResponse.json({
        success: true,
        status: 'completed',
        download_url: generatedTrack.download_url,
        audio_file: generatedTrack.audio_file,
        track: generatedTrack,
        message: 'Music generated successfully!'
      });
    }

    // If failed
    return NextResponse.json({
      success: false,
      status: 'failed',
      error: 'Music generation failed'
    }, { status: 500 });

  } catch (error) {
    console.error('Polling error:', error);
    return NextResponse.json(
      { 
        success: false, 
        error: 'Internal server error' 
      }, 
      { status: 500 }
    );
  }
}
