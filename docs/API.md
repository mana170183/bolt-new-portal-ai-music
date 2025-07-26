# API Documentation

Portal AI Music Backend API provides endpoints for generating AI music and managing tracks.

## Base URL

- **Development**: `http://localhost:5000`
- **Production**: `https://your-app-name.azurewebsites.net`

## Authentication

Currently, the API is open for demonstration purposes. In production, implement authentication using Azure AD B2C or similar.

## Endpoints

### Health Check

Check if the API is running and healthy.

**GET** `/health`

#### Response

```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "service": "Portal AI Music API"
}
```

### Generate Music

Generate AI music based on text prompt and parameters.

**POST** `/api/generate-music`

#### Request Body

```json
{
  "prompt": "An upbeat pop song with electronic beats",
  "duration": 30,
  "genre": "pop",
  "mood": "upbeat"
}
```

#### Parameters

| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| `prompt` | string | Yes | Text description of the desired music | - |
| `duration` | integer | No | Length in seconds (10-300) | 30 |
| `genre` | string | No | Music genre | "pop" |
| `mood` | string | No | Music mood/feeling | "upbeat" |

#### Response

**Success (200)**
```json
{
  "status": "success",
  "track": {
    "id": "uuid-string",
    "title": "Upbeat Pop Track",
    "duration": 30,
    "genre": "pop",
    "mood": "upbeat",
    "prompt": "An upbeat pop song with electronic beats",
    "url": "https://example.com/tracks/uuid.mp3",
    "download_url": "https://example.com/download/uuid.wav",
    "created_at": "2024-01-15T10:30:00.000Z"
  }
}
```

**Error (400)**
```json
{
  "status": "error",
  "message": "Prompt is required"
}
```

**Error (500)**
```json
{
  "status": "error",
  "message": "Failed to generate music. Please try again."
}
```

### Get Sample Tracks

Retrieve sample tracks for demonstration.

**GET** `/api/tracks`

#### Response

```json
{
  "status": "success",
  "tracks": [
    {
      "id": "track_001",
      "title": "Upbeat Pop Energy",
      "duration": 30,
      "genre": "pop",
      "mood": "upbeat",
      "url": "https://example.com/sample1.mp3",
      "download_url": "https://example.com/download/sample1.wav"
    }
  ]
}
```

### Get Available Genres

Get list of supported music genres.

**GET** `/api/genres`

#### Response

```json
{
  "status": "success",
  "genres": [
    "pop",
    "rock",
    "electronic",
    "classical",
    "jazz",
    "hip-hop",
    "country",
    "folk",
    "ambient",
    "cinematic",
    "blues",
    "reggae"
  ]
}
```

### Get Available Moods

Get list of supported music moods.

**GET** `/api/moods`

#### Response

```json
{
  "status": "success",
  "moods": [
    "upbeat",
    "calm",
    "energetic",
    "melancholic",
    "mysterious",
    "romantic",
    "epic",
    "peaceful",
    "dramatic",
    "playful"
  ]
}
```

## Error Handling

All endpoints return consistent error responses:

```json
{
  "status": "error",
  "message": "Human-readable error message"
}
```

### HTTP Status Codes

- `200` - Success
- `400` - Bad Request (invalid parameters)
- `404` - Not Found (endpoint doesn't exist)
- `500` - Internal Server Error

## Rate Limiting

In production, implement rate limiting:
- Free tier: 5 requests per minute
- Paid tier: 100 requests per minute

## CORS

The API supports CORS for web applications. Allowed origins are configured based on environment.

## Data Formats

### Audio Formats

Generated music is available in multiple formats:
- **MP3**: Compressed, suitable for web playback
- **WAV**: Uncompressed, high quality
- **FLAC**: Lossless compression (premium only)

### Duration Limits

- **Free tier**: 10-30 seconds
- **Creator tier**: 10-180 seconds  
- **Professional tier**: 10-600 seconds

## Implementation Notes

### Current Implementation

The current API returns mock data for demonstration. In production:

1. Replace mock responses with actual AI model integration
2. Implement Azure Blob Storage for file management
3. Add user authentication and authorization
4. Implement proper error logging and monitoring

### AI Model Integration

For production deployment, integrate with:

```python
from transformers import pipeline

# Initialize MusicGen model
music_generator = pipeline("text-to-audio", model="facebook/musicgen-small")

# Generate music
audio = music_generator(prompt, max_length=duration)
```

### Azure Blob Storage

Store generated files in Azure Blob Storage:

```python
from azure.storage.blob import BlobServiceClient

# Upload generated audio
blob_client = container_client.get_blob_client(blob_name)
blob_client.upload_blob(audio_data)
```

## SDK Examples

### JavaScript/TypeScript

```javascript
const API_BASE_URL = 'https://your-api.azurewebsites.net';

async function generateMusic(prompt, options = {}) {
  const response = await fetch(`${API_BASE_URL}/api/generate-music`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      prompt,
      duration: options.duration || 30,
      genre: options.genre || 'pop',
      mood: options.mood || 'upbeat'
    })
  });
  
  if (!response.ok) {
    throw new Error('Failed to generate music');
  }
  
  return await response.json();
}

// Usage
try {
  const result = await generateMusic('Upbeat electronic dance music', {
    duration: 60,
    genre: 'electronic',
    mood: 'energetic'
  });
  console.log('Generated track:', result.track);
} catch (error) {
  console.error('Error:', error.message);
}
```

### Python

```python
import requests

API_BASE_URL = 'https://your-api.azurewebsites.net'

def generate_music(prompt, duration=30, genre='pop', mood='upbeat'):
    response = requests.post(f'{API_BASE_URL}/api/generate-music', json={
        'prompt': prompt,
        'duration': duration,
        'genre': genre,
        'mood': mood
    })
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f'API Error: {response.json().get("message", "Unknown error")}')

# Usage
try:
    result = generate_music('Calm ambient music for meditation', 
                          duration=120, genre='ambient', mood='peaceful')
    print(f'Generated track: {result["track"]["title"]}')
except Exception as e:
    print(f'Error: {e}')
```

## Webhooks (Future Feature)

For long-running music generation tasks, webhooks can notify when generation is complete:

```json
{
  "event": "music.generated",
  "track_id": "uuid-string",
  "status": "completed",
  "download_url": "https://storage.com/track.wav",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

## Support

For API support:
- Documentation: [GitHub Repository](https://github.com/yourusername/portal-ai-music)
- Issues: [GitHub Issues](https://github.com/yourusername/portal-ai-music/issues)
- Email: support@portalaimusic.com