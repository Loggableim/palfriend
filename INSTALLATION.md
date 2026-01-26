# Installation Guide for PalFriend

This guide provides detailed installation instructions for PalFriend, including platform-specific notes and optional features.

## System Requirements

- **Python**: 3.8 or higher (3.11 or 3.12 recommended)
- **Operating System**: Windows, macOS, or Linux
- **RAM**: Minimum 4GB, 8GB recommended
- **Disk Space**: At least 500MB free

## Basic Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/Loggableim/palfriend.git
cd palfriend
```

### Step 2: Create a Virtual Environment (Recommended)

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Core Dependencies

Install the core dependencies required to run PalFriend:

```bash
pip install -r requirements.txt
```

This will install all the essential packages needed for the basic functionality of PalFriend.

## Optional Features

### RAG (Retrieval-Augmented Generation) Engine

The RAG engine provides enhanced conversational memory using vector embeddings. This feature is **optional** and requires additional dependencies.

**Important Note:** The RAG engine requires `chromadb` and `sentence-transformers`, which depend on `onnxruntime`. Unfortunately, `onnxruntime` pre-built wheels are not available for all platforms, particularly:
- Windows on ARM (ARM64)
- Some older or less common platforms

If you're on a supported platform and want to use the RAG feature:

```bash
pip install -r requirements-rag.txt
```

Or install via setup.py extras:

```bash
pip install -e .[rag]
```

**If Installation Fails:**
- Don't worry! PalFriend will work fine without the RAG engine
- The application gracefully handles the absence of these optional features
- You'll see a warning in the logs but the app will continue normally

### Platform-Specific Notes for RAG Installation

#### Windows (x64)
Should work out of the box with pip install.

#### Windows (ARM64)
`onnxruntime` wheels are not available. You have two options:
1. **Skip RAG features** - The app works fine without them
2. **Build from source** - Follow [ONNX Runtime build instructions](https://onnxruntime.ai/docs/build/inferencing.html#windows)

#### macOS (Intel and Apple Silicon)
Should work out of the box. If on Apple Silicon (M1/M2/M3):
```bash
brew install libomp
pip install -r requirements-rag.txt
```

#### Linux
Should work out of the box with pip install.

## Troubleshooting

### "ERROR: Cannot install palfriend because these package versions have conflicting dependencies"

This error typically occurs when:
1. You're trying to install optional dependencies (chromadb) on an unsupported platform
2. There's a version conflict between packages

**Solution:**
- Install only the core dependencies: `pip install -r requirements.txt`
- Skip the RAG features if you encounter conflicts
- Make sure you're using Python 3.8 or higher

### "No module named 'chromadb'"

This is expected if you haven't installed the optional RAG dependencies. The application will log a warning and continue without RAG features.

### onnxruntime Installation Fails

If you see errors related to `onnxruntime` during installation:
1. This is expected on unsupported platforms (e.g., Windows ARM)
2. Skip the RAG installation: `pip install -r requirements.txt` (core only)
3. The application will work without the RAG engine

### Pydantic Version Conflicts

If you encounter pydantic version conflicts:
- Make sure you're using `pydantic>=2.0.0` as specified in requirements.txt
- If you need chromadb compatibility, use chromadb >= 1.3.0 which supports pydantic 2.x

## Verifying Installation

To verify your installation is working:

```bash
python -c "import openai; import flask; import TikTokLive; print('Core dependencies OK')"
```

To check if RAG features are available:

```bash
python -c "try: import chromadb; print('RAG features available')
except ImportError: print('RAG features not installed (optional)')"
```

## Next Steps

1. Copy `settings.yaml.example` to `settings.yaml` and configure your settings
2. Copy `.env.example` to `.env` and add your API keys
3. Run the web interface: `./start_web.sh` (Linux/Mac) or `start_web.bat` (Windows)
4. Or run the legacy GUI: `python main.py`

For more information, see:
- [README.md](README.md) - General project information
- [WEB_INTERFACE_README.md](WEB_INTERFACE_README.md) - Web interface documentation
- [CONTRIBUTING.md](CONTRIBUTING.md) - Development guidelines
