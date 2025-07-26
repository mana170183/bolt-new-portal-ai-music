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

  // Health check endpoint
  if (req.method === 'GET') {
    try {
      const healthData = {
        status: 'healthy',
        message: 'AI Music Backend API is running',
        version: '2.0.0',
        timestamp: new Date().toISOString(),
        backend: 'Node.js Serverless'
      };

      res.status(200).json(healthData);
    } catch (error) {
      console.error('Health check error:', error);
      res.status(500).json({
        status: 'error',
        message: error.message
      });
    }
  } else {
    res.status(405).json({ error: 'Method not allowed' });
  }
};
