#!/bin/bash
set -ex  # -e exit on error, -x print commands as they execute

echo "================================================"
echo "=== SAFMC FMP Tracker Build Script ==="
echo "================================================"
echo "Working directory: $(pwd)"
echo "Files in working directory:"
ls -la

echo ""
echo "=== Installing Python dependencies ==="
pip install --user -r requirements.txt

echo ""
echo "=== Building React app ==="
echo "Checking if client directory exists..."
if [ -d "client" ]; then
  echo "✓ client directory found"
  cd client
  echo "Current directory: $(pwd)"
  echo "Files in client directory:"
  ls -la

  echo ""
  echo "=== Installing npm dependencies ==="
  npm install

  echo ""
  echo "=== Running npm build ==="
  npm run build

  echo ""
  echo "=== Checking build output ==="
  if [ -d "dist" ]; then
    echo "✓ Build successful! Contents of dist:"
    ls -la dist/
    echo "dist/index.html exists: $([ -f dist/index.html ] && echo 'YES' || echo 'NO')"
  else
    echo "✗ Build failed! dist folder not created"
    exit 1
  fi

  cd ..
else
  echo "✗ ERROR: client directory not found!"
  echo "Available directories:"
  ls -la
  exit 1
fi

echo ""
echo "=== Setting permissions ==="
chmod +x start.sh

echo ""
echo "================================================"
echo "=== Build complete ==="
echo "================================================"
