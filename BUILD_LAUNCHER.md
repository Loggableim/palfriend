# Building the PalFriend Windows Launcher

This document explains how to build the PalFriend Windows launcher executables.

## Overview

The PalFriend build system now creates **two executables**:

1. **palfriendlauncher.exe** - A GUI bootstrapper/installer that:
   - Provides an easy-to-use installation interface
   - Checks system requirements (disk space, permissions)
   - Installs the main application
   - Validates installation integrity (SHA256)
   - Launches PalFriend after installation
   - Shows detailed logs and diagnostics

2. **palfriend.exe** - The main PalFriend application that:
   - Starts the PalFriend web interface automatically
   - Opens your default browser to the application
   - Bundles all Python dependencies (no Python installation required on target machine)
   - Includes the React frontend build

## Prerequisites

### For Building the Launcher

1. **Python 3.12.x** (REQUIRED - NOT 3.13 or newer)
   - Download from: https://www.python.org/downloads/
   - Make sure to check "Add Python to PATH" during installation
   - **Important**: Python 3.13+ is NOT supported by PyInstaller and required dependencies
   - Python 3.11.x also works, but 3.12.x is recommended

2. **Node.js 16 or higher** (for frontend build)
   - Download from: https://nodejs.org/
   - Required to build the React frontend

3. **PyInstaller 6.x**
   - Will be installed automatically by the build script
   - Or install manually: `pip install "pyinstaller>=6.0.0,<7.0.0"`

### For Running the Built Executables

The built executables require no prerequisites on the target Windows machine - everything is bundled!

## Building the Launcher

### Automated Build (Recommended)

#### On Windows:

Simply double-click or run:
```cmd
build_launcher.bat
```

This script will:
1. **Check Python version** (must be 3.11.x or 3.12.x)
2. Check for Python and Node.js
3. Install dependencies
4. Build the React frontend (if needed)
5. Create **palfriend.exe** (main application)
6. Create **palfriendlauncher.exe** (bootstrapper)
7. Place the results in `dist/` directory

#### On Linux/Mac:

```bash
chmod +x build_launcher.sh
./build_launcher.sh
```

### Manual Build

If you prefer to build manually or need more control:

1. **Verify Python version:**
   ```cmd
   python --version
   ```
   Must be 3.11.x or 3.12.x (NOT 3.13+)

2. **Install dependencies:**
   ```cmd
   pip install -r requirements.txt
   pip install "pyinstaller>=6.0.0,<7.0.0"
   ```

3. **Build the frontend (if not already built):**
   ```cmd
   cd frontend
   npm install
   npm run build
   cd ..
   ```

4. **Build palfriend.exe (main application):**
   ```cmd
   pyinstaller --noconfirm palfriend.spec
   ```

5. **Build palfriendlauncher.exe (bootstrapper):**
   ```cmd
   pyinstaller --noconfirm palfriendlauncher.spec
   ```

6. **Find your executables at:**
   ```
   dist/palfriend/palfriend.exe       (Main application - onedir format)
   dist/palfriendlauncher.exe         (Bootstrapper - onefile format)
   ```

## Build Configuration

The build is now configured via **two spec files**:

### palfriend.spec
- Entry point: `launcher.py`
- Includes all necessary Python modules
- Bundles the frontend build directory
- Includes example configuration files
- Optimizes the executable size with UPX compression
- Keeps the console window visible for logs
- **onedir** format for better stability and compatibility

### palfriendlauncher.spec  
- Entry point: `bootstrap_launcher.py`
- Minimal dependencies (just tkinter for GUI)
- **onefile** format for easy distribution
- No console window (pure GUI)
- Can optionally embed palfriend payload for offline installation

### Key Files

- **`bootstrap_launcher.py`** - GUI bootstrapper/installer
- **`launcher.py`** - Main entry point for palfriend.exe
- **`palfriend.spec`** - PyInstaller config for main app
- **`palfriendlauncher.spec`** - PyInstaller config for bootstrapper
- **`build_launcher.bat`** - Windows build script (builds both)
- **`build_launcher.sh`** - Linux/Mac build script (builds both)
- **`validate_build_system.py`** - Build validation script

## Troubleshooting

### Build Issues

**Problem**: Python version check fails with "Unsupported Python Version"

**Solution**: You must use Python 3.11.x or 3.12.x. Python 3.13+ is not supported.
```cmd
# Download Python 3.12.x from https://www.python.org/downloads/
# Uninstall Python 3.13+ if installed
# Install Python 3.12.x and verify:
python --version
```

**Problem**: `ModuleNotFoundError` during build

**Solution**: Install all requirements first:
```cmd
pip install -r requirements.txt
```

**Problem**: Frontend not included in executable

**Solution**: Make sure to build the frontend first:
```cmd
cd frontend
npm install
npm run build
cd ..
```

**Problem**: Build fails with PyInstaller errors

**Solution**: Ensure PyInstaller 6.x is installed (NOT 7.x):
```cmd
pip install "pyinstaller>=6.0.0,<7.0.0"
```

**Problem**: Executable is very large (>100 MB for palfriend.exe)

**Solution**: This is normal. The main executable includes:
- Python runtime
- All dependencies (Flask, OpenAI, ChromaDB, etc.)
- Frontend assets
- ML models

The bootstrapper (palfriendlauncher.exe) should be much smaller (~10-20 MB).

**Problem**: Build fails with "UPX not available"

**Solution**: This is just a warning. The executable will be larger but will work fine. To enable UPX compression, download UPX from https://upx.github.io/ and add it to your PATH.

### Runtime Issues

**Problem**: palfriendlauncher.exe shows "Installation Incomplete" message

**Solution**: This is expected in development builds. The bootstrapper is designed to:
1. Extract embedded palfriend.exe from the launcher (production)
2. Download from GitHub Releases (future feature)

For testing, manually copy `dist/palfriend/` to the installation directory shown in the launcher.

**Problem**: Executable won't start or crashes immediately

**Solution**: 
1. Run from command line to see error messages:
   ```cmd
   dist\palfriend\palfriend.exe
   ```
2. Check that settings.yaml exists or can be created
3. Ensure you have write permissions in the directory

**Problem**: "Failed to start PalFriend" error

**Solution**:
1. Check that all configuration files are present
2. Verify settings.yaml.example exists and is valid
3. Run with elevated privileges if needed
4. Check antivirus isn't blocking the executable

**Problem**: Web interface doesn't load

**Solution**:
1. Check that frontend/build directory was included in the build
2. Verify port 5008 is not in use by another application
3. Check firewall settings

**Problem**: Launcher shows "No write permission" error

**Solution**:
1. Choose a different installation directory (e.g., Desktop)
2. Run launcher as administrator (right-click → Run as administrator)
3. Disable antivirus temporarily to check if it's blocking writes

## Automated Builds (CI/CD)

The repository includes a GitHub Actions workflow that automatically builds both executables:

- **Workflow File**: `.github/workflows/build_launcher.yml`
- **Trigger**: On pull requests or manual dispatch
- **Python Version**: 3.12.x (enforced)
- **Jobs**:
  1. `build-palfriend`: Builds the main application (palfriend.exe)
  2. `build-launcher`: Builds the bootstrapper (palfriendlauncher.exe)
- **Artifacts**:
  - `palfriend-app`: Main application directory
  - `palfriendlauncher-exe`: Bootstrapper executable
  - `palfriend-distribution`: Complete distribution bundle
- **Retention**: 30 days

To trigger a manual build:
1. Go to Actions tab in GitHub
2. Select "Build Launcher Executable" workflow
3. Click "Run workflow"
4. Download the artifacts when complete

## Distribution

When distributing the executables:

### End-User Distribution (Recommended)

1. **Distribute just the bootstrapper:**
   ```
   palfriendlauncher.exe
   ```
   
2. **User workflow:**
   - Download palfriendlauncher.exe
   - Run it
   - It handles installation automatically

### Full Bundle Distribution (Alternative)

1. **Create a release package:**
   ```
   palfriend-v1.0.0/
   ├── palfriendlauncher.exe      (Run this to install)
   ├── palfriend/                  (Main application folder)
   │   ├── palfriend.exe
   │   ├── (all dependencies)
   │   └── frontend/
   ├── settings.yaml.example
   ├── .env.example
   └── README.txt
   ```

2. **Compress as ZIP** for easy distribution

### GitHub Releases

When creating a GitHub release:
1. Use the `palfriend-distribution` artifact from CI
2. Add release notes
3. Attach both executables
4. Include installation instructions

## Advanced Configuration

### Customizing the Spec Files

You can modify the spec files to customize the build:

#### palfriend.spec (Main Application)
- Add an icon: Set `icon='path/to/icon.ico'` in the EXE section
- Add more hidden imports: Add to `hiddenimports` list
- Include additional data files: Add to `datas` list
- Switch to onefile: Change COLLECT to bundle everything in EXE

#### palfriendlauncher.spec (Bootstrapper)
- Add an icon: Set `icon='path/to/icon.ico'` in the EXE section
- Embed palfriend payload: Uncomment and configure the payload section in `datas`
- Show console: Change `console=False` to `console=True` for debugging

### Embedding PalFriend in the Launcher

To create a fully self-contained installer:

1. **Build palfriend.exe first:**
   ```cmd
   pyinstaller --noconfirm palfriend.spec
   ```

2. **Edit palfriendlauncher.spec to embed the payload:**
   ```python
   # In palfriendlauncher.spec, uncomment:
   palfriend_bundle = os.path.join(base_dir, 'dist', 'palfriend')
   if os.path.exists(palfriend_bundle):
       datas.append((palfriend_bundle, 'palfriend_payload'))
   ```

3. **Build the launcher:**
   ```cmd
   pyinstaller --noconfirm palfriendlauncher.spec
   ```

4. **Update bootstrap_launcher.py** to extract from the embedded payload

This creates a single .exe that contains everything.

### Building for Different Platforms

While this guide focuses on Windows, PyInstaller can also build for:

- **Linux**: Use `build_launcher.sh` on Linux
- **Mac**: Use `build_launcher.sh` on Mac

Note: You must build on the target platform (build on Windows for Windows, etc.)

## Size Optimization

To reduce executable size:

1. **Remove unused features** from requirements.txt
2. **Use exclude list** in spec files (already configured)
3. **Disable UPX** if it causes issues: `upx=False` in spec
4. **Use onefile** for launcher (already done)
5. **Use onedir** for main app (better compatibility, already done)

Current typical sizes:
- **palfriend.exe** (onedir): ~150-200 MB total (with all ML dependencies)
- **palfriendlauncher.exe** (onefile): ~10-20 MB
- Combined distribution: ~170-220 MB

## Python Version Requirements

**CRITICAL**: The build system enforces Python version requirements:

✓ **Supported**: Python 3.11.x, 3.12.x  
✗ **NOT Supported**: Python 3.13.x and newer

### Why Python 3.13+ Doesn't Work

- PyInstaller 6.x is not compatible with Python 3.13
- Many wheels and dependencies don't support Python 3.13 yet
- PyInstaller 7.x (which might support 3.13) is not stable yet

### Version Enforcement

The build system checks Python version at multiple points:
1. **build_launcher.bat/sh**: Checks and aborts if version >= 3.13
2. **validate_build_system.py**: Warns about version issues
3. **GitHub Actions**: Explicitly uses Python 3.12

If you're using Python 3.14 (as mentioned in the issue), you **must** switch to 3.12.

## Support

For issues or questions:
- Check the main [README.md](README.md)
- Review [TROUBLESHOOTING.md](README.md#troubleshooting)
- Open an issue on GitHub

## License

This build system is part of PalFriend and uses the same MIT License.
