"""
Azure OpenAI Integration for AI Music Generation
Handles fine-tuning and intelligent music generation using metadata
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import traceback

# Azure OpenAI imports
try:
    from openai import AzureOpenAI
    import openai
    AZURE_OPENAI_AVAILABLE = True
    print("🔗 Azure OpenAI SDK loaded successfully")
except ImportError as e:
    AZURE_OPENAI_AVAILABLE = False
    print(f"⚠️ Azure OpenAI SDK not available: {e}")

class AzureOpenAIManager:
    def __init__(self):
        self.client = None
        self.is_initialized = False
        
        # Azure OpenAI Configuration
        self.api_key = os.getenv('AZURE_OPENAI_API_KEY')
        self.endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
        self.api_version = os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-15-preview')
        self.deployment_name = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME', 'gpt-4')
        
        # Music-specific fine-tuned models
        self.music_model_deployment = os.getenv('AZURE_OPENAI_MUSIC_MODEL', 'music-gpt-4')
        
    def initialize(self) -> bool:
        """Initialize Azure OpenAI client"""
        if not AZURE_OPENAI_AVAILABLE:
            print("❌ Azure OpenAI SDK not available")
            return False
            
        if not self.api_key or not self.endpoint:
            print("❌ Azure OpenAI credentials not configured")
            return False
            
        try:
            self.client = AzureOpenAI(
                api_key=self.api_key,
                api_version=self.api_version,
                azure_endpoint=self.endpoint
            )
            
            # Test the connection
            self.client.models.list()
            
            self.is_initialized = True
            print("✅ Azure OpenAI client initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ Azure OpenAI initialization failed: {e}")
            self.is_initialized = False
            return False
    
    def ensure_initialized(self) -> bool:
        """Ensure OpenAI client is initialized"""
        if not self.is_initialized:
            return self.initialize()
        return True
    
    def generate_music_parameters(self, prompt: str, genre_data: Dict, mood_data: Dict, user_preferences: Dict = None) -> Dict:
        """Generate intelligent music parameters using AI"""
        if not self.ensure_initialized():
            return self._fallback_parameters(genre_data, mood_data)
            
        try:
            # Create enhanced prompt with metadata
            enhanced_prompt = self._create_enhanced_prompt(prompt, genre_data, mood_data, user_preferences)
            
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert AI music producer and composer. Generate detailed music production parameters based on user prompts, genre characteristics, and mood requirements. Return a JSON object with specific audio generation parameters."""
                    },
                    {
                        "role": "user",
                        "content": enhanced_prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            # Parse the AI response
            ai_content = response.choices[0].message.content
            
            # Extract JSON from response
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', ai_content, re.DOTALL)
            if json_match:
                ai_params = json.loads(json_match.group(1))
            else:
                # Try to parse the entire response as JSON
                ai_params = json.loads(ai_content)
            
            # Merge with base parameters
            base_params = self._get_base_parameters(genre_data, mood_data)
            enhanced_params = self._merge_parameters(base_params, ai_params)
            
            print(f"✅ AI-generated music parameters: {enhanced_params}")
            return enhanced_params
            
        except Exception as e:
            print(f"❌ AI parameter generation failed: {e}")
            traceback.print_exc()
            return self._fallback_parameters(genre_data, mood_data)
    
    def _create_enhanced_prompt(self, user_prompt: str, genre_data: Dict, mood_data: Dict, user_preferences: Dict = None) -> str:
        """Create enhanced prompt with metadata"""
        
        prompt_parts = [
            f"Generate music production parameters for the following request:",
            f"User Prompt: \"{user_prompt}\"",
            f"",
            f"Genre: {genre_data.get('name', 'Unknown')} ({genre_data.get('genre_code', '')})",
            f"Genre Description: {genre_data.get('description', '')}",
            f"BPM Range: {genre_data.get('bpm_range_min', 120)}-{genre_data.get('bpm_range_max', 140)}",
            f"Typical Instruments: {', '.join(genre_data.get('instruments', []))}",
            f"",
            f"Mood: {mood_data.get('name', 'Unknown')} ({mood_data.get('mood_code', '')})",
            f"Mood Description: {mood_data.get('description', '')}",
            f"Energy Level: {mood_data.get('energy_level', 5)}/10",
            f"Valence (Positivity): {mood_data.get('valence', 5)}/10",
            f"Arousal (Intensity): {mood_data.get('arousal', 5)}/10",
        ]
        
        if user_preferences:
            prompt_parts.extend([
                f"",
                f"User Preferences:",
                f"Preferred Duration: {user_preferences.get('preferred_duration', 30)} seconds",
                f"Favorite Genres: {', '.join(user_preferences.get('favorite_genres', []))}",
                f"Preferred Instruments: {', '.join(user_preferences.get('preferred_instruments', []))}"
            ])
        
        prompt_parts.extend([
            f"",
            f"Please generate a JSON object with these parameters:",
            f"- tempo_bpm: integer (within genre range)",
            f"- key_signature: string (appropriate for genre)",
            f"- chord_progression: array of chords",
            f"- structure: array of song sections with durations",
            f"- instruments: array of instruments to use",
            f"- audio_effects: object with reverb, compression, eq settings",
            f"- dynamics: object with volume automation",
            f"- style_notes: string with specific production guidance",
            f"",
            f"Format as valid JSON wrapped in ```json ``` blocks."
        ])
        
        return "\n".join(prompt_parts)
    
    def _get_base_parameters(self, genre_data: Dict, mood_data: Dict) -> Dict:
        """Get base parameters from genre and mood data"""
        
        # Extract audio parameters from mood
        audio_params = mood_data.get('audio_parameters', {})
        
        # Calculate BPM based on energy level and genre range
        bpm_min = genre_data.get('bpm_range_min', 120)
        bpm_max = genre_data.get('bpm_range_max', 140)
        energy_level = mood_data.get('energy_level', 5)
        
        # Scale BPM based on energy (1-10 scale)
        bpm_range = bpm_max - bpm_min
        energy_factor = (energy_level - 1) / 9  # Normalize to 0-1
        calculated_bpm = int(bpm_min + (bpm_range * energy_factor))
        
        return {
            'tempo_bpm': calculated_bpm,
            'key_signature': genre_data.get('key_signatures', ['C'])[0] if genre_data.get('key_signatures') else 'C',
            'chord_progression': genre_data.get('chord_progressions', [['C', 'Am', 'F', 'G']])[0] if genre_data.get('chord_progressions') else ['C', 'Am', 'F', 'G'],
            'instruments': genre_data.get('instruments', ['piano', 'guitar', 'drums']),
            'audio_effects': {
                'reverb': audio_params.get('reverb', 'medium'),
                'brightness': audio_params.get('brightness', 1.0),
                'volume': audio_params.get('volume', 0.7),
                'eq': audio_params.get('eq', {'low': 1.0, 'mid': 1.0, 'high': 1.0})
            },
            'adsr': {
                'attack': audio_params.get('attack', 0.1),
                'decay': audio_params.get('decay', 0.3),
                'sustain': audio_params.get('sustain', 0.7),
                'release': audio_params.get('release', 0.4)
            },
            'production_style': genre_data.get('production_style', {})
        }
    
    def _merge_parameters(self, base_params: Dict, ai_params: Dict) -> Dict:
        """Merge AI-generated parameters with base parameters"""
        merged = base_params.copy()
        
        # Update with AI parameters, validating ranges
        if 'tempo_bpm' in ai_params:
            # Validate BPM is reasonable
            bpm = ai_params['tempo_bpm']
            if isinstance(bpm, int) and 60 <= bpm <= 200:
                merged['tempo_bpm'] = bpm
        
        if 'key_signature' in ai_params:
            merged['key_signature'] = ai_params['key_signature']
        
        if 'chord_progression' in ai_params and isinstance(ai_params['chord_progression'], list):
            merged['chord_progression'] = ai_params['chord_progression']
        
        if 'instruments' in ai_params and isinstance(ai_params['instruments'], list):
            merged['instruments'] = ai_params['instruments']
        
        if 'structure' in ai_params:
            merged['structure'] = ai_params['structure']
        
        if 'audio_effects' in ai_params:
            merged['audio_effects'].update(ai_params['audio_effects'])
        
        if 'style_notes' in ai_params:
            merged['style_notes'] = ai_params['style_notes']
        
        return merged
    
    def _fallback_parameters(self, genre_data: Dict, mood_data: Dict) -> Dict:
        """Fallback parameters when AI is not available"""
        return self._get_base_parameters(genre_data, mood_data)
    
    def enhance_lyrics(self, prompt: str, genre: str, mood: str) -> str:
        """Generate or enhance lyrics using AI"""
        if not self.ensure_initialized():
            return prompt or f"A {mood} {genre} song"
            
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a professional lyricist. Create {mood} lyrics in the {genre} style. Keep it appropriate for all audiences and focus on the emotional theme."
                    },
                    {
                        "role": "user",
                        "content": f"Create lyrics based on this prompt: {prompt}. Make it {mood} and suitable for {genre} music. Keep it concise (2-3 verses or phrases)."
                    }
                ],
                temperature=0.8,
                max_tokens=300
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"❌ Lyrics enhancement failed: {e}")
            return prompt or f"A {mood} {genre} song"
    
    def analyze_user_preferences(self, generation_history: List[Dict]) -> Dict:
        """Analyze user's generation history to understand preferences"""
        if not generation_history:
            return {}
            
        # Simple analysis - could be enhanced with AI
        genre_counts = {}
        mood_counts = {}
        duration_preferences = []
        
        for entry in generation_history:
            genre = entry.get('genre')
            mood = entry.get('mood')
            duration = entry.get('duration')
            
            if genre:
                genre_counts[genre] = genre_counts.get(genre, 0) + 1
            if mood:
                mood_counts[mood] = mood_counts.get(mood, 0) + 1
            if duration:
                duration_preferences.append(duration)
        
        # Find preferences
        favorite_genre = max(genre_counts, key=genre_counts.get) if genre_counts else None
        favorite_mood = max(mood_counts, key=mood_counts.get) if mood_counts else None
        avg_duration = sum(duration_preferences) / len(duration_preferences) if duration_preferences else 30
        
        return {
            'favorite_genre': favorite_genre,
            'favorite_mood': favorite_mood,
            'preferred_duration': int(avg_duration),
            'genre_distribution': genre_counts,
            'mood_distribution': mood_counts
        }

# Global Azure OpenAI manager instance
azure_ai = AzureOpenAIManager()

def get_azure_ai() -> AzureOpenAIManager:
    """Get Azure OpenAI manager instance"""
    return azure_ai

def init_azure_openai() -> bool:
    """Initialize Azure OpenAI"""
    return azure_ai.initialize()
