#!/bin/bash
set -e

echo "=== Installing Python dependencies ==="
pip install -r requirements.txt

echo "=== Building React app ==="
cd client
echo "Current directory: $(pwd)"
echo "Files in client directory:"
ls -la

echo "=== Installing npm dependencies ==="
npm install

echo "=== Running npm build ==="
npm run build

echo "=== Checking build output ==="
if [ -d "dist" ]; then
  echo "✓ Build successful! Contents of dist:"
  ls -la dist/
else
  echo "✗ Build failed! dist folder not created"
  exit 1
fi

cd ..
chmod +x start.sh
echo "=== Build complete ==="
