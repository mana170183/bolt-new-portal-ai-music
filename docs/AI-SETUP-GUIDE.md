# AI Music Generation Setup Guide

## Overview

Your Portal AI Music platform currently uses **mock endpoints** that return demo audio. To enable real AI music generation, you need to integrate with actual AI music services.

## Quick Setup Options

### 🚀 Option 1: Mubert API (Recommended for Production)

1. **Sign up for Mubert API**:
   - Visit: https://mubert.com/api
   - Create account and get API credentials
   - Cost: ~$0.10-0.50 per track

2. **Configure Environment**:
   ```bash
   # Add to .env.local
   AI_MUSIC_PROVIDER=mubert
   MUBERT_API_KEY=your_mubert_api_key_here
   MUBERT_PAT_TOKEN=your_mubert_pat_token_here
   ```

3. **Test Integration**:
   ```bash
   npm run dev
   # Generate music - will now use real AI!
   ```

### 🎵 Option 2: Suno AI (High Quality)

1. **Get Suno API Access**:
   - Visit: https://suno.ai/api
   - Request API access (may require approval)
   - Cost: ~$1-3 per track

2. **Configure**:
   ```bash
   # Add to .env.local
   AI_MUSIC_PROVIDER=suno
   SUNO_API_KEY=your_suno_api_key_here
   ```

### 🤖 Option 3: Self-Hosted (Free but Complex)

#### Using Meta's MusicGen

1. **Setup Requirements**:
   - GPU with 8GB+ VRAM
   - Python 3.8+
   - CUDA support

2. **Install MusicGen**:
   ```bash
   # Create Python environment
   python -m venv musicgen_env
   source musicgen_env/bin/activate  # On Windows: musicgen_env\\Scripts\\activate
   
   # Install dependencies
   pip install torch torchvision torchaudio
   pip install transformers
   pip install audiocraft
   ```

3. **Create API Server**:
   ```python
   # musicgen_server.py
   from flask import Flask, request, jsonify, send_file
   from audiocraft.models import MusicGen
   import torch
   import torchaudio
   import tempfile
   import os
   
   app = Flask(__name__)
   
   # Load model (this will download ~3GB on first run)
   model = MusicGen.get_pretrained('facebook/musicgen-medium')
   model.set_generation_params(duration=30)
   
   @app.route('/generate', methods=['POST'])
   def generate_music():
       data = request.json
       prompt = data.get('prompt', 'upbeat electronic music')
       duration = data.get('duration', 30)
       
       model.set_generation_params(duration=duration)
       
       # Generate music
       wav = model.generate([prompt], progress=True)
       
       # Save to temporary file
       temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
       torchaudio.save(temp_file.name, wav[0].cpu(), model.sample_rate)
       
       return send_file(temp_file.name, as_attachment=True, download_name='generated.wav')
   
   if __name__ == '__main__':
       app.run(host='0.0.0.0', port=8000)
   ```

4. **Configure Portal AI**:
   ```bash
   # Add to .env.local
   AI_MUSIC_PROVIDER=custom
   CUSTOM_MODEL_URL=http://localhost:8000/generate
   ```

## Current Implementation Status

✅ **Infrastructure Ready**:
- Service layer (`aiMusicService.ts`) supports multiple providers
- Async generation with polling endpoints
- Error handling and status updates
- Frontend components ready for real audio

❌ **Missing**:
- Real AI provider credentials
- Production deployment setup
- Audio storage/CDN for generated tracks

## Testing the Setup

1. **Mock Mode (Current)**:
   ```bash
   AI_MUSIC_PROVIDER=mock npm run dev
   # Returns demo sine wave audio
   ```

2. **Real AI Mode**:
   ```bash
   AI_MUSIC_PROVIDER=mubert npm run dev
   # Returns actual AI-generated music!
   ```

## Production Considerations

### Audio Storage
- Generated tracks need permanent storage
- Consider AWS S3, Google Cloud Storage, or Vercel Blob
- Implement cleanup for old tracks

### Rate Limiting
- AI providers have rate limits
- Implement user quotas and billing
- Consider caching popular prompts

### Performance
- AI generation takes 30-90 seconds
- Implement job queues for high traffic
- Add progress indicators for users

### Costs
- Mubert: $0.10-0.50 per track
- Suno: $1-3 per track
- Self-hosted: GPU costs (~$0.50/hour)

## Quick Start (5 minutes)

1. **Get Mubert API key** (free tier available)
2. **Add to environment**:
   ```bash
   echo "AI_MUSIC_PROVIDER=mubert" >> .env.local
   echo "MUBERT_API_KEY=your_key" >> .env.local
   echo "MUBERT_PAT_TOKEN=your_token" >> .env.local
   ```
3. **Restart dev server**:
   ```bash
   npm run dev
   ```
4. **Generate real music!** 🎵

## Troubleshooting

### "No audio generated"
- Check API credentials in .env.local
- Verify provider has sufficient quota
- Check console for error messages

### "Audio format not supported"
- Ensure AI provider returns valid audio URLs
- Check CORS headers on audio endpoints
- Verify browser audio codec support

### Slow generation
- Normal for AI providers (30-90 seconds)
- Consider using shorter duration for testing
- Implement proper loading states
