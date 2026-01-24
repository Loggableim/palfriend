#!/bin/bash
# Build PalFriend Launcher Executable
# This script builds the launcher executable using PyInstaller

echo "=================================="
echo "PalFriend Launcher Builder"
echo "=================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3.12 from https://www.python.org/"
    exit 1
fi

# Check Python version and warn if >= 3.13
python3 -c "import sys; exit(0 if sys.version_info[:2] < (3, 13) else 1)" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "=================================="
    echo "ERROR: Unsupported Python Version"
    echo "=================================="
    echo ""
    python3 --version
    echo ""
    echo "This build requires Python 3.12.x or 3.11.x"
    echo "Python 3.13 and newer are NOT supported by PyInstaller and required dependencies."
    echo ""
    echo "Please install Python 3.12.x from https://www.python.org/downloads/"
    echo ""
    exit 1
fi

echo "Python version check:"
python3 --version
echo ""

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip is not installed"
    exit 1
fi

echo "Installing PyInstaller..."
pip3 install -q "pyinstaller>=6.0.0,<7.0.0"

# Check if Node.js is installed (for frontend build)
if ! command -v node &> /dev/null; then
    echo "Warning: Node.js is not installed"
    echo "Frontend build will be skipped. The launcher will work but web interface may not."
    echo "To install Node.js, visit https://nodejs.org/"
    echo ""
else
    # Build frontend if it doesn't exist
    if [ ! -d "frontend/build" ]; then
        echo "Building React frontend..."
        cd frontend
        if [ ! -d "node_modules" ]; then
            echo "Installing Node.js dependencies..."
            npm install
        fi
        echo "Running frontend build..."
        npm run build
        if [ $? -ne 0 ]; then
            echo "Warning: Frontend build failed"
            echo "The launcher will be built but web interface may not work properly."
        fi
        cd ..
    else
        echo "Frontend build already exists, skipping..."
    fi
fi

echo ""
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

echo ""
echo "Building executable with PyInstaller..."
echo "This may take several minutes..."
echo ""

# Clean previous build
rm -rf build dist

# Build using spec file
pyinstaller --noconfirm palfriend-launcher.spec

if [ $? -ne 0 ]; then
    echo ""
    echo "=================================="
    echo "Build FAILED"
    echo "=================================="
    echo "Please check the error messages above."
    exit 1
fi

echo ""
echo "=================================="
echo "Build SUCCESSFUL"
echo "=================================="
echo ""
echo "Executable created at: dist/palfriend-launcher"
echo ""
echo "You can now run the launcher by executing: ./dist/palfriend-launcher"
echo ""
