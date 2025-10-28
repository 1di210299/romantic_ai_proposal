#!/bin/bash

# Secure Credentials Setup Script
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

echo "🔐 Secure Credentials Setup for Romantic AI Proposal System"
echo "==========================================================="

# Check if .env already exists
if [ -f .env ]; then
    print_warning ".env file already exists."
    read -p "Do you want to overwrite it? (y/N): " overwrite
    if [ "$overwrite" != "y" ] && [ "$overwrite" != "Y" ]; then
        echo "Exiting without changes."
        exit 0
    fi
fi

# Create .env file
print_status "Creating .env file..."

echo "# Romantic AI Proposal System - Environment Configuration" > .env
echo "# Generated on $(date)" >> .env
echo "" >> .env

# OpenAI API Key
echo "🤖 OpenAI Configuration"
echo "======================="
echo "You need an OpenAI API key to use this system."
echo "1. Go to https://platform.openai.com/api-keys"
echo "2. Create a new API key"
echo "3. Copy the key (it starts with 'sk-')"
echo ""
read -p "Enter your OpenAI API key: " openai_key

if [ -z "$openai_key" ]; then
    print_error "OpenAI API key is required!"
    exit 1
fi

if [[ ! $openai_key =~ ^sk- ]]; then
    print_warning "API key doesn't start with 'sk-'. Are you sure it's correct?"
    read -p "Continue anyway? (y/N): " confirm
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        exit 1
    fi
fi

echo "OPENAI_API_KEY=$openai_key" >> .env
print_success "OpenAI API key configured"

# Secret Key
echo ""
echo "🔑 Flask Secret Key"
echo "=================="
echo "Generating a secure secret key..."
secret_key=$(openssl rand -hex 32 2>/dev/null || python3 -c "import secrets; print(secrets.token_hex(32))" 2>/dev/null || echo "$(date +%s)-$(whoami)-secret-key-change-this")
echo "SECRET_KEY=$secret_key" >> .env
print_success "Secret key configured"

# Flask Environment
echo "" >> .env
echo "# Flask Configuration" >> .env
echo "FLASK_DEBUG=False" >> .env
echo "FLASK_ENV=production" >> .env

# Paths
echo "" >> .env
echo "# Data Configuration" >> .env
echo "CONVERSATION_DATA_PATH=../karemramos_1184297046409691" >> .env

# Ports
echo "" >> .env
echo "# Port Configuration" >> .env
echo "BACKEND_PORT=5000" >> .env
echo "FRONTEND_PORT=3000" >> .env

# URLs
echo "" >> .env
echo "# URL Configuration" >> .env
echo "BACKEND_URL=http://localhost:5000" >> .env
echo "FRONTEND_URL=http://localhost:3000" >> .env

# CORS
echo "" >> .env
echo "# Security Configuration" >> .env
echo "CORS_ORIGINS=http://localhost:3000,https://yourdomain.com" >> .env

print_success "✅ .env file created successfully!"

# Set secure permissions
chmod 600 .env
print_success "✅ Secure permissions set on .env file"

# Verify configuration
echo ""
echo "🔍 Configuration Summary"
echo "======================="
echo "✅ OpenAI API Key: ${openai_key:0:7}..."
echo "✅ Secret Key: Generated (32 bytes)"
echo "✅ Environment: Production"
echo "✅ Backend Port: 5000"
echo "✅ Frontend Port: 3000"

# Test OpenAI connection
echo ""
print_status "Testing OpenAI connection..."
python3 -c "
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
try:
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    models = client.models.list()
    print('✅ OpenAI connection successful!')
    print(f'✅ Available models: {len(models.data)} models found')
except Exception as e:
    print(f'❌ OpenAI connection failed: {e}')
    print('Please check your API key and try again.')
" 2>/dev/null || print_warning "Could not test OpenAI connection (missing dependencies)"

echo ""
print_success "🎉 Credentials setup complete!"
print_status "You can now run the system with: ./start-system.sh"
print_warning "Keep your .env file secure and never commit it to version control!"

# Add .env to .gitignore if it exists
if [ -f .gitignore ]; then
    if ! grep -q "^\.env$" .gitignore; then
        echo ".env" >> .gitignore
        print_success "✅ Added .env to .gitignore"
    fi
else
    echo ".env" > .gitignore
    print_success "✅ Created .gitignore with .env"
fi