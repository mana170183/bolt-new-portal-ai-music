import axios from 'axios';

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || '/';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds for music generation
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
      // Redirect to login or refresh token
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  async generateToken(userId = 'demo_user', plan = 'free') {
    try {
      const response = await api.post('/api/auth/token', {
        user_id: userId,
        plan: plan
      });
      
      if (response.data.status === 'success') {
        authToken = response.data.token;
        localStorage.setItem('auth_token', authToken);
        return response.data;
      }
      throw new Error('Failed to generate token');
    } catch (error) {
      console.error('Token generation error:', error);
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

// Music Generation API
export const musicAPI = {
  async generateMusic(prompt, options = {}) {
    try {
      const response = await api.post('/api/generate-music', {
        prompt,
        duration: options.duration || 30,
        genre: options.genre || 'pop',
        mood: options.mood || 'upbeat'
      });
      
      return response.data;
    } catch (error) {
      if (error.response?.status === 429) {
        throw new Error('Rate limit exceeded. Please try again later.');
      }
      throw error;
    }
  },

  async getUserTracks() {
    try {
      const response = await api.get('/api/tracks');
      return response.data;
    } catch (error) {
      console.error('Error fetching tracks:', error);
      throw error;
    }
  },

  async getUserQuota() {
    try {
      const response = await api.get('/api/user/quota');
      return response.data;
    } catch (error) {
      console.error('Error fetching quota:', error);
      throw error;
    }
  }
};

// Metadata API
export const metadataAPI = {
  async getGenres() {
    try {
      const response = await api.get('/api/genres');
      return response.data;
    } catch (error) {
      console.error('Error fetching genres:', error);
      throw error;
    }
  },

  async getMoods() {
    try {
      const response = await api.get('/api/moods');
      return response.data;
    } catch (error) {
      console.error('Error fetching moods:', error);
      throw error;
    }
  }
};

// Health check
export const healthAPI = {
  async checkHealth() {
    try {
      const response = await api.get('/health');
      return response.data;
    } catch (error) {
      console.error('Health check failed:', error);
      throw error;
    }
  }
};

export default api;