"""
Tests for Phase 4: Event Processing (events.py)
"""
import time
from events import make_signature, touch_viewer


def test_make_signature():
    """Test event signature generation."""
    sig1 = make_signature("comment", "user1", "Hello")
    sig2 = make_signature("comment", "user1", "Hello")
    sig3 = make_signature("comment", "user1", "Different")
    
    # Same input should produce same signature
    assert sig1 == sig2
    
    # Different input should produce different signature
    assert sig1 != sig3
    
    # Should return hex string
    assert len(sig1) == 40  # SHA1 hex is 40 characters


def test_make_signature_prefix():
    """Test that signature includes prefix."""
    sig1 = make_signature("comment", "user1", "text")
    sig2 = make_signature("gift", "user1", "text")
    
    # Different prefix should produce different signature
    assert sig1 != sig2


def test_touch_viewer_creates_new():
    """Test creating new viewer entry."""
    viewers = {}
    
    result = touch_viewer(viewers, "user1", "John")
    
    assert "user1" in viewers
    assert viewers["user1"]["nick"] == "John"
    assert "joined" in viewers["user1"]
    assert "last_active" in viewers["user1"]
    assert viewers["user1"]["greeted"] is False


def test_touch_viewer_updates_existing():
    """Test updating existing viewer."""
    viewers = {}
    
    # Create viewer
    result1 = touch_viewer(viewers, "user1", "John")
    time1 = result1["last_active"]
    
    # Wait a bit
    time.sleep(0.1)
    
    # Update viewer
    result2 = touch_viewer(viewers, "user1", "Johnny")
    time2 = result2["last_active"]
    
    # Should have updated
    assert viewers["user1"]["nick"] == "Johnny"
    assert time2 > time1
    assert result2["joined"] == result1["joined"]  # Joined time unchanged


def test_touch_viewer_returns_dict():
    """Test that touch_viewer returns viewer dict."""
    viewers = {}
    
    result = touch_viewer(viewers, "user1", "John")
    
    assert isinstance(result, dict)
    assert "nick" in result
    assert "joined" in result
    assert "last_active" in result
    assert "greeted" in result
