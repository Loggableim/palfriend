# Contributing to PalFriend

Thank you for your interest in contributing to PalFriend! This guide will help you get started with development and ensure your contributions align with the project's standards.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Environment Setup](#development-environment-setup)
- [Using GitHub Copilot](#using-github-copilot)
- [Coding Conventions](#coding-conventions)
- [Testing Strategy](#testing-strategy)
- [Pull Request Process](#pull-request-process)
- [Project Structure](#project-structure)

## Getting Started

### Prerequisites

- Python 3.8 or higher (Python 3.12 recommended)
- Node.js 16 or higher
- Git
- A code editor (VS Code recommended for GitHub Copilot integration)

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/palfriend.git
   cd palfriend
   ```
3. Add the upstream repository:
   ```bash
   git remote add upstream https://github.com/mycommunity/palfriend.git
   ```

## Development Environment Setup

### Python Backend Setup

1. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install development tools (optional):
   ```bash
   pip install pytest pytest-asyncio black flake8 mypy
   ```

### React Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

### Running the Application

#### Development Mode (Backend + Frontend separate)

Terminal 1 - Backend:
```bash
python app.py
```

Terminal 2 - Frontend:
```bash
cd frontend
npm run dev
```

#### Production Mode

```bash
./start_web.sh  # Linux/Mac
start_web.bat   # Windows
```

## Using GitHub Copilot

GitHub Copilot is a powerful AI pair programmer that can significantly speed up development. Here's how to use it effectively with PalFriend:

### Setup GitHub Copilot

1. Install the GitHub Copilot extension in VS Code
2. Sign in with your GitHub account
3. Ensure Copilot is enabled for the workspace

### Best Practices

#### 1. Write Clear Comments

Copilot works best when you provide context through comments:

```python
# Function to process TikTok comments and generate AI responses
# Takes a comment text, user ID, and nickname
# Returns a relevance score and generated response
def process_comment(text: str, uid: str, nickname: str) -> tuple[float, str]:
```

#### 2. Use Descriptive Variable Names

```python
# Good - Copilot understands intent
user_cooldown_seconds = 30
tiktok_comment_text = event.comment.strip()

# Less helpful
cd = 30
txt = e.c.strip()
```

#### 3. Leverage Type Hints

Type hints help Copilot suggest better completions:

```python
from typing import Dict, Any, Optional

def load_user_memory(user_id: str, memory: Dict[str, Any]) -> Optional[Dict]:
    """Load user data from memory storage."""
```

#### 4. Break Down Complex Logic

For complex features, write step-by-step comments and let Copilot help:

```python
# Step 1: Check if user is on cooldown
# Step 2: Calculate relevance score for comment
# Step 3: Generate AI response if score is above threshold
# Step 4: Queue response for batching
# Step 5: Update user cooldown timestamp
```

#### 5. Review Suggestions Carefully

Always review Copilot's suggestions:
- Ensure they follow project conventions
- Check for security issues (API keys, user data handling)
- Verify async/await patterns are correct
- Test the suggested code

### Common Copilot Patterns in PalFriend

#### Async Event Handlers

```python
@client.on(CommentEvent)
async def on_comment(evt: CommentEvent):
    """Handle TikTok comment events."""
    # Copilot will suggest event processing logic
```

#### WebSocket Communication

```python
async def send_to_animaze(text: str, cfg: Dict[str, Any]) -> None:
    """Send message to Animaze via WebSocket."""
    # Copilot understands WebSocket patterns
```

#### Configuration Management

```python
def validate_settings(cfg: Dict[str, Any]) -> bool:
    """Validate configuration dictionary."""
    # Copilot will suggest validation logic
```

## Coding Conventions

### Python Style Guide

We follow [PEP 8](https://pep8.org/) with these specific guidelines:

#### 1. Type Annotations

Always use type hints for function parameters and return values:

```python
def remember_event(
    memory: Dict[str, Any],
    cfg: Dict[str, Any],
    uid: str,
    nickname: str = "",
    message: str = "",
    gift_inc: int = 0
) -> None:
    """Remember a user event in memory."""
```

#### 2. Docstrings

Use Google-style docstrings:

```python
def process_queue(items: List[str], max_size: int = 100) -> List[str]:
    """
    Process items from queue with size limit.
    
    Args:
        items: List of items to process
        max_size: Maximum number of items to process
    
    Returns:
        List of processed items
    
    Raises:
        ValueError: If max_size is negative
    """
```

#### 3. Naming Conventions

- **Functions/Methods**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_CASE`
- **Private members**: `_leading_underscore`

```python
class EventDeduper:
    """Deduplicate TikTok events."""
    
    MAX_CACHE_SIZE = 10000
    
    def __init__(self, ttl: int):
        self._cache: Dict[str, float] = {}
        self.ttl = ttl
    
    async def seen(self, signature: str) -> bool:
        """Check if event was already seen."""
```

#### 4. Imports

Group imports in this order:
1. Standard library
2. Third-party packages
3. Local modules

```python
import asyncio
import time
from typing import Dict, Any

import websockets
from TikTokLive import TikTokLiveClient

from settings import load_settings
from memory import load_memory
```

#### 5. String Formatting

Use f-strings for string formatting:

```python
# Good
log.info(f"Connected to {host}:{port}")

# Avoid
log.info("Connected to {}:{}".format(host, port))
log.info("Connected to %s:%s" % (host, port))
```

#### 6. Error Handling

Be specific about exceptions and log appropriately:

```python
try:
    result = await process_data(data)
except ValueError as e:
    log.error(f"Invalid data format: {e}")
    raise
except ConnectionError as e:
    log.warning(f"Connection lost: {e}")
    await reconnect()
except Exception as e:
    log.error(f"Unexpected error: {e}", exc_info=True)
```

### JavaScript/React Style Guide

#### 1. Component Structure

```jsx
import React, { useState, useEffect } from 'react';
import { Box, Typography } from '@mui/material';

/**
 * Dashboard component showing application status and statistics.
 */
const Dashboard = ({ onStart, onStop }) => {
  const [status, setStatus] = useState('stopped');
  
  useEffect(() => {
    // Effect logic here
  }, []);
  
  return (
    <Box>
      <Typography variant="h4">Dashboard</Typography>
    </Box>
  );
};

export default Dashboard;
```

#### 2. Naming Conventions

- **Components**: `PascalCase`
- **Functions/Variables**: `camelCase`
- **Constants**: `UPPER_CASE`
- **Files**: Match component name

#### 3. Hooks

Use hooks for state and side effects:

```jsx
// State management
const [data, setData] = useState(null);

// Side effects
useEffect(() => {
  fetchData();
}, [dependency]);

// Custom hooks
const useWebSocket = (url) => {
  // Hook logic
};
```

## Testing Strategy

### Python Backend Testing

#### Unit Tests

Create test files next to the modules they test:

```
palfriend/
  ├── memory.py
  ├── memory_test.py  (if tests exist)
  ├── settings.py
  └── settings_test.py  (if tests exist)
```

Test structure:

```python
import pytest
from memory import load_memory, save_memory, remember_event

def test_load_memory_creates_default():
    """Test that load_memory creates default structure."""
    memory = load_memory("nonexistent.json", decay_days=90)
    assert "users" in memory
    assert "metadata" in memory

@pytest.mark.asyncio
async def test_remember_event():
    """Test event remembering."""
    memory = {"users": {}}
    cfg = {"per_user_history": 10}
    remember_event(memory, cfg, "user123", nickname="Test", message="Hello")
    assert "user123" in memory["users"]
```

#### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest memory_test.py
```

### Frontend Testing

#### Component Tests

```jsx
import { render, screen } from '@testing-library/react';
import Dashboard from './Dashboard';

test('renders dashboard title', () => {
  render(<Dashboard />);
  const titleElement = screen.getByText(/Dashboard/i);
  expect(titleElement).toBeInTheDocument();
});
```

#### Running Frontend Tests

```bash
cd frontend
npm test
```

### Integration Testing

Test the full stack:

1. Start the backend: `python app.py`
2. Build the frontend: `cd frontend && npm run build`
3. Test API endpoints: `curl http://localhost:5008/api/status`
4. Test WebSocket connection in browser console

### Manual Testing Checklist

Before submitting a PR, verify:

- [ ] Application starts without errors
- [ ] Settings can be saved and loaded
- [ ] WebSocket connection works
- [ ] Real-time updates appear in UI
- [ ] Theme switching works
- [ ] Language switching works
- [ ] All buttons and controls function
- [ ] Responsive design works on mobile

## Pull Request Process

### Before Submitting

1. **Update from upstream**:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run linters**:
   ```bash
   # Python
   black *.py
   flake8 *.py
   
   # JavaScript
   cd frontend
   npm run lint
   ```

3. **Test your changes**:
   ```bash
   # Backend
   python app.py
   
   # Frontend
   cd frontend
   npm run build
   ```

4. **Commit with clear messages**:
   ```bash
   git commit -m "feat: Add user notification system"
   git commit -m "fix: Resolve WebSocket reconnection issue"
   git commit -m "docs: Update API documentation"
   ```

### PR Guidelines

1. **Title**: Use conventional commits format
   - `feat:` for new features
   - `fix:` for bug fixes
   - `docs:` for documentation
   - `refactor:` for code improvements
   - `test:` for adding tests
   - `chore:` for maintenance

2. **Description**: Include:
   - What changed and why
   - How to test the changes
   - Screenshots for UI changes
   - Related issue numbers

3. **Size**: Keep PRs focused and reasonably sized
   - One feature or fix per PR
   - Split large changes into multiple PRs

4. **Review**: Address feedback promptly
   - Be open to suggestions
   - Explain your design decisions
   - Make requested changes or discuss alternatives

## Project Structure

### Backend (Python)

```
palfriend/
├── main.py              # Main application entry point (legacy Tkinter GUI)
├── app.py               # Flask web server and API
├── settings.py          # Configuration management
├── memory.py            # User data storage
├── speech.py            # Speech and microphone state
├── events.py            # TikTok event handling
├── utils.py             # Utility functions
├── response.py          # AI response generation
├── outbox.py            # Message batching
├── gui.py               # Legacy Tkinter GUI
└── requirements.txt     # Python dependencies
```

### Frontend (React)

```
frontend/
├── src/
│   ├── components/      # Reusable UI components
│   │   ├── Dashboard.jsx
│   │   ├── Settings.jsx
│   │   ├── Logs.jsx
│   │   └── Events.jsx
│   ├── i18n/           # Internationalization
│   │   ├── config.js
│   │   └── locales/
│   │       ├── en.json
│   │       └── de.json
│   ├── utils/          # API and utility functions
│   │   └── api.js
│   ├── App.jsx         # Main app component
│   └── index.jsx       # Entry point
├── package.json        # Node.js dependencies
└── vite.config.js      # Vite configuration
```

### Configuration Files

- `settings.yaml` - Runtime configuration (created on first run)
- `memory.json` - User interaction history (created on first run)

## Need Help?

- Check existing issues on GitHub
- Read the documentation in README.md, WEB_INTERFACE_README.md, TESTING.md
- Ask questions in pull request comments
- Follow best practices in this guide

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the code, not the person
- Help others learn and grow

Thank you for contributing to PalFriend! 🎉
