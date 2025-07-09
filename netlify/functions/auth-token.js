// Auth token Netlify function
import jwt from 'jsonwebtoken';
import { prisma } from './utils/db.js';

// Secret key for JWT signing - should be in environment variables
const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key-change-this-in-production';

export async function handler(event, context) {
  // Set CORS headers
  const headers = {
    'Access-Control-Allow-Origin': '*', // Or restrict to your domain
    'Access-Control-Allow-Headers': 'Content-Type',
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

  // Only allow POST method
  if (event.httpMethod !== 'POST') {
    return {
      statusCode: 405,
      headers,
      body: JSON.stringify({ success: false, error: 'Method not allowed' })
    };
  }

  try {
    // Parse request body
    const body = JSON.parse(event.body);
    const userId = body.user_id || 'demo_user';
    const plan = body.plan || 'free';

    // Create or update user in database
    let user;
    try {
      user = await prisma.user.upsert({
        where: { id: userId },
        update: { plan },
        create: {
          id: userId,
          plan,
          quotaUsed: 0,
          quotaTotal: plan === 'free' ? 10 : 50
        }
      });
    } catch (dbError) {
      console.error('Database operation failed:', dbError);
      // Proceed with token generation anyway
    }

    // Generate JWT token
    const token = jwt.sign(
      { 
        userId, 
        plan,
        quotaTotal: user?.quotaTotal || (plan === 'free' ? 10 : 50)
      }, 
      JWT_SECRET, 
      { expiresIn: '7d' }
    );
    
    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        success: true,
        token,
        user: {
          id: userId,
          plan
        }
      })
    };
  } catch (error) {
    console.error('Error generating token:', error);
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ 
        success: false, 
        error: 'Failed to generate token',
        message: error.message
      })
    };
  }
}
