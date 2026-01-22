#!/bin/bash

# PalFriend Web Interface Startup Script

echo "=================================="
echo "PalFriend Web Interface"
echo "=================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed"
    echo "Please install Node.js 16+ from https://nodejs.org/"
    exit 1
fi

echo "Installing Python dependencies..."
pip install -q -r requirements.txt

echo "Installing Node.js dependencies..."
cd frontend
if [ ! -d "node_modules" ]; then
    npm install
fi

echo ""
echo "Building React frontend..."
npm run build

cd ..

echo ""
echo "=================================="
echo "Starting PalFriend Web Interface"
echo "=================================="
echo ""
echo "Open your browser to: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 app.py
