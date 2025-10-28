#!/bin/bash

# Production start script
set -e

echo "🚀 Starting Romantic AI Proposal in Production Mode"

# Start backend in background
cd backend
python app.py &
BACKEND_PID=$!

# Start frontend
cd ../frontend
PORT=3000 npm start &
FRONTEND_PID=$!

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID