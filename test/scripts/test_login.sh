#!/bin/bash
set -e

BASE_URL="http://localhost:8000/api/auth"

echo "=== Setting up test user ==="
# Register a test user first
curl -s -X POST "${BASE_URL}/register/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "TestPass123"
  }' | jq .

echo ""
echo "=== Test 1: Successful login ==="
curl -s -X POST "${BASE_URL}/login/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "TestPass123"
  }' | jq .

echo ""
echo "=== Test 2: Invalid password ==="
curl -s -X POST "${BASE_URL}/login/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "wrongpassword"
  }' | jq .

echo ""
echo "=== Test 3: Non-existent user ==="
curl -s -X POST "${BASE_URL}/login/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "nonexistent@example.com",
    "password": "SomePass123"
  }' | jq .

echo ""
echo "=== Test 4: Missing email ==="
curl -s -X POST "${BASE_URL}/login/" \
  -H "Content-Type: application/json" \
  -d '{
    "password": "TestPass123"
  }' | jq .

echo ""
echo "=== Test 5: Missing password ==="
curl -s -X POST "${BASE_URL}/login/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com"
  }' | jq .

echo ""
echo "All tests completed!"