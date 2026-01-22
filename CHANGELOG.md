# Changelog

All notable changes to PalFriend will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-01-16

### Added

#### Modern Web Interface
- **Complete React/Flask redesign** replacing legacy Tkinter GUI
- **Material UI components** for modern, polished appearance
- **Dark/Light theme support** with persistent user preference
- **Fully responsive design** - works seamlessly on desktop, tablet, and mobile devices
- **Real-time WebSocket updates** for live status, logs, and statistics
- **Tab-based navigation** - Dashboard, Settings, Logs, and Events sections
- **Drag-and-drop configuration** import with JSON and YAML support
- **Visual connection indicators** for TikTok, Animaze, and Microphone
- **Live VU meter** with animated microphone level visualization and history chart
- **Interactive dashboard** with real-time statistics (viewers, comments, gifts, followers)
- **Multi-language support** - English and German translations included
- **Configuration export/import** in both JSON and YAML formats
- **Modern input controls** - sliders, toggles, and dropdowns instead of plain text fields
- **Password field visibility toggle** for API keys and sensitive data
- **Auto-scrolling log viewer** with search/filter capabilities
- **Real-time event stream** showing TikTok interactions as they happen
- **Smooth animations** using Framer Motion for polished UX
- **Touch-friendly mobile interface** with optimized layout

#### API & Backend
- **RESTful API endpoints** for settings, status, memory, and device management
- **WebSocket server** for real-time bidirectional communication
- **Flask-SocketIO integration** for efficient event broadcasting
- **CORS support** for frontend/backend separation during development
- **Structured logging** with WebSocket broadcast to frontend
- **Audio device enumeration** API endpoint
- **Memory statistics** endpoint for user interaction data
- **Settings validation** on import

#### Documentation
- **WEB_INTERFACE_README.md** - Comprehensive web interface documentation
- **TESTING.md** - Detailed testing guide and checklist
- **UI_DESIGN.md** - Complete UI/UX design documentation
- **CONTRIBUTING.md** - Contribution guidelines with GitHub Copilot best practices
- **Enhanced README.md** - Updated with web interface instructions

#### Build & Deployment
- **Startup scripts** for Linux/Mac (`start_web.sh`) and Windows (`start_web.bat`)
- **Vite build system** for optimized frontend bundling
- **ESLint configuration** for code quality
- **Production build pipeline** with automatic frontend compilation
- **Static file serving** from Flask for production deployment

#### Developer Experience
- **Type annotations** throughout Python codebase
- **Comprehensive docstrings** for all functions and classes
- **Modular architecture** with clear separation of concerns
- **Hot reload** support in development mode
- **Error handling** improvements with proper logging
- **Development and production modes** clearly separated

### Changed

#### Architecture Improvements
- **Refactored monolithic code** into modular components:
  - `settings.py` - Configuration management
  - `memory.py` - User data storage
  - `speech.py` - Speech/microphone state
  - `events.py` - Event handling and deduplication
  - `utils.py` - Utility functions
  - `response.py` - AI response generation
  - `outbox.py` - Message batching
  - `gui.py` - Legacy GUI (retained for backward compatibility)
  - `app.py` - New Flask web server
- **YAML configuration** format (more readable than JSON)
- **f-strings** for cleaner string formatting throughout
- **Explicit dependency management** via requirements.txt

#### Performance Optimizations
- **Message batching** with configurable window and size limits
- **Event deduplication** to prevent duplicate processing
- **Efficient log buffering** (maximum 1000 entries in memory)
- **React component memoization** for optimized rendering
- **Asynchronous WebSocket handling** for non-blocking communication
- **Token bucket algorithm** for rate limiting
- **Periodic memory cleanup** to prevent unbounded growth
- **Garbage collection** after memory cleanup

#### User Experience
- **Configurable cooldowns** per-user and global
- **Relevance scoring** for intelligent comment filtering
- **Greeting detection** with smart response logic
- **Thanks detection** and acknowledgment
- **Join announcement batching** for better flow
- **Microphone state awareness** - pauses during user speech
- **Priority-based message queuing** for important events
- **Connection retry logic** with exponential backoff
- **Automatic reconnection** for TikTok and Animaze connections

### Fixed

#### Stability & Reliability
- **WebSocket connection handling** - proper reconnection logic
- **Session ID support** for TikTok authentication
- **Error recovery** in event processors
- **Race conditions** in async event handling
- **Memory leaks** in long-running sessions
- **Connection state synchronization** between backend and frontend
- **File permissions** handling for settings and memory files

#### UI/UX Issues
- **Theme persistence** using localStorage
- **Language persistence** across sessions
- **Log overflow** with automatic truncation
- **Mobile responsiveness** on small screens
- **Touch target sizes** on mobile devices
- **Form validation** feedback
- **API error handling** with user-friendly messages

### Security

- **Password field masking** for API keys and sensitive data
- **CORS configuration** properly scoped
- **Input validation** on all API endpoints
- **No sensitive data** stored in browser localStorage
- **Secure WebSocket** connection handling
- **API key exposure** prevention in logs and UI

### Deprecated

- **Legacy Tkinter GUI** - Still available via `main.py` but web interface is recommended
- Future versions may phase out Tkinter in favor of the web interface

### Technical Details

#### Dependencies Added
- Flask 3.0+ - Web framework
- Flask-CORS 4.0+ - CORS support
- Flask-SocketIO 5.3+ - WebSocket support
- Python-SocketIO 5.10+ - SocketIO implementation

#### Frontend Stack
- React 18.2 - UI framework
- Material UI 5.14 - Component library
- Vite 5.0 - Build tool
- React Router 6.20 - Routing
- Socket.io Client 4.5 - WebSocket client
- i18next 23.7 - Internationalization
- Framer Motion 10.16 - Animations
- Recharts 2.10 - Charts
- React Dropzone 14.2 - File upload
- Axios 1.6 - HTTP client

#### Python Version Support
- Python 3.8+ required
- Python 3.12 tested and supported
- Type hints compatible with Python 3.8+

#### Node.js Version Support
- Node.js 16+ required
- Node.js 18 and 20 tested

### Migration Guide

#### From Legacy GUI to Web Interface

1. **Configuration Migration**: Your existing `settings.yaml` will work with the new web interface without changes

2. **Starting the Application**:
   - Old: `python main.py`
   - New: `./start_web.sh` or `start_web.bat`

3. **API Integration**: If you have custom scripts that modify settings:
   - Old: Direct file modification
   - New: Use REST API endpoints (`/api/settings`)

4. **Monitoring**: 
   - Old: Watch console output
   - New: Use the Logs tab in web interface

#### Installing for the First Time

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies
cd frontend
npm install

# Build frontend
npm run build

# Start application
cd ..
python app.py
```

### Known Issues

- Legacy Tkinter GUI does not communicate with the web interface (they are separate entry points)
- WebSocket reconnection may take a few seconds during network disruptions
- Very old browsers (IE11) are not supported

### Contributors

This release represents a complete modernization of PalFriend with contributions focused on:
- UI/UX redesign and implementation
- Backend API development
- Documentation improvements
- Testing infrastructure
- Build and deployment automation

---

## [0.9.0] - Previous Version

### Initial Features

- TikTok Live event processing (comments, gifts, follows, etc.)
- AI-powered response generation using OpenAI
- Voice activity detection for microphone input
- Message batching and prioritization
- User memory and interaction history
- Event deduplication
- Configurable greeting and response rules
- Animaze WebSocket integration
- Tkinter-based GUI for configuration

---

## Version History

- **1.0.0** - Modern web interface, full documentation, production-ready release
- **0.9.0** - Initial modular refactoring from legacy monolithic code

[1.0.0]: https://github.com/mycommunity/palfriend/releases/tag/v1.0.0
[0.9.0]: https://github.com/mycommunity/palfriend/releases/tag/v0.9.0
