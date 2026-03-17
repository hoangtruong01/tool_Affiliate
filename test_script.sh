#!/bin/bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=admin123456" | jq -r .access_token)

echo "Got token: ${TOKEN:0:10}..."

curl -s -X POST "http://localhost:8000/api/v1/products/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
  "name": "Sample Product",
  "description": "An amazing sample product for testing",
  "source_url": "https://example.com/product",
  "category": "Technology"
}' | jq .
