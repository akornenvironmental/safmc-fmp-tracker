#!/bin/bash
#
# Deploy Workplan System to Production
# 1. Push code to GitHub
# 2. Deploy to Render (will run migration automatically)
# 3. Import workplan file via API
#

set -e

echo "================================"
echo "DEPLOYING WORKPLAN SYSTEM"
echo "================================"

# Step 1: Commit and push code
echo ""
echo "Step 1: Pushing code to GitHub..."
git add -A
git commit -m "Add workplan integration system

- Database schema with version history
- Excel parser for workplan files
- Import service with fuzzy matching
- Models and migrations
- Updated requirements.txt with openpyxl
- Comprehensive documentation

🤖 Generated with Claude Code

Co-Authored-By: Claude <noreply@anthropic.com>"

git push origin main

echo "✓ Code pushed to GitHub"

# Step 2: Wait for Render deployment
echo ""
echo "Step 2: Waiting for Render deployment..."
echo "Checking deployment status..."

API_KEY='rnd_vD1FgQrqLyXTPZhMnLlYDSh94p5B'

# Trigger deploy
curl -X POST "https://api.render.com/v1/services/srv-d44gjqje5dus73f7ht90/deploys" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"clearCache":"clear"}' \
  > /dev/null 2>&1

echo "Deploy triggered. Monitoring..."

# Wait for deployment
for i in {1..30}; do
  echo "  Check $i/30..."

  # Check if backend is responding
  if curl -s https://safmc-fmp-tracker.onrender.com/api/actions?limit=1 | grep -q "success"; then
    echo "✓ Backend deployed and responding!"
    break
  fi

  sleep 10
done

# Step 3: Run migration via Python script on server
echo ""
echo "Step 3: Running migration on production database..."
echo ""
echo "To run the migration and import workplan, SSH into Render or use:"
echo ""
echo "  python3 import_workplan.py"
echo ""
echo "Or create an API endpoint to trigger it remotely."
echo ""

echo "================================"
echo "DEPLOYMENT COMPLETE"
echo "================================"
echo ""
echo "Next steps:"
echo "  1. Run migration: python3 import_workplan.py (on server)"
echo "  2. Or create API endpoint for workplan upload"
echo "  3. Build frontend UI"
echo ""
