#!/usr/bin/env bash

# test_register.sh - Test user registration endpoint

echo "Testing registration endpoint..."
echo "================================"

# Test 1: Successful registration
echo -e "\n1. Testing successful registration:"
curl -s -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123",
    "first_name": "John",
    "last_name": "Doe"
  }' | python3 -m json.tool

# Test 2: Duplicate email
echo -e "\n2. Testing duplicate email (should fail):"
curl -s -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123"
  }' | python3 -m json.tool

# Test 3: Weak password
echo -e "\n3. Testing weak password (should fail):"
curl -s -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test2@example.com",
    "password": "weak"
  }' | python3 -m json.tool

# Test 4: Missing email
echo -e "\n4. Testing missing email (should fail):"
curl -s -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "password": "SecurePass123"
  }' | python3 -m json.tool

echo -e "\n================================"
echo "Tests completed"
