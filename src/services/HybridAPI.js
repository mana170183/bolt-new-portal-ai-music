// Hybrid API service - uses client-side generation as fallback
import ClientMusicService from './ClientMusicService';

// Backend API URLs
const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://portal-music-backend-new.ambitiousmeadow-4c2dba6f.uksouth.azurecontainerapps.io';

class HybridMusicAPI {
  constructor() {
    this.useClientSide = false; // Start with backend, fall back to client-side
    this.authToken = null;
  }

  async makeRequest(endpoint, options = {}) {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...(this.authToken && { 'Authorization': `Bearer ${this.authToken}` }),
          ...options.headers,
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.warn(`Backend request failed for ${endpoint}:`, error.message);
      
      // Switch to client-side mode on any backend failure
      if (!this.useClientSide) {
        console.log('🔄 Switching to client-side music generation');
        this.useClientSide = true;
      }
      
      throw error;
    }
  }

  async generateSimpleMusic(params) {
    if (this.useClientSide) {
      return await ClientMusicService.generateMusic(params);
    }

    try {
      return await this.makeRequest('/api/generate', {
        method: 'POST',
        body: JSON.stringify(params)
      });
    } catch (error) {
      console.log('🎵 Using client-side music generation');
      return await ClientMusicService.generateMusic(params);
    }
  }

  async generateAdvancedMusic(params) {
    if (this.useClientSide) {
      return await ClientMusicService.generateAdvancedMusic(params);
    }

    try {
      return await this.makeRequest('/api/generate-advanced', {
        method: 'POST',
        body: JSON.stringify(params)
      });
    } catch (error) {
      console.log('🎵 Using client-side advanced music generation');
      return await ClientMusicService.generateAdvancedMusic(params);
    }
  }
}

class HybridMetadataAPI {
  constructor() {
    this.useClientSide = false;
  }

  async makeRequest(endpoint) {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      this.useClientSide = true;
      throw error;
    }
  }

  async getGenres() {
    if (this.useClientSide) {
      return await ClientMusicService.getGenres();
    }

    try {
      return await this.makeRequest('/api/genres');
    } catch (error) {
      return await ClientMusicService.getGenres();
    }
  }

  async getMoods() {
    if (this.useClientSide) {
      return await ClientMusicService.getMoods();
    }

    try {
      return await this.makeRequest('/api/moods');
    } catch (error) {
      return await ClientMusicService.getMoods();
    }
  }

  async getInstruments() {
    if (this.useClientSide) {
      return await ClientMusicService.getInstruments();
    }

    try {
      return await this.makeRequest('/api/instruments');
    } catch (error) {
      return await ClientMusicService.getInstruments();
    }
  }

  async getTemplates() {
    if (this.useClientSide) {
      return await ClientMusicService.getTemplates();
    }

    try {
      return await this.makeRequest('/api/templates');
    } catch (error) {
      return await ClientMusicService.getTemplates();
    }
  }

  async getPresets() {
    if (this.useClientSide) {
      return await ClientMusicService.getPresets();
    }

    try {
      return await this.makeRequest('/api/presets');
    } catch (error) {
      return await ClientMusicService.getPresets();
    }
  }
}

class HybridAuthAPI {
  constructor() {
    this.useClientSide = false;
    this.isAuthenticated = true; // Always authenticated in client-side mode
  }

  async generateToken(userId, plan) {
    if (this.useClientSide) {
      // Always successful in client-side mode
      return { success: true, token: 'client-side-token' };
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/token`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ userId, plan })
      });
      return await response.json();
    } catch (error) {
      this.useClientSide = true;
      return { success: true, token: 'client-side-token' };
    }
  }

  isAuthenticated() {
    return this.useClientSide || this.isAuthenticated;
  }

  async getQuota() {
    if (this.useClientSide) {
      return await ClientMusicService.getQuota();
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/quota`);
      return await response.json();
    } catch (error) {
      return await ClientMusicService.getQuota();
    }
  }
}

class HybridHealthAPI {
  constructor() {
    this.useClientSide = false;
  }

  async checkHealth() {
    if (this.useClientSide) {
      return await ClientMusicService.checkHealth();
    }

    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      if (!response.ok) throw new Error('Backend unhealthy');
      return await response.json();
    } catch (error) {
      console.log('💡 Backend unavailable, using client-side mode');
      this.useClientSide = true;
      return await ClientMusicService.checkHealth();
    }
  }
}

// Export hybrid API instances
export const musicAPI = new HybridMusicAPI();
export const metadataAPI = new HybridMetadataAPI();
export const authAPI = new HybridAuthAPI();
export const healthAPI = new HybridHealthAPI();

// For backward compatibility, also export as default
export default {
  musicAPI,
  metadataAPI,
  authAPI,
  healthAPI
};
