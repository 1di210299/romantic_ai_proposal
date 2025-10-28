#!/bin/bash

# Romantic AI Proposal System - Complete Setup Script
# This script will set up the entire system for deployment

set -e

echo "🚀 Setting up Romantic AI Proposal System..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js 16 or higher."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    print_error "npm is not installed. Please install npm."
    exit 1
fi

print_status "Python version: $(python3 --version)"
print_status "Node.js version: $(node --version)"
print_status "npm version: $(npm --version)"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    print_warning ".env file not found. Creating from template..."
    cp .env.example .env
    print_warning "Please edit .env file with your actual credentials before continuing."
    read -p "Press Enter to continue after editing .env file..."
else
    print_success ".env file found."
fi

# Check if OPENAI_API_KEY is set
if ! grep -q "OPENAI_API_KEY=sk-" .env 2>/dev/null; then
    print_warning "OPENAI_API_KEY not properly set in .env file."
    echo "Please add your OpenAI API key to the .env file:"
    echo "OPENAI_API_KEY=sk-your-actual-api-key-here"
    read -p "Press Enter to continue after setting API key..."
fi

# Setup Backend
print_status "Setting up backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

print_success "Backend setup complete!"

# Go back to root directory
cd ..

# Setup Frontend
print_status "Setting up frontend..."
cd frontend

# Install Node.js dependencies
print_status "Installing Node.js dependencies..."
npm install

# Build the frontend
print_status "Building frontend for production..."
npm run build

print_success "Frontend setup complete!"

# Go back to root directory
cd ..

print_success "🎉 Complete setup finished!"
print_status "To start the system:"
print_status "1. Backend: ./start-backend.sh"
print_status "2. Frontend: ./start-frontend.sh"
print_status "3. Or use: ./start-system.sh (starts both)"