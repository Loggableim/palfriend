# PalFriend - TikTok ChatPal Brain

A modular TikTok live interaction bot that connects to Animaze for real-time chat responses.

## 🎨 New Modern Web Interface

PalFriend now includes a **completely redesigned modern web-based GUI** with:
- ✨ React frontend with Material UI
- 🌓 Dark/Light theme support
- 📱 Fully responsive design (desktop, tablet, mobile)
- 🔄 Real-time updates via WebSocket
- 📊 Interactive dashboard with live statistics
- 🎤 Animated VU meter for microphone monitoring
- 🌍 Multi-language support (English, German)
- 📂 Drag-and-drop configuration import/export
- ⚙️ Modern controls (sliders, toggles, dropdowns)

**Get started with the web interface:**
```bash
# Linux/Mac
./start_web.sh

# Windows
start_web.bat
```

See [WEB_INTERFACE_README.md](WEB_INTERFACE_README.md) for detailed documentation.

## Legacy Tkinter GUI

The original Tkinter GUI is still available:
```bash
python main.py
```

## Project Structure

The codebase has been refactored into modular components for better maintainability:

- **`main.py`** - Main entry point that orchestrates all components
- **`settings.py`** - Configuration management with YAML support
- **`memory.py`** - User data storage and retrieval
- **`speech.py`** - Speech and microphone state management
- **`events.py`** - TikTok event handling and deduplication
- **`utils.py`** - Utility functions and helpers
- **`response.py`** - AI response generation and relevance scoring
- **`outbox.py`** - Message batching and prioritization
- **`gui.py`** - Configuration GUI interface
- **`requirements.txt`** - Python dependencies

## Installation

### Quick Install (Recommended)

Using pip with setup.py:
```bash
# Clone the repository
git clone https://github.com/mycommunity/palfriend.git
cd palfriend

# Install the package
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

### Manual Installation

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Install Node.js dependencies (for web interface):**
```bash
cd frontend
npm install
cd ..
```

3. **Run the application:**

Web Interface (recommended):
```bash
# Linux/Mac
./start_web.sh

# Windows
start_web.bat
```

Legacy GUI:
```bash
python main.py
```

### Requirements

- **Python**: 3.8 or higher (Python 3.12 recommended)
- **Node.js**: 16 or higher (for web interface)
- **Operating System**: Linux, macOS, or Windows

## Configuration

On first run, the application will create a `settings.yaml` file with default configuration. You can also use the GUI to configure all settings.

Key configuration sections:
- **TikTok**: Live stream connection settings
- **Animaze**: WebSocket connection for speech output
- **OpenAI**: API key and model settings for AI responses
- **Comment**: Comment processing and response rules
- **Microphone**: Voice activity detection settings
- **Join Rules**: New viewer greeting settings
- **Outbox**: Message batching configuration

## Features

- Real-time TikTok live event processing (comments, gifts, follows, etc.)
- AI-powered response generation using OpenAI
- Voice activity detection for microphone input
- Message batching and prioritization
- User memory and interaction history
- Event deduplication
- Configurable greeting and response rules
- GUI for easy configuration

## Migration from Legacy Code

This is a refactored version of the original `pal_ALONE.py` monolithic script. The functionality remains the same, but the code is now organized into logical modules for better:
- **Readability**: Each module has a clear purpose
- **Maintainability**: Easier to find and modify specific functionality
- **Testability**: Modules can be tested independently
- **Extensibility**: New features can be added with minimal changes

### Key Improvements
- Type annotations throughout for better IDE support
- Comprehensive docstrings for all functions and classes
- YAML configuration files (more readable than JSON)
- f-strings for cleaner string formatting
- Explicit dependency management via requirements.txt
- Proper separation of concerns (GUI, logic, storage)

## Troubleshooting

### Common Issues and Solutions

#### Application Won't Start

**Problem**: `ModuleNotFoundError` when starting the application

**Solution**: Install all required dependencies
```bash
pip install -r requirements.txt
```

**Problem**: Port 5000 already in use (web interface)

**Solution**: Either stop the other application using port 5000, or modify `app.py` to use a different port
```python
# In app.py, change:
socketio.run(app, host='0.0.0.0', port=5000)
# To:
socketio.run(app, host='0.0.0.0', port=5001)
```

#### Frontend Issues

**Problem**: Frontend won't build (`npm run build` fails)

**Solution**: 
1. Ensure Node.js 16+ is installed: `node --version`
2. Delete node_modules and reinstall:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

**Problem**: WebSocket connection fails in browser

**Solution**:
1. Ensure Flask backend is running: `python app.py`
2. Check browser console for specific error messages
3. Try disabling browser extensions that might block WebSocket
4. Verify CORS settings in `app.py`
5. Check firewall settings

**Problem**: Real-time updates not working

**Solution**:
1. Verify WebSocket connection in browser console (look for Socket.io logs)
2. Ensure Flask-SocketIO is installed: `pip install flask-socketio python-socketio`
3. Check network proxy settings that might interfere with WebSocket

#### TikTok Connection Issues

**Problem**: Cannot connect to TikTok Live

**Solution**:
1. Verify the TikTok handle is correct in settings
2. Ensure the user is currently live streaming
3. Check if you need a session ID for that account
4. Try updating the TikTokLive library: `pip install --upgrade TikTokLive`

**Problem**: TikTok connection drops frequently

**Solution**:
1. Check your internet connection stability
2. The application has automatic reconnection - wait a few seconds
3. Verify no firewall is blocking the connection
4. Check TikTok's API rate limits

#### Animaze Connection Issues

**Problem**: Cannot connect to Animaze WebSocket

**Solution**:
1. Ensure Animaze is running
2. Verify Animaze WebSocket server is enabled
3. Check host and port settings in `settings.yaml`:
```yaml
animaze:
  host: "127.0.0.1"
  port: 8000  # Default Animaze port
```
4. Test connection manually: `telnet 127.0.0.1 8000`

#### OpenAI API Issues

**Problem**: AI responses not generating

**Solution**:
1. Verify OpenAI API key is set in settings
2. Check API key is valid at https://platform.openai.com/api-keys
3. Ensure you have API credits available
4. Check the model name is correct (e.g., "gpt-3.5-turbo", "gpt-4")
5. Review Flask logs for specific OpenAI error messages

**Problem**: Rate limit errors from OpenAI

**Solution**:
1. Increase `global_cooldown` in comment settings
2. Decrease `max_replies_per_min`
3. Increase `reply_threshold` to be more selective
4. Consider upgrading your OpenAI plan

#### Microphone Issues

**Problem**: Microphone not detected

**Solution**:
1. Check microphone is connected and working in system settings
2. List available devices via API: `curl http://localhost:5000/api/devices`
3. Set the correct device in settings using the device name from the list
4. On Linux, ensure you have proper permissions for audio devices

**Problem**: VU meter not updating

**Solution**:
1. Verify microphone is enabled in settings
2. Check WebSocket connection is active
3. Ensure sounddevice library is installed: `pip install sounddevice`
4. Test microphone access with another application

#### Settings and Configuration

**Problem**: Settings not saving

**Solution**:
1. Check file permissions in the application directory
2. Ensure `settings.yaml` is writable
3. Check Flask logs for specific error messages
4. Try exporting settings as JSON, editing manually, then importing

**Problem**: Configuration import fails

**Solution**:
1. Verify the file format is valid JSON or YAML
2. Check for syntax errors in the configuration file
3. Ensure all required fields are present
4. Try starting with default settings and modifying incrementally

#### Memory and Performance

**Problem**: Application uses too much memory

**Solution**:
1. Reduce `decay_days` in memory settings to clean up old user data sooner
2. Decrease log buffer size in `app.py` (default 1000 entries)
3. Restart the application periodically
4. The application automatically cleans memory every hour

**Problem**: Application becomes slow over time

**Solution**:
1. Check memory usage and restart if necessary
2. Review log file sizes - old logs can be deleted
3. Reduce the number of stored events in memory
4. Check for memory leaks and report as an issue

#### Development Issues

**Problem**: Hot reload not working in development mode

**Solution**:
1. Ensure you're using `npm run dev` for frontend (not `npm start`)
2. Check Vite configuration in `vite.config.js`
3. Verify files are being watched (not in node_modules or excluded)

**Problem**: ESLint errors in frontend

**Solution**:
```bash
cd frontend
npm run lint -- --fix
```

#### Getting Help

If you encounter issues not listed here:

1. **Check the logs**: 
   - Backend: Console output when running `python app.py`
   - Frontend: Browser console (F12 → Console tab)
   - Network: Browser DevTools (F12 → Network tab)

2. **Enable debug logging**:
```python
# In app.py or main.py, change:
logging.basicConfig(level=logging.INFO)
# To:
logging.basicConfig(level=logging.DEBUG)
```

3. **Review documentation**:
   - [WEB_INTERFACE_README.md](WEB_INTERFACE_README.md) - Web interface details
   - [TESTING.md](TESTING.md) - Testing guide
   - [CONTRIBUTING.md](CONTRIBUTING.md) - Development setup

4. **Report an issue**:
   - Visit: https://github.com/mycommunity/palfriend/issues
   - Include: Python version, Node.js version, OS, error messages, steps to reproduce

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines on:
- Setting up the development environment
- Using GitHub Copilot effectively
- Coding conventions and standards
- Testing strategies
- Pull request process

## Documentation

- **[README.md](README.md)** - This file, main documentation
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Complete 7-phase system architecture
- **[CHANGELOG.md](CHANGELOG.md)** - Version history and changes
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contribution guidelines
- **[WEB_INTERFACE_README.md](WEB_INTERFACE_README.md)** - Web interface documentation
- **[TESTING.md](TESTING.md)** - Testing guide
- **[UI_DESIGN.md](UI_DESIGN.md)** - UI/UX design documentation

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Version

**Current Version**: 1.0.0 (Production Ready)

See [CHANGELOG.md](CHANGELOG.md) for version history.
