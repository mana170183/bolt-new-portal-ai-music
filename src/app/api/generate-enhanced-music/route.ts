import { NextRequest, NextResponse } from 'next/server';
import { MusicGenerationService } from '@/services/aiMusicService';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { 
      prompt = '',
      lyrics = '', 
      mood = 'upbeat', 
      genre = 'pop', 
      instruments = ['piano'], 
      tempo_bpm = 120, 
      duration = 30,
      output_format = 'wav',
      export_stems = false,
      style_complexity = 'moderate',
      key = 'C',
      structure = [],
      template = ''
    } = body;

    // Validate input
    if (!instruments || instruments.length === 0) {
      return NextResponse.json(
        { 
          success: false, 
          error: 'At least one instrument is required' 
        }, 
        { status: 400 }
      );
    }

    // Initialize AI music service
    const musicService = new MusicGenerationService();
    
    // Create comprehensive prompt from all inputs
    const comprehensivePrompt = prompt || `Create a ${genre} song in ${key} major with ${mood} mood, featuring ${instruments.join(', ')}, at ${tempo_bpm} BPM for ${duration} seconds`;
    
    // Generate enhanced music using AI service
    const result = await musicService.generateMusic({
      prompt: comprehensivePrompt,
      genre,
      mood,
      duration,
      instruments,
      structure,
      template,
      bpm: tempo_bpm,
      key
    });

    if (!result.success) {
      return NextResponse.json({
        success: false,
        error: result.error || 'Failed to generate enhanced music'
      }, { status: 500 });
    }

    // If generation is immediate (mock provider)
    if (result.status === 'completed' && result.audioUrl) {
      const trackId = result.trackId;
      const enhancedTrack = {
        id: trackId,
        title: `${genre?.charAt(0).toUpperCase() + genre?.slice(1)} Composition`,
        lyrics: lyrics,
        genre: genre,
        mood: mood,
        instruments: instruments,
        tempo_bpm: tempo_bpm,
        duration: duration,
        key: key,
        structure: structure.join('-') || 'intro-verse-chorus-outro',
        url: result.audioUrl,
        download_url: result.audioUrl,
        audio_file: `${trackId}.wav`,
        output_format: output_format,
        export_stems: export_stems,
        style_complexity: style_complexity,
        template: template,
        waveform: Array.from({ length: 100 }, () => Math.random() * 100),
        created_at: new Date().toISOString(),
        status: 'completed',
        metadata: {
          lyrics: lyrics,
          genre: genre,
          mood: mood,
          instruments: instruments,
          tempo_bpm: tempo_bpm,
          duration: duration,
          key: key,
          structure: structure.join('-') || 'intro-verse-chorus-outro',
          style_complexity: style_complexity,
          title: `${genre?.charAt(0).toUpperCase() + genre?.slice(1)} Composition`,
          filename: `${trackId}.wav`
        }
      };

      return NextResponse.json({
        success: true,
        track: enhancedTrack,
        download_url: enhancedTrack.download_url,
        audio_file: enhancedTrack.audio_file,
        metadata: enhancedTrack.metadata,
        message: 'Enhanced composition generated successfully!'
      });
    }

    // If generation is async (real AI providers)
    return NextResponse.json({
      success: true,
      trackId: result.trackId,
      status: result.status,
      estimatedTime: result.estimatedTime,
      message: 'Enhanced music generation started. Use the polling endpoint to check status.',
      pollUrl: `/api/poll-generation/${result.trackId}`
    });

  } catch (error) {
    console.error('Enhanced music generation error:', error);
    return NextResponse.json(
      { 
        success: false, 
        error: 'Internal server error' 
      }, 
      { status: 500 }
    );
  }
}
