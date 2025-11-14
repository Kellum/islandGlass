#!/bin/bash

# Material Templates CRUD Endpoint Test Script
# Tests all material template endpoints with proper authentication

BASE_URL="http://localhost:8000/api/v1"
EMAIL="ry@islandglassandmirror.com"
PASSWORD="Asdfghj123!@"

echo "=========================================="
echo "FastAPI Material Templates Endpoints Test"
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

# Step 2: Get all material templates (should show existing or empty)
echo "2. GET /material-templates - List all templates"
GET_ALL_RESPONSE=$(curl -s -X GET "$BASE_URL/material-templates/" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "Response:"
echo $GET_ALL_RESPONSE | python3 -m json.tool 2>/dev/null || echo $GET_ALL_RESPONSE
echo ""

# Step 3: Create a new material template
echo "3. POST /material-templates - Create new template"
CREATE_RESPONSE=$(curl -s -X POST "$BASE_URL/material-templates/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "template_name": "Test Clear Glass 1/4 inch",
    "category": "Glass",
    "description": "Standard clear float glass, 1/4 inch thickness",
    "is_active": true,
    "sort_order": 10
  }')

echo "Response:"
echo $CREATE_RESPONSE | python3 -m json.tool 2>/dev/null || echo $CREATE_RESPONSE

# Extract template ID from response
TEMPLATE_ID=$(echo $CREATE_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['template_id'])" 2>/dev/null)

if [ -z "$TEMPLATE_ID" ]; then
  echo "❌ Template creation failed"
  echo ""
else
  echo "✅ Template created with ID: $TEMPLATE_ID"
  echo ""

  # Step 4: Get template by ID
  echo "4. GET /material-templates/$TEMPLATE_ID - Get template details"
  GET_ONE_RESPONSE=$(curl -s -X GET "$BASE_URL/material-templates/$TEMPLATE_ID" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

  echo "Response:"
  echo $GET_ONE_RESPONSE | python3 -m json.tool 2>/dev/null || echo $GET_ONE_RESPONSE
  echo ""

  # Step 5: Update template
  echo "5. PUT /material-templates/$TEMPLATE_ID - Update template"
  UPDATE_RESPONSE=$(curl -s -X PUT "$BASE_URL/material-templates/$TEMPLATE_ID" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
      "template_name": "Test Clear Glass 1/4 inch (UPDATED)",
      "description": "Updated: Standard clear float glass",
      "sort_order": 20
    }')

  echo "Response:"
  echo $UPDATE_RESPONSE | python3 -m json.tool 2>/dev/null || echo $UPDATE_RESPONSE
  echo ""

  # Step 6: Filter by category
  echo "6. GET /material-templates?category=Glass - Filter by category"
  FILTER_RESPONSE=$(curl -s -X GET "$BASE_URL/material-templates/?category=Glass" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

  echo "Response:"
  echo $FILTER_RESPONSE | python3 -m json.tool 2>/dev/null || echo $FILTER_RESPONSE
  echo ""

  # Step 7: Get all templates again (should show updated template)
  echo "7. GET /material-templates - List all templates (after update)"
  GET_ALL_AFTER_RESPONSE=$(curl -s -X GET "$BASE_URL/material-templates/" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

  echo "Response:"
  echo $GET_ALL_AFTER_RESPONSE | python3 -m json.tool 2>/dev/null || echo $GET_ALL_AFTER_RESPONSE
  echo ""

  # Step 8: Delete template (hard delete)
  echo "8. DELETE /material-templates/$TEMPLATE_ID - Delete template"
  DELETE_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X DELETE "$BASE_URL/material-templates/$TEMPLATE_ID" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

  HTTP_STATUS=$(echo "$DELETE_RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)

  if [ "$HTTP_STATUS" = "204" ]; then
    echo "✅ Template deleted (HTTP 204)"
  else
    echo "❌ Delete failed (HTTP $HTTP_STATUS)"
    echo "$DELETE_RESPONSE"
  fi
  echo ""

  # Step 9: Try to get deleted template (should return 404)
  echo "9. GET /material-templates/$TEMPLATE_ID - Try to get deleted template (should 404)"
  GET_DELETED_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X GET "$BASE_URL/material-templates/$TEMPLATE_ID" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

  HTTP_STATUS=$(echo "$GET_DELETED_RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)

  if [ "$HTTP_STATUS" = "404" ]; then
    echo "✅ Correctly returns 404 for deleted template"
  else
    echo "❌ Should return 404 (got HTTP $HTTP_STATUS)"
    echo "$GET_DELETED_RESPONSE"
  fi
  echo ""
fi

echo ""
echo "=========================================="
echo "Material Templates Endpoints Test Complete"
echo "=========================================="
