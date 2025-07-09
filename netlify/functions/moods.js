// Moods Netlify function
import { prisma } from './utils/db.js';

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

  try {
    // Get moods from database
    let moods = [];
    try {
      moods = await prisma.mood.findMany({
        orderBy: { name: 'asc' }
      });
    } catch (dbError) {
      console.error('Database query failed:', dbError);
      // Fallback to default moods if database query fails
      moods = [
        {id: 'upbeat', name: 'Upbeat', description: 'Happy, energetic feeling'},
        {id: 'calm', name: 'Calm', description: 'Peaceful, relaxing'},
        {id: 'energetic', name: 'Energetic', description: 'High-energy, motivating'},
        {id: 'melancholic', name: 'Melancholic', description: 'Sad, reflective'},
        {id: 'romantic', name: 'Romantic', description: 'Loving, passionate'},
        {id: 'dark', name: 'Dark', description: 'Ominous, mysterious'}
      ];
    }
    
    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        success: true,
        moods
      })
    };
  } catch (error) {
    console.error('Error fetching moods:', error);
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ 
        success: false, 
        error: 'Failed to fetch moods',
        message: error.message
      })
    };
  }
}
