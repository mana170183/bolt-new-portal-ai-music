#!/bin/bash

BACKEND_URL="https://portal-music-backend-bulletproof.ambitiousmeadow-4c2dba6f.uksouth.azurecontainerapps.io"
FRONTEND_URL="https://frontend-containerapp-dev.ambitiousmeadow-4c2dba6f.uksouth.azurecontainerapps.io"

echo "=== Testing Portal AI Music Backend Endpoints ==="
echo "Backend URL: $BACKEND_URL"
echo "Frontend URL: $FRONTEND_URL"
echo ""

# Test health endpoint
echo "1. Testing /health endpoint:"
curl -s -w "Status: %{http_code}\n" "$BACKEND_URL/health"
echo ""

# Test CORS preflight
echo "2. Testing CORS preflight:"
curl -s -H "Origin: $FRONTEND_URL" -H "Access-Control-Request-Method: GET" -X OPTIONS "$BACKEND_URL/api/genres" -D - | grep -E "(HTTP|access-control)"
echo ""

# Test genres
echo "3. Testing /api/genres:"
curl -s -w "Status: %{http_code}\n" "$BACKEND_URL/api/genres" | jq -r '.genres[0:3]' 2>/dev/null || echo "Failed to parse JSON"
echo ""

# Test moods
echo "4. Testing /api/moods:"
curl -s -w "Status: %{http_code}\n" "$BACKEND_URL/api/moods" | jq -r '.moods[0:3]' 2>/dev/null || echo "Failed to parse JSON"
echo ""

# Test instruments
echo "5. Testing /api/instruments:"
curl -s -w "Status: %{http_code}\n" "$BACKEND_URL/api/instruments" | jq -r '.instruments[0:3]' 2>/dev/null || echo "Failed to parse JSON"
echo ""

# Test templates
echo "6. Testing /api/templates:"
curl -s -w "Status: %{http_code}\n" "$BACKEND_URL/api/templates" | jq -r '.templates[0:3]' 2>/dev/null || echo "Failed to parse JSON"
echo ""

# Test presets
echo "7. Testing /api/presets:"
curl -s -w "Status: %{http_code}\n" "$BACKEND_URL/api/presets" | head -200
echo ""

# Test quota
echo "8. Testing /api/quota:"
curl -s -w "Status: %{http_code}\n" "$BACKEND_URL/api/quota"
echo ""

echo ""
echo "=== Frontend Test ==="
echo "Testing frontend response:"
curl -s -w "Status: %{http_code}\n" "$FRONTEND_URL" | head -5
echo ""

echo "=== Test Complete ==="
