"""
Tests for Phase 2: Memory System (memory.py)
"""
import os
import tempfile
import time
from memory import load_memory, save_memory, remember_event, get_user, get_background_info


def test_load_memory_creates_new():
    """Test that load_memory creates new memory when file doesn't exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        memory_file = os.path.join(tmpdir, "test_memory.json")
        memory = load_memory(memory_file, decay_days=90)
        
        assert "users" in memory
        assert "created" in memory
        assert len(memory["users"]) == 0


def test_remember_event():
    """Test that events are stored correctly."""
    memory = {"users": {}, "created": time.time()}
    
    remember_event(memory, "test_user", "comment", "Hello world")
    
    assert "test_user" in memory["users"]
    user = memory["users"]["test_user"]
    assert len(user["comments"]) == 1
    assert user["comments"][0] == "Hello world"


def test_get_user_creates_new():
    """Test that get_user creates new user if doesn't exist."""
    memory = {"users": {}, "created": time.time()}
    
    user = get_user(memory, "new_user")
    
    assert user is not None
    assert "first_seen" in user
    assert "last_seen" in user
    assert "comments" in user


def test_get_background_info():
    """Test background info generation."""
    memory = {"users": {}, "created": time.time()}
    
    remember_event(memory, "test_user", "comment", "Hello")
    remember_event(memory, "test_user", "comment", "How are you?")
    remember_event(memory, "test_user", "gift", "Rose")
    
    info = get_background_info(memory, "test_user")
    
    assert "test_user" in info
    assert "2 comments" in info
    assert "1 gifts" in info


def test_memory_decay():
    """Test that old user data is removed."""
    with tempfile.TemporaryDirectory() as tmpdir:
        memory_file = os.path.join(tmpdir, "test_memory.json")
        
        # Create memory with old user
        memory = {
            "users": {
                "old_user": {
                    "first_seen": time.time() - (100 * 86400),  # 100 days ago
                    "last_seen": time.time() - (100 * 86400),
                    "comments": []
                },
                "recent_user": {
                    "first_seen": time.time(),
                    "last_seen": time.time(),
                    "comments": []
                }
            },
            "created": time.time()
        }
        
        save_memory(memory, memory_file)
        
        # Load with 90-day decay
        loaded = load_memory(memory_file, decay_days=90)
        
        # Old user should be removed
        assert "old_user" not in loaded["users"]
        assert "recent_user" in loaded["users"]
