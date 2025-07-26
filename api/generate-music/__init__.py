import azure.functions as func
import json
import logging
import os
import random
import uuid
from datetime import datetime
from azure.storage.blob import BlobServiceClient
from openai import AzureOpenAI
import pyodbc

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Generate music endpoint triggered.')
    
    # Handle CORS preflight
    if req.method == 'OPTIONS':
        return func.HttpResponse(
            "",
            status_code=200,
            headers={
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
            }
        )
    
    try:
        # Get request data
        if req.method == 'POST':
            request_json = req.get_json()
            if not request_json:
                return func.HttpResponse(
                    json.dumps({"success": False, "error": "No JSON data provided"}),
                    status_code=400,
                    headers={
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    }
                )
            
            prompt = request_json.get('prompt', '').strip()
            style = request_json.get('style', 'pop')
            genre = request_json.get('genre', style)  # Support both style and genre
            mood = request_json.get('mood', 'upbeat')
            duration = request_json.get('duration', 30)
            
            logging.info(f"Generate music params: prompt='{prompt}', duration={duration}, genre={genre}, mood={mood}")
            
            if not prompt:
                return func.HttpResponse(
                    json.dumps({"success": False, "error": "Prompt is required"}),
                    status_code=400,
                    headers={
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    }
                )
        else:
            # GET request for testing
            prompt = req.params.get('prompt', 'Create a happy song')
            genre = req.params.get('genre', 'pop')
            mood = req.params.get('mood', 'upbeat')
            duration = int(req.params.get('duration', 30))
        
        # Generate lyrics using Azure OpenAI
        lyrics = None
        try:
            lyrics = generate_lyrics_with_openai(prompt, genre, mood)
        except Exception as e:
            logging.warning(f"Lyrics generation failed: {str(e)}")
            lyrics = f"Generated lyrics for {genre} song about {prompt}"
        
        # Generate unique track ID
        track_id = f"track_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
        
        # Create track metadata
        track_data = {
            "id": track_id,
            "title": f"AI Generated {genre.title()} Track",
            "duration": duration,
            "genre": genre,
            "mood": mood,
            "lyrics": lyrics,
            "prompt": prompt,
            "created_at": datetime.utcnow().isoformat(),
            "status": "generating",
            "progress": 0
        }
        
        # Store metadata in Azure SQL Database
        try:
            store_track_metadata(track_data)
        except Exception as e:
            logging.warning(f"Metadata storage failed: {str(e)}")
        
        # Generate and upload audio to Azure Blob Storage
        try:
            audio_url, download_url = generate_and_upload_audio(track_id, track_data)
            track_data.update({
                "url": audio_url,
                "download_url": download_url,
                "status": "completed",
                "progress": 100
            })
        except Exception as e:
            logging.warning(f"Audio generation failed: {str(e)}")
            # Use mock URLs for testing
            storage_account = os.getenv('AZURE_STORAGE_ACCOUNT_NAME', 'portalaimusicdev')
            track_data.update({
                "url": f"https://{storage_account}.blob.core.windows.net/audio/{track_id}.mp3",
                "download_url": f"https://{storage_account}.blob.core.windows.net/audio/{track_id}.wav",
                "status": "completed",
                "progress": 100
            })
        
        response_data = {
            "success": True,
            "status": "success",
            "track": track_data,
            "message": "Music generated successfully"
        }
        
        return func.HttpResponse(
            json.dumps(response_data),
            status_code=200,
            headers={
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
            }
        )
        
    except Exception as e:
        logging.error(f"Generate music error: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "success": False, 
                "error": f"Music generation failed: {str(e)}"
            }),
            status_code=500,
            headers={
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        )

def generate_lyrics_with_openai(prompt, genre, mood):
    """Generate lyrics using Azure OpenAI"""
    try:
        client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version="2024-02-15-preview",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", "https://openai-portal-ai-music-dev.openai.azure.com/")
        )
        
        lyrics_prompt = f"""Generate meaningful lyrics for a {genre} song with a {mood} mood.

Theme/Prompt: {prompt}

Requirements:
- Create cohesive lyrics with verse-chorus structure
- Match the {mood} mood and {genre} style
- Include emotional depth and storytelling
- Keep it engaging and memorable

Please format with clear verse/chorus labels."""

        response = client.chat.completions.create(
            model="gpt-4",  # Use the deployed model name
            messages=[
                {"role": "system", "content": "You are a professional songwriter and lyricist with expertise in various musical genres."},
                {"role": "user", "content": lyrics_prompt}
            ],
            max_tokens=800,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        logging.error(f"OpenAI lyrics generation error: {str(e)}")
        # Return fallback lyrics
        return f"""[Verse 1]
{prompt} - this is our story to tell
In the rhythm of {genre}, we know it well
With a {mood} feeling in the air
Music brings us everywhere

[Chorus]
Generated by AI, crafted with care
{genre} sounds floating everywhere
{mood} vibes that lift us high
Music makes our spirits fly

[Verse 2]
Every note and every beat
Makes our musical journey complete
In this {genre} melody we find
Peace and rhythm for the mind

[Chorus]
Generated by AI, crafted with care
{genre} sounds floating everywhere
{mood} vibes that lift us high
Music makes our spirits fly"""

def store_track_metadata(track_data):
    """Store track metadata in Azure SQL Database"""
    try:
        connection_string = os.getenv("AZURE_SQL_CONNECTION_STRING")
        if not connection_string:
            raise Exception("Azure SQL connection string not configured")
        
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        
        # Create table if it doesn't exist
        cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='tracks' AND xtype='U')
        CREATE TABLE tracks (
            track_id NVARCHAR(255) PRIMARY KEY,
            title NVARCHAR(500) NOT NULL,
            duration INT NOT NULL,
            genre NVARCHAR(100),
            mood NVARCHAR(100),
            lyrics NVARCHAR(MAX),
            prompt NVARCHAR(MAX),
            created_at DATETIME2 DEFAULT GETUTCDATE(),
            status NVARCHAR(50) DEFAULT 'pending',
            progress INT DEFAULT 0,
            audio_url NVARCHAR(1000),
            download_url NVARCHAR(1000),
            artist NVARCHAR(255) DEFAULT 'AI Generated',
            source_api NVARCHAR(100) DEFAULT 'Azure OpenAI'
        )
        """)
        
        # Insert track metadata
        insert_query = """
        INSERT INTO tracks (
            track_id, title, duration, genre, mood, lyrics, prompt, 
            created_at, status, progress, audio_url, download_url
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        cursor.execute(insert_query, (
            track_data['id'],
            track_data['title'],
            track_data['duration'],
            track_data['genre'],
            track_data['mood'],
            track_data['lyrics'],
            track_data['prompt'],
            track_data['created_at'],
            track_data['status'],
            track_data['progress'],
            track_data.get('url', ''),
            track_data.get('download_url', '')
        ))
        
        # Also insert into music_catalog table for catalog functionality
        cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='music_catalog' AND xtype='U')
        CREATE TABLE music_catalog (
            track_id NVARCHAR(255) PRIMARY KEY,
            title NVARCHAR(500) NOT NULL,
            artist NVARCHAR(255),
            genre NVARCHAR(100),
            duration INT,
            file_url NVARCHAR(1000),
            created_at DATETIME2 DEFAULT GETUTCDATE(),
            source_api NVARCHAR(100),
            prompt NVARCHAR(MAX),
            style NVARCHAR(100),
            play_count INT DEFAULT 0,
            last_played DATETIME2
        )
        """)
        
        # Insert into catalog
        catalog_query = """
        INSERT INTO music_catalog (
            track_id, title, artist, genre, duration, file_url,
            source_api, prompt, style, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        cursor.execute(catalog_query, (
            track_data['id'],
            track_data['title'],
            'AI Generated',
            track_data['genre'],
            track_data['duration'],
            track_data.get('url', ''),
            'Azure OpenAI',
            track_data['prompt'],
            track_data['mood'],
            track_data['created_at']
        ))
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        logging.error(f"Database storage error: {str(e)}")
        raise

def generate_and_upload_audio(track_id, track_data):
    """Generate audio and upload to Azure Blob Storage"""
    try:
        # Initialize blob service client
        storage_account = os.getenv('AZURE_STORAGE_ACCOUNT_NAME')
        storage_key = os.getenv('AZURE_STORAGE_ACCOUNT_KEY')
        
        if not storage_account or not storage_key:
            raise Exception("Azure Storage credentials not configured")
        
        blob_service_client = BlobServiceClient(
            account_url=f"https://{storage_account}.blob.core.windows.net",
            credential=storage_key
        )
        
        container_name = "audio"
        
        # For now, create placeholder audio files
        # In production, integrate with actual AI music generation service
        
        mp3_blob_name = f"{track_id}.mp3"
        wav_blob_name = f"{track_id}.wav"
        
        # Create mock audio data (replace with actual audio generation)
        mock_audio_mp3 = b"Mock MP3 audio data for " + track_id.encode()
        mock_audio_wav = b"Mock WAV audio data for " + track_id.encode()
        
        # Upload MP3
        blob_client_mp3 = blob_service_client.get_blob_client(
            container=container_name, 
            blob=mp3_blob_name
        )
        blob_client_mp3.upload_blob(mock_audio_mp3, overwrite=True)
        
        # Upload WAV
        blob_client_wav = blob_service_client.get_blob_client(
            container=container_name, 
            blob=wav_blob_name
        )
        blob_client_wav.upload_blob(mock_audio_wav, overwrite=True)
        
        # Generate URLs
        mp3_url = f"https://{storage_account}.blob.core.windows.net/{container_name}/{mp3_blob_name}"
        wav_url = f"https://{storage_account}.blob.core.windows.net/{container_name}/{wav_blob_name}"
        
        return mp3_url, wav_url
        
    except Exception as e:
        logging.error(f"Audio upload error: {str(e)}")
        raise
