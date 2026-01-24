@echo off
REM Build PalFriend Windows Launcher Executable
REM This script builds the Windows .exe file using PyInstaller

echo ==================================
echo PalFriend Launcher Builder
echo ==================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python 3 is not installed
    echo Please install Python 3.12 from https://www.python.org/
    pause
    exit /b 1
)

REM Check Python version and warn if >= 3.13
python -c "import sys; exit(0 if sys.version_info[:2] < (3, 13) else 1)" >nul 2>&1
if errorlevel 1 (
    echo ==================================
    echo ERROR: Unsupported Python Version
    echo ==================================
    echo.
    python --version
    echo.
    echo This build requires Python 3.12.x or 3.11.x
    echo Python 3.13 and newer are NOT supported by PyInstaller and required dependencies.
    echo.
    echo Please install Python 3.12.x from https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM Display Python version
echo Python version check:
python --version
echo.

echo Checking Python dependencies...
pip install -q "pyinstaller>=6.0.0,<7.0.0"

REM Check if Node.js is installed (for frontend build)
node --version >nul 2>&1
if errorlevel 1 (
    echo Warning: Node.js is not installed
    echo Frontend build will be skipped. The launcher will work but web interface may not.
    echo To install Node.js, visit https://nodejs.org/
    echo.
    goto skip_frontend
)

REM Build frontend if it doesn't exist
if not exist "frontend\build" (
    echo Building React frontend...
    cd frontend
    if not exist "node_modules" (
        echo Installing Node.js dependencies...
        call npm install
    )
    echo Running frontend build...
    call npm run build
    if errorlevel 1 (
        echo Warning: Frontend build failed
        echo The launcher will be built but web interface may not work properly.
    )
    cd ..
) else (
    echo Frontend build already exists, skipping...
)

:skip_frontend

echo.
echo Installing Python dependencies...
pip install -r requirements.txt

echo.
echo Building executable with PyInstaller...
echo This may take several minutes...
echo.

REM Clean previous build
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist

echo ==================================
echo Building Main Application (palfriend.exe)
echo ==================================
echo.

REM Build using spec file
pyinstaller --noconfirm palfriend.spec

if errorlevel 1 (
    echo.
    echo ==================================
    echo Build FAILED (palfriend.exe)
    echo ==================================
    echo Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo ✓ palfriend.exe built successfully
echo.

echo ==================================
echo Building Bootstrapper Launcher (palfriendlauncher.exe)
echo ==================================
echo.

REM Build bootstrapper
pyinstaller --noconfirm palfriendlauncher.spec

if errorlevel 1 (
    echo.
    echo ==================================
    echo Build FAILED (palfriendlauncher.exe)
    echo ==================================
    echo Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo ✓ palfriendlauncher.exe built successfully
echo.

echo.
echo ==================================
echo Build SUCCESSFUL
echo ==================================
echo.
echo Executables created:
echo   Main App:     dist\palfriend\palfriend.exe
echo   Launcher:     dist\palfriendlauncher.exe
echo.
echo To distribute:
echo   1. Use palfriendlauncher.exe as the installer/launcher
echo   2. Bundle dist\palfriend\ folder with it (or embed it)
echo.
echo You can test the launcher by running: dist\palfriendlauncher.exe
echo.

pause
