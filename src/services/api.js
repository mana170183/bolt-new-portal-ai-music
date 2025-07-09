import axios from 'axios';

// Force API base URL to '' in production/Netlify to avoid double /api prefix
let API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5002';

// Specific logic for Netlify environments
const isNetlify = typeof window !== 'undefined' && 
  (window.location.hostname.endsWith('netlify.app') || 
   window.location.hostname === 'localhost' && window.location.search.includes('netlify'));

if (isNetlify) {
  API_BASE_URL = '';
  console.log('📡 Netlify environment detected, using relative API URLs');
}

if (typeof window !== 'undefined') {
  // Debug log for deployed environment
  console.log('📡 API_BASE_URL used by frontend:', API_BASE_URL);
}

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds for music generation
  headers: {
    'Content-Type': 'application/json',
  },
});

// Token management
let authToken = null;
if (typeof window !== 'undefined') {
  authToken = localStorage.getItem('auth_token');
}

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
    // Get the request URL for better error reporting
    const requestUrl = error.config?.url || 'unknown endpoint';
    
    if (error.response) {
      // The request was made and the server responded with a status code
      // outside of the 2xx range
      const status = error.response.status;
      
      if (status === 401) {
        // Token expired or invalid
        console.error(`🔒 Authentication failed for ${requestUrl}: ${error.response.data?.message || 'Unauthorized'}`);
        localStorage.removeItem('auth_token');
        authToken = null;
        // Redirect to login or refresh token
      } else if (status === 404) {
        console.warn(`⚠️ API endpoint not found: ${requestUrl}. This may be expected during deployment migrations.`);
      } else {
        console.error(`❌ API Error (${status}) for ${requestUrl}:`, error.response.data);
      }
    } else if (error.request) {
      // The request was made but no response was received
      console.error(`🌐 Network error for ${requestUrl}: No response received. API service may be unavailable.`);
    } else {
      // Something happened in setting up the request that triggered an Error
      console.error(`⚙️ Request configuration error for ${requestUrl}:`, error.message);
    }
    
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  // Helper function to handle API errors consistently
  _handleApiError(error, operation, fallbackData = null) {
    const isNetlifyDeployment = isNetlify && process.env.NODE_ENV === 'production';
    
    // Log the error with context
    console.error(`API Error during ${operation}:`, error);
    
    // For Netlify deployments, provide more helpful messages during migration
    if (isNetlifyDeployment && (error.response?.status === 404 || error.request && !error.response)) {
      console.warn(`This endpoint may not be fully migrated to Netlify Functions yet.`);
      
      // If fallback data is provided, return it instead of throwing
      if (fallbackData !== null) {
        console.info(`Using fallback data for ${operation}`);
        return fallbackData;
      }
    }
    
    // Re-throw the error for the caller to handle
    throw error;
  },
  
  async generateToken(userId = 'demo_user', plan = 'free') {
    try {
      const response = await api.post('/api/auth/token', {
        user_id: userId,
        plan: plan
      });
      
      if (response.data.success === true) {
        authToken = response.data.token;
        localStorage.setItem('auth_token', authToken);
        return response.data;
      }
      throw new Error('Failed to generate token');
    } catch (error) {
      return this._handleApiError(error, 'token generation');
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

  async generateEnhancedMusic(options = {}) {
    try {
      const response = await api.post('/api/generate-enhanced-music', options);
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
  // Helper for handling metadata API errors with fallbacks
  _handleMetadataError(error, operation, fallbackData) {
    const isNetlifyDeployment = isNetlify && process.env.NODE_ENV === 'production';
    
    console.error(`Error fetching ${operation}:`, error);
    
    // If we're in Netlify and the endpoint isn't available yet, use fallback data
    if (isNetlifyDeployment && (error.response?.status === 404 || error.request && !error.response)) {
      console.warn(`Using fallback ${operation} data during Netlify migration`);
      return fallbackData;
    }
    
    throw error;
  },

  async getGenres() {
    try {
      const response = await api.get('/api/genres');
      return response.data;
    } catch (error) {
      // Fallback genres if API fails
      return this._handleMetadataError(error, 'genres', {
        genres: [
          {id: 'pop', name: 'Pop', description: 'Catchy, mainstream melodies'},
          {id: 'rock', name: 'Rock', description: 'Guitar-driven, energetic'},
          {id: 'electronic', name: 'Electronic', description: 'Synthesized, digital sounds'},
          {id: 'jazz', name: 'Jazz', description: 'Improvisational, complex harmonies'},
          {id: 'classical', name: 'Classical', description: 'Orchestral, complex compositions'}
        ]
      });
    }
  },

  async getMoods() {
    try {
      const response = await api.get('/api/moods');
      return response.data;
    } catch (error) {
      // Fallback moods if API fails
      return this._handleMetadataError(error, 'moods', {
        moods: [
          {id: 'upbeat', name: 'Upbeat', description: 'Happy, energetic feeling'},
          {id: 'calm', name: 'Calm', description: 'Peaceful, relaxing'},
          {id: 'energetic', name: 'Energetic', description: 'High-energy, motivating'},
          {id: 'melancholic', name: 'Melancholic', description: 'Sad, reflective'},
          {id: 'dramatic', name: 'Dramatic', description: 'Intense, emotional'}
        ]
      });
    }
  },

  async getInstruments() {
    try {
      const response = await api.get('/api/instruments');
      return response.data;
    } catch (error) {
      // Fallback instruments if API fails
      return this._handleMetadataError(error, 'instruments', {
        instruments: [
          {id: 'piano', name: 'Piano', family: 'keyboard'},
          {id: 'guitar', name: 'Guitar', family: 'string'},
          {id: 'drums', name: 'Drums', family: 'percussion'},
          {id: 'bass', name: 'Bass', family: 'string'},
          {id: 'synth', name: 'Synthesizer', family: 'electronic'}
        ]
      });
    }
  },

  async getCompositionTemplates() {
    try {
      const response = await api.get('/api/composition-templates');
      return response.data;
    } catch (error) {
      // Fallback templates if API fails
      return this._handleMetadataError(error, 'composition templates', {
        templates: [
          {id: 'verse-chorus', name: 'Verse-Chorus', description: 'Classic song structure'},
          {id: 'edm', name: 'EDM', description: 'Electronic dance music structure'},
          {id: 'ambient', name: 'Ambient', description: 'Evolving atmospheric composition'}
        ]
      });
    }
  }
};

// Health check
export const healthAPI = {
  async checkHealth() {
    try {
      const response = await api.get('/api/health');
      
      // Check if we're on Netlify by looking for netlify flag in the response
      if (response.data && response.data.netlify === true) {
        console.info('✅ Connected to Netlify Functions backend');
      }
      
      return response.data;
    } catch (error) {
      console.error('Health check failed:', error);
      
      if (isNetlify && (error.response?.status === 404 || error.request && !error.response)) {
        console.warn('⚠️ Health check endpoint may not be migrated to Netlify Functions yet');
        
        // Return a minimal health response to prevent app from breaking
        return {
          status: 'partial',
          message: 'Health check endpoint not available, but app can continue in limited mode',
          timestamp: new Date().toISOString(),
          environment: 'netlify-migration',
          fallback: true
        };
      }
      
      throw error;
    }
  }
};

export default api;