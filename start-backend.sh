#!/bin/bash

# Start Backend Server Script
set -e

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

echo "🔧 Starting Romantic AI Proposal Backend..."

# Navigate to backend directory
cd backend

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found. Run ./setup.sh first."
    exit 1
fi

# Check if OpenAI API key is set
if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "your_openai_api_key_here" ]; then
    echo "❌ OPENAI_API_KEY not set in .env file"
    echo "Please set your OpenAI API key in the .env file"
    exit 1
fi

# Set default port if not specified
if [ -z "$BACKEND_PORT" ]; then
    export BACKEND_PORT=5000
fi

echo "🚀 Starting Flask server on port $BACKEND_PORT..."
echo "🔑 OpenAI API Key: ${OPENAI_API_KEY:0:7}..."
echo "📂 Backend URL: http://localhost:$BACKEND_PORT"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the Flask application with production settings
python app.py