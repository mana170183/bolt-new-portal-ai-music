const express = require('express');
const cors = require('cors');
const axios = require('axios');
const app = express();
const PORT = 7071;

console.log('🎵 Starting AI Music API Test Server with FREE APIs...');
console.log('Loading free music APIs for comprehensive testing...');

// Middleware
app.use(cors());
app.use(express.json());

// Mock database for storing generated tracks
let tracks = [];
let trackId = 1;

// Free Music APIs Configuration
const FREE_MUSIC_APIS = {
  freeMusicArchive: {
    name: 'Free Music Archive',
    baseUrl: 'https://freemusicarchive.org/api/v1',
    type: 'free',
    status: 'available',
    description: 'High-quality creative commons music'
  },
  jamendo: {
    name: 'Jamendo',
    baseUrl: 'https://api.jamendo.com/v3.0',
    clientId: 'YOUR_CLIENT_ID', // Free registration required
    type: 'freemium',
    status: 'available',
    description: 'Free music platform with API'
  },
  deezer: {
    name: 'Deezer',
    baseUrl: 'https://api.deezer.com',
    type: 'free',
    status: 'available',
    description: 'Music search and metadata (no auth needed for search)'
  },
  lastfm: {
    name: 'Last.fm',
    baseUrl: 'https://ws.audioscrobbler.com/2.0/',
    apiKey: 'YOUR_API_KEY', // Free registration
    type: 'free',
    status: 'available',
    description: 'Music metadata and recommendations'
  },
  spotify: {
    name: 'Spotify Web API',
    baseUrl: 'https://api.spotify.com/v1',
    type: 'free',
    status: 'available',
    description: 'Music search and metadata (client credentials flow)'
  },
  musicbrainz: {
    name: 'MusicBrainz',
    baseUrl: 'https://musicbrainz.org/ws/2',
    type: 'free',
    status: 'available',
    description: 'Open music encyclopedia'
  },
  internetarchive: {
    name: 'Internet Archive',
    baseUrl: 'https://archive.org/advancedsearch.php',
    type: 'free',
    status: 'available',
    description: 'Historical and public domain audio'
  },
  ccmixter: {
    name: 'ccMixter',
    baseUrl: 'http://ccmixter.org/api/query',
    type: 'free',
    status: 'available',
    description: 'Remixes and samples under Creative Commons'
  },
  freesound: {
    name: 'Freesound',
    baseUrl: 'https://freesound.org/apiv2',
    type: 'freemium',
    status: 'available',
    description: 'Sound effects and audio samples'
  },
  zapsplat: {
    name: 'Zapsplat',
    baseUrl: 'https://api.zapsplat.com',
    type: 'freemium',
    status: 'available',
    description: 'Sound effects library'
  },
  incompetech: {
    name: 'Incompetech',
    baseUrl: 'https://incompetech.com/graphql',
    type: 'free',
    status: 'available',
    description: 'Kevin MacLeod royalty-free music'
  },
  pixabay: {
    name: 'Pixabay Music',
    baseUrl: 'https://pixabay.com/api',
    type: 'free',
    status: 'available',
    description: 'Royalty-free music and audio'
  }
};

// Free Audio URLs for testing (actual working URLs)
const FREE_AUDIO_SAMPLES = [
  'https://commondatastorage.googleapis.com/codeskulptor-demos/DDR_assets/Kangaroo_MusiQue_-_The_Neverwritten_Role_Playing_Game.mp3',
  'https://commondatastorage.googleapis.com/codeskulptor-assets/week7-brrring.m4a',
  'https://commondatastorage.googleapis.com/codeskulptor-demos/pyman_assets/intromusic.ogg',
  'https://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/soundtrack.mp3',
  'https://www.soundjay.com/misc/sounds/bell-ringing-05.wav',
  'https://archive.org/download/testmp3testfile/mpthreetest.mp3',
  'https://file-examples.com/storage/fe68c0b49c66a8beb8c2bb9/2017/11/file_example_MP3_700KB.mp3',
  'https://download.samplelib.com/mp3/sample-3s.mp3',
  'https://download.samplelib.com/mp3/sample-6s.mp3',
  'https://download.samplelib.com/mp3/sample-9s.mp3',
  'https://download.samplelib.com/mp3/sample-12s.mp3',
  'https://download.samplelib.com/mp3/sample-15s.mp3'
];

// Enhanced mock tracks with free audio URLs
const MOCK_TRACKS = [
  {
    id: 1,
    title: 'Electronic Journey',
    artist: 'AI Composer',
    genre: 'electronic',
    mood: 'energetic',
    duration: 180,
    audioUrl: FREE_AUDIO_SAMPLES[0],
    source: 'Free Music Archive',
    license: 'Creative Commons'
  },
  {
    id: 2,
    title: 'Ambient Dreams',
    artist: 'Digital Soundscape',
    genre: 'ambient',
    mood: 'calm',
    duration: 240,
    audioUrl: FREE_AUDIO_SAMPLES[1],
    source: 'Jamendo',
    license: 'Creative Commons'
  },
  {
    id: 3,
    title: 'Jazz Fusion',
    artist: 'Virtual Trio',
    genre: 'jazz',
    mood: 'upbeat',
    duration: 200,
    audioUrl: FREE_AUDIO_SAMPLES[2],
    source: 'Internet Archive',
    license: 'Public Domain'
  },
  {
    id: 4,
    title: 'Rock Anthem',
    artist: 'AI Band',
    genre: 'rock',
    mood: 'energetic',
    duration: 220,
    audioUrl: FREE_AUDIO_SAMPLES[3],
    source: 'ccMixter',
    license: 'Creative Commons'
  },
  {
    id: 5,
    title: 'Classical Serenade',
    artist: 'Digital Orchestra',
    genre: 'classical',
    mood: 'romantic',
    duration: 300,
    audioUrl: FREE_AUDIO_SAMPLES[4],
    source: 'Incompetech',
    license: 'Royalty Free'
  }
];

// Initialize tracks with mock data
tracks = [...MOCK_TRACKS];

// Health check endpoints
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    message: 'AI Music API is running (Local Test Server)',
    timestamp: new Date().toISOString(),
    version: '2.0.0'
  });
});

app.get('/api/health', (req, res) => {
  res.json({
    status: 'ok',
    message: 'AI Music API is running (Local Test Server)',
    timestamp: new Date().toISOString(),
    version: '2.0.0'
  });
});

// Get genres
app.get('/api/genres', (req, res) => {
  const genres = [
    { id: 'pop', name: 'Pop', description: 'Modern popular music' },
    { id: 'rock', name: 'Rock', description: 'Rock and alternative music' },
    { id: 'electronic', name: 'Electronic', description: 'Electronic and dance music' },
    { id: 'jazz', name: 'Jazz', description: 'Jazz and blues' },
    { id: 'classical', name: 'Classical', description: 'Classical and orchestral' },
    { id: 'hiphop', name: 'Hip Hop', description: 'Hip hop and rap' },
    { id: 'ambient', name: 'Ambient', description: 'Ambient and atmospheric' },
    { id: 'folk', name: 'Folk', description: 'Folk and acoustic' }
  ];
  res.json({ genres });
});

// Get moods
app.get('/api/moods', (req, res) => {
  const moods = [
    { id: 'happy', name: 'Happy', description: 'Upbeat and joyful' },
    { id: 'sad', name: 'Sad', description: 'Melancholic and emotional' },
    { id: 'energetic', name: 'Energetic', description: 'High energy and motivating' },
    { id: 'relaxed', name: 'Relaxed', description: 'Calm and peaceful' },
    { id: 'dramatic', name: 'Dramatic', description: 'Intense and powerful' },
    { id: 'romantic', name: 'Romantic', description: 'Love and affection' },
    { id: 'mysterious', name: 'Mysterious', description: 'Dark and intriguing' },
    { id: 'uplifting', name: 'Uplifting', description: 'Inspiring and positive' }
  ];
  res.json({ moods });
});

// Generate music
app.post('/api/generate-music', (req, res) => {
  const { prompt, genre, mood, duration = 30 } = req.body;
  
  // Simulate processing time
  setTimeout(() => {
    // Randomly select an audio source and URL
    const randomAudioUrl = FREE_AUDIO_SAMPLES[Math.floor(Math.random() * FREE_AUDIO_SAMPLES.length)];
    const apiSources = Object.keys(FREE_MUSIC_APIS);
    const randomSource = apiSources[Math.floor(Math.random() * apiSources.length)];
    const sourceInfo = FREE_MUSIC_APIS[randomSource];
    
    const newTrack = {
      id: trackId++,
      title: `Generated Track ${trackId - 1}`,
      description: prompt || `A ${mood} ${genre} track`,
      genre,
      mood,
      duration,
      audioUrl: randomAudioUrl,
      waveformUrl: `https://example.com/waveform-${trackId - 1}.png`,
      createdAt: new Date().toISOString(),
      status: 'completed',
      // Enhanced with free API metadata
      source: sourceInfo.name,
      sourceType: sourceInfo.type,
      license: randomSource === 'internetarchive' ? 'Public Domain' : 
               randomSource === 'incompetech' ? 'CC BY 3.0' :
               randomSource === 'freeMusicArchive' ? 'CC BY-SA 4.0' :
               'Creative Commons',
      apiProvider: sourceInfo.description
    };
    
    tracks.push(newTrack);
    
    res.json({
      success: true,
      track: newTrack,
      message: 'Music generated successfully using free APIs',
      metadata: {
        usedAPI: sourceInfo.name,
        sourceType: sourceInfo.type,
        totalAvailableAPIs: Object.keys(FREE_MUSIC_APIS).length
      }
    });
  }, 2000); // 2 second delay to simulate processing
});

// Generate advanced music
app.post('/api/generate-advanced-music', (req, res) => {
  const { 
    prompt, 
    genre = 'electronic', 
    mood = 'energetic', 
    duration = 60,
    tempo = 120,
    key = 'C',
    instruments = ['synthesizer'],
    effects = ['reverb'],
    structure = 'verse-chorus-verse-chorus-bridge-chorus'
  } = req.body;
  
  // Simulate processing time
  setTimeout(() => {
    // Randomly select an audio source and URL for advanced generation
    const randomAudioUrl = FREE_AUDIO_SAMPLES[Math.floor(Math.random() * FREE_AUDIO_SAMPLES.length)];
    const apiSources = Object.keys(FREE_MUSIC_APIS);
    const randomSource = apiSources[Math.floor(Math.random() * apiSources.length)];
    const sourceInfo = FREE_MUSIC_APIS[randomSource];
    
    const newTrack = {
      id: trackId++,
      title: `Advanced Track ${trackId - 1}`,
      description: prompt || `An advanced ${mood} ${genre} track`,
      genre,
      mood,
      duration,
      tempo,
      key,
      instruments,
      effects,
      structure,
      audioUrl: randomAudioUrl,
      waveformUrl: `https://example.com/waveform-${trackId - 1}.png`,
      createdAt: new Date().toISOString(),
      status: 'completed',
      // Enhanced with free API metadata
      source: sourceInfo.name,
      sourceType: sourceInfo.type,
      license: randomSource === 'internetarchive' ? 'Public Domain' : 
               randomSource === 'incompetech' ? 'CC BY 3.0' :
               randomSource === 'freeMusicArchive' ? 'CC BY-SA 4.0' :
               'Creative Commons',
      apiProvider: sourceInfo.description,
      // Advanced metadata
      complexity: 'Advanced',
      generationMethod: 'AI-Enhanced with Free APIs'
    };
    
    tracks.push(newTrack);
    
    res.json({
      success: true,
      track: newTrack,
      message: 'Advanced music generated successfully using free APIs',
      metadata: {
        usedAPI: sourceInfo.name,
        sourceType: sourceInfo.type,
        totalAvailableAPIs: Object.keys(FREE_MUSIC_APIS).length,
        advancedFeatures: {
          tempo,
          key,
          instruments: instruments.length,
          effects: effects.length,
          structure
        }
      }
    });
  }, 3000); // 3 second delay to simulate processing
});

// Get user quota
app.get('/api/user-quota', (req, res) => {
  const { user_id = 'demo_user' } = req.query;
  
  res.json({
    quota: {
      daily_remaining: 45,
      daily_limit: 50,
      monthly_remaining: 485,
      monthly_limit: 500,
      reset_time: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString()
    },
    user: {
      id: user_id,
      plan: 'free',
      status: 'active'
    }
  });
});

// Get user tracks
app.get('/api/tracks', (req, res) => {
  res.json({
    tracks: tracks.reverse(), // Most recent first
    total: tracks.length
  });
});

// Delete track
app.delete('/api/tracks/:id', (req, res) => {
  const { id } = req.params;
  const trackIndex = tracks.findIndex(track => track.id === parseInt(id));
  
  if (trackIndex === -1) {
    return res.status(404).json({
      success: false,
      message: 'Track not found'
    });
  }
  
  tracks.splice(trackIndex, 1);
  res.json({
    success: true,
    message: 'Track deleted successfully'
  });
});

// ============ FREE MUSIC APIs ENDPOINTS ============

// List all available free music APIs
app.get('/api/music-sources', (req, res) => {
  res.json({
    message: 'Available free music APIs for testing',
    sources: FREE_MUSIC_APIS,
    totalSources: Object.keys(FREE_MUSIC_APIS).length,
    timestamp: new Date().toISOString()
  });
});

// Search Free Music Archive
app.get('/api/fma/search', async (req, res) => {
  try {
    const { query = 'ambient', limit = 10 } = req.query;
    
    // Mock FMA response with working audio URLs
    const mockResults = [
      {
        id: 'fma_1',
        title: `FMA: ${query} Track 1`,
        artist: 'Creative Commons Artist',
        genre: query,
        duration: 180,
        audioUrl: FREE_AUDIO_SAMPLES[Math.floor(Math.random() * FREE_AUDIO_SAMPLES.length)],
        downloadUrl: FREE_AUDIO_SAMPLES[0],
        license: 'CC BY-SA 4.0',
        source: 'Free Music Archive'
      },
      {
        id: 'fma_2', 
        title: `FMA: ${query} Track 2`,
        artist: 'Open Source Musician',
        genre: query,
        duration: 220,
        audioUrl: FREE_AUDIO_SAMPLES[Math.floor(Math.random() * FREE_AUDIO_SAMPLES.length)],
        downloadUrl: FREE_AUDIO_SAMPLES[1],
        license: 'CC BY 4.0',
        source: 'Free Music Archive'
      }
    ];
    
    res.json({
      query,
      results: mockResults.slice(0, limit),
      total: mockResults.length,
      source: 'Free Music Archive (Mock)',
      api: FREE_MUSIC_APIS.freeMusicArchive
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Search Jamendo
app.get('/api/jamendo/search', async (req, res) => {
  try {
    const { query = 'electronic', limit = 10 } = req.query;
    
    const mockResults = [
      {
        id: 'jamendo_1',
        title: `Jamendo: ${query} Beat`,
        artist: 'Digital Creator',
        genre: query,
        duration: 240,
        audioUrl: FREE_AUDIO_SAMPLES[Math.floor(Math.random() * FREE_AUDIO_SAMPLES.length)],
        streamUrl: FREE_AUDIO_SAMPLES[2],
        license: 'CC BY-NC-SA',
        source: 'Jamendo'
      },
      {
        id: 'jamendo_2',
        title: `Jamendo: ${query} Melody`,
        artist: 'Indie Producer',
        genre: query,
        duration: 200,
        audioUrl: FREE_AUDIO_SAMPLES[Math.floor(Math.random() * FREE_AUDIO_SAMPLES.length)],
        streamUrl: FREE_AUDIO_SAMPLES[3],
        license: 'CC BY',
        source: 'Jamendo'
      }
    ];
    
    res.json({
      query,
      results: mockResults.slice(0, limit),
      total: mockResults.length,
      source: 'Jamendo (Mock)',
      api: FREE_MUSIC_APIS.jamendo
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Search Deezer (metadata only)
app.get('/api/deezer/search', async (req, res) => {
  try {
    const { query = 'jazz', limit = 10 } = req.query;
    
    const mockResults = [
      {
        id: 'deezer_1',
        title: `${query} Collection`,
        artist: 'Various Artists',
        album: `Best of ${query}`,
        genre: query,
        duration: 180,
        preview: FREE_AUDIO_SAMPLES[4], // Deezer provides 30s previews
        link: 'https://deezer.com/track/123',
        source: 'Deezer'
      },
      {
        id: 'deezer_2',
        title: `${query} Essentials`,
        artist: 'Compilation',
        album: `${query} Hits`,
        genre: query,
        duration: 220,
        preview: FREE_AUDIO_SAMPLES[5],
        link: 'https://deezer.com/track/456',
        source: 'Deezer'
      }
    ];
    
    res.json({
      query,
      results: mockResults.slice(0, limit),
      total: mockResults.length,
      source: 'Deezer (Mock Metadata)',
      api: FREE_MUSIC_APIS.deezer
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Internet Archive Audio Search
app.get('/api/archive/search', async (req, res) => {
  try {
    const { query = 'classical', limit = 10 } = req.query;
    
    const mockResults = [
      {
        id: 'archive_1',
        title: `Archive: ${query} Recording`,
        creator: 'Public Domain Artist',
        date: '1920-01-01',
        genre: query,
        duration: 300,
        audioUrl: FREE_AUDIO_SAMPLES[6],
        downloadUrl: FREE_AUDIO_SAMPLES[6],
        license: 'Public Domain',
        source: 'Internet Archive'
      },
      {
        id: 'archive_2',
        title: `Archive: Historical ${query}`,
        creator: 'Classical Ensemble',
        date: '1935-06-15',
        genre: query,
        duration: 420,
        audioUrl: FREE_AUDIO_SAMPLES[7],
        downloadUrl: FREE_AUDIO_SAMPLES[7],
        license: 'Public Domain',
        source: 'Internet Archive'
      }
    ];
    
    res.json({
      query,
      results: mockResults.slice(0, limit),
      total: mockResults.length,
      source: 'Internet Archive (Mock)',
      api: FREE_MUSIC_APIS.internetarchive
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// ccMixter Remixes and Samples
app.get('/api/ccmixter/search', async (req, res) => {
  try {
    const { query = 'remix', limit = 10 } = req.query;
    
    const mockResults = [
      {
        id: 'ccmixter_1',
        title: `${query} Creation`,
        artist: 'Remix Artist',
        originalArtist: 'Source Creator',
        genre: 'remix',
        duration: 180,
        audioUrl: FREE_AUDIO_SAMPLES[8],
        downloadUrl: FREE_AUDIO_SAMPLES[8],
        license: 'CC BY-NC 3.0',
        source: 'ccMixter'
      },
      {
        id: 'ccmixter_2',
        title: `${query} Mashup`,
        artist: 'Creative Mixer',
        originalArtist: 'Original Creator',
        genre: 'remix',
        duration: 200,
        audioUrl: FREE_AUDIO_SAMPLES[9],
        downloadUrl: FREE_AUDIO_SAMPLES[9],
        license: 'CC BY 3.0',
        source: 'ccMixter'
      }
    ];
    
    res.json({
      query,
      results: mockResults.slice(0, limit),
      total: mockResults.length,
      source: 'ccMixter (Mock)',
      api: FREE_MUSIC_APIS.ccmixter
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Freesound Audio Samples
app.get('/api/freesound/search', async (req, res) => {
  try {
    const { query = 'ambient', limit = 10 } = req.query;
    
    const mockResults = [
      {
        id: 'freesound_1',
        name: `${query} sample 1`,
        username: 'AudioCreator',
        duration: 30,
        audioUrl: FREE_AUDIO_SAMPLES[10],
        downloadUrl: FREE_AUDIO_SAMPLES[10],
        license: 'CC0',
        tags: [query, 'sample', 'loop'],
        source: 'Freesound'
      },
      {
        id: 'freesound_2',
        name: `${query} sample 2`,
        username: 'SoundDesigner',
        duration: 45,
        audioUrl: FREE_AUDIO_SAMPLES[11],
        downloadUrl: FREE_AUDIO_SAMPLES[11],
        license: 'CC BY 3.0',
        tags: [query, 'sound', 'effect'],
        source: 'Freesound'
      }
    ];
    
    res.json({
      query,
      results: mockResults.slice(0, limit),
      total: mockResults.length,
      source: 'Freesound (Mock)',
      api: FREE_MUSIC_APIS.freesound
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Incompetech (Kevin MacLeod) Royalty-Free Music
app.get('/api/incompetech/search', async (req, res) => {
  try {
    const { genre = 'Cinematic', limit = 10 } = req.query;
    
    const mockResults = [
      {
        id: 'incompetech_1',
        title: `${genre} Theme`,
        artist: 'Kevin MacLeod',
        genre: genre,
        mood: 'Dramatic',
        duration: 180,
        audioUrl: FREE_AUDIO_SAMPLES[0],
        downloadUrl: FREE_AUDIO_SAMPLES[0],
        license: 'CC BY 3.0',
        attribution: 'Kevin MacLeod (incompetech.com)',
        source: 'Incompetech'
      },
      {
        id: 'incompetech_2',
        title: `${genre} Underscore`,
        artist: 'Kevin MacLeod',
        genre: genre,
        mood: 'Mysterious',
        duration: 240,
        audioUrl: FREE_AUDIO_SAMPLES[1],
        downloadUrl: FREE_AUDIO_SAMPLES[1],
        license: 'CC BY 3.0',
        attribution: 'Kevin MacLeod (incompetech.com)',
        source: 'Incompetech'
      }
    ];
    
    res.json({
      genre,
      results: mockResults.slice(0, limit),
      total: mockResults.length,
      source: 'Incompetech (Mock)',
      api: FREE_MUSIC_APIS.incompetech
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Combined search across all free APIs
app.get('/api/search-all', async (req, res) => {
  try {
    const { query = 'music', limit = 20 } = req.query;
    
    // Combine results from all mock APIs
    const allResults = [
      // FMA results
      {
        id: 'fma_combined_1',
        title: `${query} - FMA`,
        artist: 'FMA Artist',
        source: 'Free Music Archive',
        audioUrl: FREE_AUDIO_SAMPLES[0],
        license: 'CC BY-SA'
      },
      // Jamendo results
      {
        id: 'jamendo_combined_1',
        title: `${query} - Jamendo`,
        artist: 'Jamendo Artist',
        source: 'Jamendo',
        audioUrl: FREE_AUDIO_SAMPLES[1],
        license: 'CC BY-NC'
      },
      // Archive results
      {
        id: 'archive_combined_1',
        title: `${query} - Archive`,
        artist: 'Archive Collection',
        source: 'Internet Archive',
        audioUrl: FREE_AUDIO_SAMPLES[2],
        license: 'Public Domain'
      },
      // ccMixter results
      {
        id: 'ccmixter_combined_1',
        title: `${query} - Remix`,
        artist: 'ccMixter Artist',
        source: 'ccMixter',
        audioUrl: FREE_AUDIO_SAMPLES[3],
        license: 'CC BY'
      },
      // Incompetech results
      {
        id: 'incompetech_combined_1',
        title: `${query} - Royalty Free`,
        artist: 'Kevin MacLeod',
        source: 'Incompetech',
        audioUrl: FREE_AUDIO_SAMPLES[4],
        license: 'CC BY 3.0'
      }
    ];
    
    res.json({
      query,
      results: allResults.slice(0, limit),
      total: allResults.length,
      sources: Object.keys(FREE_MUSIC_APIS),
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Random free music discovery
app.get('/api/discover', (req, res) => {
  try {
    const randomTracks = MOCK_TRACKS.concat([
      {
        id: 'discover_1',
        title: 'Discovered Gem 1',
        artist: 'Hidden Artist',
        genre: 'experimental',
        audioUrl: FREE_AUDIO_SAMPLES[Math.floor(Math.random() * FREE_AUDIO_SAMPLES.length)],
        source: 'Discovery Mix',
        license: 'Creative Commons'
      },
      {
        id: 'discover_2',
        title: 'Discovered Gem 2',
        artist: 'Underground Creator',
        genre: 'indie',
        audioUrl: FREE_AUDIO_SAMPLES[Math.floor(Math.random() * FREE_AUDIO_SAMPLES.length)],
        source: 'Discovery Mix',
        license: 'Royalty Free'
      }
    ]);
    
    // Shuffle and return random selection
    const shuffled = randomTracks.sort(() => 0.5 - Math.random());
    
    res.json({
      message: 'Discover new free music',
      tracks: shuffled.slice(0, 10),
      sources: Object.keys(FREE_MUSIC_APIS),
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Free music statistics
app.get('/api/stats', (req, res) => {
  res.json({
    totalAPIs: Object.keys(FREE_MUSIC_APIS).length,
    totalTracks: tracks.length,
    totalSources: Object.keys(FREE_MUSIC_APIS).length,
    freeAudioSamples: FREE_AUDIO_SAMPLES.length,
    apiStatus: Object.entries(FREE_MUSIC_APIS).map(([key, api]) => ({
      name: api.name,
      type: api.type,
      status: api.status
    })),
    lastUpdated: new Date().toISOString()
  });
});

// ============ END FREE MUSIC APIs ============

// Start server
app.listen(PORT, () => {
  console.log(`🎵 AI Music API Test Server running on http://localhost:${PORT}`);
  console.log(`📋 Health check: http://localhost:${PORT}/api/health`);
});
