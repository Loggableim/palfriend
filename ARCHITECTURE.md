# 7-Phase System Architecture

This document describes the 7 modular phases (components) that make up the PalFriend system architecture.

---

## Overview

PalFriend is built on a modular architecture with 7 distinct phases that work together to create an intelligent TikTok live interaction bot. Each phase has a specific responsibility and interfaces cleanly with other phases.

```
┌─────────────────────────────────────────────────────────────┐
│                     PalFriend Architecture                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Phase 1  │  │ Phase 2  │  │ Phase 3  │  │ Phase 4  │  │
│  │Settings  │──│ Memory   │──│ Speech   │──│ Events   │  │
│  │Management│  │ System   │  │& Mic     │  │Processing│  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
│       │             │             │             │          │
│       └─────────────┴─────────────┴─────────────┘          │
│                      │                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                │
│  │ Phase 5  │  │ Phase 6  │  │ Phase 7  │                │
│  │Response  │──│ Message  │──│GUI/Web   │                │
│  │Generator │  │ Batching │  │Interface │                │
│  └──────────┘  └──────────┘  └──────────┘                │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Settings Management (`settings.py`)

### Purpose
Centralized configuration management for all system components.

### Functionality
- **Load/Save Configuration**: Supports both JSON (legacy) and YAML formats
- **Default Settings**: Provides sensible defaults for all configuration values
- **Hot Reload**: Settings can be updated without restarting the application
- **Validation**: Ensures configuration values are valid and type-safe

### Key Components
- `load_settings()` - Load configuration from file or create defaults
- `save_settings()` - Persist configuration changes to disk
- `DEFAULT_SETTINGS` - Complete default configuration structure

### Configuration Sections
1. **TikTok**: Live stream connection (unique_id, session_id)
2. **Animaze**: WebSocket connection for speech output
3. **OpenAI**: API configuration for AI responses
4. **Comment**: Comment processing rules and filters
5. **Microphone**: Voice activity detection settings
6. **Memory**: User data storage configuration
7. **Join Rules**: New viewer greeting settings
8. **Outbox**: Message batching configuration

### API/Interface
```python
# Load settings
settings = load_settings()

# Access configuration
tiktok_id = settings["tiktok"]["unique_id"]
api_key = settings["openai"]["api_key"]

# Save changes
settings["comment"]["enabled"] = 1
save_settings(settings)
```

### Dependencies
- `yaml` - YAML parsing
- `json` - JSON parsing
- Standard library: `os`, `logging`

### Usage Example
```python
from settings import load_settings, save_settings

# Load configuration
config = load_settings()

# Modify settings
config["openai"]["model"] = "gpt-4"
config["comment"]["reply_threshold"] = 0.7

# Persist changes
save_settings(config)
```

---

## Phase 2: Memory System (`memory.py`)

### Purpose
Persistent storage and retrieval of user interaction history and data.

### Functionality
- **User Data Storage**: Stores per-user interaction history
- **Event Tracking**: Records comments, gifts, follows, etc.
- **Data Decay**: Automatically removes stale user data
- **Background Info**: Generates context for AI responses
- **Memory Cleaning**: Periodic cleanup of old data

### Key Components
- `load_memory()` - Load memory from disk with decay cleanup
- `save_memory()` - Persist memory to disk
- `remember_event()` - Store a new user event
- `get_user()` - Retrieve or create user record
- `get_background_info()` - Generate context from user history

### Data Structure
```python
{
    "users": {
        "username": {
            "first_seen": timestamp,
            "last_seen": timestamp,
            "comments": deque([...]),  # Limited history
            "gifts": [...],
            "follows": count,
            "likes": count,
            "shares": count,
            "subscriptions": count
        }
    },
    "created": timestamp
}
```

### API/Interface
```python
# Load memory with 90-day decay
memory = load_memory("memory.json", decay_days=90)

# Get or create user
user = get_user(memory, "username")

# Store event
remember_event(memory, "username", "comment", "Hello!")

# Get context for AI
context = get_background_info(memory, "username")
```

### Dependencies
- `json` - JSON serialization
- `collections.deque` - Fixed-size history queues
- Standard library: `time`, `logging`

### Usage Example
```python
from memory import load_memory, remember_event, get_background_info

# Initialize
memory = load_memory("memory.json", decay_days=90)

# Record interaction
remember_event(memory, "john_doe", "comment", "What's your favorite color?")
remember_event(memory, "john_doe", "gift", "Rose")

# Get context
background = get_background_info(memory, "john_doe")
# Returns: "john_doe: 2 comments, 1 gifts"
```

---

## Phase 3: Speech & Microphone (`speech.py`)

### Purpose
Manages speech output state and microphone voice activity detection.

### Functionality
- **Speech State Tracking**: Monitors current speech state (idle, speaking, done)
- **Microphone Monitoring**: Real-time voice activity detection
- **VU Meter**: Audio level monitoring for UI feedback
- **Device Management**: Audio device selection and configuration
- **Silence Detection**: Intelligent silence threshold detection

### Key Components
- `SpeechState` - Enum for speech states (IDLE, SPEAKING, DONE)
- `MicState` - Tracks microphone state and audio levels
- `MicrophoneMonitor` - Real-time audio monitoring thread
- Audio level calculation and smoothing
- Device enumeration and selection

### States
```python
class SpeechState(Enum):
    IDLE = "idle"        # No speech in progress
    SPEAKING = "speaking"  # Currently speaking
    DONE = "done"        # Speech completed
```

### API/Interface
```python
# Create microphone monitor
mic_state = MicState()
monitor = MicrophoneMonitor(
    mic_state=mic_state,
    device_name="Default",
    silence_threshold=0.02,
    chunk_time=0.1
)

# Start monitoring
monitor.start()

# Check state
if mic_state.voice_detected:
    print(f"Voice detected! Level: {mic_state.audio_level:.2f}")

# Stop monitoring
monitor.stop()
```

### Dependencies
- `sounddevice` - Audio device access
- `numpy` - Audio processing
- `threading` - Background monitoring
- Standard library: `enum`, `time`, `logging`

### Usage Example
```python
from speech import MicState, MicrophoneMonitor, SpeechState

# Initialize microphone monitoring
mic_state = MicState()
monitor = MicrophoneMonitor(
    mic_state=mic_state,
    device_name="",  # Use default device
    silence_threshold=0.02,
    chunk_time=0.1
)

# Start monitoring
monitor.start()

# Check voice activity in main loop
while True:
    if mic_state.voice_detected:
        print("Voice detected, pausing AI responses...")
    time.sleep(0.1)
```

---

## Phase 4: Event Processing (`events.py`)

### Purpose
TikTok event handling, deduplication, and viewer management.

### Functionality
- **Event Deduplication**: Prevents duplicate events from being processed
- **Signature Generation**: Creates unique signatures for events
- **Viewer Tracking**: Manages viewer join times and greeting schedules
- **Join Greetings**: Schedules greetings for new viewers
- **Event Expiration**: Automatic cleanup of old event signatures

### Key Components
- `EventDeduper` - Deduplication engine with TTL-based expiration
- `make_signature()` - Generate unique event signatures
- `touch_viewer()` - Update viewer last-seen time
- `schedule_greeting()` - Schedule greeting for new viewer

### Deduplication Strategy
```python
# Events are deduplicated based on:
# - Event type (comment, gift, follow, etc.)
# - User identifier
# - Event content/value
# - Timestamp (within TTL window)

signature = f"{event_type}:{user}:{content_hash}"
```

### API/Interface
```python
# Create deduplicator with 600-second TTL
deduper = EventDeduper(ttl_seconds=600)

# Check if event is duplicate
signature = make_signature(event_type, user, content)
is_new = deduper.add(signature)

# Track viewer
viewers = {}
touch_viewer(viewers, username, current_time)

# Schedule greeting
greeting_scheduled = schedule_greeting(
    viewers=viewers,
    username=username,
    now=current_time,
    cooldown=300  # 5 minutes
)
```

### Dependencies
- `hashlib` - SHA1 hashing for signatures
- Standard library: `time`, `typing`, `logging`

### Usage Example
```python
from events import EventDeduper, make_signature, schedule_greeting

# Initialize deduplicator
deduper = EventDeduper(ttl_seconds=600)
viewers = {}

# Process comment event
def on_comment(username, text):
    signature = make_signature("comment", username, text)
    
    if deduper.add(signature):
        # New event, process it
        print(f"Processing comment from {username}: {text}")
        
        # Check if we should greet
        if schedule_greeting(viewers, username, time.time(), 300):
            print(f"Greeting scheduled for {username}")
```

---

## Phase 5: Response Generation (`response.py`)

### Purpose
AI-powered response generation with relevance scoring and context awareness.

### Functionality
- **Relevance Scoring**: Scores comments to determine if response is needed
- **Special Message Detection**: Identifies greetings, thanks, questions
- **Context Generation**: Creates AI prompts with user history
- **OpenAI Integration**: Generates contextual responses using GPT
- **Caching**: LRU cache for repeated similar queries

### Key Components
- `Relevance` - Comment scoring and classification
  - `score()` - Calculate relevance score (0.0 - 1.0)
  - `is_ignored()` - Check if comment should be ignored
  - `is_greeting()` - Detect greeting messages
  - `is_thanks()` - Detect thank you messages
- `ResponseEngine` - AI response generation
  - `generate_response()` - Create contextual AI response
  - `build_context()` - Construct AI prompt with history

### Relevance Scoring Algorithm
```python
# Base score: 0.5
# + Question words: +0.2 per keyword
# + Length bonus: +0.1 for 5+ words
# - URL penalty: -1.0 (instant ignore)
# - Starts with ! or /: -1.0 (commands)
```

### API/Interface
```python
# Initialize relevance scorer
relevance = Relevance(settings["comment"])

# Score comment
score = relevance.score("How does this work?")
# Returns: 0.9 (base + question word bonus + length)

# Generate response
engine = ResponseEngine(settings, memory)
response = await engine.generate_response(
    comment_text="What's your favorite color?",
    username="john_doe",
    background_info="john_doe: 5 comments"
)
```

### Dependencies
- `openai` - OpenAI API client
- `functools.lru_cache` - Response caching
- Standard library: `re`, `asyncio`, `logging`

### Usage Example
```python
from response import Relevance, ResponseEngine

# Initialize
relevance = Relevance(comment_config)
engine = ResponseEngine(settings, memory)

# Process comment
async def process_comment(username, text):
    # Score relevance
    score = relevance.score(text)
    threshold = settings["comment"]["reply_threshold"]
    
    if score >= threshold:
        # Generate response
        background = get_background_info(memory, username)
        response = await engine.generate_response(
            comment_text=text,
            username=username,
            background_info=background
        )
        return response
    
    return None  # Below threshold
```

---

## Phase 6: Message Batching (`outbox.py`)

### Purpose
Intelligent message queuing, batching, and prioritization for optimized output.

### Functionality
- **Priority Queues**: Separate high and normal priority messages
- **Message Batching**: Groups messages within time window
- **Duplicate Removal**: Prevents sending duplicate messages
- **Overflow Protection**: Limits batch size to prevent spam
- **Automatic Flushing**: Time-based batch release

### Key Components
- `OutboxBatcher` - Message batching engine
  - `add()` - Add message to queue
  - `flush()` - Get current batch and clear
  - `size()` - Get total queued messages
  - High priority queue (greetings, important)
  - Normal priority queue (comments, reactions)

### Batching Strategy
```python
# Messages are batched based on:
# 1. Priority (high priority sent first)
# 2. Time window (batch_window seconds)
# 3. Max batch size (10 messages default)
# 4. Deduplication (no duplicates in batch)

# Example batch:
# ["Welcome Alice!", "Hi Bob!", "Response to question"]
```

### API/Interface
```python
# Create batcher
batcher = OutboxBatcher(batch_window=25)

# Add messages
batcher.add("Hello John!", priority=True)
batcher.add("Thanks for the comment!", priority=False)

# Get batch
batch = batcher.flush()
# Returns: ["Hello John!", "Thanks for the comment!"]
```

### Dependencies
- Standard library: `time`, `typing`, `logging`

### Usage Example
```python
from outbox import OutboxBatcher
import asyncio

# Initialize
batcher = OutboxBatcher(batch_window=25)

# Add messages as they come in
batcher.add("Welcome new viewer!", priority=True)
batcher.add("Thanks for the gift!", priority=False)
batcher.add("Here's the answer...", priority=False)

# Periodic flush (in main loop)
async def message_sender():
    while True:
        await asyncio.sleep(5)  # Check every 5 seconds
        
        batch = batcher.flush()
        if batch:
            combined = " ".join(batch)
            await send_to_animaze(combined)
```

---

## Phase 7: GUI/Interface (`gui.py`, `app.py`)

### Purpose
User interfaces for configuration and monitoring.

### Functionality

#### Legacy GUI (`gui.py`)
- **Tkinter Interface**: Traditional desktop GUI
- **Configuration Editor**: All settings editable via GUI
- **Validation**: Input validation and error handling
- **File I/O**: Load/save configuration files

#### Modern Web Interface (`app.py`)
- **Flask Backend**: RESTful API server
- **WebSocket Support**: Real-time updates via Socket.IO
- **React Frontend**: Modern, responsive web UI
- **Dashboard**: Live statistics and monitoring
- **Settings Editor**: Web-based configuration
- **Event Log**: Real-time event stream
- **Theme Support**: Dark/light modes
- **Multi-language**: English, German

### Key Components

**Backend (`app.py`)**
- API Endpoints:
  - `GET /api/settings` - Get current settings
  - `POST /api/settings` - Update settings
  - `GET /api/devices` - List audio devices
  - `GET /api/logs` - Get recent logs
  - `POST /api/start` - Start TikTok connection
  - `POST /api/stop` - Stop TikTok connection
- WebSocket Events:
  - `connect` - Client connection
  - `disconnect` - Client disconnection
  - Real-time event broadcasting

**Frontend (`frontend/`)**
- `Dashboard.jsx` - Main dashboard with stats
- `Settings.jsx` - Configuration editor
- `Events.jsx` - Event log viewer
- `Logs.jsx` - System log viewer
- WebSocket integration for live updates
- Material-UI components

### API/Interface

**Legacy GUI**
```python
from gui import ConfigGUI

# Launch GUI
gui = ConfigGUI(settings)
gui.run()  # Blocks until window closed
```

**Web Interface**
```python
from app import app, socketio

# Start web server
socketio.run(app, host='0.0.0.0', port=5000)
```

### Dependencies

**Backend**
- `flask` - Web framework
- `flask-socketio` - WebSocket support
- `flask-cors` - CORS handling

**Frontend**
- `react` - UI framework
- `@mui/material` - Material Design components
- `socket.io-client` - WebSocket client
- `vite` - Build tool

### Usage Example

**Legacy GUI**
```python
from gui import ConfigGUI
from settings import load_settings, save_settings

# Load settings
settings = load_settings()

# Show GUI
gui = ConfigGUI(settings)
gui.run()

# Settings are automatically saved when GUI closes
```

**Web Interface**
```bash
# Start backend
python app.py

# Or use startup script
./start_web.sh  # Linux/Mac
start_web.bat   # Windows

# Access at http://localhost:5000
```

---

## Phase Integration

### Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                      Event Flow                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  TikTok Event                                               │
│       │                                                      │
│       ├──► Phase 4: Event Processing                        │
│       │         ├──► Deduplication                          │
│       │         └──► Viewer Tracking                        │
│       │                                                      │
│       ├──► Phase 2: Memory                                  │
│       │         └──► Store Event                            │
│       │                                                      │
│       ├──► Phase 5: Response Generation                     │
│       │         ├──► Relevance Scoring                      │
│       │         └──► AI Response                            │
│       │                                                      │
│       ├──► Phase 6: Message Batching                        │
│       │         └──► Queue Message                          │
│       │                                                      │
│       ├──► Phase 3: Speech State                            │
│       │         └──► Check Mic Active                       │
│       │                                                      │
│       └──► Phase 7: GUI/Web                                 │
│                   └──► Display Event                        │
│                                                              │
│  Animaze Output ◄─── Batched Messages                       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Component Dependencies

```
Phase 1 (Settings)
    └──► All Phases (configuration)

Phase 2 (Memory)
    ├──► Phase 5 (context generation)
    └──► Phase 4 (user tracking)

Phase 3 (Speech)
    └──► Phase 6 (pause detection)

Phase 4 (Events)
    ├──► Phase 2 (store events)
    └──► Phase 5 (event data)

Phase 5 (Response)
    ├──► Phase 2 (user context)
    └──► Phase 6 (output queue)

Phase 6 (Outbox)
    └──► Phase 3 (timing)

Phase 7 (GUI)
    └──► All Phases (monitoring/control)
```

### Startup Sequence

1. **Phase 1**: Load settings from disk
2. **Phase 2**: Load memory with decay cleanup
3. **Phase 3**: Initialize microphone monitoring
4. **Phase 4**: Create event deduplicator
5. **Phase 5**: Initialize response engine
6. **Phase 6**: Create message batcher
7. **Phase 7**: Start GUI/Web interface
8. Connect to TikTok and Animaze
9. Begin event processing loop

---

## Best Practices

### Adding New Features

1. **Identify the appropriate phase** for your feature
2. **Update the module** with new functionality
3. **Update documentation** (this file and module docstrings)
4. **Add tests** for new functionality
5. **Update configuration** if needed (Phase 1)

### Modifying Existing Features

1. **Understand the phase dependencies**
2. **Make minimal changes** to interfaces
3. **Test all dependent phases**
4. **Update documentation**

### Testing Phases

Each phase should be testable independently:

```python
# Test Phase 1 (Settings)
from settings import load_settings
settings = load_settings()
assert "tiktok" in settings

# Test Phase 2 (Memory)
from memory import load_memory, remember_event
memory = load_memory("test_memory.json", 90)
remember_event(memory, "test_user", "comment", "test")
assert "test_user" in memory["users"]

# Test Phase 5 (Response)
from response import Relevance
relevance = Relevance({"keywords_bonus": ["why", "how"]})
score = relevance.score("Why is the sky blue?")
assert score > 0.5
```

---

## Performance Considerations

### Phase 1 (Settings)
- Settings loaded once at startup
- Saves are infrequent (user-initiated)
- Minimal performance impact

### Phase 2 (Memory)
- Deque-based history limits memory growth
- Periodic cleanup removes stale data
- Save frequency configurable

### Phase 3 (Speech)
- Real-time audio processing in background thread
- Efficient numpy-based calculations
- Configurable chunk size for CPU/latency tradeoff

### Phase 4 (Events)
- O(1) signature checking with TTL cleanup
- Automatic expiration prevents memory growth
- Lightweight string-based signatures

### Phase 5 (Response)
- LRU cache for repeated queries
- Async OpenAI calls (non-blocking)
- Configurable request timeout

### Phase 6 (Outbox)
- Minimal memory (few queued messages)
- O(1) add/flush operations
- Duplicate checking prevents spam

### Phase 7 (GUI)
- Web interface: React performance optimization
- WebSocket for efficient real-time updates
- Legacy GUI: Tkinter event loop

---

## Security Considerations

### Phase 1 (Settings)
- API keys stored in plaintext (consider encryption)
- File permissions should be restrictive

### Phase 2 (Memory)
- Personal data stored (consider GDPR compliance)
- Automatic decay helps with data retention

### Phase 3 (Speech)
- No audio is recorded or stored
- Only real-time level detection

### Phase 4 (Events)
- SHA1 hashing for signatures (not cryptographic use)
- No sensitive data in signatures

### Phase 5 (Response)
- OpenAI API calls include user data
- Consider data privacy policies

### Phase 6 (Outbox)
- No security concerns (temporary storage)

### Phase 7 (GUI)
- Web interface: CORS configuration important
- Consider authentication for public deployments

---

## Troubleshooting

### Phase 1 Issues
- **Settings not loading**: Check file permissions, JSON/YAML syntax
- **Defaults not working**: Verify DEFAULT_SETTINGS structure

### Phase 2 Issues
- **Memory file corrupt**: Delete and restart (auto-creates)
- **High memory usage**: Decrease per_user_history or decay_days

### Phase 3 Issues
- **Mic not detected**: Check device name, permissions
- **High CPU usage**: Increase chunk_time

### Phase 4 Issues
- **Duplicate events**: Decrease TTL or check signature generation
- **Missing greetings**: Check cooldown settings

### Phase 5 Issues
- **No responses**: Check threshold, OpenAI key, quota
- **Wrong responses**: Adjust system_prompt in settings

### Phase 6 Issues
- **Messages delayed**: Check batch_window
- **Too many messages**: Decrease max batch size

### Phase 7 Issues
- **Web UI not loading**: Check port, frontend build
- **Legacy GUI crashes**: Check Tkinter installation

---

## Future Enhancements

### Potential Improvements

1. **Phase 1**: Add settings validation schema
2. **Phase 2**: Implement database backend option
3. **Phase 3**: Add support for more audio backends
4. **Phase 4**: Add event analytics and statistics
5. **Phase 5**: Add more AI providers (Anthropic, etc.)
6. **Phase 6**: Add message templating system
7. **Phase 7**: Add mobile app interface

---

## Conclusion

The 7-phase architecture provides:
- ✅ Clear separation of concerns
- ✅ Independent testability
- ✅ Easy extensibility
- ✅ Maintainable codebase
- ✅ Production-ready design

Each phase is well-documented, has clear interfaces, and can be modified independently while maintaining system integrity.
