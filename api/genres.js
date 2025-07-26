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

      res.status(200).json(genres);
    } catch (error) {
      console.error('Get genres error:', error);
      res.status(500).json({
        error: 'Failed to get genres',
        message: error.message
      });
    }
  } else {
    res.status(405).json({ error: 'Method not allowed' });
  }
};
