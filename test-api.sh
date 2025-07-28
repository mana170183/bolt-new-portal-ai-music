#!/bin/bash

echo "🧪 Testing AI Music Platform API Endpoints..."
echo "=============================================="

BASE_URL="http://localhost:7071/api"

echo ""
echo "1. Testing Health Endpoint..."
curl -s -X GET "$BASE_URL/health" | jq '.'

echo ""
echo "2. Testing Genres Endpoint..."
curl -s -X GET "$BASE_URL/genres" | jq '.'

echo ""
echo "3. Testing Moods Endpoint..."
curl -s -X GET "$BASE_URL/moods" | jq '.'

echo ""
echo "4. Testing Music Generation..."
curl -s -X POST "$BASE_URL/generate-music" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A happy pop song with upbeat tempo",
    "genre": "pop",
    "mood": "happy",
    "duration": 30
  }' | jq '.'

echo ""
echo "5. Testing Get Tracks..."
curl -s -X GET "$BASE_URL/tracks" | jq '.'

echo ""
echo "✅ All API tests completed!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 API Server: http://localhost:7071"
