// Configuration management for AI Music Portal
// This file centralizes all configuration to prevent repeated issues

const isDevelopment = import.meta.env.MODE === 'development';
const isProduction = import.meta.env.MODE === 'production';

// API Configuration
export const API_CONFIG = {
  // Base URLs
  BASE_URL: isDevelopment 
    ? 'http://localhost:5002/api'
    : 'https://portal-ai-music-backend.azurewebsites.net/api',
  
  // Audio serving URL
  AUDIO_BASE_URL: isDevelopment
    ? 'http://localhost:5002/audio'
    : 'https://portal-ai-music-backend.azurewebsites.net/audio',
    
  // Frontend URL
  FRONTEND_URL: isDevelopment
    ? 'http://localhost:3000'
    : 'https://portal-ai-music.azurewebsites.net',
    
  // API Timeouts
  TIMEOUT: 5000, // Reduced to 5 seconds for faster fallback
  
  // Request retry configuration
  RETRY_ATTEMPTS: 2,
  RETRY_DELAY: 500, // 500ms
};

// Audio Configuration
export const AUDIO_CONFIG = {
  // Supported formats
  SUPPORTED_FORMATS: ['wav', 'mp3', 'ogg'],
  
  // Default audio settings
  DEFAULT_VOLUME: 0.8,
  DEFAULT_PLAYBACK_RATE: 1.0,
  
  // Audio constraints
  MAX_DURATION: 300, // 5 minutes
  MIN_DURATION: 15,  // 15 seconds
  
  // Audio quality settings
  SAMPLE_RATE: 44100,
  BIT_DEPTH: 16,
  CHANNELS: 2, // Stereo
};

// Music Generation Configuration
export const MUSIC_CONFIG = {
  // Default parameters
  DEFAULT_GENRE: 'electronic',
  DEFAULT_MOOD: 'energetic',
  DEFAULT_TEMPO: 120,
  DEFAULT_KEY: 'C',
  DEFAULT_DURATION: 60,
  
  // Available options
  GENRES: [
    'pop', 'rock', 'electronic', 'classical', 'jazz', 'blues', 'country', 
    'hip-hop', 'reggae', 'folk', 'ambient', 'techno', 'house', 'trance'
  ],
  
  MOODS: [
    'happy', 'sad', 'energetic', 'calm', 'mysterious', 'romantic', 
    'aggressive', 'melancholic', 'uplifting', 'dramatic', 'peaceful', 'intense'
  ],
  
  INSTRUMENTS: [
    { id: 'piano', name: 'Piano' },
    { id: 'guitar', name: 'Guitar' },
    { id: 'drums', name: 'Drums' },
    { id: 'bass', name: 'Bass' },
    { id: 'synthesizer', name: 'Synthesizer' },
    { id: 'vocals', name: 'Vocals' },
    { id: 'strings', name: 'Strings' },
    { id: 'brass', name: 'Brass' },
    { id: 'flute', name: 'Flute' },
    { id: 'saxophone', name: 'Saxophone' }
  ],
  
  EFFECTS: [
    'reverb', 'delay', 'chorus', 'distortion', 'compressor', 
    'equalizer', 'flanger', 'phaser', 'tremolo', 'vibrato'
  ],
  
  STRUCTURES: [
    'verse-chorus-verse-chorus',
    'verse-chorus-verse-chorus-bridge-chorus',
    'intro-verse-chorus-verse-chorus-bridge-chorus-outro',
    'a-b-a-b-c-b',
    'custom'
  ],
  
  // Tempo constraints
  MIN_TEMPO: 60,
  MAX_TEMPO: 200,
  
  // Key signatures
  KEYS: ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
};

// Azure Configuration
export const AZURE_CONFIG = {
  // Service Principal credentials
  SP_APP_ID: "6a069624-67ed-4bfe-b4e6-301f6e02a853",
  SP_TENANT: "bca013b2-c163-4a0d-ad43-e6f1d3cda34b",
  
  // Resource Group
  RESOURCE_GROUP: "rg-portal-ai-music",
  
  // Storage Account
  STORAGE_ACCOUNT: "portalaimusicstg",
  STORAGE_CONTAINER: "audio-files",
  
  // SQL Database
  SQL_SERVER: "portal-ai-music-sql.database.windows.net",
  SQL_DATABASE: "portal-ai-music-db",
  
  // App Services
  BACKEND_APP_SERVICE: "portal-ai-music-backend",
  FRONTEND_APP_SERVICE: "portal-ai-music-frontend",
  
  // Regions
  PRIMARY_REGION: "East US",
  SECONDARY_REGION: "West US 2"
};

// External API Configuration
export const EXTERNAL_API_CONFIG = {
  // Jamendo API
  JAMENDO: {
    BASE_URL: 'https://api.jamendo.com/v3.0',
    CLIENT_ID: 'b6747d04', // Free tier client ID
    FORMAT: 'json',
    LIMIT: 10
  },
  
  // Spotify API (requires authentication)
  SPOTIFY: {
    BASE_URL: 'https://api.spotify.com/v1',
    AUTH_URL: 'https://accounts.spotify.com/api/token',
    SCOPE: 'user-read-private user-read-email'
  },
  
  // Freesound API
  FREESOUND: {
    BASE_URL: 'https://freesound.org/apiv2',
    // Note: Requires API key registration
  },
  
  // MusicBrainz API
  MUSICBRAINZ: {
    BASE_URL: 'https://musicbrainz.org/ws/2',
    FORMAT: 'json',
    USER_AGENT: 'PortalAIMusic/1.0.0'
  }
};

// UI Configuration
export const UI_CONFIG = {
  // Theme colors
  COLORS: {
    PRIMARY: '#8B5CF6', // Purple
    SECONDARY: '#06B6D4', // Cyan
    SUCCESS: '#10B981', // Green
    WARNING: '#F59E0B', // Amber
    ERROR: '#EF4444', // Red
    DARK: '#1F2937', // Dark gray
    LIGHT: '#F9FAFB' // Light gray
  },
  
  // Animation durations
  ANIMATIONS: {
    FAST: 150,
    NORMAL: 300,
    SLOW: 500
  },
  
  // Breakpoints
  BREAKPOINTS: {
    SM: '640px',
    MD: '768px',
    LG: '1024px',
    XL: '1280px'
  }
};

// Feature Flags
export const FEATURES = {
  // Core features
  MUSIC_GENERATION: true,
  ADVANCED_STUDIO: true,
  MUSIC_LIBRARY: true,
  DEMO_TRACKS: true,
  
  // Premium features
  UNLIMITED_GENERATION: false,
  HIGH_QUALITY_AUDIO: false,
  COMMERCIAL_LICENSE: false,
  
  // External integrations
  SPOTIFY_INTEGRATION: true,
  JAMENDO_INTEGRATION: true,
  FREESOUND_INTEGRATION: false, // Requires API key
  MUSICBRAINZ_INTEGRATION: true,
  
  // Azure features
  AZURE_STORAGE: false, // Will enable after setup
  AZURE_SQL: false, // Will enable after setup
  AZURE_DEPLOYMENT: false // Will enable after deployment
};

// Environment-specific overrides
if (isProduction) {
  // Enable Azure features in production
  FEATURES.AZURE_STORAGE = true;
  FEATURES.AZURE_SQL = true;
  FEATURES.AZURE_DEPLOYMENT = true;
}

// Validation functions
export const validateConfig = () => {
  const errors = [];
  
  if (!API_CONFIG.BASE_URL) {
    errors.push('API_CONFIG.BASE_URL is required');
  }
  
  if (!AUDIO_CONFIG.SAMPLE_RATE) {
    errors.push('AUDIO_CONFIG.SAMPLE_RATE is required');
  }
  
  if (FEATURES.AZURE_STORAGE && !AZURE_CONFIG.STORAGE_ACCOUNT) {
    errors.push('AZURE_CONFIG.STORAGE_ACCOUNT is required when Azure Storage is enabled');
  }
  
  return errors;
};

// Configuration initialization
export const initializeConfig = () => {
  const errors = validateConfig();
  
  if (errors.length > 0) {
    console.error('Configuration validation failed:', errors);
    throw new Error(`Configuration validation failed: ${errors.join(', ')}`);
  }
  
  console.log('Configuration initialized successfully');
  console.log('Environment:', isDevelopment ? 'Development' : 'Production');
  console.log('API Base URL:', API_CONFIG.BASE_URL);
  console.log('Features enabled:', Object.entries(FEATURES).filter(([, enabled]) => enabled).map(([name]) => name));
  
  return true;
};

// Export default configuration
export default {
  API_CONFIG,
  AUDIO_CONFIG,
  MUSIC_CONFIG,
  AZURE_CONFIG,
  EXTERNAL_API_CONFIG,
  UI_CONFIG,
  FEATURES,
  isDevelopment,
  isProduction,
  validateConfig,
  initializeConfig
};
