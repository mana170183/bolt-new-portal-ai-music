#!/usr/bin/env python3
"""
Comprehensive test script for all AI Music Platform endpoints
Tests both local Azure Functions and deployed Static Web App
"""

import requests
import json
import time
import os
from datetime import datetime
import base64

# Configuration
LOCAL_BASE_URL = "http://localhost:7071/api"
DEPLOYED_BASE_URL = "https://your-static-web-app.azurestaticapps.net/api"

# Use local for testing, deployed for production validation
BASE_URL = LOCAL_BASE_URL

class EndpointTester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, endpoint, method, status_code, success, details=""):
        result = {
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {method} {endpoint} - {status_code} - {details}")
        
    def test_health(self):
        """Test health endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            success = response.status_code == 200
            details = response.json() if success else response.text
            self.log_test("/health", "GET", response.status_code, success, str(details))
            return success
        except Exception as e:
            self.log_test("/health", "GET", 0, False, str(e))
            return False
    
    def test_status(self):
        """Test status endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/status")
            success = response.status_code == 200
            details = response.json() if success else response.text
            self.log_test("/status", "GET", response.status_code, success, str(details))
            return success
        except Exception as e:
            self.log_test("/status", "GET", 0, False, str(e))
            return False
    
    def test_root(self):
        """Test root endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/root")
            success = response.status_code == 200
            details = response.json() if success else response.text
            self.log_test("/root", "GET", response.status_code, success, str(details))
            return success
        except Exception as e:
            self.log_test("/root", "GET", 0, False, str(e))
            return False
    
    def test_genres(self):
        """Test genres endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/genres")
            success = response.status_code == 200
            details = response.json() if success else response.text
            self.log_test("/genres", "GET", response.status_code, success, str(details))
            return success
        except Exception as e:
            self.log_test("/genres", "GET", 0, False, str(e))
            return False
    
    def test_moods(self):
        """Test moods endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/moods")
            success = response.status_code == 200
            details = response.json() if success else response.text
            self.log_test("/moods", "GET", response.status_code, success, str(details))
            return success
        except Exception as e:
            self.log_test("/moods", "GET", 0, False, str(e))
            return False
    
    def test_auth_token(self):
        """Test auth token endpoint"""
        try:
            test_data = {
                "username": "test_user",
                "password": "test_password"
            }
            response = self.session.post(f"{self.base_url}/auth-token", json=test_data)
            success = response.status_code in [200, 401]  # 401 is expected for demo
            details = response.json() if response.status_code == 200 else "Demo auth (expected)"
            self.log_test("/auth-token", "POST", response.status_code, success, str(details))
            return success
        except Exception as e:
            self.log_test("/auth-token", "POST", 0, False, str(e))
            return False
    
    def test_user_quota(self):
        """Test user quota endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/user-quota?user_id=demo_user")
            success = response.status_code == 200
            details = response.json() if success else response.text
            self.log_test("/user-quota", "GET", response.status_code, success, str(details))
            return success
        except Exception as e:
            self.log_test("/user-quota", "GET", 0, False, str(e))
            return False
    
    def test_music_apis(self):
        """Test music APIs endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/music-apis")
            success = response.status_code == 200
            details = response.json() if success else response.text
            self.log_test("/music-apis", "GET", response.status_code, success, str(details))
            return success
        except Exception as e:
            self.log_test("/music-apis", "GET", 0, False, str(e))
            return False
    
    def test_music_library(self):
        """Test music library endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/music-library?user_id=demo_user")
            success = response.status_code == 200
            details = response.json() if success else response.text
            self.log_test("/music-library", "GET", response.status_code, success, str(details))
            return success
        except Exception as e:
            self.log_test("/music-library", "GET", 0, False, str(e))
            return False
    
    def test_music_catalog(self):
        """Test music catalog endpoint"""
        try:
            # Test GET
            response = self.session.get(f"{self.base_url}/music-catalog")
            success = response.status_code == 200
            details = response.json() if success else response.text
            self.log_test("/music-catalog", "GET", response.status_code, success, str(details))
            
            # Test search
            response = self.session.get(f"{self.base_url}/music-catalog?query=rock")
            success = response.status_code == 200
            details = response.json() if success else response.text
            self.log_test("/music-catalog?query=rock", "GET", response.status_code, success, str(details))
            
            return success
        except Exception as e:
            self.log_test("/music-catalog", "GET", 0, False, str(e))
            return False
    
    def test_user_profile(self):
        """Test user profile endpoint"""
        try:
            # Test GET profile
            response = self.session.get(f"{self.base_url}/user-profile?user_id=demo_user")
            success = response.status_code == 200
            details = response.json() if success else response.text
            self.log_test("/user-profile", "GET", response.status_code, success, str(details))
            
            # Test POST (create/update profile)
            test_data = {
                "user_id": "test_user_profile",
                "username": "test_user",
                "email": "test@example.com",
                "preferences": {
                    "favorite_genres": ["rock", "jazz"],
                    "default_mood": "energetic"
                }
            }
            response = self.session.post(f"{self.base_url}/user-profile", json=test_data)
            success = response.status_code in [200, 201]
            details = response.json() if success else response.text
            self.log_test("/user-profile", "POST", response.status_code, success, str(details))
            
            return success
        except Exception as e:
            self.log_test("/user-profile", "GET/POST", 0, False, str(e))
            return False
    
    def test_playlists(self):
        """Test playlists endpoint"""
        try:
            # Test GET playlists
            response = self.session.get(f"{self.base_url}/playlists?user_id=demo_user")
            success = response.status_code == 200
            details = response.json() if success else response.text
            self.log_test("/playlists", "GET", response.status_code, success, str(details))
            
            # Test POST (create playlist)
            test_data = {
                "user_id": "demo_user",
                "name": "Test Playlist",
                "description": "A test playlist for validation",
                "is_public": False
            }
            response = self.session.post(f"{self.base_url}/playlists", json=test_data)
            success = response.status_code in [200, 201]
            details = response.json() if success else response.text
            self.log_test("/playlists", "POST", response.status_code, success, str(details))
            
            return success
        except Exception as e:
            self.log_test("/playlists", "GET/POST", 0, False, str(e))
            return False
    
    def test_generate_music(self):
        """Test music generation endpoint"""
        try:
            test_data = {
                "prompt": "Create a happy upbeat pop song about sunshine",
                "genre": "pop",
                "mood": "happy",
                "duration": 30,
                "user_id": "demo_user"
            }
            response = self.session.post(f"{self.base_url}/generate-music", json=test_data)
            success = response.status_code == 200
            details = response.json() if success else response.text
            self.log_test("/generate-music", "POST", response.status_code, success, str(details))
            return success
        except Exception as e:
            self.log_test("/generate-music", "POST", 0, False, str(e))
            return False
    
    def test_advanced_generate(self):
        """Test advanced music generation endpoint"""
        try:
            test_data = {
                "prompt": "Create an advanced AI-generated song",
                "genre": "electronic",
                "mood": "energetic",
                "tempo": 120,
                "key": "C",
                "instruments": ["synthesizer", "drums"],
                "structure": ["intro", "verse", "chorus", "verse", "chorus", "outro"],
                "user_id": "demo_user"
            }
            response = self.session.post(f"{self.base_url}/advanced-generate", json=test_data)
            success = response.status_code == 200
            details = response.json() if success else response.text
            self.log_test("/advanced-generate", "POST", response.status_code, success, str(details))
            return success
        except Exception as e:
            self.log_test("/advanced-generate", "POST", 0, False, str(e))
            return False
    
    def test_upload(self):
        """Test upload endpoint"""
        try:
            # Test with a small fake audio file (base64 encoded)
            fake_audio_data = base64.b64encode(b"fake audio data for testing").decode()
            test_data = {
                "user_id": "demo_user",
                "file_name": "test_upload.mp3",
                "file_data": fake_audio_data,
                "content_type": "audio/mpeg"
            }
            response = self.session.post(f"{self.base_url}/upload", json=test_data)
            success = response.status_code in [200, 201]
            details = response.json() if success else response.text
            self.log_test("/upload", "POST", response.status_code, success, str(details))
            return success
        except Exception as e:
            self.log_test("/upload", "POST", 0, False, str(e))
            return False
    
    def run_all_tests(self):
        """Run all endpoint tests"""
        print("🎵 Starting AI Music Platform Endpoint Tests")
        print(f"📍 Testing against: {self.base_url}")
        print("=" * 60)
        
        test_methods = [
            self.test_health,
            self.test_status,
            self.test_root,
            self.test_genres,
            self.test_moods,
            self.test_auth_token,
            self.test_user_quota,
            self.test_music_apis,
            self.test_music_library,
            self.test_music_catalog,
            self.test_user_profile,
            self.test_playlists,
            self.test_generate_music,
            self.test_advanced_generate,
            self.test_upload
        ]
        
        passed = 0
        failed = 0
        
        for test_method in test_methods:
            try:
                if test_method():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"❌ FAIL {test_method.__name__} - Exception: {str(e)}")
                failed += 1
            
            time.sleep(0.5)  # Small delay between tests
        
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {passed} passed, {failed} failed")
        print(f"✅ Success Rate: {(passed/(passed+failed)*100):.1f}%")
        
        # Save detailed results
        with open('test_results.json', 'w') as f:
            json.dump({
                "summary": {
                    "passed": passed,
                    "failed": failed,
                    "success_rate": passed/(passed+failed)*100,
                    "base_url": self.base_url,
                    "timestamp": datetime.now().isoformat()
                },
                "detailed_results": self.test_results
            }, f, indent=2)
        
        print(f"📄 Detailed results saved to test_results.json")
        
        return passed, failed

def main():
    print("🎵 AI Music Platform - Comprehensive Endpoint Testing")
    print("Choose testing environment:")
    print("1. Local Azure Functions (http://localhost:7071)")
    print("2. Deployed Static Web App")
    print("3. Both")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        tester = EndpointTester(LOCAL_BASE_URL)
        tester.run_all_tests()
    elif choice == "2":
        deployed_url = input("Enter your Static Web App URL: ").strip()
        if not deployed_url.startswith('http'):
            deployed_url = f"https://{deployed_url}"
        if not deployed_url.endswith('/api'):
            deployed_url = f"{deployed_url}/api"
        tester = EndpointTester(deployed_url)
        tester.run_all_tests()
    elif choice == "3":
        print("\n🧪 Testing Local Environment:")
        local_tester = EndpointTester(LOCAL_BASE_URL)
        local_passed, local_failed = local_tester.run_all_tests()
        
        deployed_url = input("\nEnter your Static Web App URL: ").strip()
        if not deployed_url.startswith('http'):
            deployed_url = f"https://{deployed_url}"
        if not deployed_url.endswith('/api'):
            deployed_url = f"{deployed_url}/api"
        
        print("\n🌐 Testing Deployed Environment:")
        deployed_tester = EndpointTester(deployed_url)
        deployed_passed, deployed_failed = deployed_tester.run_all_tests()
        
        print(f"\n📊 Overall Results:")
        print(f"🏠 Local: {local_passed} passed, {local_failed} failed")
        print(f"🌐 Deployed: {deployed_passed} passed, {deployed_failed} failed")
    else:
        print("Invalid choice. Exiting.")

if __name__ == "__main__":
    main()
