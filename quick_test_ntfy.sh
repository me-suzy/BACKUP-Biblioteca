#!/bin/bash
echo "Test manual simplu NTFY"

# Test cu argument direct
echo "=== TEST 1: Curl direct ==="
curl -s -X POST -d "Test direct curl" "http://ntfy.sh/bariasi-5f07b8571f7c"

# Test scriptul
echo ""
echo "=== TEST 2: Script NTFY ==="
echo "Test argument" | /usr/local/bin/ntfy_notify.sh "Test backend"

echo "Gata!"

