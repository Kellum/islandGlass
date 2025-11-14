#!/bin/bash

# Vendor CRUD Endpoint Test Script
# Tests all vendor endpoints with proper authentication

BASE_URL="http://localhost:8000/api/v1"
EMAIL="ry@islandglassandmirror.com"
PASSWORD="Asdfghj123!@"

echo "=========================================="
echo "FastAPI Vendors Endpoints Test"
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

# Step 2: Get all vendors (should show existing or empty)
echo "2. GET /vendors - List all vendors"
GET_ALL_RESPONSE=$(curl -s -X GET "$BASE_URL/vendors/" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "Response:"
echo $GET_ALL_RESPONSE | python3 -m json.tool 2>/dev/null || echo $GET_ALL_RESPONSE
echo ""

# Step 3: Create a new vendor
echo "3. POST /vendors - Create new vendor"
CREATE_RESPONSE=$(curl -s -X POST "$BASE_URL/vendors/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "vendor_name": "Test Glass Supplier",
    "vendor_type": "Glass",
    "contact_person": "Jane Manager",
    "email": "jane@testglass.com",
    "phone": "555-1000",
    "address_line1": "789 Industrial Blvd",
    "city": "GlassCity",
    "state": "CA",
    "zip_code": "90210",
    "is_active": true,
    "notes": "Test vendor for glass supplies"
  }')

echo "Response:"
echo $CREATE_RESPONSE | python3 -m json.tool 2>/dev/null || echo $CREATE_RESPONSE

# Extract vendor ID from response
VENDOR_ID=$(echo $CREATE_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['vendor_id'])" 2>/dev/null)

if [ -z "$VENDOR_ID" ]; then
  echo "❌ Vendor creation failed"
  echo ""
else
  echo "✅ Vendor created with ID: $VENDOR_ID"
  echo ""

  # Step 4: Get vendor by ID
  echo "4. GET /vendors/$VENDOR_ID - Get vendor details"
  GET_ONE_RESPONSE=$(curl -s -X GET "$BASE_URL/vendors/$VENDOR_ID" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

  echo "Response:"
  echo $GET_ONE_RESPONSE | python3 -m json.tool 2>/dev/null || echo $GET_ONE_RESPONSE
  echo ""

  # Step 5: Update vendor
  echo "5. PUT /vendors/$VENDOR_ID - Update vendor"
  UPDATE_RESPONSE=$(curl -s -X PUT "$BASE_URL/vendors/$VENDOR_ID" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
      "vendor_name": "Test Glass Supplier (UPDATED)",
      "phone": "555-2000",
      "is_active": false
    }')

  echo "Response:"
  echo $UPDATE_RESPONSE | python3 -m json.tool 2>/dev/null || echo $UPDATE_RESPONSE
  echo ""

  # Step 6: Get all vendors again (should show updated vendor)
  echo "6. GET /vendors - List all vendors (after update)"
  GET_ALL_AFTER_RESPONSE=$(curl -s -X GET "$BASE_URL/vendors/" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

  echo "Response:"
  echo $GET_ALL_AFTER_RESPONSE | python3 -m json.tool 2>/dev/null || echo $GET_ALL_AFTER_RESPONSE
  echo ""

  # Step 7: Delete vendor (hard delete)
  echo "7. DELETE /vendors/$VENDOR_ID - Delete vendor (hard delete)"
  DELETE_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X DELETE "$BASE_URL/vendors/$VENDOR_ID" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

  HTTP_STATUS=$(echo "$DELETE_RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)

  if [ "$HTTP_STATUS" = "204" ]; then
    echo "✅ Vendor deleted (HTTP 204)"
  else
    echo "❌ Delete failed (HTTP $HTTP_STATUS)"
    echo "$DELETE_RESPONSE"
  fi
  echo ""

  # Step 8: Try to get deleted vendor (should return 404)
  echo "8. GET /vendors/$VENDOR_ID - Try to get deleted vendor (should 404)"
  GET_DELETED_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X GET "$BASE_URL/vendors/$VENDOR_ID" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

  HTTP_STATUS=$(echo "$GET_DELETED_RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)

  if [ "$HTTP_STATUS" = "404" ]; then
    echo "✅ Correctly returns 404 for deleted vendor"
  else
    echo "❌ Should return 404 (got HTTP $HTTP_STATUS)"
    echo "$GET_DELETED_RESPONSE"
  fi
  echo ""
fi

echo ""
echo "=========================================="
echo "Vendors Endpoints Test Complete"
echo "=========================================="
