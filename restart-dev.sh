#!/bin/bash
# Quick restart script for development servers

echo "🔄 Restarting Development Servers..."

# Kill existing servers
echo "Stopping existing servers..."
/usr/sbin/lsof -ti:5001 | xargs kill -9 2>/dev/null || true
/usr/sbin/lsof -ti:5174 | xargs kill -9 2>/dev/null || true
sleep 2

# Start backend
echo "🔧 Starting backend on port 5001..."
export PATH="/opt/homebrew/opt/postgresql@15/bin:/usr/bin:/bin:$PATH"
source venv/bin/activate
python3 app.py &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Wait for backend to start
sleep 3

# Start frontend
echo "🎨 Starting frontend..."
cd client
npm run dev &
FRONTEND_PID=$!
cd ..
echo "Frontend PID: $FRONTEND_PID"

echo ""
echo "✅ Servers started!"
echo "   Backend:  http://localhost:5001"
echo "   Frontend: http://localhost:5174"
echo ""
echo "Press Ctrl+C to stop"

# Wait for both processes
wait
