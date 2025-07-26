const { app } = require('@azure/functions');

// Health endpoint
app.http('health', {
  methods: ['GET', 'POST', 'OPTIONS'],
  authLevel: 'anonymous',
  handler: async (request, context) => {
    context.log('Health check requested');
    
    // Handle CORS preflight
    if (request.method === 'OPTIONS') {
      return {
        status: 200,
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type'
        }
      };
    }
    
    return {
      status: 200,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      },
      jsonBody: {
        status: 'ok',
        message: 'AI Music API is running',
        timestamp: new Date().toISOString(),
        version: '2.0.0'
      }
    };
  }
});

// Music generation endpoint
app.http('generate-music', {
  methods: ['POST', 'OPTIONS'],
  authLevel: 'anonymous',
  handler: async (request, context) => {
    context.log('Music generation requested');
    
    // Handle CORS preflight
    if (request.method === 'OPTIONS') {
      return {
        status: 200,
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'POST, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type'
        }
      };
    }
    
    // Mock music generation response
    return {
      status: 200,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      },
      jsonBody: {
        id: 'track_' + Date.now(),
        title: 'AI Generated Track',
        duration: 30,
        url: 'https://www.soundjay.com/misc/sounds/bell-ringing-05.wav',
        status: 'completed'
      }
    };
  }
});

// Genres endpoint
app.http('genres', {
  methods: ['GET', 'OPTIONS'],
  authLevel: 'anonymous',
  handler: async (request, context) => {
    context.log('Genres requested');
    
    // Handle CORS preflight
    if (request.method === 'OPTIONS') {
      return {
        status: 200,
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type'
        }
      };
    }
    
    return {
      status: 200,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      },
      jsonBody: [
        'Pop', 'Rock', 'Jazz', 'Classical', 'Electronic', 'Hip Hop',
        'Country', 'Blues', 'Reggae', 'Folk', 'R&B', 'Funk'
      ]
    };
  }
});

// Moods endpoint
app.http('moods', {
  methods: ['GET', 'OPTIONS'],
  authLevel: 'anonymous',
  handler: async (request, context) => {
    context.log('Moods requested');
    
    // Handle CORS preflight
    if (request.method === 'OPTIONS') {
      return {
        status: 200,
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type'
        }
      };
    }
    
    return {
      status: 200,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      },
      jsonBody: [
        'Happy', 'Sad', 'Energetic', 'Calm', 'Romantic', 'Dark',
        'Uplifting', 'Mysterious', 'Nostalgic', 'Aggressive'
      ]
    };
  }
});

module.exports = { app };
