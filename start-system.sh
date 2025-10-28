#!/bin/bash

# Start Complete System Script
set -e

echo "🚀 Starting Complete Romantic AI Proposal System..."

# Check if setup has been run
if [ ! -f .env ]; then
    echo "❌ .env file not found. Run ./setup.sh first."
    exit 1
fi

if [ ! -d "backend/venv" ]; then
    echo "❌ Backend virtual environment not found. Run ./setup.sh first."
    exit 1
fi

if [ ! -d "frontend/node_modules" ]; then
    echo "❌ Frontend dependencies not found. Run ./setup.sh first."
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Set default ports
BACKEND_PORT=${BACKEND_PORT:-5000}
FRONTEND_PORT=${FRONTEND_PORT:-3000}

echo "🔧 Backend will run on: http://localhost:$BACKEND_PORT"
echo "🎨 Frontend will run on: http://localhost:$FRONTEND_PORT"
echo ""
echo "Starting both servers..."
echo "Press Ctrl+C to stop both servers"
echo ""

# Function to kill background processes on exit
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    exit 0
}

# Set trap to cleanup on exit
trap cleanup SIGINT SIGTERM

# Start backend in background
./start-backend.sh &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend in background
./start-frontend.sh &
FRONTEND_PID=$!

# Wait for both processes
wait