#!/bin/bash

# BI Voice Agent Frontend - Setup Script
# This script automates the setup process

echo "=================================="
echo "BI Voice Agent Frontend Setup"
echo "=================================="
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null
then
    echo "❌ Node.js is not installed!"
    echo "Please install Node.js 16+ from https://nodejs.org/"
    exit 1
fi

echo "✅ Node.js version: $(node --version)"
echo "✅ npm version: $(npm --version)"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
npm install

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✅ Dependencies installed successfully!"
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOL
# Backend API Base URL
VITE_API_BASE_URL=http://127.0.0.1:8000

# Frontend Base URL (for email verification links)
VITE_FRONTEND_URL=http://localhost:5173
EOL
    echo "✅ .env file created!"
else
    echo "ℹ️  .env file already exists"
fi

echo ""
echo "=================================="
echo "✅ Setup Complete!"
echo "=================================="
echo ""
echo "🚀 To start the development server, run:"
echo "   npm run dev"
echo ""
echo "📱 The app will be available at:"
echo "   http://localhost:5173"
echo ""
echo "⚠️  Make sure the backend is running on:"
echo "   http://127.0.0.1:8000"
echo ""
echo "📚 For more information, see:"
echo "   - QUICK_START.md"
echo "   - FRONTEND_README.md"
echo ""

