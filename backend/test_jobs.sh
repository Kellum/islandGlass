#!/bin/bash

# Job CRUD Endpoint Test Script
# Tests all job endpoints with proper authentication

BASE_URL="http://localhost:8000/api/v1"
EMAIL="ry@islandglassandmirror.com"
PASSWORD="Asdfghj123!@"

echo "=========================================="
echo "FastAPI Jobs Endpoints Test"
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

# Step 1.5: Get/Create a test client first
echo "1.5. Creating test client for job..."
CLIENT_RESPONSE=$(curl -s -X POST "$BASE_URL/clients/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "client_type": "residential",
    "client_name": "Job Test Client",
    "address": "456 Test Ave",
    "city": "TestCity",
    "state": "CA",
    "primary_contact": {
      "first_name": "Jane",
      "last_name": "Smith",
      "email": "jane@test.com",
      "phone": "555-5678",
      "is_primary": true
    }
  }')

CLIENT_ID=$(echo $CLIENT_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)

if [ -z "$CLIENT_ID" ]; then
  echo "❌ Failed to create test client"
  echo "Response: $CLIENT_RESPONSE"
  exit 1
fi

echo "✅ Test client created with ID: $CLIENT_ID"
echo ""

# Step 2: Get all jobs (should be empty or show existing)
echo "2. GET /jobs - List all jobs"
GET_ALL_RESPONSE=$(curl -s -X GET "$BASE_URL/jobs/" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "Response:"
echo $GET_ALL_RESPONSE | python3 -m json.tool 2>/dev/null || echo $GET_ALL_RESPONSE
echo ""

# Step 3: Create a new job
echo "3. POST /jobs - Create new job"
PO_NUMBER="PO-TEST-$(date +%s)"
CREATE_RESPONSE=$(curl -s -X POST "$BASE_URL/jobs/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"po_number\": \"$PO_NUMBER\",
    \"client_id\": $CLIENT_ID,
    \"status\": \"Quote\",
    \"job_description\": \"Test shower installation\",
    \"site_address\": \"456 Test Ave, TestCity, CA\",
    \"total_estimate\": 1500.00,
    \"internal_notes\": \"This is a test job\"
  }")

echo "Response:"
echo $CREATE_RESPONSE | python3 -m json.tool 2>/dev/null || echo $CREATE_RESPONSE

# Extract job ID from response
JOB_ID=$(echo $CREATE_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['job_id'])" 2>/dev/null)

if [ -z "$JOB_ID" ]; then
  echo "❌ Job creation failed"
  echo ""
else
  echo "✅ Job created with ID: $JOB_ID"
  echo ""

  # Step 4: Get job by ID
  echo "4. GET /jobs/$JOB_ID - Get job details"
  GET_ONE_RESPONSE=$(curl -s -X GET "$BASE_URL/jobs/$JOB_ID" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

  echo "Response:"
  echo $GET_ONE_RESPONSE | python3 -m json.tool 2>/dev/null || echo $GET_ONE_RESPONSE
  echo ""

  # Step 5: Update job
  echo "5. PUT /jobs/$JOB_ID - Update job"
  UPDATE_RESPONSE=$(curl -s -X PUT "$BASE_URL/jobs/$JOB_ID" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
      "status": "Scheduled",
      "job_description": "Test shower installation (UPDATED)",
      "total_estimate": 1750.00
    }')

  echo "Response:"
  echo $UPDATE_RESPONSE | python3 -m json.tool 2>/dev/null || echo $UPDATE_RESPONSE
  echo ""

  # Step 6: Get all jobs again (should show updated job)
  echo "6. GET /jobs - List all jobs (after update)"
  GET_ALL_AFTER_RESPONSE=$(curl -s -X GET "$BASE_URL/jobs/" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

  echo "Response:"
  echo $GET_ALL_AFTER_RESPONSE | python3 -m json.tool 2>/dev/null || echo $GET_ALL_AFTER_RESPONSE
  echo ""

  # Step 7: Delete job (soft delete)
  echo "7. DELETE /jobs/$JOB_ID - Delete job (soft delete)"
  DELETE_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X DELETE "$BASE_URL/jobs/$JOB_ID" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

  HTTP_STATUS=$(echo "$DELETE_RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)

  if [ "$HTTP_STATUS" = "204" ]; then
    echo "✅ Job deleted (HTTP 204)"
  else
    echo "❌ Delete failed (HTTP $HTTP_STATUS)"
    echo "$DELETE_RESPONSE"
  fi
  echo ""

  # Step 8: Try to get deleted job (should return 404)
  echo "8. GET /jobs/$JOB_ID - Try to get deleted job (should 404)"
  GET_DELETED_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X GET "$BASE_URL/jobs/$JOB_ID" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

  HTTP_STATUS=$(echo "$GET_DELETED_RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)

  if [ "$HTTP_STATUS" = "404" ]; then
    echo "✅ Correctly returns 404 for deleted job"
  else
    echo "❌ Should return 404 (got HTTP $HTTP_STATUS)"
    echo "$GET_DELETED_RESPONSE"
  fi
  echo ""

  # Cleanup: Delete test client
  echo "9. Cleanup - Delete test client"
  curl -s -X DELETE "$BASE_URL/clients/$CLIENT_ID" \
    -H "Authorization: Bearer $ACCESS_TOKEN" > /dev/null
  echo "✅ Test client cleaned up"
fi

echo ""
echo "=========================================="
echo "Jobs Endpoints Test Complete"
echo "=========================================="
