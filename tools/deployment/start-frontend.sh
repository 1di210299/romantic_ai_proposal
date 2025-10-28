#!/bin/bash

# Start Frontend Server Script
set -e

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

echo "🎨 Starting Romantic AI Proposal Frontend..."

# Navigate to frontend directory
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "❌ node_modules not found. Run ./setup.sh first."
    exit 1
fi

# Set default port if not specified
if [ -z "$FRONTEND_PORT" ]; then
    export FRONTEND_PORT=3000
fi

# Set backend URL for the frontend
if [ -z "$BACKEND_URL" ]; then
    export NEXT_PUBLIC_BACKEND_URL=http://localhost:5000
else
    export NEXT_PUBLIC_BACKEND_URL=$BACKEND_URL
fi

echo "🚀 Starting Next.js server on port $FRONTEND_PORT..."
echo "🔗 Frontend URL: http://localhost:$FRONTEND_PORT"
echo "🔗 Backend URL: $NEXT_PUBLIC_BACKEND_URL"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the Next.js application
npm start -- -p $FRONTEND_PORT