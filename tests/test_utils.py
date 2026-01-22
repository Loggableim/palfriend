"""
Tests for Phase 7: Utility Functions (utils.py)
"""
import asyncio
from utils import trim_text, TokenBucket


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
