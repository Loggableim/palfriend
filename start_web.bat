@echo off
REM PalFriend Web Interface Startup Script for Windows

echo ==================================
echo PalFriend Web Interface
echo ==================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python 3 is not installed
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo Error: Node.js is not installed
    echo Please install Node.js 16+ from https://nodejs.org/
    pause
    exit /b 1
)

echo Installing Python dependencies...
pip install -q -r requirements.txt

echo Installing Node.js dependencies...
cd frontend
if not exist "node_modules" (
    call npm install
)

echo.
echo Building React frontend...
call npm run build

cd ..

echo.
echo ==================================
echo Starting PalFriend Web Interface
echo ==================================
echo.
echo Open your browser to: http://localhost:5008
echo.
echo Press Ctrl+C to stop the server
echo.

python app.py
