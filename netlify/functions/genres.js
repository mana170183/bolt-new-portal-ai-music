// Genres Netlify function
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
    // Get genres from database
    let genres = [];
    try {
      genres = await prisma.genre.findMany({
        orderBy: { name: 'asc' }
      });
    } catch (dbError) {
      console.error('Database query failed:', dbError);
      // Fallback to default genres if database query fails
      genres = [
        {id: 'pop', name: 'Pop', description: 'Catchy, mainstream melodies'},
        {id: 'rock', name: 'Rock', description: 'Guitar-driven, energetic'},
        {id: 'electronic', name: 'Electronic', description: 'Synthesized, digital sounds'},
        {id: 'hip-hop', name: 'Hip Hop', description: 'Rhythmic, spoken vocals'},
        {id: 'jazz', name: 'Jazz', description: 'Improvisational, complex harmonies'},
        {id: 'classical', name: 'Classical', description: 'Orchestral, sophisticated compositions'}
      ];
    }
    
    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        success: true,
        genres
      })
    };
  } catch (error) {
    console.error('Error fetching genres:', error);
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ 
        success: false, 
        error: 'Failed to fetch genres',
        message: error.message
      })
    };
  }
}
