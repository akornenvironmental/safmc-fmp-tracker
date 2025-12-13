#!/bin/bash

# SAFMC FMP Tracker - Development Server Startup Script
# This script helps you start both backend and frontend servers

set -e  # Exit on error

echo "🚀 Starting SAFMC FMP Tracker Development Environment"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if PostgreSQL is running
echo -e "${BLUE}Checking PostgreSQL...${NC}"
if ! command -v psql &> /dev/null; then
    echo -e "${RED}✗ PostgreSQL not found!${NC}"
    echo -e "${YELLOW}Please install PostgreSQL first:${NC}"
    echo "  brew install postgresql@15"
    echo "  brew services start postgresql@15"
    echo ""
    echo "Or download Postgres.app: https://postgresapp.com/"
    exit 1
fi

# Check if database exists
if psql -lqt | cut -d \| -f 1 | grep -qw safmc_fmp_tracker; then
    echo -e "${GREEN}✓ Database 'safmc_fmp_tracker' exists${NC}"
else
    echo -e "${YELLOW}! Database 'safmc_fmp_tracker' not found${NC}"
    echo "Creating database..."
    createdb safmc_fmp_tracker || {
        echo -e "${RED}✗ Failed to create database${NC}"
        echo "Try running manually: createdb safmc_fmp_tracker"
        exit 1
    }
    echo -e "${GREEN}✓ Database created${NC}"
fi

# Check for virtual environment
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}! Virtual environment not found${NC}"
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import flask" 2>/dev/null; then
    echo -e "${YELLOW}! Installing Python dependencies...${NC}"
    pip install -r requirements.txt
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${GREEN}✓ Python dependencies installed${NC}"
fi

# Check for .env file
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}! .env file not found${NC}"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo -e "${GREEN}✓ .env file created${NC}"
    echo -e "${YELLOW}⚠ Please edit .env with your configuration${NC}"
fi

# Check if frontend dependencies are installed
echo -e "${BLUE}Checking frontend dependencies...${NC}"
if [ ! -d "client/node_modules" ]; then
    echo -e "${YELLOW}! Installing frontend dependencies...${NC}"
    cd client
    npm install
    cd ..
    echo -e "${GREEN}✓ Frontend dependencies installed${NC}"
else
    echo -e "${GREEN}✓ Frontend dependencies installed${NC}"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ Environment setup complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Starting development servers..."
echo ""
echo -e "${BLUE}Backend will run on:${NC}  http://localhost:5000"
echo -e "${BLUE}Frontend will run on:${NC} http://localhost:5173"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all servers${NC}"
echo ""

# Function to cleanup background jobs on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down servers...${NC}"
    jobs -p | xargs -r kill
    exit 0
}

trap cleanup INT TERM

# Start backend in background
echo -e "${BLUE}Starting Flask backend...${NC}"
python app.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend in background
echo -e "${BLUE}Starting React frontend...${NC}"
cd client
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}🎉 Development servers are running!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "Open your browser to: ${BLUE}http://localhost:5173${NC}"
echo ""
echo -e "To stop: Press ${YELLOW}Ctrl+C${NC}"
echo ""

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
