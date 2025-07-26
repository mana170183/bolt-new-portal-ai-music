module.exports = async (req, res) => {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  // Handle preflight requests
  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  if (req.method === 'POST') {
    try {
      const { prompt, duration = 30, genre = 'pop', mood = 'happy' } = req.body || {};

      if (!prompt) {
        return res.status(400).json({
          error: 'Prompt is required'
        });
      }

      // Simulate music generation
      const trackId = `track_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      
      const generatedTrack = {
        success: true,
        message: 'Music generated successfully',
        track: {
          id: trackId,
          title: `AI Generated - ${prompt.substring(0, 30)}`,
          duration: parseInt(duration),
          genre: genre,
          mood: mood,
          url: `https://example.com/tracks/${trackId}.mp3`,
          preview_url: `https://example.com/previews/${trackId}.mp3`,
          created_at: new Date().toISOString(),
          prompt: prompt
        }
      };

      res.status(200).json(generatedTrack);
    } catch (error) {
      console.error('Music generation error:', error);
      res.status(500).json({
        error: 'Failed to generate music',
        message: error.message
      });
    }
  } else {
    res.status(405).json({ error: 'Method not allowed' });
  }
};
