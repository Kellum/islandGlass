#!/bin/bash

# Site Visits CRUD Endpoint Test Script
# Tests all site visit endpoints with proper authentication

BASE_URL="http://localhost:8000/api/v1"
EMAIL="ry@islandglassandmirror.com"
PASSWORD="Asdfghj123!@"

echo "=========================================="
echo "FastAPI Site Visits Endpoints Test"
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

# Step 2: Create a test client for the job
echo "2. Creating test client..."
CLIENT_RESPONSE=$(curl -s -X POST "$BASE_URL/clients/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "client_type": "residential",
    "client_name": "Test Client for Site Visits",
    "address": "123 Test St",
    "city": "TestCity",
    "state": "CA",
    "primary_contact": {
      "first_name": "John",
      "last_name": "Test",
      "email": "sitevisits@test.com",
      "phone": "555-8888",
      "is_primary": true
    }
  }')

CLIENT_ID=$(echo $CLIENT_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)

if [ -z "$CLIENT_ID" ]; then
  echo "❌ Client creation failed"
  exit 1
fi

echo "✅ Test client created with ID: $CLIENT_ID"
echo ""

# Step 3: Create a test job
echo "3. Creating test job..."
PO_NUMBER="PO-SITEVISITS-TEST-$(date +%s)"
JOB_RESPONSE=$(curl -s -X POST "$BASE_URL/jobs/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"po_number\": \"$PO_NUMBER\",
    \"client_id\": $CLIENT_ID,
    \"status\": \"Quote\",
    \"job_description\": \"Test job for site visits\",
    \"total_estimate\": 5000.00
  }")

JOB_ID=$(echo $JOB_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['job_id'])" 2>/dev/null)

if [ -z "$JOB_ID" ]; then
  echo "❌ Job creation failed"
  echo "Response: $JOB_RESPONSE"
  exit 1
fi

echo "✅ Test job created with ID: $JOB_ID"
echo ""

# Step 4: Create a site visit
echo "4. Creating site visit (Measure/Estimate)..."
VISIT_RESPONSE=$(curl -s -X POST "$BASE_URL/site-visits/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"job_id\": $JOB_ID,
    \"visit_date\": \"2025-11-08\",
    \"visit_time\": \"10:00:00\",
    \"duration_hours\": 2.5,
    \"visit_type\": \"Measure/Estimate\",
    \"employee_name\": \"Bob Smith\",
    \"notes\": \"Initial site measurement for shower door\",
    \"completed\": false
  }")

VISIT_ID=$(echo $VISIT_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['visit_id'])" 2>/dev/null)

if [ -z "$VISIT_ID" ]; then
  echo "❌ Site visit creation failed"
  echo "Response: $VISIT_RESPONSE"
  exit 1
fi

echo "✅ Site visit created with ID: $VISIT_ID"
echo ""

# Step 5: Get site visit by ID
echo "5. Get site visit by ID..."
GET_VISIT_RESPONSE=$(curl -s -X GET "$BASE_URL/site-visits/$VISIT_ID" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

FETCHED_VISIT_ID=$(echo $GET_VISIT_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['visit_id'])" 2>/dev/null)

if [ "$FETCHED_VISIT_ID" != "$VISIT_ID" ]; then
  echo "❌ Get site visit failed"
  echo "Response: $GET_VISIT_RESPONSE"
  exit 1
fi

echo "✅ Site visit retrieved successfully"
echo ""

# Step 6: List site visits for job
echo "6. List site visits for job..."
LIST_RESPONSE=$(curl -s -X GET "$BASE_URL/site-visits/?job_id=$JOB_ID" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

VISIT_COUNT=$(echo $LIST_RESPONSE | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null)

if [ -z "$VISIT_COUNT" ] || [ "$VISIT_COUNT" -lt 1 ]; then
  echo "❌ List site visits failed"
  echo "Response: $LIST_RESPONSE"
  exit 1
fi

echo "✅ Found $VISIT_COUNT site visit(s) for job"
echo ""

# Step 7: Update site visit (mark as completed)
echo "7. Update site visit (mark as completed)..."
UPDATE_RESPONSE=$(curl -s -X PUT "$BASE_URL/site-visits/$VISIT_ID" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "completed": true,
    "outcome": "Measurements taken successfully",
    "issues_found": "Shower base not level - needs adjustment"
  }')

UPDATED_COMPLETED=$(echo $UPDATE_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('completed', False))" 2>/dev/null)

if [ "$UPDATED_COMPLETED" != "True" ]; then
  echo "❌ Site visit update failed"
  echo "Response: $UPDATE_RESPONSE"
  exit 1
fi

echo "✅ Site visit updated successfully"
echo ""

# Step 8: Create another site visit (Install)
echo "8. Creating second site visit (Install)..."
VISIT2_RESPONSE=$(curl -s -X POST "$BASE_URL/site-visits/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"job_id\": $JOB_ID,
    \"visit_date\": \"2025-11-15\",
    \"visit_time\": \"14:00:00\",
    \"duration_hours\": 4.0,
    \"visit_type\": \"Install\",
    \"employee_name\": \"Bob Smith\",
    \"notes\": \"Install frameless shower door\",
    \"completed\": false
  }")

VISIT2_ID=$(echo $VISIT2_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['visit_id'])" 2>/dev/null)

if [ -z "$VISIT2_ID" ]; then
  echo "❌ Second site visit creation failed"
  exit 1
fi

echo "✅ Second site visit created with ID: $VISIT2_ID"
echo ""

# Step 9: Filter by visit type
echo "9. Filter site visits by type (Install)..."
FILTER_RESPONSE=$(curl -s -X GET "$BASE_URL/site-visits/?job_id=$JOB_ID&visit_type=Install" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

FILTER_COUNT=$(echo $FILTER_RESPONSE | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null)

if [ "$FILTER_COUNT" != "1" ]; then
  echo "❌ Filter by visit type failed"
  echo "Expected 1 result, got $FILTER_COUNT"
  exit 1
fi

echo "✅ Filter by visit type working correctly"
echo ""

# Step 10: Filter by completed status
echo "10. Filter site visits by completed status (false)..."
COMPLETED_FILTER_RESPONSE=$(curl -s -X GET "$BASE_URL/site-visits/?job_id=$JOB_ID&completed=false" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

COMPLETED_FILTER_COUNT=$(echo $COMPLETED_FILTER_RESPONSE | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null)

if [ "$COMPLETED_FILTER_COUNT" != "1" ]; then
  echo "❌ Filter by completed status failed"
  echo "Expected 1 result, got $COMPLETED_FILTER_COUNT"
  exit 1
fi

echo "✅ Filter by completed status working correctly"
echo ""

# Step 11: Delete first site visit
echo "11. Delete first site visit..."
DELETE_RESPONSE=$(curl -s -w "\n%{http_code}" -X DELETE "$BASE_URL/site-visits/$VISIT_ID" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

HTTP_CODE=$(echo "$DELETE_RESPONSE" | tail -n1)

if [ "$HTTP_CODE" != "204" ]; then
  echo "❌ Delete site visit failed (HTTP $HTTP_CODE)"
  exit 1
fi

echo "✅ Site visit deleted successfully"
echo ""

# Step 12: Verify deletion
echo "12. Verify site visit was deleted..."
VERIFY_RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/site-visits/$VISIT_ID" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

HTTP_CODE=$(echo "$VERIFY_RESPONSE" | tail -n1)

if [ "$HTTP_CODE" != "404" ]; then
  echo "❌ Site visit should be deleted (expected 404, got $HTTP_CODE)"
  exit 1
fi

echo "✅ Verified site visit deletion"
echo ""

# Cleanup: Delete test job
echo "13. Cleanup: Deleting test job..."
curl -s -X DELETE "$BASE_URL/jobs/$JOB_ID" \
  -H "Authorization: Bearer $ACCESS_TOKEN" > /dev/null

echo "✅ Test job deleted"
echo ""

# Cleanup: Delete test client
echo "14. Cleanup: Deleting test client..."
curl -s -X DELETE "$BASE_URL/clients/$CLIENT_ID" \
  -H "Authorization: Bearer $ACCESS_TOKEN" > /dev/null

echo "✅ Test client deleted"
echo ""

echo "=========================================="
echo "✅ All Site Visits Tests Passed! (14/14)"
echo "=========================================="
