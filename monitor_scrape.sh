#!/bin/bash

# Script to trigger and monitor the comprehensive scraper
# Usage: ./monitor_scrape.sh

echo "=== SAFMC Comprehensive Scraper Monitor ==="
echo ""

# Get auth token from user
read -p "Enter your auth token (from localStorage): " AUTH_TOKEN

if [ -z "$AUTH_TOKEN" ]; then
    echo "❌ Error: Auth token required"
    exit 1
fi

echo ""
echo "🚀 Triggering comprehensive scraper..."
echo ""

# Trigger the scraper
RESPONSE=$(curl -s -X POST https://safmc-fmp-tracker.onrender.com/api/scrape/amendments/comprehensive \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -H "Content-Type: application/json")

echo "$RESPONSE" | /Library/Frameworks/Python.framework/Versions/3.14/bin/python3 -m json.tool

echo ""
echo "✅ Scraper started in background!"
echo ""
echo "⏳ Monitoring progress (checking every 30 seconds)..."
echo "   Scraper will take 10-15 minutes to complete."
echo "   Press Ctrl+C to stop monitoring (scraper will continue running)."
echo ""

# Monitor progress
COUNTER=0
while true; do
    sleep 30
    COUNTER=$((COUNTER + 1))

    # Check latest log
    LOG=$(curl -s "https://safmc-fmp-tracker.onrender.com/api/logs/scrape?source=amendments_comprehensive&limit=1")

    # Extract status using Python
    STATUS=$(echo "$LOG" | /Library/Frameworks/Python.framework/Versions/3.14/bin/python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if data and len(data) > 0:
        log = data[0]
        print(f\"Status: {log.get('status', 'unknown')} | Items: {log.get('items_found', 0)} found, {log.get('items_new', 0)} new | Duration: {log.get('duration_ms', 0)/1000:.1f}s\")
    else:
        print('No logs yet...')
except:
    print('Waiting for logs...')
" 2>/dev/null)

    echo "[$COUNTER] $STATUS"

    # Check if completed
    if echo "$LOG" | grep -q '"status":"success"' || echo "$LOG" | grep -q '"status":"partial"'; then
        echo ""
        echo "🎉 Scraper completed successfully!"
        echo ""
        echo "=== FINAL RESULTS ==="
        echo "$LOG" | /Library/Frameworks/Python.framework/Versions/3.14/bin/python3 -m json.tool
        break
    fi

    if echo "$LOG" | grep -q '"status":"error"'; then
        echo ""
        echo "❌ Scraper encountered an error!"
        echo ""
        echo "=== ERROR DETAILS ==="
        echo "$LOG" | /Library/Frameworks/Python.framework/Versions/3.14/bin/python3 -m json.tool
        break
    fi
done

echo ""
echo "✅ Monitoring complete!"
echo ""
