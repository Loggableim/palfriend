# Building the PalFriend Windows Launcher

This document explains how to build the PalFriend Windows launcher executable.

## Overview

The PalFriend launcher is a standalone Windows executable (.exe) that:
- Starts the PalFriend web interface automatically
- Opens your default browser to the application
- Bundles all Python dependencies (no Python installation required on target machine)
- Includes the React frontend build

## Prerequisites

### For Building the Launcher

1. **Python 3.8 to 3.13** (3.12 recommended)
   - Download from: https://www.python.org/downloads/
   - Make sure to check "Add Python to PATH" during installation
   - **Note:** Python 3.14 is not fully supported due to missing onnxruntime wheels on Windows
   - If using Python 3.14+, the build will succeed but without optional RAG features

2. **Node.js 16 or higher** (for frontend build)
   - Download from: https://nodejs.org/
   - Required to build the React frontend

3. **PyInstaller**
   - Will be installed automatically by the build script
   - Or install manually: `pip install pyinstaller`

### For Running the Built Executable

The built executable requires no prerequisites on the target Windows machine - everything is bundled!

## Building the Launcher

### Automated Build (Recommended)

#### On Windows:

Simply double-click or run:
```cmd
build_launcher.bat
```

This script will:
1. Check for Python and Node.js
2. Install dependencies
3. Build the React frontend (if needed)
4. Create the executable using PyInstaller
5. Place the result in `dist/palfriend-launcher.exe`

#### On Linux/Mac:

```bash
chmod +x build_launcher.sh
./build_launcher.sh
```

### Manual Build

If you prefer to build manually or need more control:

1. **Install dependencies:**
   ```cmd
   pip install -r requirements.txt
   pip install pyinstaller
   ```

2. **Build the frontend (if not already built):**
   ```cmd
   cd frontend
   npm install
   npm run build
   cd ..
   ```

3. **Run PyInstaller with the spec file:**
   ```cmd
   pyinstaller --noconfirm palfriend-launcher.spec
   ```

4. **Find your executable at:**
   ```
   dist/palfriend-launcher.exe
   ```

## Build Configuration

The build is configured via the `palfriend-launcher.spec` file, which:

- Uses `launcher.py` as the entry point
- Includes all necessary Python modules
- Bundles the frontend build directory
- Includes example configuration files
- Optimizes the executable size with UPX compression
- Keeps the console window visible for logs

### Key Files

- **`launcher.py`** - Main entry point for the executable
- **`palfriend-launcher.spec`** - PyInstaller configuration
- **`build_launcher.bat`** - Windows build script
- **`build_launcher.sh`** - Linux/Mac build script

### Optional Features

The launcher includes core functionality by default. Advanced features like RAG (Retrieval-Augmented Generation) are optional:

- **RAG Features** (chromadb, sentence-transformers): Optional, requires compatible Python version (3.8-3.13)
  - If not available, the application will still work but without semantic memory search
  - The build script will continue even if these dependencies can't be installed
  
To enable optional features, uncomment the relevant lines in `requirements.txt` before building.

## Troubleshooting

### Build Issues

**Problem**: `onnxruntime` or chromadb dependency conflict (especially on Python 3.14+)

**Solution**: ChromaDB and its dependencies are now optional. The build will continue without them:
- The launcher will build successfully but without RAG (Retrieval-Augmented Generation) features
- To include RAG features, use Python 3.12 or 3.13 and uncomment chromadb/sentence-transformers in requirements.txt
- The application will work fine without these optional features

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

**Problem**: Executable is very large (>100 MB)

**Solution**: This is normal. The executable includes:
- Python runtime
- All dependencies (Flask, OpenAI, etc.)
- Optional ML dependencies (ChromaDB, sentence-transformers) if available
- Frontend assets

**Problem**: Build fails with "UPX not available"

**Solution**: This is just a warning. The executable will be larger but will work fine. To enable UPX compression, download UPX from https://upx.github.io/ and add it to your PATH.

### Runtime Issues

**Problem**: Executable won't start or crashes immediately

**Solution**: 
1. Run from command line to see error messages:
   ```cmd
   dist\palfriend-launcher.exe
   ```
2. Check that settings.yaml exists or can be created
3. Ensure you have write permissions in the directory

**Problem**: "Failed to start PalFriend" error

**Solution**:
1. Check that all configuration files are present
2. Verify settings.yaml.example exists and is valid
3. Run with elevated privileges if needed

**Problem**: Web interface doesn't load

**Solution**:
1. Check that frontend/build directory was included in the build
2. Verify port 5008 is not in use by another application
3. Check firewall settings

## Automated Builds (CI/CD)

The repository includes a GitHub Actions workflow that automatically builds the launcher:

- **Workflow File**: `.github/workflows/build_launcher.yml`
- **Trigger**: On pull requests or manual dispatch
- **Output**: Uploaded as GitHub Actions artifact
- **Retention**: 30 days

To trigger a manual build:
1. Go to Actions tab in GitHub
2. Select "Build Launcher Executable" workflow
3. Click "Run workflow"
4. Download the artifact when complete

## Distribution

When distributing the executable:

1. **Include these files with the .exe:**
   - `settings.yaml.example` (as a template)
   - `.env.example` (for API keys)
   - `README.md` (for documentation)

2. **Create a release package:**
   ```
   palfriend-launcher-v1.0.0/
   ├── palfriend-launcher.exe
   ├── settings.yaml.example
   ├── .env.example
   └── README.md
   ```

3. **Compress as ZIP** for easy distribution

## Advanced Configuration

### Customizing the Spec File

You can modify `palfriend-launcher.spec` to:

- Add an icon: Set `icon='path/to/icon.ico'` in the EXE section
- Hide console window: Change `console=True` to `console=False`
- Add more hidden imports: Add to `hiddenimports` list
- Include additional data files: Add to `datas` list

### Building for Different Platforms

While this guide focuses on Windows, PyInstaller can also build for:

- **Linux**: Use `build_launcher.sh` on Linux
- **Mac**: Use `build_launcher.sh` on Mac

Note: You must build on the target platform (build on Windows for Windows, etc.)

## Size Optimization

To reduce executable size:

1. **Remove unused features** from requirements.txt
2. **Use `--onefile --noupx`** if UPX causes issues
3. **Exclude test dependencies** (already done in spec file)
4. **Use `--strip`** for Linux builds

Current typical sizes:
- Windows .exe: ~150-200 MB (with all ML dependencies)
- Without ML models: ~50-100 MB

## Support

For issues or questions:
- Check the main [README.md](README.md)
- Review [TROUBLESHOOTING.md](README.md#troubleshooting)
- Open an issue on GitHub

## License

This build system is part of PalFriend and uses the same MIT License.
