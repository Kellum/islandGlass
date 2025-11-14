#!/bin/bash
# Test Authentication Flow
# Usage: ./test_auth.sh your-email@example.com yourpassword

EMAIL=$1
PASSWORD=$2

if [ -z "$EMAIL" ] || [ -z "$PASSWORD" ]; then
    echo "Usage: ./test_auth.sh email@example.com password"
    exit 1
fi

echo "=========================================="
echo "Testing Island Glass CRM Authentication"
echo "=========================================="
echo ""

# Test 1: Login
echo "1. Testing LOGIN endpoint..."
echo "   POST /api/v1/auth/login"
echo ""

LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")

echo "Response:"
echo "$LOGIN_RESPONSE" | python3 -m json.tool

# Extract access token
ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))" 2>/dev/null)

if [ -z "$ACCESS_TOKEN" ]; then
    echo ""
    echo "❌ LOGIN FAILED - No access token received"
    echo "Check your email/password and make sure the user exists in Supabase"
    exit 1
fi

echo ""
echo "✅ LOGIN SUCCESSFUL!"
echo "   Access token: ${ACCESS_TOKEN:0:20}..."
echo ""

# Test 2: Get current user info
echo "=========================================="
echo "2. Testing /ME endpoint (with token)..."
echo "   GET /api/v1/auth/me"
echo ""

ME_RESPONSE=$(curl -s -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "Response:"
echo "$ME_RESPONSE" | python3 -m json.tool

# Check if user info was returned
USER_ID=$(echo "$ME_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)

if [ -z "$USER_ID" ]; then
    echo ""
    echo "⚠️  /ME endpoint failed - Check server logs"
else
    echo ""
    echo "✅ /ME endpoint works!"
    echo "   User ID: $USER_ID"
fi

echo ""

# Test 3: Refresh token
echo "=========================================="
echo "3. Testing REFRESH endpoint..."
echo "   POST /api/v1/auth/refresh"
echo ""

REFRESH_TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('refresh_token', ''))" 2>/dev/null)

if [ -n "$REFRESH_TOKEN" ]; then
    REFRESH_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/refresh \
      -H "Content-Type: application/json" \
      -d "{\"refresh_token\":\"$REFRESH_TOKEN\"}")

    echo "Response:"
    echo "$REFRESH_RESPONSE" | python3 -m json.tool

    NEW_TOKEN=$(echo "$REFRESH_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))" 2>/dev/null)

    if [ -n "$NEW_TOKEN" ]; then
        echo ""
        echo "✅ Token refresh works!"
    else
        echo ""
        echo "⚠️  Token refresh failed"
    fi
else
    echo "⚠️  No refresh token from login"
fi

echo ""
echo "=========================================="
echo "Authentication Tests Complete!"
echo "=========================================="
