#!/bin/bash

# Job Comments CRUD Endpoint Test Script
# Tests all job comment endpoints with proper authentication

BASE_URL="http://localhost:8000/api/v1"
EMAIL="ry@islandglassandmirror.com"
PASSWORD="Asdfghj123!@"

echo "=========================================="
echo "FastAPI Job Comments Endpoints Test"
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
    "client_name": "Test Client for Comments",
    "address": "123 Test St",
    "city": "TestCity",
    "state": "CA",
    "primary_contact": {
      "first_name": "John",
      "last_name": "Test",
      "email": "comments@test.com",
      "phone": "555-7777",
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
PO_NUMBER="PO-COMMENTS-TEST-$(date +%s)"
JOB_RESPONSE=$(curl -s -X POST "$BASE_URL/jobs/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"po_number\": \"$PO_NUMBER\",
    \"client_id\": $CLIENT_ID,
    \"status\": \"Quote\",
    \"job_description\": \"Test job for comments\",
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

# Step 4: Create a job comment (Note)
echo "4. Creating job comment (Note)..."
COMMENT_RESPONSE=$(curl -s -X POST "$BASE_URL/job-comments/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"job_id\": $JOB_ID,
    \"comment_text\": \"Customer called about timeline\",
    \"comment_type\": \"Note\"
  }")

COMMENT_ID=$(echo $COMMENT_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['comment_id'])" 2>/dev/null)

if [ -z "$COMMENT_ID" ]; then
  echo "❌ Job comment creation failed"
  echo "Response: $COMMENT_RESPONSE"
  exit 1
fi

echo "✅ Job comment created with ID: $COMMENT_ID"
echo ""

# Step 5: Get job comment by ID
echo "5. Get job comment by ID..."
GET_COMMENT_RESPONSE=$(curl -s -X GET "$BASE_URL/job-comments/$COMMENT_ID" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

FETCHED_COMMENT_ID=$(echo $GET_COMMENT_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['comment_id'])" 2>/dev/null)

if [ "$FETCHED_COMMENT_ID" != "$COMMENT_ID" ]; then
  echo "❌ Get job comment failed"
  echo "Response: $GET_COMMENT_RESPONSE"
  exit 1
fi

echo "✅ Job comment retrieved successfully"
echo ""

# Step 6: List job comments for job
echo "6. List job comments for job..."
LIST_RESPONSE=$(curl -s -X GET "$BASE_URL/job-comments/?job_id=$JOB_ID" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

COMMENT_COUNT=$(echo $LIST_RESPONSE | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null)

if [ -z "$COMMENT_COUNT" ] || [ "$COMMENT_COUNT" -lt 1 ]; then
  echo "❌ List job comments failed"
  echo "Response: $LIST_RESPONSE"
  exit 1
fi

echo "✅ Found $COMMENT_COUNT job comment(s)"
echo ""

# Step 7: Update job comment
echo "7. Update job comment..."
UPDATE_RESPONSE=$(curl -s -X PUT "$BASE_URL/job-comments/$COMMENT_ID" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "comment_text": "Customer called about timeline - confirmed 2 weeks"
  }')

UPDATED_EDITED=$(echo $UPDATE_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('edited', False))" 2>/dev/null)

if [ "$UPDATED_EDITED" != "True" ]; then
  echo "❌ Job comment update failed"
  echo "Response: $UPDATE_RESPONSE"
  exit 1
fi

echo "✅ Job comment updated successfully"
echo ""

# Step 8: Create another comment (Update type)
echo "8. Creating second job comment (Update)..."
COMMENT2_RESPONSE=$(curl -s -X POST "$BASE_URL/job-comments/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"job_id\": $JOB_ID,
    \"comment_text\": \"Job status changed to In Progress\",
    \"comment_type\": \"Update\"
  }")

COMMENT2_ID=$(echo $COMMENT2_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['comment_id'])" 2>/dev/null)

if [ -z "$COMMENT2_ID" ]; then
  echo "❌ Second job comment creation failed"
  exit 1
fi

echo "✅ Second job comment created with ID: $COMMENT2_ID"
echo ""

# Step 9: Create a third comment (Issue type)
echo "9. Creating third job comment (Issue)..."
COMMENT3_RESPONSE=$(curl -s -X POST "$BASE_URL/job-comments/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"job_id\": $JOB_ID,
    \"comment_text\": \"Materials delivery delayed\",
    \"comment_type\": \"Issue\"
  }")

COMMENT3_ID=$(echo $COMMENT3_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['comment_id'])" 2>/dev/null)

if [ -z "$COMMENT3_ID" ]; then
  echo "❌ Third job comment creation failed"
  exit 1
fi

echo "✅ Third job comment created with ID: $COMMENT3_ID"
echo ""

# Step 10: Filter by comment type (Issue)
echo "10. Filter job comments by type (Issue)..."
FILTER_RESPONSE=$(curl -s -X GET "$BASE_URL/job-comments/?job_id=$JOB_ID&comment_type=Issue" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

FILTER_COUNT=$(echo $FILTER_RESPONSE | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null)

if [ "$FILTER_COUNT" != "1" ]; then
  echo "❌ Filter by comment type failed"
  echo "Expected 1 result, got $FILTER_COUNT"
  exit 1
fi

echo "✅ Filter by comment type working correctly"
echo ""

# Step 11: Create a reply comment (thread)
echo "11. Creating reply comment (thread)..."
REPLY_RESPONSE=$(curl -s -X POST "$BASE_URL/job-comments/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"job_id\": $JOB_ID,
    \"comment_text\": \"Materials now scheduled for tomorrow\",
    \"comment_type\": \"Resolution\",
    \"parent_comment_id\": $COMMENT3_ID
  }")

REPLY_ID=$(echo $REPLY_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['comment_id'])" 2>/dev/null)

if [ -z "$REPLY_ID" ]; then
  echo "❌ Reply comment creation failed"
  exit 1
fi

echo "✅ Reply comment created with ID: $REPLY_ID"
echo ""

# Step 12: Verify total comment count
echo "12. Verify total comment count..."
TOTAL_RESPONSE=$(curl -s -X GET "$BASE_URL/job-comments/?job_id=$JOB_ID" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

TOTAL_COUNT=$(echo $TOTAL_RESPONSE | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null)

if [ "$TOTAL_COUNT" != "4" ]; then
  echo "❌ Total comment count incorrect (expected 4, got $TOTAL_COUNT)"
  exit 1
fi

echo "✅ Total comment count correct (4 comments)"
echo ""

# Step 13: Delete second comment
echo "13. Delete second comment..."
DELETE_RESPONSE=$(curl -s -w "\n%{http_code}" -X DELETE "$BASE_URL/job-comments/$COMMENT2_ID" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

HTTP_CODE=$(echo "$DELETE_RESPONSE" | tail -n1)

if [ "$HTTP_CODE" != "204" ]; then
  echo "❌ Delete job comment failed (HTTP $HTTP_CODE)"
  exit 1
fi

echo "✅ Job comment deleted successfully"
echo ""

# Step 14: Verify deletion
echo "14. Verify comment was deleted..."
VERIFY_RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/job-comments/$COMMENT2_ID" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

HTTP_CODE=$(echo "$VERIFY_RESPONSE" | tail -n1)

if [ "$HTTP_CODE" != "404" ]; then
  echo "❌ Comment should be deleted (expected 404, got $HTTP_CODE)"
  exit 1
fi

echo "✅ Verified comment deletion"
echo ""

# Cleanup: Delete test job
echo "15. Cleanup: Deleting test job..."
curl -s -X DELETE "$BASE_URL/jobs/$JOB_ID" \
  -H "Authorization: Bearer $ACCESS_TOKEN" > /dev/null

echo "✅ Test job deleted"
echo ""

# Cleanup: Delete test client
echo "16. Cleanup: Deleting test client..."
curl -s -X DELETE "$BASE_URL/clients/$CLIENT_ID" \
  -H "Authorization: Bearer $ACCESS_TOKEN" > /dev/null

echo "✅ Test client deleted"
echo ""

echo "=========================================="
echo "✅ All Job Comments Tests Passed! (16/16)"
echo "=========================================="
