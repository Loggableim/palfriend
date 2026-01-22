"""
Tests for Phase 6: Message Batching (outbox.py)
"""
import asyncio
import pytest
from speech import SpeechState, MicState
from outbox import OutboxBatcher


@pytest.fixture
def mock_send_callback():
    """Mock send callback that stores sent messages."""
    sent_messages = []
    
    async def callback(text):
        sent_messages.append(text)
    
    callback.sent_messages = sent_messages
    return callback


@pytest.fixture
def mock_states():
    """Create mock speech and mic states."""
    speech_state = SpeechState.IDLE
    mic_state = MicState()
    return speech_state, mic_state


@pytest.mark.asyncio
async def test_outbox_initialization(mock_send_callback, mock_states):
    """Test basic outbox initialization."""
    speech_state, mic_state = mock_states
    
    batcher = OutboxBatcher(
        window_s=10,
        max_items=10,
        max_chars=1000,
        sep=" ",
        send_callback=mock_send_callback,
        speech_state=speech_state,
        mic_state=mic_state
    )
    
    assert batcher.window_s == 10
    assert batcher.max_items == 10
    assert batcher.max_chars == 1000
    assert len(batcher.buffer) == 0


@pytest.mark.asyncio
async def test_outbox_add_message(mock_send_callback, mock_states):
    """Test adding messages to outbox."""
    speech_state, mic_state = mock_states
    
    batcher = OutboxBatcher(
        window_s=10,
        max_items=10,
        max_chars=1000,
        sep=" ",
        send_callback=mock_send_callback,
        speech_state=speech_state,
        mic_state=mic_state
    )
    
    await batcher.add("Test message", priority=1)
    
    assert len(batcher.buffer) == 1
    assert batcher.buffer[0][1] == "Test message"


@pytest.mark.asyncio
async def test_outbox_priority_ordering(mock_send_callback, mock_states):
    """Test that messages are ordered by priority."""
    speech_state, mic_state = mock_states
    
    batcher = OutboxBatcher(
        window_s=10,
        max_items=10,
        max_chars=1000,
        sep=" ",
        send_callback=mock_send_callback,
        speech_state=speech_state,
        mic_state=mic_state
    )
    
    await batcher.add("Normal", priority=1)
    await batcher.add("Important", priority=5)
    await batcher.add("Low", priority=0)
    
    # Buffer should be sorted by priority (high to low)
    assert batcher.buffer[0][1] == "Important"
    assert batcher.buffer[1][1] == "Normal"
    assert batcher.buffer[2][1] == "Low"


@pytest.mark.asyncio
async def test_outbox_max_items_flush(mock_send_callback, mock_states):
    """Test that batch flushes when max items reached."""
    speech_state, mic_state = mock_states
    
    batcher = OutboxBatcher(
        window_s=10,
        max_items=3,
        max_chars=1000,
        sep=" ",
        send_callback=mock_send_callback,
        speech_state=speech_state,
        mic_state=mic_state
    )
    
    # Add messages up to max
    await batcher.add("Message 1", priority=1)
    await batcher.add("Message 2", priority=1)
    await batcher.add("Message 3", priority=1)
    
    # Should have flushed
    assert len(batcher.buffer) == 0
    assert len(mock_send_callback.sent_messages) == 1
    assert "Message 1" in mock_send_callback.sent_messages[0]


@pytest.mark.asyncio
async def test_outbox_empty_text_ignored(mock_send_callback, mock_states):
    """Test that empty text is ignored."""
    speech_state, mic_state = mock_states
    
    batcher = OutboxBatcher(
        window_s=10,
        max_items=10,
        max_chars=1000,
        sep=" ",
        send_callback=mock_send_callback,
        speech_state=speech_state,
        mic_state=mic_state
    )
    
    await batcher.add("", priority=1)
    await batcher.add("   ", priority=1)
    
    # Empty/whitespace messages should be ignored
    # Note: strip() in add() will make whitespace empty
    assert len(batcher.buffer) == 0
