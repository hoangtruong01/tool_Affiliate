#!/bin/sh
set -e

echo "Logging in..."
AUTH_RES=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=admin123456")
TOKEN=$(echo $AUTH_RES | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
echo "Token length: ${#TOKEN}"

echo "Creating product..."
PROD_RES=$(curl -s -X POST "http://localhost:8000/api/v1/products/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Validation Product", "description": "A great test product", "category": "Tech"}')
PROD_ID=$(echo $PROD_RES | grep -o '"id":"[^"]*' | cut -d'"' -f4)
echo "Created product ID: $PROD_ID"

echo "Creating dummy image..."
printf '\xff\xd8\xff\xe0\x00\x10\x4a\x46\x49\x46\x00\x01' > /tmp/dummy.jpg

echo "Uploading asset..."
ASSET_RES=$(curl -s -X POST "http://localhost:8000/api/v1/assets/" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/tmp/dummy.jpg;type=image/jpeg")
ASSET_ID=$(echo $ASSET_RES | grep -o '"id":"[^"]*' | cut -d'"' -f4)
echo "Uploaded asset ID: $ASSET_ID"

echo "Listing media/uploads directory:"
ls -la /app/media/uploads/
