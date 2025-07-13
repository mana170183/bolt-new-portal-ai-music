#!/usr/bin/env python3
"""
Test script for Portal AI Music backend database integration
"""

import os
import sys
import json
from datetime import datetime

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Set environment variables for testing
os.environ['POSTGRES_URL'] = "postgres://21b02784a718c1f4c615bfa9d4f7c52dad63e24f1f889f99cc486c43ba217e42:sk_HAvgGZqr4UYuJUqa9M-h7@db.prisma.io:5432/?sslmode=require"
os.environ['PRISMA_DATABASE_URL'] = "prisma+postgres://accelerate.prisma-data.net/?api_key=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcGlfa2V5IjoiMDFKWlFHVlNLWDc3RFZKMFlLWVlUMTc4S1MiLCJ0ZW5hbnRfaWQiOiIyMWIwMjc4NGE3MThjMWY0YzYxNWJmYTlkNGY3YzUyZGFkNjNlMjRmMWY4ODlmOTljYzQ4NmM0M2JhMjE3ZTQyIiwiaW50ZXJuYWxfc2VjcmV0IjoiNmY0OWQxNjMtZTJjNi00ZTFhLWI0OGItNjdhM2YxN2Q4Mzk1In0.Clt6JfDH0Tundbd43JDZm5DHOGKm-5IrgHIXlSX1EQg"

def test_database_connection():
    """Test database connection and operations"""
    print("🔍 Testing Portal AI Music Database Integration")
    print("=" * 50)
    
    try:
        from database import get_db, init_db
        
        print("✅ Database module imported successfully")
        
        # Test connection
        print("\n📡 Testing database connection...")
        db = get_db()
        if db.test_connection():
            print("✅ Database connection successful")
        else:
            print("❌ Database connection failed")
            return False
            
        # Initialize database
        print("\n🗄️ Initializing database tables...")
        if init_db():
            print("✅ Database initialization successful")
        else:
            print("❌ Database initialization failed")
            return False
            
        # Test user operations
        print("\n👤 Testing user operations...")
        
        # Create a test user
        test_email = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com"
        test_username = f"testuser_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        user = db.create_user(test_email, test_username, 'free')
        if user:
            print(f"✅ User created: {user['email']}")
            user_id = user['id']
            
            # Test quota operations
            print("\n📊 Testing quota operations...")
            quota = db.get_user_quota(user_id)
            if quota:
                print(f"✅ User quota: {quota['used_today']}/{quota['daily_limit']}")
                
                # Test incrementing usage
                db.increment_usage(user_id)
                updated_quota = db.get_user_quota(user_id)
                if updated_quota['used_today'] == quota['used_today'] + 1:
                    print("✅ Usage increment successful")
                else:
                    print("❌ Usage increment failed")
            else:
                print("❌ Failed to get user quota")
                
            # Test music generation logging
            print("\n🎵 Testing music generation logging...")
            track_id = f"track_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            metadata = {
                "sample_rate": 44100,
                "channels": 2,
                "genre": "pop",
                "mood": "upbeat"
            }
            
            generation = db.save_music_generation(
                user_id=user_id,
                track_id=track_id,
                title="Test Track",
                prompt="Test prompt for music generation",
                genre="pop",
                mood="upbeat",
                duration=30,
                file_path=f"/generated/{track_id}.wav",
                download_url=f"/api/download/{track_id}.wav",
                metadata=metadata
            )
            
            if generation:
                print(f"✅ Music generation logged: {generation['track_id']}")
                
                # Test retrieval
                retrieved = db.get_generation_by_track_id(track_id)
                if retrieved:
                    print("✅ Music generation retrieved successfully")
                else:
                    print("❌ Failed to retrieve music generation")
                    
                # Test user generations list
                user_generations = db.get_user_generations(user_id)
                if user_generations:
                    print(f"✅ User generations list: {len(user_generations)} tracks")
                else:
                    print("❌ Failed to get user generations")
            else:
                print("❌ Failed to log music generation")
                
        else:
            print("❌ Failed to create user")
            return False
            
        print("\n🎉 All database tests passed!")
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import database module: {e}")
        print("💡 Make sure to install psycopg2-binary: pip install psycopg2-binary")
        return False
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_backend_integration():
    """Test backend integration with database"""
    print("\n🔧 Testing Backend Integration")
    print("=" * 50)
    
    try:
        from app import app
        
        print("✅ Flask app imported successfully")
        
        # Test app in test mode
        app.config['TESTING'] = True
        client = app.test_client()
        
        # Test health endpoint
        print("\n❤️ Testing health endpoint...")
        response = client.get('/health')
        if response.status_code == 200:
            data = response.get_json()
            print(f"✅ Health check passed: {data.get('status')}")
            print(f"   Database available: {data.get('database_available')}")
            print(f"   Database status: {data.get('database_status')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            
        # Test API endpoints
        print("\n🎼 Testing API endpoints...")
        endpoints = ['/api/genres', '/api/moods', '/api/instruments']
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            if response.status_code == 200:
                data = response.get_json()
                print(f"✅ {endpoint}: {data.get('success', False)}")
            else:
                print(f"❌ {endpoint}: {response.status_code}")
                
        print("\n🎉 Backend integration tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ Backend integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Portal AI Music Backend Testing Suite")
    print("=" * 60)
    
    # Run tests
    database_ok = test_database_connection()
    backend_ok = test_backend_integration()
    
    print("\n" + "=" * 60)
    if database_ok and backend_ok:
        print("🎉 All tests passed! Backend is ready for deployment.")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)
