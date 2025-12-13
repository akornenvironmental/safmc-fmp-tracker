#!/bin/bash

# Simplified manual startup script
# Opens two terminal windows for backend and frontend

echo "🚀 SAFMC FMP Tracker - Manual Startup"
echo ""
echo "This will open 2 terminal windows:"
echo "  1. Backend (Flask) - Port 5000"
echo "  2. Frontend (React) - Port 5173"
echo ""
echo "Press Enter to continue..."
read

# Backend terminal
osascript <<EOF
tell application "Terminal"
    do script "cd '$PWD' && source venv/bin/activate && echo '🔧 Starting Backend Server...' && python app.py"
    activate
end tell
EOF

# Wait a moment
sleep 2

# Frontend terminal
osascript <<EOF
tell application "Terminal"
    do script "cd '$PWD/client' && echo '🎨 Starting Frontend Server...' && npm run dev"
end tell
EOF

echo ""
echo "✓ Terminal windows opened!"
echo ""
echo "Check the terminal windows for server status."
echo "Once both are running, open: http://localhost:5173"
echo ""
echo "To stop: Press Ctrl+C in each terminal window"
