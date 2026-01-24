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
    echo Please install Python 3.8 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo Checking Python dependencies...
pip install -q pyinstaller

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

REM Build using spec file
pyinstaller --noconfirm palfriend-launcher.spec

if errorlevel 1 (
    echo.
    echo ==================================
    echo Build FAILED
    echo ==================================
    echo Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo ==================================
echo Build SUCCESSFUL
echo ==================================
echo.
echo Executable created at: dist\palfriend-launcher.exe
echo.
echo You can now run the launcher by double-clicking the .exe file
echo or by running: dist\palfriend-launcher.exe
echo.

pause
