#!/bin/bash

# Client API Edge Case Tests
# Tests validation, error handling, and edge cases

BASE_URL="http://localhost:8000/api/v1"
EMAIL="ry@islandglassandmirror.com"
PASSWORD="Asdfghj123!@"

echo "=========================================="
echo "Client API Edge Case Tests"
echo "=========================================="
echo ""

# Login
echo "Logging in..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")

ACCESS_TOKEN=$(echo $LOGIN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ -z "$ACCESS_TOKEN" ]; then
  echo "❌ Login failed"
  exit 1
fi
echo "✅ Login successful"
echo ""

# Test 1: Invalid client_type
echo "Test 1: Invalid client_type (should return 422)"
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/clients/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "client_type": "invalid",
    "client_name": "Test",
    "primary_contact": {"first_name": "John", "last_name": "Doe"}
  }')
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | head -1)
if [ "$HTTP_CODE" = "422" ]; then
  echo "✅ PASS - Validation rejected invalid client_type"
else
  echo "❌ FAIL - Expected 422, got $HTTP_CODE"
fi
echo ""

# Test 2: Invalid email format
echo "Test 2: Invalid email format (should return 422)"
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/clients/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "client_type": "residential",
    "client_name": "Test",
    "primary_contact": {"first_name": "John", "last_name": "Doe", "email": "not-an-email"}
  }')
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
if [ "$HTTP_CODE" = "422" ]; then
  echo "✅ PASS - Validation rejected invalid email"
else
  echo "❌ FAIL - Expected 422, got $HTTP_CODE"
fi
echo ""

# Test 3: Name too short
echo "Test 3: client_name too short (should return 422)"
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/clients/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "client_type": "residential",
    "client_name": "A",
    "primary_contact": {"first_name": "John", "last_name": "Doe"}
  }')
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
if [ "$HTTP_CODE" = "422" ]; then
  echo "✅ PASS - Validation rejected short name"
else
  echo "❌ FAIL - Expected 422, got $HTTP_CODE"
fi
echo ""

# Test 4: Contact first name too short
echo "Test 4: Contact first_name too short (should return 422)"
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/clients/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "client_type": "residential",
    "client_name": "Valid Name",
    "primary_contact": {"first_name": "J", "last_name": "Doe"}
  }')
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
if [ "$HTTP_CODE" = "422" ]; then
  echo "✅ PASS - Validation rejected short contact name"
else
  echo "❌ FAIL - Expected 422, got $HTTP_CODE"
fi
echo ""

# Test 5: Very long client name (valid)
echo "Test 5: Very long client_name (should succeed)"
LONG_NAME="This is a very long client name that should still be accepted because we dont have a maximum length validation and thats okay for now"
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/clients/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"client_type\": \"commercial\",
    \"client_name\": \"$LONG_NAME\",
    \"primary_contact\": {\"first_name\": \"Jane\", \"last_name\": \"Smith\", \"email\": \"jane@example.com\"}
  }")
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
if [ "$HTTP_CODE" = "201" ]; then
  echo "✅ PASS - Long name accepted"
  CLIENT_ID=$(echo "$RESPONSE" | head -1 | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)
else
  echo "❌ FAIL - Expected 201, got $HTTP_CODE"
fi
echo ""

# Test 6: Special characters in name (valid)
echo "Test 6: Special characters in name (should succeed)"
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/clients/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "client_type": "residential",
    "client_name": "O'\''Brien & Sons, LLC.",
    "primary_contact": {"first_name": "Patrick", "last_name": "O'\''Brien"}
  }')
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
if [ "$HTTP_CODE" = "201" ]; then
  echo "✅ PASS - Special characters accepted"
else
  echo "❌ FAIL - Expected 201, got $HTTP_CODE"
fi
echo ""

# Test 7: Update non-existent client (should return 404)
echo "Test 7: Update non-existent client (should return 404)"
RESPONSE=$(curl -s -w "\n%{http_code}" -X PUT "$BASE_URL/clients/999999" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"client_name": "Updated"}')
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
if [ "$HTTP_CODE" = "404" ]; then
  echo "✅ PASS - Returned 404 for non-existent client"
else
  echo "❌ FAIL - Expected 404, got $HTTP_CODE"
fi
echo ""

# Test 8: Delete non-existent client (should return 404)
echo "Test 8: Delete non-existent client (should return 404)"
RESPONSE=$(curl -s -w "\n%{http_code}" -X DELETE "$BASE_URL/clients/999999" \
  -H "Authorization: Bearer $ACCESS_TOKEN")
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
if [ "$HTTP_CODE" = "404" ]; then
  echo "✅ PASS - Returned 404 for non-existent client"
else
  echo "❌ FAIL - Expected 404, got $HTTP_CODE"
fi
echo ""

# Test 9: Get deleted client (should return 404)
if [ -n "$CLIENT_ID" ]; then
  echo "Test 9: Access deleted client (should return 404)"
  # Delete the client from Test 5
  curl -s -X DELETE "$BASE_URL/clients/$CLIENT_ID" \
    -H "Authorization: Bearer $ACCESS_TOKEN" > /dev/null

  # Try to get it
  RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/clients/$CLIENT_ID" \
    -H "Authorization: Bearer $ACCESS_TOKEN")
  HTTP_CODE=$(echo "$RESPONSE" | tail -1)
  if [ "$HTTP_CODE" = "404" ]; then
    echo "✅ PASS - Deleted client returns 404"
  else
    echo "❌ FAIL - Expected 404, got $HTTP_CODE"
  fi
  echo ""
fi

# Test 10: Missing required field (primary_contact)
echo "Test 10: Missing required field (should return 422)"
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/clients/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "client_type": "residential",
    "client_name": "Test"
  }')
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
if [ "$HTTP_CODE" = "422" ]; then
  echo "✅ PASS - Validation rejected missing primary_contact"
else
  echo "❌ FAIL - Expected 422, got $HTTP_CODE"
fi
echo ""

echo "=========================================="
echo "Edge Case Tests Complete!"
echo "=========================================="
