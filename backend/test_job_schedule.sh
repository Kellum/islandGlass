#!/bin/bash

# Job Schedule CRUD Endpoint Test Script
# Tests all job schedule endpoints with proper authentication

BASE_URL="http://localhost:8000/api/v1"
EMAIL="ry@islandglassandmirror.com"
PASSWORD="Asdfghj123!@"

echo "================================================"
echo "FastAPI Job Schedule Endpoints Test"
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
    -d "{\"client_id\":$CLIENT_ID,\"job_name\":\"Test Job for Schedule\",\"status\":\"Active\"}")

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

# Step 3: Get all schedule events for this job (should be empty initially)
echo "3. GET /jobs/$JOB_ID/schedule - List all schedule events for job"
GET_ALL_RESPONSE=$(curl -s -X GET "$BASE_URL/jobs/$JOB_ID/schedule/" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "Response:"
echo $GET_ALL_RESPONSE | python3 -m json.tool 2>/dev/null || echo $GET_ALL_RESPONSE
echo ""

# Step 4: Create a new schedule event (Install)
echo "4. POST /jobs/$JOB_ID/schedule - Create new schedule event (Install)"
CREATE_PAYLOAD='{
  "event_type": "Install",
  "scheduled_date": "2025-01-15",
  "scheduled_time": "09:00:00",
  "duration_hours": 4.0,
  "assigned_name": "John Doe",
  "status": "Scheduled",
  "send_reminder": true,
  "notes": "Customer prefers morning installation"
}'

CREATE_RESPONSE=$(curl -s -X POST "$BASE_URL/jobs/$JOB_ID/schedule/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$CREATE_PAYLOAD")

echo "Response:"
echo $CREATE_RESPONSE | python3 -m json.tool 2>/dev/null || echo $CREATE_RESPONSE

# Extract schedule ID from response
SCHEDULE_ID=$(echo $CREATE_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['schedule_id'])" 2>/dev/null)

if [ -z "$SCHEDULE_ID" ]; then
  echo "❌ Schedule event creation failed"
  echo ""
else
  echo "✅ Schedule event created with ID: $SCHEDULE_ID"
  echo ""

  # Step 5: Get schedule event by ID
  echo "5. GET /jobs/$JOB_ID/schedule/$SCHEDULE_ID - Get schedule event details"
  GET_ONE_RESPONSE=$(curl -s -X GET "$BASE_URL/jobs/$JOB_ID/schedule/$SCHEDULE_ID" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

  echo "Response:"
  echo $GET_ONE_RESPONSE | python3 -m json.tool 2>/dev/null || echo $GET_ONE_RESPONSE
  echo ""

  # Step 6: Update schedule event (mark as confirmed)
  echo "6. PUT /jobs/$JOB_ID/schedule/$SCHEDULE_ID - Update schedule (mark confirmed)"
  UPDATE_RESPONSE=$(curl -s -X PUT "$BASE_URL/jobs/$JOB_ID/schedule/$SCHEDULE_ID" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
      "status": "Confirmed",
      "notes": "Customer confirmed installation appointment"
    }')

  echo "Response:"
  echo $UPDATE_RESPONSE | python3 -m json.tool 2>/dev/null || echo $UPDATE_RESPONSE
  echo ""

  # Step 7: Create a second schedule event (Measure)
  echo "7. POST /jobs/$JOB_ID/schedule - Create second schedule event (Measure)"
  CREATE2_PAYLOAD='{
    "event_type": "Measure",
    "scheduled_date": "2025-01-10",
    "scheduled_time": "14:00:00",
    "duration_hours": 1.5,
    "assigned_name": "Jane Smith",
    "status": "Completed",
    "notes": "Initial measurement appointment"
  }'

  CREATE2_RESPONSE=$(curl -s -X POST "$BASE_URL/jobs/$JOB_ID/schedule/" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d "$CREATE2_PAYLOAD")

  SCHEDULE2_ID=$(echo $CREATE2_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['schedule_id'])" 2>/dev/null)

  if [ -z "$SCHEDULE2_ID" ]; then
    echo "❌ Second schedule event creation failed"
  else
    echo "✅ Second schedule event created with ID: $SCHEDULE2_ID"
  fi
  echo ""

  # Step 8: Get all schedule events again (should show both)
  echo "8. GET /jobs/$JOB_ID/schedule - List all schedule events (should show 2)"
  GET_ALL_AFTER_RESPONSE=$(curl -s -X GET "$BASE_URL/jobs/$JOB_ID/schedule/" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

  echo "Response:"
  echo $GET_ALL_AFTER_RESPONSE | python3 -m json.tool 2>/dev/null || echo $GET_ALL_AFTER_RESPONSE
  echo ""

  # Step 9: Filter by event type
  echo "9. GET /jobs/$JOB_ID/schedule?event_type=Install - Filter by event type"
  EVENT_TYPE_FILTER_RESPONSE=$(curl -s -X GET "$BASE_URL/jobs/$JOB_ID/schedule/?event_type=Install" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

  echo "Response:"
  echo $EVENT_TYPE_FILTER_RESPONSE | python3 -m json.tool 2>/dev/null || echo $EVENT_TYPE_FILTER_RESPONSE
  echo ""

  # Step 10: Filter by status
  echo "10. GET /jobs/$JOB_ID/schedule?status=Confirmed - Filter by status"
  STATUS_FILTER_RESPONSE=$(curl -s -X GET "$BASE_URL/jobs/$JOB_ID/schedule/?status=Confirmed" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

  echo "Response:"
  echo $STATUS_FILTER_RESPONSE | python3 -m json.tool 2>/dev/null || echo $STATUS_FILTER_RESPONSE
  echo ""

  # Step 11: Create a third schedule event (Delivery)
  echo "11. POST /jobs/$JOB_ID/schedule - Create third schedule event (Delivery)"
  CREATE3_PAYLOAD='{
    "event_type": "Delivery",
    "scheduled_date": "2025-01-14",
    "scheduled_time": "10:00:00",
    "duration_hours": 0.5,
    "assigned_name": "Delivery Team",
    "status": "Scheduled",
    "send_reminder": false,
    "notes": "Material delivery expected"
  }'

  CREATE3_RESPONSE=$(curl -s -X POST "$BASE_URL/jobs/$JOB_ID/schedule/" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d "$CREATE3_PAYLOAD")

  SCHEDULE3_ID=$(echo $CREATE3_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['schedule_id'])" 2>/dev/null)

  if [ -z "$SCHEDULE3_ID" ]; then
    echo "❌ Third schedule event creation failed"
  else
    echo "✅ Third schedule event created with ID: $SCHEDULE3_ID"
  fi
  echo ""

  # Step 12: Update third event to mark completed
  echo "12. PUT /jobs/$JOB_ID/schedule/$SCHEDULE3_ID - Update delivery status to Completed"
  UPDATE3_RESPONSE=$(curl -s -X PUT "$BASE_URL/jobs/$JOB_ID/schedule/$SCHEDULE3_ID" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
      "status": "Completed",
      "notes": "Material delivered on time"
    }')

  echo "Response:"
  echo $UPDATE3_RESPONSE | python3 -m json.tool 2>/dev/null || echo $UPDATE3_RESPONSE
  echo ""

  # Step 13: Delete first schedule event
  echo "13. DELETE /jobs/$JOB_ID/schedule/$SCHEDULE_ID - Delete schedule event"
  DELETE_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X DELETE "$BASE_URL/jobs/$JOB_ID/schedule/$SCHEDULE_ID" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

  HTTP_STATUS=$(echo "$DELETE_RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)

  if [ "$HTTP_STATUS" = "204" ]; then
    echo "✅ Schedule event deleted (HTTP 204)"
  else
    echo "❌ Delete failed (HTTP $HTTP_STATUS)"
    echo "$DELETE_RESPONSE"
  fi
  echo ""

  # Step 14: Try to get deleted schedule event (should return 404)
  echo "14. GET /jobs/$JOB_ID/schedule/$SCHEDULE_ID - Try to get deleted event (should 404)"
  GET_DELETED_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X GET "$BASE_URL/jobs/$JOB_ID/schedule/$SCHEDULE_ID" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

  HTTP_STATUS=$(echo "$GET_DELETED_RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)

  if [ "$HTTP_STATUS" = "404" ]; then
    echo "✅ Correctly returns 404 for deleted event"
  else
    echo "❌ Should return 404 (got HTTP $HTTP_STATUS)"
    echo "$GET_DELETED_RESPONSE"
  fi
  echo ""

  # Step 15: Delete second schedule event (cleanup)
  if [ -n "$SCHEDULE2_ID" ]; then
    echo "15. DELETE /jobs/$JOB_ID/schedule/$SCHEDULE2_ID - Delete second event (cleanup)"
    DELETE2_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X DELETE "$BASE_URL/jobs/$JOB_ID/schedule/$SCHEDULE2_ID" \
      -H "Authorization: Bearer $ACCESS_TOKEN")

    HTTP_STATUS=$(echo "$DELETE2_RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)

    if [ "$HTTP_STATUS" = "204" ]; then
      echo "✅ Second event deleted (HTTP 204)"
    else
      echo "❌ Delete failed (HTTP $HTTP_STATUS)"
      echo "$DELETE2_RESPONSE"
    fi
    echo ""
  fi

  # Step 16: Delete third schedule event (cleanup)
  if [ -n "$SCHEDULE3_ID" ]; then
    echo "16. DELETE /jobs/$JOB_ID/schedule/$SCHEDULE3_ID - Delete third event (cleanup)"
    DELETE3_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X DELETE "$BASE_URL/jobs/$JOB_ID/schedule/$SCHEDULE3_ID" \
      -H "Authorization: Bearer $ACCESS_TOKEN")

    HTTP_STATUS=$(echo "$DELETE3_RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)

    if [ "$HTTP_STATUS" = "204" ]; then
      echo "✅ Third event deleted (HTTP 204)"
    else
      echo "❌ Delete failed (HTTP $HTTP_STATUS)"
      echo "$DELETE3_RESPONSE"
    fi
    echo ""
  fi
fi

echo ""
echo "================================================"
echo "Job Schedule Endpoints Test Complete"
echo "================================================"
