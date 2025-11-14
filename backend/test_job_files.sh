#!/bin/bash

# Job Files CRUD Endpoint Test Script
# Tests all job file endpoints with proper authentication

BASE_URL="http://localhost:8000/api/v1"
EMAIL="ry@islandglassandmirror.com"
PASSWORD="Asdfghj123!@"

echo "================================================"
echo "FastAPI Job Files Endpoints Test"
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
  echo "❌ No jobs found. Cannot run tests without a job."
  exit 1
fi

echo "✅ Found job ID: $JOB_ID"
echo ""

# Step 3: Get all files for this job (should be empty initially)
echo "3. GET /jobs/$JOB_ID/files - List all files for job"
GET_ALL_RESPONSE=$(curl -s -X GET "$BASE_URL/jobs/$JOB_ID/files/" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "Response:"
echo $GET_ALL_RESPONSE | python3 -m json.tool 2>/dev/null || echo $GET_ALL_RESPONSE
echo ""

# Step 4: Create a new file entry (Photo)
echo "4. POST /jobs/$JOB_ID/files - Create new file entry (Photo)"
CREATE_PAYLOAD='{
  "file_name": "shower_door_measurement.jpg",
  "file_type": "Photo",
  "file_size": 2048576,
  "file_path": "/storage/jobs/5/photos/shower_door_measurement.jpg",
  "thumbnail_path": "/storage/jobs/5/photos/thumbs/shower_door_measurement_thumb.jpg",
  "description": "Measurements for custom shower door",
  "tags": ["measurement", "shower", "photo"]
}'

CREATE_RESPONSE=$(curl -s -X POST "$BASE_URL/jobs/$JOB_ID/files/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$CREATE_PAYLOAD")

echo "Response:"
echo $CREATE_RESPONSE | python3 -m json.tool 2>/dev/null || echo $CREATE_RESPONSE

# Extract file ID from response
FILE_ID=$(echo $CREATE_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['file_id'])" 2>/dev/null)

if [ -z "$FILE_ID" ]; then
  echo "❌ File entry creation failed"
  echo ""
else
  echo "✅ File entry created with ID: $FILE_ID"
  echo ""

  # Step 5: Get file by ID
  echo "5. GET /jobs/$JOB_ID/files/$FILE_ID - Get file details"
  GET_ONE_RESPONSE=$(curl -s -X GET "$BASE_URL/jobs/$JOB_ID/files/$FILE_ID" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

  echo "Response:"
  echo $GET_ONE_RESPONSE | python3 -m json.tool 2>/dev/null || echo $GET_ONE_RESPONSE
  echo ""

  # Step 6: Update file entry (add more tags)
  echo "6. PUT /jobs/$JOB_ID/files/$FILE_ID - Update file (add tags)"
  UPDATE_RESPONSE=$(curl -s -X PUT "$BASE_URL/jobs/$JOB_ID/files/$FILE_ID" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
      "description": "Updated measurement photo with annotations",
      "tags": ["measurement", "shower", "photo", "annotated"]
    }')

  echo "Response:"
  echo $UPDATE_RESPONSE | python3 -m json.tool 2>/dev/null || echo $UPDATE_RESPONSE
  echo ""

  # Step 7: Create a second file entry (PDF)
  echo "7. POST /jobs/$JOB_ID/files - Create second file entry (PDF)"
  CREATE2_PAYLOAD='{
    "file_name": "contract_signed.pdf",
    "file_type": "PDF",
    "file_size": 512000,
    "file_path": "/storage/jobs/5/documents/contract_signed.pdf",
    "description": "Signed customer contract",
    "tags": ["contract", "legal", "signed"]
  }'

  CREATE2_RESPONSE=$(curl -s -X POST "$BASE_URL/jobs/$JOB_ID/files/" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d "$CREATE2_PAYLOAD")

  FILE2_ID=$(echo $CREATE2_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['file_id'])" 2>/dev/null)

  if [ -z "$FILE2_ID" ]; then
    echo "❌ Second file entry creation failed"
  else
    echo "✅ Second file entry created with ID: $FILE2_ID"
  fi
  echo ""

  # Step 8: Get all files again (should show both)
  echo "8. GET /jobs/$JOB_ID/files - List all files (should show 2)"
  GET_ALL_AFTER_RESPONSE=$(curl -s -X GET "$BASE_URL/jobs/$JOB_ID/files/" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

  echo "Response:"
  echo $GET_ALL_AFTER_RESPONSE | python3 -m json.tool 2>/dev/null || echo $GET_ALL_AFTER_RESPONSE
  echo ""

  # Step 9: Filter by file type
  echo "9. GET /jobs/$JOB_ID/files?file_type=Photo - Filter by file type"
  FILE_TYPE_FILTER_RESPONSE=$(curl -s -X GET "$BASE_URL/jobs/$JOB_ID/files/?file_type=Photo" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

  echo "Response:"
  echo $FILE_TYPE_FILTER_RESPONSE | python3 -m json.tool 2>/dev/null || echo $FILE_TYPE_FILTER_RESPONSE
  echo ""

  # Step 10: Create a third file entry (Drawing)
  echo "10. POST /jobs/$JOB_ID/files - Create third file entry (Drawing)"
  CREATE3_PAYLOAD='{
    "file_name": "shower_design.dwg",
    "file_type": "Drawing",
    "file_size": 1048576,
    "file_path": "/storage/jobs/5/drawings/shower_design.dwg",
    "thumbnail_path": "/storage/jobs/5/drawings/thumbs/shower_design_thumb.jpg",
    "description": "CAD drawing of shower enclosure",
    "tags": ["drawing", "cad", "shower"]
  }'

  CREATE3_RESPONSE=$(curl -s -X POST "$BASE_URL/jobs/$JOB_ID/files/" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d "$CREATE3_PAYLOAD")

  FILE3_ID=$(echo $CREATE3_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['file_id'])" 2>/dev/null)

  if [ -z "$FILE3_ID" ]; then
    echo "❌ Third file entry creation failed"
  else
    echo "✅ Third file entry created with ID: $FILE3_ID"
  fi
  echo ""

  # Step 11: Update third file entry
  echo "11. PUT /jobs/$JOB_ID/files/$FILE3_ID - Update drawing description"
  UPDATE3_RESPONSE=$(curl -s -X PUT "$BASE_URL/jobs/$JOB_ID/files/$FILE3_ID" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
      "description": "Final approved CAD drawing of shower enclosure"
    }')

  echo "Response:"
  echo $UPDATE3_RESPONSE | python3 -m json.tool 2>/dev/null || echo $UPDATE3_RESPONSE
  echo ""

  # Step 12: Create a fourth file entry (Video)
  echo "12. POST /jobs/$JOB_ID/files - Create fourth file entry (Video)"
  CREATE4_PAYLOAD='{
    "file_name": "installation_walkthrough.mp4",
    "file_type": "Video",
    "file_size": 10485760,
    "file_path": "/storage/jobs/5/videos/installation_walkthrough.mp4",
    "thumbnail_path": "/storage/jobs/5/videos/thumbs/installation_walkthrough_thumb.jpg",
    "description": "Video walkthrough of completed installation",
    "tags": ["video", "installation", "walkthrough"]
  }'

  CREATE4_RESPONSE=$(curl -s -X POST "$BASE_URL/jobs/$JOB_ID/files/" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d "$CREATE4_PAYLOAD")

  FILE4_ID=$(echo $CREATE4_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['file_id'])" 2>/dev/null)

  if [ -z "$FILE4_ID" ]; then
    echo "❌ Fourth file entry creation failed"
  else
    echo "✅ Fourth file entry created with ID: $FILE4_ID"
  fi
  echo ""

  # Step 13: Get all files (should show 4)
  echo "13. GET /jobs/$JOB_ID/files - List all files (should show 4)"
  GET_ALL_FINAL_RESPONSE=$(curl -s -X GET "$BASE_URL/jobs/$JOB_ID/files/" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

  FILE_COUNT=$(echo $GET_ALL_FINAL_RESPONSE | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data))" 2>/dev/null)

  if [ "$FILE_COUNT" = "4" ]; then
    echo "✅ All 4 files listed correctly"
  else
    echo "❌ Expected 4 files, got $FILE_COUNT"
  fi
  echo ""

  # Step 14: Delete first file entry
  echo "14. DELETE /jobs/$JOB_ID/files/$FILE_ID - Delete file entry"
  DELETE_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X DELETE "$BASE_URL/jobs/$JOB_ID/files/$FILE_ID" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

  HTTP_STATUS=$(echo "$DELETE_RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)

  if [ "$HTTP_STATUS" = "204" ]; then
    echo "✅ File entry deleted (HTTP 204)"
  else
    echo "❌ Delete failed (HTTP $HTTP_STATUS)"
    echo "$DELETE_RESPONSE"
  fi
  echo ""

  # Step 15: Try to get deleted file (should return 404)
  echo "15. GET /jobs/$JOB_ID/files/$FILE_ID - Try to get deleted file (should 404)"
  GET_DELETED_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X GET "$BASE_URL/jobs/$JOB_ID/files/$FILE_ID" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

  HTTP_STATUS=$(echo "$GET_DELETED_RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)

  if [ "$HTTP_STATUS" = "404" ]; then
    echo "✅ Correctly returns 404 for deleted file"
  else
    echo "❌ Should return 404 (got HTTP $HTTP_STATUS)"
    echo "$GET_DELETED_RESPONSE"
  fi
  echo ""

  # Step 16: Delete second file entry (cleanup)
  if [ -n "$FILE2_ID" ]; then
    echo "16. DELETE /jobs/$JOB_ID/files/$FILE2_ID - Delete second file (cleanup)"
    DELETE2_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X DELETE "$BASE_URL/jobs/$JOB_ID/files/$FILE2_ID" \
      -H "Authorization: Bearer $ACCESS_TOKEN")

    HTTP_STATUS=$(echo "$DELETE2_RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)

    if [ "$HTTP_STATUS" = "204" ]; then
      echo "✅ Second file deleted (HTTP 204)"
    else
      echo "❌ Delete failed (HTTP $HTTP_STATUS)"
      echo "$DELETE2_RESPONSE"
    fi
    echo ""
  fi

  # Step 17: Delete third file entry (cleanup)
  if [ -n "$FILE3_ID" ]; then
    echo "17. DELETE /jobs/$JOB_ID/files/$FILE3_ID - Delete third file (cleanup)"
    DELETE3_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X DELETE "$BASE_URL/jobs/$JOB_ID/files/$FILE3_ID" \
      -H "Authorization: Bearer $ACCESS_TOKEN")

    HTTP_STATUS=$(echo "$DELETE3_RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)

    if [ "$HTTP_STATUS" = "204" ]; then
      echo "✅ Third file deleted (HTTP 204)"
    else
      echo "❌ Delete failed (HTTP $HTTP_STATUS)"
      echo "$DELETE3_RESPONSE"
    fi
    echo ""
  fi

  # Step 18: Delete fourth file entry (cleanup)
  if [ -n "$FILE4_ID" ]; then
    echo "18. DELETE /jobs/$JOB_ID/files/$FILE4_ID - Delete fourth file (cleanup)"
    DELETE4_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X DELETE "$BASE_URL/jobs/$JOB_ID/files/$FILE4_ID" \
      -H "Authorization: Bearer $ACCESS_TOKEN")

    HTTP_STATUS=$(echo "$DELETE4_RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)

    if [ "$HTTP_STATUS" = "204" ]; then
      echo "✅ Fourth file deleted (HTTP 204)"
    else
      echo "❌ Delete failed (HTTP $HTTP_STATUS)"
      echo "$DELETE4_RESPONSE"
    fi
    echo ""
  fi

  # Step 19: Verify all files are deleted (list should be empty)
  echo "19. GET /jobs/$JOB_ID/files - Verify all files deleted (should be empty)"
  FINAL_LIST_RESPONSE=$(curl -s -X GET "$BASE_URL/jobs/$JOB_ID/files/" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

  FINAL_COUNT=$(echo $FINAL_LIST_RESPONSE | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data))" 2>/dev/null)

  if [ "$FINAL_COUNT" = "0" ]; then
    echo "✅ All files successfully deleted (list is empty)"
  else
    echo "⚠️  Expected 0 files, got $FINAL_COUNT (may have pre-existing files)"
  fi
  echo ""
fi

echo ""
echo "================================================"
echo "Job Files Endpoints Test Complete"
echo "================================================"
