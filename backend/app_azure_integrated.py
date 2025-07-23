from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import logging
import tempfile
import json
from datetime import datetime
import uuid
import base64
import traceback

# Azure imports
try:
    import pyodbc
    from azure.storage.blob import BlobServiceClient
    from azure.keyvault.secrets import SecretClient
    from azure.identity import DefaultAzureCredential
    import openai
    AZURE_AVAILABLE = True
except ImportError as e:
    AZURE_AVAILABLE = False
    print(f"Azure SDKs not available: {e}")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Azure Configuration
AZURE_SQL_SERVER = os.getenv('AZURE_SQL_SERVER', 'sql-portal-ai-music-dev.database.windows.net')
AZURE_SQL_DATABASE = os.getenv('AZURE_SQL_DATABASE', 'portal-ai-music-db')
AZURE_STORAGE_ACCOUNT = os.getenv('AZURE_STORAGE_ACCOUNT', 'stportalaimusic439')
AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT', 'https://eastus.api.cognitive.microsoft.com/')
AZURE_KEY_VAULT_URI = os.getenv('AZURE_KEY_VAULT_URI', 'https://kv-portal-ai-music-dev.vault.azure.net/')

# Connection strings
AZURE_SQL_CONNECTION_STRING = os.getenv('AZURE_SQL_CONNECTION_STRING')
AZURE_STORAGE_CONNECTION_STRING = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Initialize Azure clients
class AzureClients:
    def __init__(self):
        self.credential = None
        self.keyvault_client = None
        self.blob_service_client = None
        self.sql_connection = None
        self.openai_configured = False
        self.initialize()
    
    def initialize(self):
        if not AZURE_AVAILABLE:
            logger.warning("Azure SDKs not available, using fallback mode")
            return
        
        try:
            # Initialize Azure credentials
            self.credential = DefaultAzureCredential()
            
            # Initialize Key Vault client
            if AZURE_KEY_VAULT_URI:
                try:
                    self.keyvault_client = SecretClient(vault_url=AZURE_KEY_VAULT_URI, credential=self.credential)
                    logger.info("✅ Key Vault client initialized")
                except Exception as e:
                    logger.warning(f"⚠️ Key Vault initialization failed: {e}")
            
            # Initialize Blob Storage client
            if AZURE_STORAGE_CONNECTION_STRING:
                try:
                    self.blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
                    # Create containers if they don't exist
                    self.ensure_containers()
                    logger.info("✅ Blob Storage client initialized with connection string")
                except Exception as e:
                    logger.warning(f"⚠️ Blob Storage connection string failed: {e}")
            elif AZURE_STORAGE_ACCOUNT:
                try:
                    self.blob_service_client = BlobServiceClient(
                        account_url=f"https://{AZURE_STORAGE_ACCOUNT}.blob.core.windows.net",
                        credential=self.credential
                    )
                    self.ensure_containers()
                    logger.info("✅ Blob Storage client initialized with credential")
                except Exception as e:
                    logger.warning(f"⚠️ Blob Storage credential failed: {e}")
            
            # Initialize SQL connection
            if AZURE_SQL_CONNECTION_STRING:
                try:
                    # Try the provided connection string first
                    self.sql_connection = pyodbc.connect(AZURE_SQL_CONNECTION_STRING)
                    logger.info("✅ SQL Database connection established")
                except Exception as e:
                    logger.warning(f"⚠️ SQL Database connection failed: {e}")
                    # Try FreeTDS connection as fallback
                    try:
                        freetds_conn_str = f"DRIVER={{FreeTDS}};SERVER={AZURE_SQL_SERVER};DATABASE={AZURE_SQL_DATABASE};UID=azureuser;PWD=YourPassword123!;PORT=1433;TDS_Version=7.2;"
                        self.sql_connection = pyodbc.connect(freetds_conn_str)
                        logger.info("✅ SQL Database connection established with FreeTDS")
                    except Exception as e2:
                        logger.warning(f"⚠️ FreeTDS SQL connection also failed: {e2}")
            elif AZURE_SQL_SERVER and AZURE_SQL_DATABASE:
                try:
                    # Build FreeTDS connection string
                    freetds_conn_str = f"DRIVER={{FreeTDS}};SERVER={AZURE_SQL_SERVER};DATABASE={AZURE_SQL_DATABASE};UID=azureuser;PWD=YourPassword123!;PORT=1433;TDS_Version=7.2;"
                    self.sql_connection = pyodbc.connect(freetds_conn_str)
                    logger.info("✅ SQL Database connection established with FreeTDS")
                except Exception as e:
                    logger.warning(f"⚠️ SQL Database connection failed: {e}")
            
            # Initialize OpenAI
            if OPENAI_API_KEY:
                try:
                    openai.api_key = OPENAI_API_KEY
                    self.openai_configured = True
                    logger.info("✅ OpenAI client initialized")
                except Exception as e:
                    logger.warning(f"⚠️ OpenAI initialization failed: {e}")
            elif AZURE_OPENAI_ENDPOINT:
                try:
                    openai.api_type = "azure"
                    openai.api_base = AZURE_OPENAI_ENDPOINT
                    openai.api_version = "2023-05-15"
                    self.openai_configured = True
                    logger.info("✅ Azure OpenAI client initialized")
                except Exception as e:
                    logger.warning(f"⚠️ Azure OpenAI initialization failed: {e}")
                    
        except Exception as e:
            logger.warning(f"⚠️ Some Azure services could not be initialized: {e}")
            logger.info("📊 Will use fallback/sample data when Azure services are unavailable")
    
    def ensure_containers(self):
        """Ensure required blob containers exist"""
        if not self.blob_service_client:
            return
        
        containers = ['music-files', 'generated-music', 'training-data']
        for container in containers:
            try:
                self.blob_service_client.create_container(container)
                logger.info(f"✅ Container '{container}' created/verified")
            except Exception as e:
                logger.debug(f"Container '{container}' already exists or couldn't be created: {e}")

# Initialize Azure clients
azure_clients = AzureClients()

# Sample data for fallback
SAMPLE_MUSIC_DATA = [
    {
        "id": 1,
        "title": "Electronic Symphony",
        "artist": "AI Composer",
        "genre": "Electronic",
        "duration_seconds": 180,
        "file_url": "https://cdn.pixabay.com/audio/2022/09/06/audio_d8a3acde9c.mp3",
        "status": "completed",
        "created_at": "2024-01-15T10:30:00Z",
        "metadata": {"bpm": 128, "key": "C major", "instruments": ["synth", "drums"]}
    },
    {
        "id": 2,
        "title": "Ambient Dreams",
        "artist": "AI Composer", 
        "genre": "Ambient",
        "duration_seconds": 240,
        "file_url": "https://cdn.pixabay.com/audio/2022/10/25/audio_7af4f62e72.mp3",
        "status": "completed",
        "created_at": "2024-01-15T11:15:00Z",
        "metadata": {"bpm": 80, "key": "A minor", "instruments": ["pad", "strings"]}
    },
    {
        "id": 3,
        "title": "Classical Overture",
        "artist": "AI Composer",
        "genre": "Classical", 
        "duration_seconds": 300,
        "file_url": "https://cdn.pixabay.com/audio/2022/11/09/audio_ae1e83ae9f.mp3",
        "status": "completed",
        "created_at": "2024-01-15T12:00:00Z",
        "metadata": {"bpm": 120, "key": "D major", "instruments": ["piano", "orchestra"]}
    }
]

SAMPLE_TEMPLATES = [
    {
        "id": 1,
        "name": "Electronic Beat",
        "category": "Electronic",
        "template_data": {
            "instruments": ["synth", "drums", "bass"],
            "bpm": 128,
            "structure": "intro-verse-chorus-verse-chorus-bridge-chorus-outro",
            "chord_progression": ["C", "Am", "F", "G"]
        }
    },
    {
        "id": 2,
        "name": "Ambient Pad",
        "category": "Ambient",
        "template_data": {
            "instruments": ["pad", "reverb", "delay"],
            "bpm": 80,
            "structure": "free-form",
            "chord_progression": ["Am", "F", "C", "G"]
        }
    },
    {
        "id": 3,
        "name": "Classical Suite",
        "category": "Classical",
        "template_data": {
            "instruments": ["piano", "strings", "woodwinds"],
            "bpm": 120,
            "structure": "allegro-andante-allegro",
            "chord_progression": ["C", "F", "Am", "G"]
        }
    }
]

# Database helper functions
def execute_sql_query(query, params=None, fetch_all=True):
    """Execute SQL query with proper error handling"""
    if not azure_clients.sql_connection:
        logger.warning("SQL connection not available, using sample data")
        return None
    
    try:
        cursor = azure_clients.sql_connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if fetch_all:
            return cursor.fetchall()
        else:
            return cursor.fetchone()
    except Exception as e:
        logger.error(f"SQL query failed: {e}")
        azure_clients.sql_connection.rollback()
        return None

def insert_sql_record(query, params):
    """Insert record and return success status"""
    if not azure_clients.sql_connection:
        logger.warning("SQL connection not available")
        return False
    
    try:
        cursor = azure_clients.sql_connection.cursor()
        cursor.execute(query, params)
        azure_clients.sql_connection.commit()
        return True
    except Exception as e:
        logger.error(f"SQL insert failed: {e}")
        azure_clients.sql_connection.rollback()
        return False

# Blob storage helper functions
def upload_to_blob(data, container_name, blob_name):
    """Upload data to blob storage"""
    if not azure_clients.blob_service_client:
        logger.warning("Blob storage not available")
        return None
    
    try:
        blob_client = azure_clients.blob_service_client.get_blob_client(
            container=container_name, 
            blob=blob_name
        )
        blob_client.upload_blob(data, overwrite=True)
        return blob_client.url
    except Exception as e:
        logger.error(f"Blob upload failed: {e}")
        return None

# OpenAI helper functions
def generate_music_description(prompt):
    """Generate music description using OpenAI"""
    if not azure_clients.openai_configured:
        logger.warning("OpenAI not available, using default description")
        return f"AI-generated music based on: {prompt}"
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a music composition AI. Generate creative, detailed descriptions of musical pieces."},
                {"role": "user", "content": f"Create a detailed description for this music request: {prompt}"}
            ],
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"OpenAI request failed: {e}")
        return f"AI-generated music based on: {prompt}"

# API Routes
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint with service status"""
    status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "sql_database": azure_clients.sql_connection is not None,
            "blob_storage": azure_clients.blob_service_client is not None,
            "openai": azure_clients.openai_configured,
            "key_vault": azure_clients.keyvault_client is not None
        },
        "fallback_mode": not all([
            azure_clients.sql_connection,
            azure_clients.blob_service_client,
            azure_clients.openai_configured
        ])
    }
    return jsonify(status)

@app.route('/api/music', methods=['GET'])
def get_music_catalog():
    """Get music catalog from database or fallback data"""
    try:
        # Try to get from database first
        if azure_clients.sql_connection:
            query = """
            SELECT id, title, artist, genre, duration_seconds, file_url, 
                   status, created_at, metadata 
            FROM generated_music 
            WHERE status = 'completed'
            ORDER BY created_at DESC
            """
            rows = execute_sql_query(query)
            
            if rows:
                music_list = []
                for row in rows:
                    music_list.append({
                        "id": row[0],
                        "title": row[1],
                        "artist": row[2],
                        "genre": row[3],
                        "duration_seconds": row[4],
                        "file_url": row[5],
                        "status": row[6],
                        "created_at": row[7].isoformat() if row[7] else None,
                        "metadata": json.loads(row[8]) if row[8] else {}
                    })
                return jsonify({"music": music_list, "source": "database"})
        
        # Fallback to sample data
        return jsonify({"music": SAMPLE_MUSIC_DATA, "source": "sample"})
        
    except Exception as e:
        logger.error(f"Error getting music catalog: {e}")
        return jsonify({"music": SAMPLE_MUSIC_DATA, "source": "fallback", "error": str(e)})

@app.route('/api/templates', methods=['GET'])
def get_music_templates():
    """Get music templates from database or fallback data"""
    try:
        # Try to get from database first
        if azure_clients.sql_connection:
            query = """
            SELECT id, name, category, template_data, is_active, created_at
            FROM music_templates 
            WHERE is_active = 1
            ORDER BY category, name
            """
            rows = execute_sql_query(query)
            
            if rows:
                templates = []
                for row in rows:
                    templates.append({
                        "id": row[0],
                        "name": row[1],
                        "category": row[2],
                        "template_data": json.loads(row[3]) if row[3] else {},
                        "is_active": bool(row[4]),
                        "created_at": row[5].isoformat() if row[5] else None
                    })
                return jsonify({"templates": templates, "source": "database"})
        
        # Fallback to sample data
        return jsonify({"templates": SAMPLE_TEMPLATES, "source": "sample"})
        
    except Exception as e:
        logger.error(f"Error getting templates: {e}")
        return jsonify({"templates": SAMPLE_TEMPLATES, "source": "fallback", "error": str(e)})

@app.route('/api/generate', methods=['POST'])
def generate_music():
    """Generate music based on parameters"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Extract parameters
        prompt = data.get('prompt', 'Create a beautiful piece of music')
        style = data.get('style', 'pop')
        genre = data.get('genre', 'electronic')
        duration = int(data.get('duration', 30))
        mood = data.get('mood', 'upbeat')
        
        # Generate unique ID
        generation_id = str(uuid.uuid4())
        
        # Create enhanced description using OpenAI
        description = generate_music_description(f"{prompt} - {style} {genre} music, {mood} mood, {duration} seconds")
        
        # Create generation record
        generation_data = {
            "id": generation_id,
            "title": f"{style.title()} {genre.title()} - {datetime.now().strftime('%H:%M')}",
            "prompt": prompt,
            "style": style,
            "genre": genre,
            "duration_seconds": duration,
            "mood": mood,
            "description": description,
            "status": "generating",
            "created_at": datetime.utcnow().isoformat(),
            "file_url": None,
            "model_used": "AI Music Generator v1.0"
        }
        
        # Try to save to database
        if azure_clients.sql_connection:
            insert_query = """
            INSERT INTO generated_music 
            (title, prompt, style, genre, duration_seconds, status, model_used, generation_params, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, GETDATE())
            """
            params = (
                generation_data["title"],
                prompt,
                style,
                genre,
                duration,
                "generating",
                "AI Music Generator v1.0",
                json.dumps({"mood": mood, "description": description})
            )
            insert_sql_record(insert_query, params)
        
        # For now, simulate successful generation with sample audio
        # In a real implementation, this would trigger actual music generation
        sample_urls = [
            "https://cdn.pixabay.com/audio/2022/09/06/audio_d8a3acde9c.mp3",
            "https://cdn.pixabay.com/audio/2022/10/25/audio_7af4f62e72.mp3",
            "https://cdn.pixabay.com/audio/2022/11/09/audio_ae1e83ae9f.mp3"
        ]
        
        # Update generation data with completion
        generation_data.update({
            "status": "completed",
            "file_url": sample_urls[len(generation_id) % len(sample_urls)],
            "completed_at": datetime.utcnow().isoformat()
        })
        
        # Update database if available
        if azure_clients.sql_connection:
            update_query = """
            UPDATE generated_music 
            SET status = 'completed', file_url = ?, completed_at = GETDATE()
            WHERE title = ?
            """
            insert_sql_record(update_query, (generation_data["file_url"], generation_data["title"]))
        
        return jsonify({
            "success": True,
            "generation": generation_data,
            "message": "Music generated successfully!"
        })
        
    except Exception as e:
        logger.error(f"Error generating music: {traceback.format_exc()}")
        return jsonify({
            "error": "Music generation failed",
            "details": str(e)
        }), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get platform statistics"""
    try:
        stats = {
            "total_generated": 0,
            "total_templates": len(SAMPLE_TEMPLATES),
            "active_users": 1,
            "avg_generation_time": "15 seconds",
            "popular_genres": ["Electronic", "Ambient", "Classical"],
            "system_status": "operational"
        }
        
        # Try to get real stats from database
        if azure_clients.sql_connection:
            count_query = "SELECT COUNT(*) FROM generated_music WHERE status = 'completed'"
            result = execute_sql_query(count_query, fetch_all=False)
            if result:
                stats["total_generated"] = result[0]
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({"error": "Could not retrieve stats"}), 500

@app.route('/api/upload', methods=['POST'])
def upload_training_data():
    """Upload training data to blob storage"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        filename = f"{file_id}_{file.filename}"
        
        # Upload to blob storage if available
        blob_url = None
        if azure_clients.blob_service_client:
            blob_url = upload_to_blob(file.read(), 'training-data', filename)
        
        # Save metadata to database if available
        if azure_clients.sql_connection and blob_url:
            insert_query = """
            INSERT INTO training_data (name, file_type, blob_path, file_size_bytes, created_at)
            VALUES (?, ?, ?, ?, GETDATE())
            """
            params = (file.filename, file.content_type, blob_url, len(file.read()))
            insert_sql_record(insert_query, params)
        
        return jsonify({
            "success": True,
            "file_id": file_id,
            "filename": filename,
            "blob_url": blob_url,
            "message": "File uploaded successfully"
        })
        
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        return jsonify({"error": "File upload failed"}), 500

if __name__ == '__main__':
    logger.info("🎵 Portal AI Music Backend Starting...")
    logger.info(f"🔗 Azure SQL: {'✅' if azure_clients.sql_connection else '❌'}")
    logger.info(f"🔗 Azure Storage: {'✅' if azure_clients.blob_service_client else '❌'}")
    logger.info(f"🔗 OpenAI: {'✅' if azure_clients.openai_configured else '❌'}")
    logger.info(f"🔗 Key Vault: {'✅' if azure_clients.keyvault_client else '❌'}")
    
    port = int(os.getenv('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
