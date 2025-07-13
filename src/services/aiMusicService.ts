// AI Music Generation Service Layer
// This handles integration with various AI music generation providers

export interface MusicGenerationRequest {
  prompt: string;
  genre?: string;
  mood?: string;
  duration?: number;
  instruments?: string[];
  structure?: string[];
  template?: string;
  bpm?: number;
  key?: string;
}

export interface MusicGenerationResponse {
  success: boolean;
  trackId: string;
  audioUrl?: string;
  status: 'processing' | 'completed' | 'failed';
  estimatedTime?: number;
  error?: string;
}

export interface PollingResponse {
  success: boolean;
  status: 'processing' | 'completed' | 'failed';
  audioUrl?: string;
  progress?: number;
  error?: string;
}

class MubertProvider {
  private apiKey: string;
  private patToken: string;

  constructor(apiKey: string, patToken: string) {
    this.apiKey = apiKey;
    this.patToken = patToken;
  }

  async generateMusic(request: MusicGenerationRequest): Promise<MusicGenerationResponse> {
    try {
      const response = await fetch('https://api.mubert.com/v2/RecordTrack', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          method: 'RecordTrack',
          params: {
            pat: this.patToken,
            duration: request.duration || 30,
            tags: `${request.genre || 'electronic'},${request.mood || 'energetic'}`,
            mode: 'loop',
            bitrate: 320
          }
        })
      });

      const data = await response.json();

      if (data.error) {
        throw new Error(data.error.message || 'Mubert API error');
      }

      return {
        success: true,
        trackId: data.data.id,
        status: 'processing',
        estimatedTime: request.duration || 30
      };
    } catch (error) {
      return {
        success: false,
        trackId: '',
        status: 'failed',
        error: error.message
      };
    }
  }

  async pollGeneration(trackId: string): Promise<PollingResponse> {
    try {
      const response = await fetch('https://api.mubert.com/v2/TrackStatus', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          method: 'TrackStatus',
          params: {
            pat: this.patToken,
            track_id: trackId
          }
        })
      });

      const data = await response.json();

      if (data.error) {
        return {
          success: false,
          status: 'failed',
          error: data.error.message
        };
      }

      const status = data.data.status;
      const audioUrl = data.data.download_url;

      return {
        success: true,
        status: status === 'ready' ? 'completed' : 'processing',
        audioUrl: status === 'ready' ? audioUrl : undefined,
        progress: status === 'ready' ? 100 : undefined
      };
    } catch (error) {
      return {
        success: false,
        status: 'failed',
        error: error.message
      };
    }
  }
}

class SunoProvider {
  private apiKey: string;

  constructor(apiKey: string) {
    this.apiKey = apiKey;
  }

  async generateMusic(request: MusicGenerationRequest): Promise<MusicGenerationResponse> {
    try {
      const response = await fetch('https://api.suno.ai/generate', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: request.prompt,
          duration: request.duration || 30,
          genre: request.genre,
          mood: request.mood,
          instruments: request.instruments
        })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Suno API error');
      }

      return {
        success: true,
        trackId: data.id,
        status: 'processing',
        estimatedTime: 60 // Suno typically takes ~60 seconds
      };
    } catch (error) {
      return {
        success: false,
        trackId: '',
        status: 'failed',
        error: error.message
      };
    }
  }

  async pollGeneration(trackId: string): Promise<PollingResponse> {
    try {
      const response = await fetch(`https://api.suno.ai/status/${trackId}`, {
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
        }
      });

      const data = await response.json();

      if (!response.ok) {
        return {
          success: false,
          status: 'failed',
          error: data.error || 'Suno API error'
        };
      }

      return {
        success: true,
        status: data.status === 'completed' ? 'completed' : 'processing',
        audioUrl: data.status === 'completed' ? data.audio_url : undefined,
        progress: data.progress
      };
    } catch (error) {
      return {
        success: false,
        status: 'failed',
        error: error.message
      };
    }
  }
}

class MockProvider {
  async generateMusic(request: MusicGenerationRequest): Promise<MusicGenerationResponse> {
    // Simulate processing time
    await new Promise(resolve => setTimeout(resolve, 2000));

    const trackId = `mock_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    return {
      success: true,
      trackId,
      status: 'completed',
      audioUrl: 'http://localhost:3000/api/demo-audio'
    };
  }

  async pollGeneration(trackId: string): Promise<PollingResponse> {
    return {
      success: true,
      status: 'completed',
      audioUrl: 'http://localhost:3000/api/demo-audio',
      progress: 100
    };
  }
}

export class MusicGenerationService {
  private provider: MubertProvider | SunoProvider | MockProvider;

  constructor() {
    const providerType = process.env.AI_MUSIC_PROVIDER || 'mock';

    switch (providerType) {
      case 'mubert':
        if (!process.env.MUBERT_API_KEY || !process.env.MUBERT_PAT_TOKEN) {
          console.warn('Mubert credentials not found, falling back to mock provider');
          this.provider = new MockProvider();
        } else {
          this.provider = new MubertProvider(
            process.env.MUBERT_API_KEY,
            process.env.MUBERT_PAT_TOKEN
          );
        }
        break;
      
      case 'suno':
        if (!process.env.SUNO_API_KEY) {
          console.warn('Suno API key not found, falling back to mock provider');
          this.provider = new MockProvider();
        } else {
          this.provider = new SunoProvider(process.env.SUNO_API_KEY);
        }
        break;
      
      default:
        this.provider = new MockProvider();
    }
  }

  async generateMusic(request: MusicGenerationRequest): Promise<MusicGenerationResponse> {
    return this.provider.generateMusic(request);
  }

  async pollGeneration(trackId: string): Promise<PollingResponse> {
    return this.provider.pollGeneration(trackId);
  }
}
