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

  if (req.method === 'GET') {
    try {
      const moods = [
        { id: 'happy', name: 'Happy', description: 'Upbeat and joyful' },
        { id: 'sad', name: 'Sad', description: 'Melancholic and emotional' },
        { id: 'energetic', name: 'Energetic', description: 'High energy and motivating' },
        { id: 'relaxed', name: 'Relaxed', description: 'Calm and peaceful' },
        { id: 'dramatic', name: 'Dramatic', description: 'Intense and powerful' },
        { id: 'mysterious', name: 'Mysterious', description: 'Dark and intriguing' },
        { id: 'romantic', name: 'Romantic', description: 'Love and passion' },
        { id: 'nostalgic', name: 'Nostalgic', description: 'Reminiscent and wistful' }
      ];

      res.status(200).json(moods);
    } catch (error) {
      console.error('Get moods error:', error);
      res.status(500).json({
        error: 'Failed to get moods',
        message: error.message
      });
    }
  } else {
    res.status(405).json({ error: 'Method not allowed' });
  }
};
