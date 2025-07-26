import axios from 'axios';

// API Configuration - Updated to use Azure Static Web App backend
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 
                     import.meta.env.VITE_API_URL || 
                     (import.meta.env.PROD ? '/api' : '/api');

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // 60 seconds for music generation
  headers: {
    'Content-Type': 'application/json',
  },
});

// Token management
let authToken = localStorage.getItem('auth_token');

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
      const response = await api.get('/user-quota', {
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

      console.log('Generating music with params:', { prompt, genre, mood, duration });

      const response = await api.post('/generate-music', {
        prompt,
        genre: genre || style,
        mood,
        duration
      });

      return response.data;
    } catch (error) {
      console.error('Music generation failed:', error);
      throw error;
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

      console.log('Generating advanced music with params:', params);
      
      const response = await api.post('/advanced-generate', {
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
      console.error('Failed to get genres:', error);
      // Return fallback data
      return {
        success: true,
        genres: ['pop', 'rock', 'jazz', 'classical', 'electronic', 'ambient', 'country', 'blues']
      };
    }
  },

  async getMoods() {
    try {
      const response = await api.get('/moods');
      return response.data;
    } catch (error) {
      console.error('Failed to get moods:', error);
      // Return fallback data
      return {
        success: true,
        moods: ['happy', 'sad', 'energetic', 'calm', 'mysterious', 'epic', 'romantic', 'upbeat']
      };
    }
  }
};

// Music Library API
export const libraryAPI = {
  async getTracks(userId = 'demo_user', page = 1, limit = 20, filters = {}) {
    try {
      const params = { user_id: userId, page, limit };
      if (filters.genre) params.genre = filters.genre;
      if (filters.mood) params.mood = filters.mood;

      const response = await api.get('/music-library', { params });
      return response.data;
    } catch (error) {
      console.error('Failed to get music library:', error);
      throw error;
    }
  },

  async saveTrack(trackId, userId = 'demo_user') {
    try {
      const response = await api.post('/music-library', {
        track_id: trackId,
        user_id: userId
      });
      return response.data;
    } catch (error) {
      console.error('Failed to save track:', error);
      throw error;
    }
  },

  async removeTrack(trackId, userId = 'demo_user') {
    try {
      const response = await api.delete('/music-library', {
        params: { track_id: trackId, user_id: userId }
      });
      return response.data;
    } catch (error) {
      console.error('Failed to remove track:', error);
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
      console.error('Health check failed:', error);
      throw error;
    }
  },

  async getInfo() {
    try {
      const response = await api.get('/');
      return response.data;
    } catch (error) {
      console.error('Failed to get API info:', error);
      throw error;
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
