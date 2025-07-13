# Free Platform Deployment Guide for Portal AI Music

> **Branch**: `stage` - This guide focuses on free/low-cost deployment alternatives for rapid prototyping and testing before moving to Azure production.

## Overview

This guide provides step-by-step instructions for deploying the Portal AI Music application using entirely free platforms, allowing you to test and validate your concept without any upfront costs. The architecture uses modern, production-ready services with generous free tiers.

## Architecture Overview

```
Frontend (Vercel) → API Gateway → Backend (Railway) → Database (Supabase)
                                      ↓
                               AI Services (Hugging Face)
                                      ↓
                               File Storage (Supabase Storage)
```

## Free Platform Stack

| Component | Platform | Free Tier Limits | Cost |
|-----------|----------|------------------|------|
| Frontend | Vercel | 100GB bandwidth/month | $0 |
| Backend API | Railway | $5 credit/month | $0 |
| Database | Supabase | 500MB DB, 1GB storage | $0 |
| AI/ML | Hugging Face | Rate-limited inference | $0 |
| Authentication | Supabase Auth | 50,000 MAU | $0 |
| File Storage | Supabase Storage | 1GB | $0 |
| Monitoring | Sentry | 5K errors/month | $0 |
| **Total** | | | **$0/month** |

## Prerequisites

1. GitHub account
2. Accounts on: Vercel, Railway, Supabase, Hugging Face
3. Node.js 18+ installed locally
4. Git CLI
5. Basic familiarity with React and Python/Flask

## Step-by-Step Deployment

### Phase 1: Setup Accounts & Services

#### 1.1 Create Supabase Project
```bash
# Go to https://supabase.com
# Click "Start your project" → "New project"
# Choose organization, name: "portal-ai-music"
# Set password and region
# Wait for setup to complete (~2 minutes)
```

#### 1.2 Setup Supabase Database Schema
```sql
-- Run in Supabase SQL Editor
CREATE TABLE users (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE music_generations (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  prompt TEXT NOT NULL,
  style TEXT,
  duration INTEGER,
  file_url TEXT,
  status TEXT DEFAULT 'pending',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE music_generations ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Users can view own data" ON users FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can insert own data" ON users FOR INSERT WITH CHECK (auth.uid() = id);
CREATE POLICY "Users can view own generations" ON music_generations FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own generations" ON music_generations FOR INSERT WITH CHECK (auth.uid() = user_id);
```

#### 1.3 Configure Supabase Storage
```bash
# In Supabase Dashboard → Storage
# Create bucket: "music-files"
# Set as public bucket
# Configure CORS for your frontend domain
```

#### 1.4 Get Hugging Face API Key
```bash
# Go to https://huggingface.co/settings/tokens
# Create new token with "Read" permissions
# Save token for later use
```

### Phase 2: Backend Deployment (Railway)

#### 2.1 Prepare Backend Code
```bash
# Create backend directory if not exists
mkdir -p backend-free
cd backend-free

# Create requirements.txt
cat > requirements.txt << EOF
flask==3.0.0
flask-cors==4.0.0
python-dotenv==1.0.0
requests==2.31.0
supabase==2.0.0
gunicorn==21.2.0
psycopg2-binary==2.9.9
librosa==0.10.1
numpy==1.24.0
EOF

# Create Procfile for Railway
cat > Procfile << EOF
web: gunicorn app:app --bind 0.0.0.0:\$PORT
EOF
```

#### 2.2 Create Flask Application
```python
# app.py
import os
import requests
import json
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from supabase import create_client, Client
from datetime import datetime
import uuid

app = Flask(__name__)
CORS(app)

# Initialize Supabase
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_ANON_KEY')
supabase: Client = create_client(supabase_url, supabase_key)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route('/generate-music', methods=['POST'])
def generate_music():
    try:
        data = request.json
        user_id = data.get('user_id')
        prompt = data.get('prompt', '')
        style = data.get('style', 'general')
        duration = data.get('duration', 30)
        
        # Create generation record
        generation_id = str(uuid.uuid4())
        
        # Insert into database
        result = supabase.table('music_generations').insert({
            'id': generation_id,
            'user_id': user_id,
            'prompt': prompt,
            'style': style,
            'duration': duration,
            'status': 'processing'
        }).execute()
        
        # Call Hugging Face API
        hf_token = os.getenv('HUGGINGFACE_API_KEY')
        hf_url = "https://api-inference.huggingface.co/models/facebook/musicgen-small"
        
        headers = {"Authorization": f"Bearer {hf_token}"}
        payload = {
            "inputs": f"{prompt} in {style} style",
            "parameters": {"duration": duration}
        }
        
        response = requests.post(hf_url, headers=headers, json=payload)
        
        if response.status_code == 200:
            # Save audio file to Supabase storage
            audio_data = response.content
            file_name = f"generated/{generation_id}.wav"
            
            storage_response = supabase.storage.from_('music-files').upload(
                file_name, audio_data, {"content-type": "audio/wav"}
            )
            
            # Update record with file URL
            file_url = supabase.storage.from_('music-files').get_public_url(file_name)
            
            supabase.table('music_generations').update({
                'file_url': file_url.get('publicURL'),
                'status': 'completed'
            }).eq('id', generation_id).execute()
            
            return jsonify({
                "id": generation_id,
                "status": "completed",
                "file_url": file_url.get('publicURL')
            })
        else:
            # Update status to failed
            supabase.table('music_generations').update({
                'status': 'failed'
            }).eq('id', generation_id).execute()
            
            return jsonify({"error": "Failed to generate music"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/generations/<user_id>', methods=['GET'])
def get_user_generations(user_id):
    try:
        result = supabase.table('music_generations').select('*').eq('user_id', user_id).order('created_at', desc=True).execute()
        return jsonify(result.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
```

#### 2.3 Deploy to Railway
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and create project
railway login
railway init
# Choose "Deploy from GitHub repo" and connect your repository

# Add environment variables
railway variables set SUPABASE_URL=https://[your-project-id].supabase.co
railway variables set SUPABASE_ANON_KEY=[your-anon-key]
railway variables set HUGGINGFACE_API_KEY=[your-hf-token]

# Deploy
railway up
```

### Phase 3: Frontend Deployment (Vercel)

#### 3.1 Update Frontend for Free Stack
```javascript
// src/services/api.js
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  async generateMusic(prompt, style = 'general', duration = 30, userId) {
    try {
      const response = await fetch(`${this.baseURL}/generate-music`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt,
          style,
          duration,
          user_id: userId
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error generating music:', error);
      throw error;
    }
  }

  async getUserGenerations(userId) {
    try {
      const response = await fetch(`${this.baseURL}/generations/${userId}`);
      return await response.json();
    } catch (error) {
      console.error('Error fetching generations:', error);
      throw error;
    }
  }
}

export default new ApiService();
```

#### 3.2 Add Supabase Authentication
```bash
# Install Supabase client
npm install @supabase/supabase-js

# Create Supabase client
# src/services/supabase.js
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.REACT_APP_SUPABASE_URL
const supabaseAnonKey = process.env.REACT_APP_SUPABASE_ANON_KEY

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
```

#### 3.3 Deploy to Vercel
```bash
# Install Vercel CLI
npm install -g vercel

# Create vercel.json config
cat > vercel.json << EOF
{
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/static-build"
    }
  ],
  "routes": [
    {
      "src": "/static/(.*)",
      "dest": "/static/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ],
  "env": {
    "REACT_APP_API_URL": "@api-url",
    "REACT_APP_SUPABASE_URL": "@supabase-url",
    "REACT_APP_SUPABASE_ANON_KEY": "@supabase-anon-key"
  }
}
EOF

# Deploy
vercel --prod

# Set environment variables in Vercel dashboard
# Go to vercel.com → your project → Settings → Environment Variables
# Add:
# REACT_APP_API_URL = https://your-railway-app.railway.app
# REACT_APP_SUPABASE_URL = https://your-project.supabase.co
# REACT_APP_SUPABASE_ANON_KEY = your-anon-key
```

## Environment Configuration

### Backend (.env for local development)
```env
SUPABASE_URL=https://[your-project-id].supabase.co
SUPABASE_ANON_KEY=[your-anon-key]
HUGGINGFACE_API_KEY=[your-hf-token]
PORT=5000
FLASK_ENV=development
```

### Frontend (.env.local)
```env
REACT_APP_API_URL=https://[your-railway-app].railway.app
REACT_APP_SUPABASE_URL=https://[your-project-id].supabase.co
REACT_APP_SUPABASE_ANON_KEY=[your-anon-key]
```

## Cost Breakdown & Limits

| Service | Free Tier | Soft Limits | Hard Limits |
|---------|-----------|-------------|-------------|
| **Vercel** | 100GB bandwidth | ~100K page views | 1TB bandwidth |
| **Railway** | $5 credit | ~100 hours runtime | Credit exhaustion |
| **Supabase** | 500MB DB, 1GB storage | ~10K queries/day | Storage/bandwidth |
| **Hugging Face** | Rate limited | ~1K inferences/day | API rate limits |
| **Expected Users** | ~50-100 | Light usage | Heavy usage |

**Monthly Cost Estimate**: $0 for first month, $5-15/month after Railway credit expires

## Alternative Free Platforms

### Option B: Render + PlanetScale + Cloudflare
```bash
# Backend on Render (750 hours/month free)
# Database on PlanetScale (5GB free)
# CDN on Cloudflare (Free tier)
# Frontend on Cloudflare Pages
```

### Option C: Heroku + FaunaDB + Netlify
```bash
# Backend on Heroku (550 dyno hours/month)
# Database on FaunaDB (100K reads/writes daily)
# Frontend on Netlify (100GB bandwidth)
```

## Testing & Validation

### 1. Local Development Setup
```bash
# Clone and setup
git clone [your-repo]
cd portal-ai-music
npm install

# Backend setup
cd backend-free
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file with your keys
cp .env.example .env
# Edit .env with your API keys

# Run backend
python app.py

# In new terminal, run frontend
cd ..
npm start
```

### 2. API Testing
```bash
# Test health endpoint
curl https://your-railway-app.railway.app/health

# Test music generation
curl -X POST https://your-railway-app.railway.app/generate-music \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "relaxing piano music",
    "style": "classical",
    "duration": 15,
    "user_id": "test-user-123"
  }'
```

### 3. Load Testing
```bash
# Install Artillery
npm install -g artillery

# Create test script
cat > load-test.yml << EOF
config:
  target: 'https://your-railway-app.railway.app'
  phases:
    - duration: 60
      arrivalRate: 5
scenarios:
  - name: 'Generate music'
    requests:
      - post:
          url: '/generate-music'
          json:
            prompt: 'upbeat dance music'
            style: 'electronic'
            duration: 10
            user_id: 'load-test-user'
EOF

# Run load test
artillery run load-test.yml
```

## Free Music Datasets & Resources

### Public Domain Music
| Source | Type | License | Size |
|--------|------|---------|------|
| [Musopen](https://musopen.org/) | Classical recordings | Public domain | ~4GB |
| [IMSLP](https://imslp.org/) | Sheet music + audio | Public domain | ~100GB |
| [Internet Archive](https://archive.org/details/audio) | Various genres | Mixed licenses | ~500GB |

### Sample Libraries
| Source | Type | API | Free Tier |
|--------|------|-----|-----------|
| [Freesound](https://freesound.org/) | Sound effects | REST API | 2K downloads/day |
| [BBC Sounds](https://sound-effects.bbcrewind.co.uk/) | Professional SFX | Download only | Unlimited |
| [Zapsplat](https://www.zapsplat.com/) | Music + SFX | API available | 10 downloads/day |

### Training Datasets
```bash
# Download common datasets for ML training
wget https://www.kaggle.com/api/v1/datasets/download/imsparsh/musicnet-dataset
wget https://github.com/mdeff/fma/releases/download/v1.0/fma_small.zip
wget http://marsyas.info/downloads/datasets/gtzan.tar.gz
```

## Monitoring & Analytics

### 1. Setup Sentry for Error Tracking
```bash
# Install Sentry
pip install sentry-sdk[flask]

# Add to app.py
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="https://your-sentry-dsn@sentry.io/project-id",
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0
)
```

### 2. Supabase Analytics
```sql
-- Create analytics views in Supabase
CREATE VIEW daily_generations AS
SELECT 
  DATE(created_at) as date,
  COUNT(*) as total_generations,
  COUNT(CASE WHEN status = 'completed' THEN 1 END) as successful_generations,
  AVG(duration) as avg_duration
FROM music_generations 
GROUP BY DATE(created_at)
ORDER BY date DESC;
```

### 3. Custom Dashboard
```javascript
// Add to your React app - components/Analytics.jsx
import { useState, useEffect } from 'react';
import { supabase } from '../services/supabase';

export default function Analytics() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    async function fetchStats() {
      const { data } = await supabase
        .from('daily_generations')
        .select('*')
        .limit(7);
      setStats(data);
    }
    fetchStats();
  }, []);

  return (
    <div className="analytics-dashboard">
      <h2>Generation Analytics</h2>
      {stats?.map(day => (
        <div key={day.date} className="stat-card">
          <h3>{day.date}</h3>
          <p>Total: {day.total_generations}</p>
          <p>Success Rate: {(day.successful_generations / day.total_generations * 100).toFixed(1)}%</p>
        </div>
      ))}
    </div>
  );
}
```

## Migration Path to Azure

### Phase 1: Data Migration
```bash
# Export Supabase data
pg_dump postgresql://[supabase-connection] > backup.sql

# Import to Azure SQL Database
sqlcmd -S [azure-server].database.windows.net -d [database] -i backup.sql
```

### Phase 2: Service Migration
```bash
# Update environment variables for Azure services
AZURE_SQL_CONNECTION_STRING=...
AZURE_STORAGE_CONNECTION_STRING=...
AZURE_COGNITIVE_SERVICES_KEY=...

# Deploy to Azure Container Apps
az containerapp create \
  --name portal-ai-music-api \
  --resource-group portal-ai-music-rg \
  --environment portal-ai-music-env \
  --image your-registry/portal-ai-music:latest
```

### Phase 3: DNS & SSL
```bash
# Point custom domain to Azure
# Update DNS records to point to Azure Front Door
# Configure SSL certificates
```

## Performance Optimization

### 1. Caching Strategy
```python
# Add Redis caching for Railway
import redis
import json

redis_client = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379'))

@app.route('/generate-music', methods=['POST'])
def generate_music():
    data = request.json
    cache_key = f"music:{hash(data['prompt'])}"
    
    # Check cache first
    cached_result = redis_client.get(cache_key)
    if cached_result:
        return json.loads(cached_result)
    
    # Generate music...
    result = generate_music_logic(data)
    
    # Cache result for 1 hour
    redis_client.setex(cache_key, 3600, json.dumps(result))
    return result
```

### 2. File Optimization
```python
# Compress audio files before storage
import librosa
import soundfile as sf

def compress_audio(audio_data, target_size_mb=2):
    # Load audio
    y, sr = librosa.load(audio_data, sr=22050)
    
    # Compress to target size
    # ... compression logic
    
    return compressed_audio
```

## Troubleshooting

### Common Issues

1. **Railway App Sleeping**: Free tier apps sleep after 30 min inactivity
   - Solution: Use UptimeRobot to ping every 5 minutes

2. **Supabase Storage Limits**: 1GB free storage fills up quickly
   - Solution: Implement auto-cleanup of old files

3. **Hugging Face Rate Limits**: Free tier has strict limits
   - Solution: Implement queue system with retries

### Debug Commands
```bash
# Check Railway logs
railway logs

# Check Vercel deployment logs
vercel logs

# Test API connectivity
curl -f https://your-app.railway.app/health || echo "API down"
```

## Success Metrics

Track these KPIs for your free deployment:

- **Response Time**: Target <3s for music generation
- **Success Rate**: Target >95% for completed generations
- **User Growth**: Monitor daily/weekly active users
- **Cost Efficiency**: Stay within free tier limits
- **Error Rate**: Keep below 5% using Sentry

## Next Steps

1. **Week 1**: Deploy basic version, test core functionality
2. **Week 2**: Add user authentication and file storage
3. **Week 3**: Implement caching and performance optimizations
4. **Week 4**: Add analytics and monitoring
5. **Month 2**: Evaluate upgrade to Azure based on usage patterns

This free deployment approach allows you to validate your product-market fit before investing in paid infrastructure!
