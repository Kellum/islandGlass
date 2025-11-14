#!/bin/bash

# Job Vendor Materials CRUD Endpoint Test Script
# Tests all job vendor materials endpoints with proper authentication

BASE_URL="http://localhost:8000/api/v1"
EMAIL="ry@islandglassandmirror.com"
PASSWORD="Asdfghj123!@"

echo "================================================"
echo "FastAPI Job Vendor Materials Endpoints Test"
echo "================================================"
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

# Step 2: Get existing jobs to use in tests
echo "2. GET /jobs - Get existing jobs"
JOBS_RESPONSE=$(curl -s -X GET "$BASE_URL/jobs/" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

JOB_ID=$(echo $JOBS_RESPONSE | python3 -c "import sys, json; data=json.load(sys.stdin); print(data[0]['job_id']) if data else ''" 2>/dev/null)

if [ -z "$JOB_ID" ]; then
  echo "❌ No jobs found. Creating a test job..."

  # Get clients
  CLIENTS_RESPONSE=$(curl -s -X GET "$BASE_URL/clients/" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

  CLIENT_ID=$(echo $CLIENTS_RESPONSE | python3 -c "import sys, json; data=json.load(sys.stdin); print(data[0]['client_id']) if data else ''" 2>/dev/null)

  if [ -z "$CLIENT_ID" ]; then
    echo "❌ No clients found. Cannot run tests without a job."
    exit 1
  fi

  # Create a test job
  CREATE_JOB_RESPONSE=$(curl -s -X POST "$BASE_URL/jobs/" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"client_id\":$CLIENT_ID,\"job_name\":\"Test Job for Materials\",\"status\":\"Active\"}")

  JOB_ID=$(echo $CREATE_JOB_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['job_id'])" 2>/dev/null)

  if [ -z "$JOB_ID" ]; then
    echo "❌ Failed to create test job"
    exit 1
  fi

  echo "✅ Test job created with ID: $JOB_ID"
else
  echo "✅ Found job ID: $JOB_ID"
fi
echo ""

# Step 3: Get existing vendors to use in tests
echo "3. GET /vendors - Get existing vendors"
VENDORS_RESPONSE=$(curl -s -X GET "$BASE_URL/vendors/" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

VENDOR_ID=$(echo $VENDORS_RESPONSE | python3 -c "import sys, json; data=json.load(sys.stdin); print(data[0]['vendor_id']) if data else ''" 2>/dev/null)

if [ -z "$VENDOR_ID" ]; then
  echo "⚠️  No vendors found. Will create material without vendor_id."
  VENDOR_ID=""
else
  echo "✅ Found vendor ID: $VENDOR_ID"
fi
echo ""

# Step 4: Get all materials for this job (should be empty initially)
echo "4. GET /jobs/$JOB_ID/vendor-materials - List all materials for job"
GET_ALL_RESPONSE=$(curl -s -X GET "$BASE_URL/jobs/$JOB_ID/vendor-materials/" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "Response:"
echo $GET_ALL_RESPONSE | python3 -m json.tool 2>/dev/null || echo $GET_ALL_RESPONSE
echo ""

# Step 5: Create a new material
echo "5. POST /jobs/$JOB_ID/vendor-materials - Create new material"
if [ -z "$VENDOR_ID" ]; then
  CREATE_PAYLOAD='{
    "description": "Test Material: Shower door crystalline bypass",
    "ordered_date": "2025-01-10",
    "expected_delivery_date": "2025-01-20",
    "cost": 1250.00,
    "status": "Ordered",
    "notes": "Need to confirm measurements before ordering"
  }'
else
  CREATE_PAYLOAD="{
    \"vendor_id\": $VENDOR_ID,
    \"description\": \"Test Material: Shower door crystalline bypass\",
    \"ordered_date\": \"2025-01-10\",
    \"expected_delivery_date\": \"2025-01-20\",
    \"cost\": 1250.00,
    \"status\": \"Ordered\",
    \"tracking_number\": \"1Z999AA10123456784\",
    \"carrier\": \"UPS\",
    \"notes\": \"Need to confirm measurements before ordering\"
  }"
fi

CREATE_RESPONSE=$(curl -s -X POST "$BASE_URL/jobs/$JOB_ID/vendor-materials/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$CREATE_PAYLOAD")

echo "Response:"
echo $CREATE_RESPONSE | python3 -m json.tool 2>/dev/null || echo $CREATE_RESPONSE

# Extract material ID from response
MATERIAL_ID=$(echo $CREATE_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['material_id'])" 2>/dev/null)

if [ -z "$MATERIAL_ID" ]; then
  echo "❌ Material creation failed"
  echo ""
else
  echo "✅ Material created with ID: $MATERIAL_ID"
  echo ""

  # Step 6: Get material by ID
  echo "6. GET /jobs/$JOB_ID/vendor-materials/$MATERIAL_ID - Get material details"
  GET_ONE_RESPONSE=$(curl -s -X GET "$BASE_URL/jobs/$JOB_ID/vendor-materials/$MATERIAL_ID" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

  echo "Response:"
  echo $GET_ONE_RESPONSE | python3 -m json.tool 2>/dev/null || echo $GET_ONE_RESPONSE
  echo ""

  # Step 7: Update material (mark as delivered)
  echo "7. PUT /jobs/$JOB_ID/vendor-materials/$MATERIAL_ID - Update material (mark delivered)"
  UPDATE_RESPONSE=$(curl -s -X PUT "$BASE_URL/jobs/$JOB_ID/vendor-materials/$MATERIAL_ID" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
      "actual_delivery_date": "2025-01-18",
      "status": "Delivered",
      "notes": "Delivered 2 days early. Quality looks good."
    }')

  echo "Response:"
  echo $UPDATE_RESPONSE | python3 -m json.tool 2>/dev/null || echo $UPDATE_RESPONSE
  echo ""

  # Step 8: Filter by status
  echo "8. GET /jobs/$JOB_ID/vendor-materials?status=Delivered - Filter by status"
  FILTER_RESPONSE=$(curl -s -X GET "$BASE_URL/jobs/$JOB_ID/vendor-materials/?status=Delivered" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

  echo "Response:"
  echo $FILTER_RESPONSE | python3 -m json.tool 2>/dev/null || echo $FILTER_RESPONSE
  echo ""

  # Step 9: Create a second material (for testing multiple materials)
  echo "9. POST /jobs/$JOB_ID/vendor-materials - Create second material"
  CREATE2_PAYLOAD='{
    "description": "Mirror panels 36x60 polished edge",
    "ordered_date": "2025-01-12",
    "expected_delivery_date": "2025-01-25",
    "cost": 875.50,
    "status": "Ordered"
  }'

  CREATE2_RESPONSE=$(curl -s -X POST "$BASE_URL/jobs/$JOB_ID/vendor-materials/" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d "$CREATE2_PAYLOAD")

  MATERIAL2_ID=$(echo $CREATE2_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['material_id'])" 2>/dev/null)

  if [ -z "$MATERIAL2_ID" ]; then
    echo "❌ Second material creation failed"
  else
    echo "✅ Second material created with ID: $MATERIAL2_ID"
  fi
  echo ""

  # Step 10: Get all materials again (should show both)
  echo "10. GET /jobs/$JOB_ID/vendor-materials - List all materials (should show 2)"
  GET_ALL_AFTER_RESPONSE=$(curl -s -X GET "$BASE_URL/jobs/$JOB_ID/vendor-materials/" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

  echo "Response:"
  echo $GET_ALL_AFTER_RESPONSE | python3 -m json.tool 2>/dev/null || echo $GET_ALL_AFTER_RESPONSE
  echo ""

  # Step 11: Filter by vendor
  if [ -n "$VENDOR_ID" ]; then
    echo "11. GET /jobs/$JOB_ID/vendor-materials?vendor_id=$VENDOR_ID - Filter by vendor"
    VENDOR_FILTER_RESPONSE=$(curl -s -X GET "$BASE_URL/jobs/$JOB_ID/vendor-materials/?vendor_id=$VENDOR_ID" \
      -H "Authorization: Bearer $ACCESS_TOKEN")

    echo "Response:"
    echo $VENDOR_FILTER_RESPONSE | python3 -m json.tool 2>/dev/null || echo $VENDOR_FILTER_RESPONSE
    echo ""
  fi

  # Step 12: Delete first material
  echo "12. DELETE /jobs/$JOB_ID/vendor-materials/$MATERIAL_ID - Delete material"
  DELETE_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X DELETE "$BASE_URL/jobs/$JOB_ID/vendor-materials/$MATERIAL_ID" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

  HTTP_STATUS=$(echo "$DELETE_RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)

  if [ "$HTTP_STATUS" = "204" ]; then
    echo "✅ Material deleted (HTTP 204)"
  else
    echo "❌ Delete failed (HTTP $HTTP_STATUS)"
    echo "$DELETE_RESPONSE"
  fi
  echo ""

  # Step 13: Try to get deleted material (should return 404)
  echo "13. GET /jobs/$JOB_ID/vendor-materials/$MATERIAL_ID - Try to get deleted material (should 404)"
  GET_DELETED_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X GET "$BASE_URL/jobs/$JOB_ID/vendor-materials/$MATERIAL_ID" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

  HTTP_STATUS=$(echo "$GET_DELETED_RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)

  if [ "$HTTP_STATUS" = "404" ]; then
    echo "✅ Correctly returns 404 for deleted material"
  else
    echo "❌ Should return 404 (got HTTP $HTTP_STATUS)"
    echo "$GET_DELETED_RESPONSE"
  fi
  echo ""

  # Step 14: Delete second material (cleanup)
  if [ -n "$MATERIAL2_ID" ]; then
    echo "14. DELETE /jobs/$JOB_ID/vendor-materials/$MATERIAL2_ID - Delete second material (cleanup)"
    DELETE2_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X DELETE "$BASE_URL/jobs/$JOB_ID/vendor-materials/$MATERIAL2_ID" \
      -H "Authorization: Bearer $ACCESS_TOKEN")

    HTTP_STATUS=$(echo "$DELETE2_RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)

    if [ "$HTTP_STATUS" = "204" ]; then
      echo "✅ Second material deleted (HTTP 204)"
    else
      echo "❌ Delete failed (HTTP $HTTP_STATUS)"
      echo "$DELETE2_RESPONSE"
    fi
    echo ""
  fi
fi

echo ""
echo "================================================"
echo "Job Vendor Materials Endpoints Test Complete"
echo "================================================"
