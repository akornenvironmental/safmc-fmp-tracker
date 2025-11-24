#!/bin/bash

# Script to trigger comprehensive amendment scraping on production
# This will populate the database with ~215 historical amendments from 2018-present

echo "🔍 Triggering comprehensive amendment scrape on production..."
echo "This will take 10-15 minutes to complete."
echo ""

# Get auth token from user
read -p "Enter your auth token (from localStorage): " AUTH_TOKEN

if [ -z "$AUTH_TOKEN" ]; then
    echo "❌ Error: Auth token required"
    exit 1
fi

echo ""
echo "Starting scrape..."
echo ""

# Trigger the comprehensive scrape endpoint
curl -X POST https://safmc-fmp-tracker.onrender.com/api/scrape/amendments/comprehensive \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -v

echo ""
echo ""
echo "✅ Scrape request sent!"
echo ""
echo "Check the logs at: https://safmc-fmp-tracker.onrender.com/api/logs/scrape?limit=1"
