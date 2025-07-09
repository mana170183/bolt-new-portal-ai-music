// User quota Netlify function
import { prisma } from './utils/db.js';

export async function handler(event, context) {
  // Set CORS headers
  const headers = {
    'Access-Control-Allow-Origin': '*', // Or restrict to your domain
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Content-Type': 'application/json'
  };

  // Handle preflight requests for CORS
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers,
      body: ''
    };
  }

  try {
    // Extract user ID from authorization header or query params
    let userId = 'demo_user'; // Default user ID
    const authHeader = event.headers.authorization || '';
    
    if (authHeader.startsWith('Bearer ')) {
      // Extract token and decode/verify it
      const token = authHeader.substring(7);
      try {
        // Here you would decode and verify the JWT token
        // For now we're using a simple placeholder
        // userId = verifyToken(token);
      } catch (tokenError) {
        console.error('Token verification failed:', tokenError);
      }
    }

    // Get user quota from database
    let quota = {};
    try {
      // Try to find user quota in database
      const user = await prisma.user.findUnique({
        where: { id: userId },
        select: {
          quotaUsed: true,
          quotaTotal: true,
          plan: true
        }
      });

      if (user) {
        quota = {
          used: user.quotaUsed || 0,
          total: user.quotaTotal || 10,
          remaining: Math.max(0, (user.quotaTotal || 10) - (user.quotaUsed || 0)),
          plan: user.plan || 'free',
          nextReset: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString() // 24 hours from now
        };
      } else {
        // If no user found, provide default quota
        quota = {
          used: 0,
          total: 10,
          remaining: 10,
          plan: 'free',
          nextReset: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString() // 24 hours from now
        };
      }
    } catch (dbError) {
      console.error('Database query failed:', dbError);
      // Fallback to default quota values
      quota = {
        used: 0,
        total: 10,
        remaining: 10,
        plan: 'free',
        nextReset: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString() // 24 hours from now
      };
    }
    
    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        success: true,
        quota
      })
    };
  } catch (error) {
    console.error('Error fetching user quota:', error);
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ 
        success: false, 
        error: 'Failed to fetch user quota',
        message: error.message
      })
    };
  }
}
