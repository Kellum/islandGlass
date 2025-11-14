#!/bin/bash

# Client CRUD Endpoint Test Script
# Tests all client endpoints with proper authentication

BASE_URL="http://localhost:8000/api/v1"
EMAIL="ry@islandglassandmirror.com"
PASSWORD="Asdfghj123!@"

echo "=========================================="
echo "FastAPI Client Endpoints Test"
echo "=========================================="
echo ""

# Step 1: Login and get JWT token
echo "1. Login..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")

ACCESS_TOKEN=$(echo $LOGIN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ -z "$ACCESS_TOKEN" ]; then
  echo "❌ Login failed"
  echo "Response: $LOGIN_RESPONSE"
  exit 1
fi

echo "✅ Login successful"
echo "Token: ${ACCESS_TOKEN:0:20}..."
echo ""

# Step 2: Get all clients (should be empty or show existing)
echo "2. GET /clients - List all clients"
GET_ALL_RESPONSE=$(curl -s -X GET "$BASE_URL/clients/" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "Response:"
echo $GET_ALL_RESPONSE | python3 -m json.tool 2>/dev/null || echo $GET_ALL_RESPONSE
echo ""

# Step 3: Create a new client
echo "3. POST /clients - Create new client"
CREATE_RESPONSE=$(curl -s -X POST "$BASE_URL/clients/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "client_type": "residential",
    "client_name": "Test Client - John Doe",
    "address": "123 Main St",
    "city": "Anytown",
    "state": "CA",
    "primary_contact": {
      "first_name": "John",
      "last_name": "Doe",
      "email": "john.doe@example.com",
      "phone": "555-1234",
      "is_primary": true
    }
  }')

echo "Response:"
echo $CREATE_RESPONSE | python3 -m json.tool 2>/dev/null || echo $CREATE_RESPONSE

# Extract client ID from response
CLIENT_ID=$(echo $CREATE_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)

if [ -z "$CLIENT_ID" ]; then
  echo "❌ Client creation failed"
  echo ""
else
  echo "✅ Client created with ID: $CLIENT_ID"
  echo ""

  # Step 4: Get client by ID
  echo "4. GET /clients/$CLIENT_ID - Get client details"
  GET_ONE_RESPONSE=$(curl -s -X GET "$BASE_URL/clients/$CLIENT_ID" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

  echo "Response:"
  echo $GET_ONE_RESPONSE | python3 -m json.tool 2>/dev/null || echo $GET_ONE_RESPONSE
  echo ""

  # Step 5: Update client
  echo "5. PUT /clients/$CLIENT_ID - Update client"
  UPDATE_RESPONSE=$(curl -s -X PUT "$BASE_URL/clients/$CLIENT_ID" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
      "client_name": "Test Client - John Doe (Updated)",
      "city": "New City"
    }')

  echo "Response:"
  echo $UPDATE_RESPONSE | python3 -m json.tool 2>/dev/null || echo $UPDATE_RESPONSE
  echo ""

  # Step 6: Get all clients again (should show updated client)
  echo "6. GET /clients - List all clients (after update)"
  GET_ALL_AFTER_RESPONSE=$(curl -s -X GET "$BASE_URL/clients/" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

  echo "Response:"
  echo $GET_ALL_AFTER_RESPONSE | python3 -m json.tool 2>/dev/null || echo $GET_ALL_AFTER_RESPONSE
  echo ""

  # Step 7: Delete client
  echo "7. DELETE /clients/$CLIENT_ID - Soft delete client"
  DELETE_RESPONSE=$(curl -s -w "\nHTTP Status: %{http_code}" -X DELETE "$BASE_URL/clients/$CLIENT_ID" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

  echo "Response: $DELETE_RESPONSE"
  echo ""

  # Step 8: Try to get deleted client (should return 404)
  echo "8. GET /clients/$CLIENT_ID - Try to get deleted client (should fail)"
  GET_DELETED_RESPONSE=$(curl -s -w "\nHTTP Status: %{http_code}" -X GET "$BASE_URL/clients/$CLIENT_ID" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

  echo "Response: $GET_DELETED_RESPONSE"
  echo ""
fi

echo "=========================================="
echo "Test Complete!"
echo "=========================================="
