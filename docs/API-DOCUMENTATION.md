# AI Music Portal - API Documentation

## Overview

The AI Music Portal provides a comprehensive set of APIs for AI-powered music generation, integrated with Azure services including OpenAI, SQL Database, and Blob Storage. The APIs also integrate with popular music services like Spotify and MusicBrainz.

## Base URLs

- **Production**: `https://your-static-web-app.azurestaticapps.net/api`
- **Development**: `http://localhost:7071/api`

## Authentication

Most endpoints require authentication via Bearer token:
```
Authorization: Bearer <token>
```

## API Endpoints

### 1. Health Check

**GET** `/health`

Check if the API is running.

**Response:**
```json
{
  "status": "healthy",
  "message": "AI Music Backend API is running",
  "version": "1.0.0",
  "timestamp": "2025-01-26T10:30:00Z"
}
```

### 2. Root Endpoint

**GET** `/`

Get API information and available endpoints.

**Response:**
```json
{
  "success": true,
  "message": "AI Music Portal API",
  "version": "1.0.0",
  "endpoints": [...]
}
```

### 3. Generate Music

**POST** `/generate-music`

Generate music using AI with basic parameters.

**Request Body:**
```json
{
  "prompt": "Create a relaxing ambient track",
  "genre": "ambient",
  "mood": "relaxing",
  "duration": 60
}
```

**Response:**
```json
{
  "success": true,
  "status": "success",
  "track": {
    "id": "track_20250126_123456_abcd1234",
    "title": "AI Generated Ambient Track",
    "duration": 60,
    "genre": "ambient",
    "mood": "relaxing",
    "lyrics": "Generated lyrics...",
    "prompt": "Create a relaxing ambient track",
    "url": "https://storage.blob.core.windows.net/audio/track_id.mp3",
    "download_url": "https://storage.blob.core.windows.net/audio/track_id.wav",
    "created_at": "2025-01-26T12:34:56Z",
    "status": "completed",
    "progress": 100
  },
  "message": "Music generated successfully"
}
```

### 4. Advanced Music Generation

**POST** `/advanced-generate`

Generate music with advanced parameters and control.

**Request Body:**
```json
{
  "prompt": "Epic orchestral battle theme",
  "genre": "orchestral",
  "mood": "epic",
  "duration": 180,
  "tempo": 120,
  "key": "C",
  "instruments": ["orchestra", "choir", "percussion"],
  "vocals": true,
  "structure": "intro-verse-chorus-bridge-chorus-outro",
  "lyricsStyle": "epic",
  "customTags": ["cinematic", "battle", "heroic"]
}
```

**Response:**
```json
{
  "success": true,
  "status": "success",
  "track": {
    "id": "advanced_20250126_123456_efgh5678",
    "title": "AI Generated Orchestral - Epic orchestral battle theme",
    "duration": 180,
    "genre": "orchestral",
    "mood": "epic",
    "tempo": 120,
    "key": "C",
    "instruments": ["orchestra", "choir", "percussion"],
    "vocals": true,
    "structure": "intro-verse-chorus-bridge-chorus-outro",
    "lyrics_style": "epic",
    "custom_tags": ["cinematic", "battle", "heroic"],
    "lyrics": "Detailed epic lyrics...",
    "prompt": "Epic orchestral battle theme",
    "url": "https://storage.blob.core.windows.net/audio/advanced_id.mp3",
    "download_url": "https://storage.blob.core.windows.net/audio/advanced_id.wav",
    "created_at": "2025-01-26T12:34:56Z",
    "status": "completed",
    "progress": 100
  },
  "message": "Advanced music generated successfully",
  "processing_time": "35 seconds",
  "quality": "high",
  "format": "wav"
}
```

### 5. Music Library

**GET** `/music-library`

Get user's saved music tracks.

**Query Parameters:**
- `user_id` (optional): User ID (default: "demo_user")
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 20)
- `genre` (optional): Filter by genre
- `mood` (optional): Filter by mood

**Response:**
```json
{
  "success": true,
  "tracks": [...],
  "page": 1,
  "limit": 20,
  "total": 2
}
```

**POST** `/music-library`

Save a track to user's library.

**Request Body:**
```json
{
  "track_id": "track_20250126_123456_abcd1234",
  "user_id": "demo_user"
}
```

**DELETE** `/music-library?track_id=<id>&user_id=<user_id>`

Remove a track from user's library.

### 6. Music APIs Integration

**GET** `/music-apis/{service}`

Access external music APIs for research and inspiration.

**Supported Services:**
- `spotify` (Paid API)
- `musicbrainz` (Free API)
- `freesound` (Free API with registration)
- `jamendo` (Free API)

#### Spotify API Examples:

**Search tracks:**
```
GET /music-apis/spotify?action=search&q=pop%20music&type=track&limit=20
```

**Get track details:**
```
GET /music-apis/spotify?action=track&id=4iV5W9uYEdYUVa79Axb7Rh
```

**Get recommendations:**
```
GET /music-apis/spotify?action=recommendations&genres=pop,rock&limit=20
```

#### MusicBrainz API Examples:

**Search recordings:**
```
GET /music-apis/musicbrainz?action=search&q=beethoven&type=recording&limit=20
```

**Get artist details:**
```
GET /music-apis/musicbrainz?action=artist&id=1f038562-a9f0-4525-be8f-c303babe2a8d
```

### 7. Genres and Moods

**GET** `/genres`

Get available music genres.

**Response:**
```json
{
  "success": true,
  "genres": [
    "pop", "rock", "jazz", "classical", "electronic", 
    "ambient", "orchestral", "folk", "country", "blues"
  ]
}
```

**GET** `/moods`

Get available music moods.

**Response:**
```json
{
  "success": true,
  "moods": [
    "happy", "sad", "energetic", "calm", "mysterious",
    "epic", "romantic", "upbeat", "melancholy", "triumphant"
  ]
}
```

### 8. Authentication

**POST** `/auth-token`

Generate authentication token.

**Request Body:**
```json
{
  "user_id": "user123",
  "plan": "premium"
}
```

**Response:**
```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 3600,
  "user_id": "user123",
  "plan": "premium"
}
```

### 9. User Quota

**GET** `/user-quota`

Check user's API usage quota.

**Query Parameters:**
- `user_id` (optional): User ID (default: "demo_user")

**Response:**
```json
{
  "success": true,
  "user_id": "demo_user",
  "plan": "free",
  "quota": {
    "daily_limit": 10,
    "daily_used": 3,
    "daily_remaining": 7,
    "monthly_limit": 100,
    "monthly_used": 25,
    "monthly_remaining": 75,
    "reset_time": "2025-01-27T00:00:00Z"
  }
}
```

## Error Responses

All endpoints return errors in this format:

```json
{
  "success": false,
  "error": "Error description",
  "code": "ERROR_CODE"
}
```

Common HTTP status codes:
- `400` - Bad Request (invalid parameters)
- `401` - Unauthorized (missing or invalid token)
- `403` - Forbidden (quota exceeded)
- `404` - Not Found
- `500` - Internal Server Error

## Rate Limiting

- **Free Plan**: 10 requests/day, 100 requests/month
- **Premium Plan**: 100 requests/day, 1000 requests/month
- **Enterprise Plan**: Unlimited

## Azure Services Integration

### Azure OpenAI
- **Purpose**: Lyrics generation and music description
- **Model**: GPT-4
- **Endpoint**: Configured via `AZURE_OPENAI_ENDPOINT`

### Azure SQL Database
- **Purpose**: Store track metadata, user libraries, and quotas
- **Tables**: `tracks`, `user_library`, `user_quotas`
- **Connection**: Uses connection string with encrypted communication

### Azure Blob Storage
- **Purpose**: Store generated audio files
- **Containers**: `audio` (for music files), `metadata` (for additional data)
- **Access**: Public read access for audio streaming

## External Music APIs Setup

### Spotify API (Paid)
1. Go to https://developer.spotify.com/dashboard/
2. Create a new app
3. Add environment variables:
   - `SPOTIFY_CLIENT_ID`
   - `SPOTIFY_CLIENT_SECRET`

### MusicBrainz API (Free)
- No setup required
- Automatic rate limiting applied

### Freesound API (Free)
1. Go to https://freesound.org/
2. Create account and apply for API access
3. Add environment variable: `FREESOUND_API_KEY`

### Jamendo API (Free)
1. Go to https://developer.jamendo.com/
2. Register your app
3. Add environment variable: `JAMENDO_CLIENT_ID`

## Example Frontend Integration

```javascript
import axios from 'axios';

const API_BASE_URL = 'https://your-app.azurestaticapps.net/api';

// Generate music
const generateMusic = async (prompt, genre, mood, duration) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/generate-music`, {
      prompt,
      genre,
      mood,
      duration
    }, {
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json'
      }
    });
    return response.data;
  } catch (error) {
    console.error('Music generation failed:', error);
    throw error;
  }
};

// Get music library
const getMusicLibrary = async (userId = 'demo_user', page = 1) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/music-library`, {
      params: { user_id: userId, page, limit: 20 },
      headers: { 'Authorization': `Bearer ${authToken}` }
    });
    return response.data;
  } catch (error) {
    console.error('Failed to get music library:', error);
    throw error;
  }
};
```

## Testing

You can test all endpoints using tools like Postman, curl, or the built-in Azure Static Web Apps testing tools.

### Sample curl commands:

```bash
# Health check
curl https://your-app.azurestaticapps.net/api/health

# Generate music
curl -X POST https://your-app.azurestaticapps.net/api/generate-music \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Happy birthday song", "genre": "pop", "mood": "happy", "duration": 30}'

# Get genres
curl https://your-app.azurestaticapps.net/api/genres
```
