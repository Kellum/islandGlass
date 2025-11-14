#!/bin/bash

# Work Items CRUD Endpoint Test Script
# Tests all work item endpoints with proper authentication

BASE_URL="http://localhost:8000/api/v1"
EMAIL="ry@islandglassandmirror.com"
PASSWORD="Asdfghj123!@"

echo "=========================================="
echo "FastAPI Work Items Endpoints Test"
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
    "client_name": "Test Client for Work Items",
    "address": "123 Test St",
    "city": "TestCity",
    "state": "CA",
    "primary_contact": {
      "first_name": "John",
      "last_name": "Test",
      "email": "workitems@test.com",
      "phone": "555-9999",
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
PO_NUMBER="PO-WORKITEMS-TEST-$(date +%s)"
JOB_RESPONSE=$(curl -s -X POST "$BASE_URL/jobs/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"po_number\": \"$PO_NUMBER\",
    \"client_id\": $CLIENT_ID,
    \"status\": \"Quote\",
    \"job_description\": \"Test job for work items\",
    \"total_estimate\": 5000.00
  }")

JOB_ID=$(echo $JOB_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['job_id'])" 2>/dev/null)

if [ -z "$JOB_ID" ]; then
  echo "❌ Job creation failed"
  exit 1
fi

echo "✅ Test job created with ID: $JOB_ID"
echo ""

# Step 4: Get work items for the job (should be empty initially)
echo "4. GET /work-items?job_id=$JOB_ID - List work items for job"
GET_JOB_ITEMS_RESPONSE=$(curl -s -X GET "$BASE_URL/work-items/?job_id=$JOB_ID" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "Response:"
echo $GET_JOB_ITEMS_RESPONSE | python3 -m json.tool 2>/dev/null || echo $GET_JOB_ITEMS_RESPONSE
echo ""

# Step 5: Create a new work item
echo "5. POST /work-items - Create new work item"
CREATE_RESPONSE=$(curl -s -X POST "$BASE_URL/work-items/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"job_id\": $JOB_ID,
    \"work_type\": \"Shower\",
    \"quantity\": 1,
    \"description\": \"Test frameless shower enclosure\",
    \"specifications\": {
      \"width\": \"60 inches\",
      \"height\": \"72 inches\",
      \"glass_type\": \"3/8 clear tempered\"
    },
    \"estimated_cost\": 1200.00,
    \"status\": \"Pending\",
    \"sort_order\": 1
  }")

echo "Response:"
echo $CREATE_RESPONSE | python3 -m json.tool 2>/dev/null || echo $CREATE_RESPONSE

# Extract item ID from response
ITEM_ID=$(echo $CREATE_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['item_id'])" 2>/dev/null)

if [ -z "$ITEM_ID" ]; then
  echo "❌ Work item creation failed"
  echo ""
else
  echo "✅ Work item created with ID: $ITEM_ID"
  echo ""

  # Step 6: Get work item by ID
  echo "6. GET /work-items/$ITEM_ID - Get work item details"
  GET_ONE_RESPONSE=$(curl -s -X GET "$BASE_URL/work-items/$ITEM_ID" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

  echo "Response:"
  echo $GET_ONE_RESPONSE | python3 -m json.tool 2>/dev/null || echo $GET_ONE_RESPONSE
  echo ""

  # Step 7: Update work item
  echo "7. PUT /work-items/$ITEM_ID - Update work item"
  UPDATE_RESPONSE=$(curl -s -X PUT "$BASE_URL/work-items/$ITEM_ID" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
      \"description\": \"Test frameless shower enclosure (UPDATED)\",
      \"actual_cost\": 1350.50,
      \"status\": \"In Progress\"
    }")

  echo "Response:"
  echo $UPDATE_RESPONSE | python3 -m json.tool 2>/dev/null || echo $UPDATE_RESPONSE
  echo ""

  # Step 8: Get work items for job again (should show updated item)
  echo "8. GET /work-items?job_id=$JOB_ID - List work items (after update)"
  GET_JOB_ITEMS_AFTER_RESPONSE=$(curl -s -X GET "$BASE_URL/work-items/?job_id=$JOB_ID" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

  echo "Response:"
  echo $GET_JOB_ITEMS_AFTER_RESPONSE | python3 -m json.tool 2>/dev/null || echo $GET_JOB_ITEMS_AFTER_RESPONSE
  echo ""

  # Step 9: Filter by work type
  echo "9. GET /work-items?job_id=$JOB_ID&work_type=Shower - Filter by work type"
  FILTER_RESPONSE=$(curl -s -X GET "$BASE_URL/work-items/?job_id=$JOB_ID&work_type=Shower" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

  echo "Response:"
  echo $FILTER_RESPONSE | python3 -m json.tool 2>/dev/null || echo $FILTER_RESPONSE
  echo ""

  # Step 10: Delete work item (hard delete)
  echo "10. DELETE /work-items/$ITEM_ID - Delete work item"
  DELETE_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X DELETE "$BASE_URL/work-items/$ITEM_ID" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

  HTTP_STATUS=$(echo "$DELETE_RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)

  if [ "$HTTP_STATUS" = "204" ]; then
    echo "✅ Work item deleted (HTTP 204)"
  else
    echo "❌ Delete failed (HTTP $HTTP_STATUS)"
    echo "$DELETE_RESPONSE"
  fi
  echo ""

  # Step 11: Try to get deleted work item (should return 404)
  echo "11. GET /work-items/$ITEM_ID - Try to get deleted work item (should 404)"
  GET_DELETED_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X GET "$BASE_URL/work-items/$ITEM_ID" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

  HTTP_STATUS=$(echo "$GET_DELETED_RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)

  if [ "$HTTP_STATUS" = "404" ]; then
    echo "✅ Correctly returns 404 for deleted work item"
  else
    echo "❌ Should return 404 (got HTTP $HTTP_STATUS)"
    echo "$GET_DELETED_RESPONSE"
  fi
  echo ""
fi

# Cleanup: Delete test job and client
echo "12. Cleanup - Deleting test job and client..."
if [ ! -z "$JOB_ID" ]; then
  curl -s -X DELETE "$BASE_URL/jobs/$JOB_ID" -H "Authorization: Bearer $ACCESS_TOKEN" > /dev/null
fi
if [ ! -z "$CLIENT_ID" ]; then
  curl -s -X DELETE "$BASE_URL/clients/$CLIENT_ID" -H "Authorization: Bearer $ACCESS_TOKEN" > /dev/null
fi
echo "✅ Cleanup complete"
echo ""

echo ""
echo "=========================================="
echo "Work Items Endpoints Test Complete"
echo "=========================================="
