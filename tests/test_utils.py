"""
Tests for Phase 7: Utility Functions (utils.py)
"""
import asyncio
from utils import trim_text, TokenBucket, fuzzy_match, TokenBuffer


def test_trim_text_no_trim():
    """Test that short text is not trimmed."""
    text = "Short text"
    result = trim_text(text, max_length=100)
    assert result == text


def test_trim_text_trims_long():
    """Test that long text is trimmed."""
    text = "This is a very long text that should be trimmed"
    result = trim_text(text, max_length=20)
    
    assert len(result) <= 20
    assert result.endswith("…")


def test_token_bucket_initialization():
    """Test token bucket initialization."""
    bucket = TokenBucket(capacity=5, rate_per_sec=1.0)
    
    assert bucket.capacity == 5
    assert bucket.tokens == 5.0
    assert bucket.rate == 1.0


def test_token_bucket_has_lock():
    """Test that token bucket has async lock."""
    bucket = TokenBucket(capacity=3, rate_per_sec=1.0)
    
    assert hasattr(bucket, '_lock')
    assert isinstance(bucket._lock, asyncio.Lock)


def test_fuzzy_match_exact():
    """Test fuzzy match with exact match."""
    assert fuzzy_match("Follow me", "follow me") == True
    assert fuzzy_match("Hello world", "hello") == True


def test_fuzzy_match_typo():
    """Test fuzzy match with typos."""
    # Test common spam variations
    assert fuzzy_match("F0llow me", "follow") == True
    assert fuzzy_match("Folow me", "follow") == True
    assert fuzzy_match("Follow mee", "follow") == True


def test_fuzzy_match_no_match():
    """Test fuzzy match when there's no match."""
    assert fuzzy_match("Hello world", "goodbye", max_distance=2) == False
    assert fuzzy_match("Python", "Java", max_distance=1) == False


def test_token_buffer_initialization():
    """Test TokenBuffer initialization."""
    buffer = TokenBuffer(max_tokens=1000, model="gpt-3.5-turbo")
    
    assert buffer.max_tokens == 1000
    assert buffer.model == "gpt-3.5-turbo"
    assert len(buffer.messages) == 0


def test_token_buffer_add_message():
    """Test adding messages to buffer."""
    buffer = TokenBuffer(max_tokens=1000)
    
    buffer.add_message("Hello")
    buffer.add_message("World")
    
    assert len(buffer.messages) == 2
    assert buffer.messages[0] == "Hello"
    assert buffer.messages[1] == "World"


def test_token_buffer_get_total_tokens():
    """Test token counting."""
    buffer = TokenBuffer(max_tokens=1000)
    
    buffer.add_message("Hello world")
    tokens = buffer.get_total_tokens()
    
    # Should have some tokens (exact count depends on tokenizer)
    assert tokens > 0


def test_token_buffer_needs_summarization():
    """Test summarization trigger."""
    buffer = TokenBuffer(max_tokens=100)
    
    # Add messages until we approach limit
    for i in range(50):
        buffer.add_message("This is a test message with some content")
    
    # Should trigger summarization
    assert buffer.needs_summarization() == True


def test_token_buffer_get_messages_for_summarization():
    """Test getting messages for summarization."""
    buffer = TokenBuffer(max_tokens=1000)
    
    buffer.add_message("Message 1")
    buffer.add_message("Message 2")
    buffer.add_message("Message 3")
    buffer.add_message("Message 4")
    
    messages = buffer.get_messages_for_summarization()
    
    # Should return first 50% (2 messages)
    assert len(messages) == 2
    assert messages[0] == "Message 1"
    assert messages[1] == "Message 2"


def test_token_buffer_replace_with_summary():
    """Test replacing messages with summary."""
    buffer = TokenBuffer(max_tokens=1000)
    
    buffer.add_message("Message 1")
    buffer.add_message("Message 2")
    buffer.add_message("Message 3")
    buffer.add_message("Message 4")
    
    buffer.replace_with_summary("Summary of first two messages")
    
    # Should have 3 messages: summary + last 2 original
    assert len(buffer.messages) == 3
    assert buffer.messages[0].startswith("SUMMARY:")
    assert buffer.messages[1] == "Message 3"
    assert buffer.messages[2] == "Message 4"


def test_token_buffer_clear():
    """Test clearing buffer."""
    buffer = TokenBuffer(max_tokens=1000)
    
    buffer.add_message("Message 1")
    buffer.add_message("Message 2")
    
    buffer.clear()
    
    assert len(buffer.messages) == 0
