#!/bin/bash

API_URL="http://localhost:8080"
ACCOUNT_NAME="test_user_$(date +%s)"
PASSWORD="secret123"

echo "Test 1: Register new user $ACCOUNT_NAME"
response=$(curl -s -X POST "$API_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"account_name\": \"$ACCOUNT_NAME\", \"password\": \"$PASSWORD\"}")

echo "Register response:"
echo "$response"

status=$(echo "$response" | jq -r '.status')
if [ "$status" != "success" ]; then
  echo "Test failed: User registration should succeed"
  exit 1
fi

echo ""
echo "Test 2: Login with correct password"
response=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"account_name\": \"$ACCOUNT_NAME\", \"password\": \"$PASSWORD\"}")

echo "Login response:"
echo "$response"

token=$(echo "$response" | jq -r '.access_token')
if [ "$token" == "null" ]; then
  echo "Test failed: Login should return a valid access_token"
  exit 1
fi

echo ""
echo "Test 3: Login with incorrect password"
response=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"account_name\": \"$ACCOUNT_NAME\", \"password\": \"wrongpass\"}")

echo "Login (wrong password) response:"
echo "$response"

status=$(echo "$response" | jq -r '.status')
if [ "$status" == "success" ]; then
  echo "Test failed: Login with wrong password should not succeed"
  exit 1
fi

echo ""
echo "All auth tests passed."
