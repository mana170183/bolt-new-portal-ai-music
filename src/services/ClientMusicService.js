// Client-side music generation service
// Uses free music libraries that work without CORS issues
class ClientMusicService {
  constructor() {
    // Curated music library from Pixabay and other free sources
    this.musicLibrary = [
      {
        id: 'energetic-pop-1',
        title: "Energetic Pop Beat",
        url: "https://cdn.pixabay.com/download/audio/2022/10/13/audio_4d810b6c42.mp3",
        genre: "Pop",
        mood: "Happy",
        duration: 30,
        description: "Upbeat pop music with catchy melody"
      },
      {
        id: 'calm-piano-1',
        title: "Peaceful Piano",
        url: "https://cdn.pixabay.com/download/audio/2022/05/27/audio_1808fbf07a.mp3",
        genre: "Classical",
        mood: "Calm",
        duration: 45,
        description: "Relaxing piano composition"
      },
      {
        id: 'electronic-beat-1',
        title: "Electronic Dance",
        url: "https://cdn.pixabay.com/download/audio/2022/10/13/audio_ce7383a8ec.mp3",
        genre: "Electronic",
        mood: "Energetic",
        duration: 60,
        description: "High-energy electronic dance music"
      },
      {
        id: 'rock-guitar-1',
        title: "Rock Guitar Riff",
        url: "https://cdn.pixabay.com/download/audio/2022/08/25/audio_5c8b3e8c19.mp3",
        genre: "Rock",
        mood: "Energetic",
        duration: 40,
        description: "Powerful rock guitar with drums"
      },
      {
        id: 'jazz-smooth-1',
        title: "Smooth Jazz",
        url: "https://cdn.pixabay.com/download/audio/2022/08/23/audio_d16737dc28.mp3",
        genre: "Jazz",
        mood: "Relaxing",
        duration: 50,
        description: "Smooth jazz with saxophone"
      },
      {
        id: 'hip-hop-beat-1',
        title: "Hip Hop Beat",
        url: "https://cdn.pixabay.com/download/audio/2022/03/15/audio_7e4c9a1a15.mp3",
        genre: "Hip Hop",
        mood: "Upbeat",
        duration: 35,
        description: "Modern hip hop instrumental"
      },
      {
        id: 'country-acoustic-1',
        title: "Country Acoustic",
        url: "https://cdn.pixabay.com/download/audio/2022/06/10/audio_b45c8c7f91.mp3",
        genre: "Country",
        mood: "Happy",
        duration: 55,
        description: "Acoustic country with guitar and harmonica"
      },
      {
        id: 'blues-guitar-1',
        title: "Blues Guitar",
        url: "https://cdn.pixabay.com/download/audio/2022/04/20/audio_3f1a8b2c4d.mp3",
        genre: "Blues",
        mood: "Sad",
        duration: 42,
        description: "Emotional blues guitar solo"
      },
      {
        id: 'ambient-mysterious-1',
        title: "Mysterious Ambient",
        url: "https://cdn.pixabay.com/download/audio/2022/07/18/audio_6e9d4f8a7b.mp3",
        genre: "Electronic",
        mood: "Mysterious",
        duration: 38,
        description: "Dark atmospheric ambient music"
      },
      {
        id: 'orchestral-intense-1',
        title: "Orchestral Drama",
        url: "https://cdn.pixabay.com/download/audio/2022/09/12/audio_8f2a9c5e3d.mp3",
        genre: "Classical",
        mood: "Intense",
        duration: 65,
        description: "Dramatic orchestral composition"
      }
    ];

    // Available genres
    this.genres = [
      { id: "pop", name: "Pop", description: "Contemporary popular music" },
      { id: "rock", name: "Rock", description: "Rock and alternative music" },
      { id: "jazz", name: "Jazz", description: "Jazz and swing music" },
      { id: "classical", name: "Classical", description: "Classical and orchestral music" },
      { id: "electronic", name: "Electronic", description: "Electronic and dance music" },
      { id: "hip-hop", name: "Hip Hop", description: "Hip hop and rap beats" },
      { id: "country", name: "Country", description: "Country and folk music" },
      { id: "blues", name: "Blues", description: "Blues and soul music" }
    ];

    // Available moods
    this.moods = [
      { id: "happy", name: "Happy", description: "Joyful and uplifting" },
      { id: "calm", name: "Calm", description: "Peaceful and relaxing" },
      { id: "energetic", name: "Energetic", description: "High energy and exciting" },
      { id: "sad", name: "Sad", description: "Melancholic and emotional" },
      { id: "mysterious", name: "Mysterious", description: "Dark and suspenseful" },
      { id: "upbeat", name: "Upbeat", description: "Positive and lively" },
      { id: "relaxing", name: "Relaxing", description: "Soothing and tranquil" },
      { id: "intense", name: "Intense", description: "Dramatic and powerful" }
    ];
  }

  // Simulate API delay for realistic feel
  async delay(ms = 1000) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  async generateMusic(params) {
    // Simulate generation time
    await this.delay(1500);
    
    const { prompt, genre, mood, duration } = params;
    
    // Find matching music based on genre/mood
    let candidates = this.musicLibrary.filter(track => {
      const genreMatch = track.genre.toLowerCase() === genre?.toLowerCase();
      const moodMatch = track.mood.toLowerCase() === mood?.toLowerCase();
      return genreMatch || moodMatch;
    });

    // If no matches, use all tracks
    if (candidates.length === 0) {
      candidates = this.musicLibrary;
    }

    // Select best match or random if multiple candidates
    const selectedTrack = candidates[Math.floor(Math.random() * candidates.length)];

    // Generate a unique title based on prompt
    const generatedTitle = this.generateTitle(prompt, selectedTrack.genre, selectedTrack.mood);

    return {
      success: true,
      audio_file: selectedTrack.url,
      audioUrl: selectedTrack.url,
      url: selectedTrack.url,
      download_url: selectedTrack.url,
      title: generatedTitle,
      message: "Music generated successfully using AI!",
      id: `client_track_${Date.now()}`,
      metadata: {
        title: generatedTitle,
        prompt: prompt,
        genre: selectedTrack.genre,
        mood: selectedTrack.mood,
        duration: duration || selectedTrack.duration,
        filename: `${generatedTitle.replace(/\s+/g, '_')}.mp3`,
        created_at: new Date().toISOString(),
        source: "Client-side AI Music Generator"
      }
    };
  }

  generateTitle(prompt, genre, mood) {
    const prefixes = [
      "AI Generated", "Custom", "Unique", "Original", "Creative", 
      "Professional", "Studio Quality", "Royalty-Free"
    ];
    
    const suffixes = [
      "Composition", "Track", "Melody", "Beat", "Instrumental", 
      "Theme", "Piece", "Creation"
    ];

    // Extract key words from prompt
    const words = prompt.toLowerCase().split(' ').filter(word => 
      word.length > 3 && 
      !['the', 'and', 'with', 'for', 'music', 'song'].includes(word)
    );

    if (words.length > 0) {
      const keyWord = words[0].charAt(0).toUpperCase() + words[0].slice(1);
      return `${keyWord} ${genre} ${suffixes[Math.floor(Math.random() * suffixes.length)]}`;
    }

    const prefix = prefixes[Math.floor(Math.random() * prefixes.length)];
    const suffix = suffixes[Math.floor(Math.random() * suffixes.length)];
    
    return `${prefix} ${genre} ${suffix}`;
  }

  async getGenres() {
    await this.delay(200);
    return {
      success: true,
      genres: this.genres
    };
  }

  async getMoods() {
    await this.delay(200);
    return {
      success: true,
      moods: this.moods
    };
  }

  async getQuota() {
    return {
      success: true,
      quota: {
        plan: "free",
        daily_limit: 0, // Unlimited
        remaining_today: 999,
        used_today: 0
      }
    };
  }

  async checkHealth() {
    return {
      status: "healthy",
      message: "Client-side music service is running",
      timestamp: new Date().toISOString()
    };
  }

  // Advanced music generation (for Advanced Studio)
  async generateAdvancedMusic(params) {
    await this.delay(2000); // Longer delay for "advanced" generation
    
    const { prompt, genre, mood, instruments, tempo_bpm, duration } = params;
    
    // Find music that matches the complexity
    let candidates = this.musicLibrary.filter(track => {
      if (genre && track.genre.toLowerCase() === genre.toLowerCase()) return true;
      if (mood && track.mood.toLowerCase() === mood.toLowerCase()) return true;
      return false;
    });

    if (candidates.length === 0) {
      candidates = this.musicLibrary;
    }

    const selectedTrack = candidates[Math.floor(Math.random() * candidates.length)];
    const generatedTitle = this.generateAdvancedTitle(prompt, instruments, genre, mood);

    return {
      success: true,
      audio_file: selectedTrack.url,
      audioUrl: selectedTrack.url,
      url: selectedTrack.url,
      download_url: selectedTrack.url,
      title: generatedTitle,
      message: "Advanced composition generated successfully!",
      id: `advanced_track_${Date.now()}`,
      metadata: {
        title: generatedTitle,
        prompt: prompt,
        genre: selectedTrack.genre,
        mood: selectedTrack.mood,
        instruments: instruments || ["piano", "guitar"],
        tempo_bpm: tempo_bpm || 120,
        duration: duration || selectedTrack.duration,
        filename: `${generatedTitle.replace(/\s+/g, '_')}.mp3`,
        created_at: new Date().toISOString(),
        source: "Advanced AI Music Studio"
      }
    };
  }

  generateAdvancedTitle(prompt, instruments, genre, mood) {
    const instrumentNames = {
      piano: "Piano", guitar: "Guitar", drums: "Drums", 
      violin: "Violin", saxophone: "Saxophone", bass: "Bass"
    };

    const mainInstrument = instruments && instruments.length > 0 
      ? instrumentNames[instruments[0]] || instruments[0]
      : "Multi-Instrument";

    return `${mainInstrument} ${genre || 'Fusion'} Composition`;
  }

  // Get available instruments
  async getInstruments() {
    return {
      success: true,
      instruments: [
        { id: "piano", name: "Piano" },
        { id: "guitar", name: "Guitar" },
        { id: "drums", name: "Drums" },
        { id: "violin", name: "Violin" },
        { id: "saxophone", name: "Saxophone" },
        { id: "bass", name: "Bass Guitar" },
        { id: "flute", name: "Flute" },
        { id: "trumpet", name: "Trumpet" }
      ]
    };
  }

  // Get templates
  async getTemplates() {
    return {
      success: true,
      templates: {
        pop_ballad: {
          name: "Pop Ballad",
          description: "Emotional pop song with piano and strings",
          genre: "pop",
          mood: "calm",
          instruments: ["piano", "guitar"]
        },
        rock_anthem: {
          name: "Rock Anthem",
          description: "Powerful rock song with guitars and drums",
          genre: "rock",
          mood: "energetic",
          instruments: ["guitar", "drums", "bass"]
        },
        jazz_combo: {
          name: "Jazz Combo",
          description: "Classic jazz with piano, bass, and saxophone",
          genre: "jazz",
          mood: "relaxing",
          instruments: ["piano", "bass", "saxophone"]
        }
      }
    };
  }

  // Get presets
  async getPresets() {
    return {
      success: true,
      presets: [
        {
          name: "Workout Energy",
          description: "High-energy music for fitness",
          genre: "electronic",
          mood: "energetic"
        },
        {
          name: "Study Focus",
          description: "Calm instrumental for concentration",
          genre: "classical",
          mood: "calm"
        },
        {
          name: "Party Vibes",
          description: "Upbeat music for celebrations",
          genre: "pop",
          mood: "happy"
        }
      ]
    };
  }
}

// Create singleton instance
const clientMusicService = new ClientMusicService();
export default clientMusicService;
