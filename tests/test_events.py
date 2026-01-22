"""
Tests for Phase 4: Event Processing (events.py)
"""
import time
from events import EventDeduper, make_signature, touch_viewer, schedule_greeting


def test_make_signature():
    """Test event signature generation."""
    sig1 = make_signature("comment", "user1", "Hello")
    sig2 = make_signature("comment", "user1", "Hello")
    sig3 = make_signature("comment", "user1", "Different")
    
    # Same input should produce same signature
    assert sig1 == sig2
    
    # Different input should produce different signature
    assert sig1 != sig3


def test_event_deduper():
    """Test event deduplication."""
    deduper = EventDeduper(ttl_seconds=10)
    
    # First event should be new
    assert deduper.add("event1") is True
    
    # Same event should be duplicate
    assert deduper.add("event1") is False
    
    # Different event should be new
    assert deduper.add("event2") is True


def test_event_deduper_expiration():
    """Test that events expire after TTL."""
    deduper = EventDeduper(ttl_seconds=1)
    
    # Add event
    assert deduper.add("event1") is True
    
    # Immediately duplicate
    assert deduper.add("event1") is False
    
    # Wait for expiration
    time.sleep(2)
    
    # Should be new again after expiration
    assert deduper.add("event1") is True


def test_touch_viewer():
    """Test viewer tracking."""
    viewers = {}
    now = time.time()
    
    touch_viewer(viewers, "user1", now)
    
    assert "user1" in viewers
    assert viewers["user1"] == now


def test_schedule_greeting():
    """Test greeting scheduling."""
    viewers = {}
    now = time.time()
    
    # First join should trigger greeting
    assert schedule_greeting(viewers, "user1", now, cooldown=300) is True
    
    # Immediate rejoin should not trigger greeting (cooldown)
    assert schedule_greeting(viewers, "user1", now + 1, cooldown=300) is False
    
    # After cooldown should trigger greeting
    assert schedule_greeting(viewers, "user1", now + 301, cooldown=300) is True


def test_schedule_greeting_new_user():
    """Test that new users always get greeting."""
    viewers = {}
    now = time.time()
    
    # First time should always greet
    assert schedule_greeting(viewers, "new_user", now, cooldown=300) is True
    
    # Verify user was added to viewers
    assert "new_user" in viewers
