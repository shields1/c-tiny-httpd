#!/bin/bash

set -e

URL="http://127.0.0.1:3490"

echo "Testing index..."

curl -fs "$URL/" > /dev/null

echo "Testing missing file..."

STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$URL/nope")

if [ "$STATUS" != "404" ]; then
    echo "Expected 404, got $STATUS"
    exit 1
fi

echo "All tests passed"