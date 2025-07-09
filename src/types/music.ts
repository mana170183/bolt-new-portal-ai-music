export interface MusicGenerationRequest {
  prompt: string;
  lyrics?: string;
  genre: string;
  mood: string;
  duration: number;
  tempo?: number;
  keySignature?: string;
  timeSignature?: string;
  instruments: string[];
  style?: string;
  userId: string;
}

export interface CompositionResult {
  id: string;
  title: string;
  audioUrl: string;
  stemUrls?: Record<string, string>;
  waveformData?: number[];
  metadata: CompositionMetadata;
  status: 'generating' | 'completed' | 'failed';
}

export interface CompositionMetadata {
  duration: number;
  sampleRate: number;
  bitrate: number;
  format: string;
  bpm: number;
  key: string;
  timeSignature: string;
  instruments: string[];
  generatedAt: string;
  generationModel: string;
}

export interface AudioStem {
  name: string;
  instrument: string;
  url: string;
  volume: number;
  muted: boolean;
  soloed: boolean;
}

export interface GenerationProgress {
  stage: 'initializing' | 'generating' | 'processing' | 'finalizing' | 'complete';
  progress: number; // 0-100
  message: string;
  estimatedTimeRemaining?: number;
}

export interface StyleTransferRequest {
  compositionId: string;
  targetStyle: string;
  intensity: number; // 0.0 to 1.0
}

export interface UserPreferences {
  favoriteGenres: string[];
  favoriteMoods: string[];
  defaultDuration: number;
  defaultTempo: number;
  defaultInstruments: string[];
  aiPersonality: 'creative' | 'balanced' | 'precise';
  exportFormat: 'mp3' | 'wav' | 'flac' | 'midi';
  quality: 'low' | 'medium' | 'high' | 'lossless';
}

export interface CollaborationSession {
  id: string;
  compositionId: string;
  participants: Participant[];
  activeEdits: ActiveEdit[];
  isLive: boolean;
}

export interface Participant {
  userId: string;
  username: string;
  role: 'owner' | 'editor' | 'viewer';
  isOnline: boolean;
  cursor?: {
    position: number;
    timestamp: number;
  };
}

export interface ActiveEdit {
  id: string;
  userId: string;
  type: 'tempo' | 'volume' | 'instrument' | 'effects';
  target: string; // what's being edited
  value: any;
  timestamp: number;
}

export interface ExportOptions {
  format: 'mp3' | 'wav' | 'flac' | 'midi' | 'stems';
  quality: 'low' | 'medium' | 'high' | 'lossless';
  includeStems: boolean;
  includeMidi: boolean;
  sampleRate?: number;
  bitrate?: number;
}

export interface AIFeedback {
  compositionId: string;
  rating: number; // 1-5
  aspects: {
    melody: number;
    harmony: number;
    rhythm: number;
    arrangement: number;
    production: number;
  };
  suggestions: string[];
  userNotes?: string;
}

export interface APIProvider {
  name: string;
  enabled: boolean;
  priority: number;
  capabilities: string[];
  rateLimit: number;
  costPerGeneration: number;
}

export type MusicGenre = 
  | 'pop' | 'rock' | 'jazz' | 'blues' | 'classical' | 'electronic' 
  | 'hip-hop' | 'country' | 'folk' | 'reggae' | 'metal' | 'punk'
  | 'indie' | 'ambient' | 'house' | 'techno' | 'dubstep' | 'trap';

export type MusicMood = 
  | 'happy' | 'sad' | 'energetic' | 'calm' | 'mysterious' | 'romantic'
  | 'aggressive' | 'melancholic' | 'uplifting' | 'dark' | 'nostalgic'
  | 'peaceful' | 'intense' | 'playful' | 'dramatic' | 'dreamy';

export type Instrument = 
  | 'piano' | 'guitar' | 'bass' | 'drums' | 'violin' | 'saxophone'
  | 'trumpet' | 'cello' | 'flute' | 'synthesizer' | 'organ' | 'harp'
  | 'accordion' | 'banjo' | 'mandolin' | 'harmonica' | 'xylophone';
