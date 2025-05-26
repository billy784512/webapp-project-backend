#!/bin/bash

API_URL="http://localhost:8080/match"

TMP1=$(mktemp)
TMP2=$(mktemp)

curl -s -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_1"}' > "$TMP1" &

sleep 5

curl -s -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_2"}' > "$TMP2" &

wait

echo "User 1 response:"
cat "$TMP1"
echo ""

echo "User 2 response:"
cat "$TMP2"
echo ""

ROOM1=$(jq -r '.room_id' "$TMP1")
ROOM2=$(jq -r '.room_id' "$TMP2")
rm "$TMP1" "$TMP2"


if [ "$ROOM1" == "null" ] || [ "$ROOM2" == "null" ]; then
  echo "Test failed: One of the responses does not contain a room_id"
  exit 1
fi

if [ "$ROOM1" != "$ROOM2" ]; then
  echo "Test failed: Room IDs do not match"
  echo "ROOM1: $ROOM1"
  echo "ROOM2: $ROOM2"
  exit 1
fi

echo "Test passed: Both users matched into room $ROOM1"
