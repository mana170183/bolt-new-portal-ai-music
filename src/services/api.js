import axios from 'axios';
import { API_CONFIG, EXTERNAL_API_CONFIG, FEATURES, initializeConfig } from '../config/index.js';

// Initialize configuration
initializeConfig();

// Create axios instance with centralized config
const api = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  timeout: API_CONFIG.TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Token management
let authToken = localStorage.getItem('auth_token');

// Mock data for fallback when API is not available
const MOCK_DATA = {
  health: {
    status: 'healthy',
    message: 'AI Music Backend API is running (Mock Mode)',
    version: '2.0.0',
    timestamp: new Date().toISOString(),
    backend: 'Mock/Fallback'
  },
  genres: [
    { id: 'pop', name: 'Pop', description: 'Modern popular music' },
    { id: 'rock', name: 'Rock', description: 'Rock and alternative music' },
    { id: 'electronic', name: 'Electronic', description: 'Electronic and dance music' },
    { id: 'jazz', name: 'Jazz', description: 'Jazz and blues' },
    { id: 'classical', name: 'Classical', description: 'Classical and orchestral' },
    { id: 'hiphop', name: 'Hip Hop', description: 'Hip hop and rap' },
    { id: 'ambient', name: 'Ambient', description: 'Ambient and atmospheric' },
    { id: 'folk', name: 'Folk', description: 'Folk and acoustic' }
  ],
  moods: [
    { id: 'happy', name: 'Happy', description: 'Upbeat and joyful' },
    { id: 'sad', name: 'Sad', description: 'Melancholic and emotional' },
    { id: 'energetic', name: 'Energetic', description: 'High energy and motivating' },
    { id: 'relaxed', name: 'Relaxed', description: 'Calm and peaceful' },
    { id: 'dramatic', name: 'Dramatic', description: 'Intense and powerful' },
    { id: 'mysterious', name: 'Mysterious', description: 'Dark and intriguing' },
    { id: 'romantic', name: 'Romantic', description: 'Love and passion' },
    { id: 'nostalgic', name: 'Nostalgic', description: 'Reminiscent and wistful' }
  ]
};

// Fallback function when API is not available
const createMockResponse = (data) => {
  return new Promise(resolve => {
    setTimeout(() => resolve({ data }), 500); // Simulate network delay
  });
};

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    if (authToken) {
      config.headers.Authorization = `Bearer ${authToken}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('auth_token');
      authToken = null;
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  async generateToken(userId = 'demo_user', plan = 'free') {
    try {
      const response = await api.post('/auth-token', {
        user_id: userId,
        plan: plan
      });
      
      if (response.data.success) {
        authToken = response.data.token;
        localStorage.setItem('auth_token', authToken);
      }
      
      return response.data;
    } catch (error) {
      console.error('Token generation failed:', error);
      throw error;
    }
  },

  logout() {
    authToken = null;
    localStorage.removeItem('auth_token');
  },

  isAuthenticated() {
    return !!authToken;
  }
};

// User API
export const userAPI = {
  async getQuota(userId = 'demo_user') {
    try {
      const response = await api.get('/user/quota', {
        params: { user_id: userId }
      });
      return response.data;
    } catch (error) {
      console.error('Failed to get user quota:', error);
      throw error;
    }
  }
};

// Music Generation API
export const musicAPI = {
  async generateMusic(params) {
    try {
      const {
        prompt,
        genre = 'pop',
        mood = 'happy',
        duration = 30,
        style // backward compatibility
      } = params;

      const response = await api.post('/generate-music', {
        prompt,
        genre: genre || style,
        mood,
        duration
      });

      return response.data;
    } catch (error) {
      console.warn('Music generation failed, using mock data:', error.message);
      
      // Create mock response
      const trackId = `track_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      const mockTrack = {
        success: true,
        message: 'Music generated successfully (Mock Mode)',
        track: {
          id: trackId,
          title: `AI Generated - ${prompt?.substring(0, 30) || 'Demo Track'}`,
          duration: duration || 30,
          genre: genre || 'pop',
          mood: mood || 'happy',
          url: `https://www.soundjay.com/misc/sounds/bell-ringing-05.wav`,
          preview_url: `https://www.soundjay.com/misc/sounds/bell-ringing-05.wav`,
          created_at: new Date().toISOString(),
          prompt: prompt || 'Demo music generation'
        }
      };
      
      return createMockResponse(mockTrack).then(res => res.data);
    }
  },

  async generateAdvancedMusic(params) {
    try {
      const {
        prompt,
        genre = 'pop',
        mood = 'happy',
        duration = 60,
        tempo = 120,
        key = 'C',
        instruments = ['piano'],
        vocals = true,
        structure = 'verse-chorus-verse-chorus-bridge-chorus',
        lyricsStyle = 'narrative',
        customTags = []
      } = params;
      
      const response = await api.post('/generate-advanced-music', {
        prompt,
        genre,
        mood,
        duration,
        tempo,
        key,
        instruments,
        vocals,
        structure,
        lyricsStyle,
        customTags
      });

      return response.data;
    } catch (error) {
      console.error('Advanced music generation failed:', error);
      throw error;
    }
  },

  async getGenres() {
    try {
      const response = await api.get('/genres');
      return response.data;
    } catch (error) {
      console.warn('❌ Failed to get genres, using mock data:', error.message);
      return createMockResponse({ genres: MOCK_DATA.genres }).then(res => res.data);
    }
  },

  async getMoods() {
    try {
      const response = await api.get('/moods');
      return response.data;
    } catch (error) {
      console.warn('❌ Failed to get moods, using mock data:', error.message);
      return createMockResponse({ moods: MOCK_DATA.moods }).then(res => res.data);
    }
  },

  async getUserQuota(userId = 'demo_user') {
    try {
      const response = await api.get('/user/quota', {
        params: { user_id: userId }
      });
      return response.data;
    } catch (error) {
      console.warn('Failed to get user quota, using mock data:', error.message);
      
      // Return mock quota data
      const mockQuota = {
        quota: {
          daily_remaining: 50,
          daily_limit: 50,
          monthly_remaining: 500,
          monthly_limit: 500,
          reset_time: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString()
        },
        user: {
          id: userId,
          plan: 'free',
          status: 'active'
        }
      };
      
      return createMockResponse(mockQuota).then(res => res.data);
    }
  },

  async getDemoTracks() {
    try {
      const response = await api.get('/demo-tracks');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch demo tracks:', error);
      // Return mock demo tracks if API fails
      return {
        success: true,
        tracks: [
          {
            id: 'demo_1',
            title: 'Electronic Dreams',
            genre: 'Electronic',
            mood: 'Energetic',
            duration: 45,
            url: 'https://www.soundjay.com/misc/sounds/bell-ringing-05.wav',
            waveform: [0.2, 0.8, 0.4, 0.9, 0.3, 0.7, 0.6, 0.5],
            created_at: '2025-01-20T10:00:00Z'
          }
        ],
        total: 1
      };
    }
  }
};

// Music Library API
export const libraryAPI = {
  async getMusicLibrary(params = {}) {
    try {
      const { userId = 'demo_user', page = 1, limit = 20, ...filters } = params;
      const requestParams = { user_id: userId, page, limit };
      
      // Add filters
      if (filters.genre) requestParams.genre = filters.genre;
      if (filters.mood) requestParams.mood = filters.mood;

      const response = await api.get('/music-library', { params: requestParams });
      return response.data;
    } catch (error) {
      console.warn('Music library fetch failed, using fallback:', error.message);
      // Return mock data as fallback
      return {
        success: true,
        tracks: [
          {
            id: 'mock_1',
            title: "Epic Adventure",
            genre: "orchestral",
            mood: "Epic", 
            duration: 180,
            url: "https://commondatastorage.googleapis.com/codeskulptor-demos/DDR_assets/Kangaroo_MusiQue_-_The_Neverwritten_Role_Playing_Game.mp3",
            created_at: "2024-01-15T10:00:00Z",
            is_favorite: true,
            tags: ["cinematic", "epic", "adventure"]
          },
          {
            id: 'mock_2',
            title: "Calm Meditation",
            genre: "ambient",
            mood: "Peaceful",
            duration: 240,
            url: "https://commondatastorage.googleapis.com/codeskulptor-assets/week7-brrring.m4a",
            created_at: "2024-01-14T15:30:00Z", 
            is_favorite: false,
            tags: ["relaxing", "meditation", "calm"]
          }
        ],
        total: 2,
        page: 1,
        limit: 20,
        has_more: false
      };
    }
  },

  async searchMusicLibrary(params = {}) {
    try {
      const { query, userId = 'demo_user', genre, mood } = params;
      const requestParams = { q: query, user_id: userId };
      
      if (genre) requestParams.genre = genre;
      if (mood) requestParams.mood = mood;

      const response = await api.get('/music-library/search', { params: requestParams });
      return response.data;
    } catch (error) {
      console.warn('Music library search failed:', error.message);
      return { 
        success: false, 
        message: 'Search failed', 
        tracks: [],
        total: 0,
        query: params.query || ''
      };
    }
  },

  async addToFavorites(trackId, userId = 'demo_user') {
    try {
      const response = await api.post('/music-library/favorite', {
        track_id: trackId,
        user_id: userId
      });
      return response.data;
    } catch (error) {
      console.warn('Add to favorites failed:', error.message);
      return { success: true, message: 'Added to favorites (mock)' };
    }
  },

  async removeFromFavorites(trackId, userId = 'demo_user') {
    try {
      const response = await api.delete(`/music-library/favorite/${trackId}`, {
        params: { user_id: userId }
      });
      return response.data;
    } catch (error) {
      console.warn('Remove from favorites failed:', error.message);
      return { success: true, message: 'Removed from favorites (mock)' };
    }
  },

  async deleteTrack(trackId, userId = 'demo_user') {
    try {
      const response = await api.delete(`/music-library/${trackId}`, {
        params: { user_id: userId }
      });
      return response.data;
    } catch (error) {
      console.warn('Delete track failed:', error.message);
      throw error;
    }
  },

  async getTracks(userId = 'demo_user', page = 1, limit = 20, filters = {}) {
    // Alias for getMusicLibrary for backward compatibility
    return this.getMusicLibrary({ userId, page, limit, ...filters });
  },

  async saveTrack(trackId, userId = 'demo_user') {
    // For saving generated tracks to library - implementation would depend on backend
    try {
      const response = await api.post('/music-library/save', {
        track_id: trackId,
        user_id: userId
      });
      return response.data;
    } catch (error) {
      console.warn('Save track failed:', error.message);
      return { success: true, message: 'Track saved (mock)' };
    }
  },

  async removeTrack(trackId, userId = 'demo_user') {
    // Alias for deleteTrack
    return this.deleteTrack(trackId, userId);
  },

  async toggleFavorite(trackId, userId = 'demo_user') {
    try {
      // Check if already favorited (this would need to be implemented in backend)
      const response = await api.post('/music-library/favorite', {
        track_id: trackId,
        user_id: userId
      });
      return response.data;
    } catch (error) {
      console.warn('Toggle favorite failed:', error.message);
      return { success: true, is_favorite: true }; // Optimistic response
    }
  },

  async shareTrack(trackId, shareType = 'link', userId = 'demo_user') {
    try {
      const response = await api.post('/music-library/share', {
        track_id: trackId,
        share_type: shareType,
        user_id: userId
      });
      return response.data;
    } catch (error) {
      console.warn('Share track failed:', error.message);
      return { 
        success: true, 
        share_url: `https://portal-ai-music.com/track/${trackId}`,
        message: 'Share link generated (mock)'
      };
    }
  },

  async downloadTrack(trackId, format = 'wav', userId = 'demo_user') {
    try {
      const response = await api.get(`/music-library/download/${trackId}`, {
        params: { format, user_id: userId }
      });
      return response.data;
    } catch (error) {
      console.warn('Download track failed:', error.message);
      throw error;
    }
  }
};

// External Music APIs Integration
export const externalMusicAPI = {
  async searchSpotify(query, type = 'track', limit = 20) {
    try {
      const response = await api.get('/music-apis/spotify', {
        params: { action: 'search', q: query, type, limit }
      });
      return response.data;
    } catch (error) {
      console.error('Spotify search failed:', error);
      throw error;
    }
  },

  async getSpotifyTrack(trackId) {
    try {
      const response = await api.get('/music-apis/spotify', {
        params: { action: 'track', id: trackId }
      });
      return response.data;
    } catch (error) {
      console.error('Failed to get Spotify track:', error);
      throw error;
    }
  },

  async getSpotifyRecommendations(genres, limit = 20) {
    try {
      const response = await api.get('/music-apis/spotify', {
        params: { action: 'recommendations', genres: genres.join(','), limit }
      });
      return response.data;
    } catch (error) {
      console.error('Failed to get Spotify recommendations:', error);
      throw error;
    }
  },

  async searchMusicBrainz(query, type = 'recording', limit = 20) {
    try {
      const response = await api.get('/music-apis/musicbrainz', {
        params: { action: 'search', q: query, type, limit }
      });
      return response.data;
    } catch (error) {
      console.error('MusicBrainz search failed:', error);
      throw error;
    }
  },

  async searchFreesound(query, limit = 20) {
    try {
      const response = await api.get('/music-apis/freesound', {
        params: { action: 'search', q: query, limit }
      });
      return response.data;
    } catch (error) {
      console.error('Freesound search failed:', error);
      throw error;
    }
  },

  async searchJamendo(query, limit = 20) {
    try {
      const response = await api.get('/music-apis/jamendo', {
        params: { action: 'search', q: query, limit }
      });
      return response.data;
    } catch (error) {
      console.error('Jamendo search failed:', error);
      throw error;
    }
  }
};

// Health Check API
export const healthAPI = {
  async check() {
    try {
      const response = await api.get('/health');
      return response.data;
    } catch (error) {
      console.warn('Health check failed, using mock data:', error.message);
      return createMockResponse(MOCK_DATA.health).then(res => res.data);
    }
  },

  async getInfo() {
    try {
      const response = await api.get('/');
      return response.data;
    } catch (error) {
      console.warn('API info failed, using mock data:', error.message);
      return createMockResponse(MOCK_DATA.health).then(res => res.data);
    }
  },

  async getStatus() {
    try {
      const response = await api.get('/status');
      return response.data;
    } catch (error) {
      console.error('Failed to get architecture status:', error);
      throw error;
    }
  }
};

// Upload API
export const uploadAPI = {
  async uploadAudio(file, metadata = {}) {
    try {
      // Convert file to base64 if it's a File object
      let fileData = file;
      if (file instanceof File) {
        fileData = await new Promise((resolve) => {
          const reader = new FileReader();
          reader.onload = () => resolve(reader.result.split(',')[1]); // Remove data URL prefix
          reader.readAsDataURL(file);
        });
      }

      const response = await api.post('/upload', {
        filename: metadata.filename || file.name || 'upload.mp3',
        fileData: fileData,
        contentType: metadata.contentType || file.type || 'audio/mpeg',
        metadata: metadata
      });

      return response.data;
    } catch (error) {
      console.error('Audio upload failed:', error);
      throw error;
    }
  }
};

// Music Catalog API
export const catalogAPI = {
  async getCatalog(page = 1, limit = 20, filters = {}) {
    try {
      const params = { page, limit };
      if (filters.genre) params.genre = filters.genre;
      if (filters.source) params.source = filters.source;
      if (filters.search) params.search = filters.search;

      const response = await api.get('/music-catalog', { params });
      return response.data;
    } catch (error) {
      console.error('Failed to get music catalog:', error);
      throw error;
    }
  },

  async addToCategory(trackData) {
    try {
      const response = await api.post('/music-catalog', trackData);
      return response.data;
    } catch (error) {
      console.error('Failed to add track to catalog:', error);
      throw error;
    }
  }
};

// User Profile API
export const userProfileAPI = {
  async getProfile(userId = 'demo_user', includeStats = false) {
    try {
      const response = await api.get('/user-profile', {
        params: { user_id: userId, include_stats: includeStats }
      });
      return response.data;
    } catch (error) {
      console.error('Failed to get user profile:', error);
      throw error;
    }
  },

  async createProfile(profileData) {
    try {
      const response = await api.post('/user-profile', profileData);
      return response.data;
    } catch (error) {
      console.error('Failed to create user profile:', error);
      throw error;
    }
  },

  async updateProfile(userId, updateData) {
    try {
      const response = await api.put('/user-profile', updateData, {
        params: { user_id: userId }
      });
      return response.data;
    } catch (error) {
      console.error('Failed to update user profile:', error);
      throw error;
    }
  },

  async deleteProfile(userId) {
    try {
      const response = await api.delete('/user-profile', {
        params: { user_id: userId }
      });
      return response.data;
    } catch (error) {
      console.error('Failed to delete user profile:', error);
      throw error;
    }
  }
};

// Playlists API
export const playlistsAPI = {
  async getPlaylists(userId = 'demo_user', includeTracks = false) {
    try {
      const response = await api.get('/playlists', {
        params: { user_id: userId, include_tracks: includeTracks }
      });
      return response.data;
    } catch (error) {
      console.error('Failed to get playlists:', error);
      throw error;
    }
  },

  async getPlaylist(playlistId, userId = 'demo_user', includeTracks = true) {
    try {
      const response = await api.get('/playlists', {
        params: { playlist_id: playlistId, user_id: userId, include_tracks: includeTracks }
      });
      return response.data;
    } catch (error) {
      console.error('Failed to get playlist:', error);
      throw error;
    }
  },

  async createPlaylist(playlistData) {
    try {
      const response = await api.post('/playlists', playlistData);
      return response.data;
    } catch (error) {
      console.error('Failed to create playlist:', error);
      throw error;
    }
  },

  async updatePlaylist(playlistId, updateData) {
    try {
      const response = await api.put('/playlists', updateData, {
        params: { playlist_id: playlistId }
      });
      return response.data;
    } catch (error) {
      console.error('Failed to update playlist:', error);
      throw error;
    }
  },

  async deletePlaylist(playlistId, userId = 'demo_user') {
    try {
      const response = await api.delete('/playlists', {
        params: { playlist_id: playlistId, user_id: userId }
      });
      return response.data;
    } catch (error) {
      console.error('Failed to delete playlist:', error);
      throw error;
    }
  },

  async addTrackToPlaylist(playlistId, trackId, userId = 'demo_user') {
    try {
      const response = await api.post('/playlists', {
        playlist_id: playlistId,
        track_id: trackId,
        user_id: userId
      });
      return response.data;
    } catch (error) {
      console.error('Failed to add track to playlist:', error);
      throw error;
    }
  },

  async removeTrackFromPlaylist(playlistId, trackId, userId = 'demo_user') {
    try {
      const response = await api.delete('/playlists', {
        params: { playlist_id: playlistId, track_id: trackId, user_id: userId }
      });
      return response.data;
    } catch (error) {
      console.error('Failed to remove track from playlist:', error);
      throw error;
    }
  }
};

// Metadata API (for backward compatibility)
export const metadataAPI = {
  async getGenres() {
    return musicAPI.getGenres();
  },

  async getMoods() {
    return musicAPI.getMoods();
  }
};

// Export all APIs as a single object for convenience
export const APIs = {
  auth: authAPI,
  user: userAPI,
  music: musicAPI,
  library: libraryAPI,
  external: externalMusicAPI,
  health: healthAPI,
  upload: uploadAPI,
  catalog: catalogAPI
};

// Utility functions
export const utils = {
  // Format duration from seconds to MM:SS
  formatDuration(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  },

  // Check if user has remaining quota
  checkQuota(quotaData) {
    return quotaData.quota.daily_remaining > 0 && quotaData.quota.monthly_remaining > 0;
  },

  // Format file size
  formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  },

  // Validate audio URL
  isValidAudioUrl(url) {
    return url && (url.includes('.mp3') || url.includes('.wav') || url.includes('.ogg'));
  }
};

// Default export
export default api;
