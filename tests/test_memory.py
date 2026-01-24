"""
Tests for Memory System with SQLite backend (memory.py)
"""
import asyncio
import os
import tempfile
import time
import pytest
import pytest_asyncio
from memory import MemoryDB, UserModel


@pytest_asyncio.fixture
async def memory_db():
    """Create a temporary memory database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_memory.db")
        db = MemoryDB(db_path=db_path, per_user_history=10)
        await db.initialize()
        yield db
        await db.close()


@pytest.mark.asyncio
async def test_memory_db_initialization():
    """Test that MemoryDB initializes correctly."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_memory.db")
        db = MemoryDB(db_path=db_path)
        await db.initialize()
        
        # Check that database file was created
        assert os.path.exists(db_path)
        
        # Check initial user count is 0
        count = await db.get_user_count()
        assert count == 0
        
        await db.close()


@pytest.mark.asyncio
async def test_get_user_creates_new(memory_db):
    """Test that get_user creates new user if doesn't exist."""
    user = await memory_db.get_user("test_user")
    
    assert user is not None
    assert user.uid == "test_user"
    assert user.first_seen > 0
    assert user.last_seen > 0
    assert user.nickname == ""
    assert user.likes == 0
    assert user.gifts == 0


@pytest.mark.asyncio
async def test_get_user_returns_existing(memory_db):
    """Test that get_user returns existing user."""
    # Create user first
    user1 = await memory_db.get_user("test_user")
    original_first_seen = user1.first_seen
    
    # Wait a moment
    await asyncio.sleep(0.01)
    
    # Get user again
    user2 = await memory_db.get_user("test_user")
    
    # Should have same first_seen (same user)
    assert user2.first_seen == original_first_seen
    assert user2.uid == "test_user"


@pytest.mark.asyncio
async def test_remember_event_message(memory_db):
    """Test that events with messages are stored correctly."""
    await memory_db.remember_event("test_user", nickname="TestNick", message="Hello world")
    
    user = await memory_db.get_user("test_user")
    assert user.nickname == "TestNick"
    assert len(user.messages) == 1
    assert user.messages[0] == "Hello world"


@pytest.mark.asyncio
async def test_remember_event_increments(memory_db):
    """Test that event increments work correctly."""
    await memory_db.remember_event("test_user", like_inc=5, gift_inc=2)
    user = await memory_db.get_user("test_user")
    
    assert user.likes == 5
    assert user.gifts == 2
    
    # Increment again
    await memory_db.remember_event("test_user", like_inc=3, gift_inc=1)
    user = await memory_db.get_user("test_user")
    
    assert user.likes == 8
    assert user.gifts == 3


@pytest.mark.asyncio
async def test_remember_event_flags(memory_db):
    """Test that boolean event flags work correctly."""
    await memory_db.remember_event("test_user", follow=True, sub=True)
    user = await memory_db.get_user("test_user")
    
    assert user.follows == 1
    assert user.subs == 1
    
    # Trigger again
    await memory_db.remember_event("test_user", follow=True, share=True)
    user = await memory_db.get_user("test_user")
    
    assert user.follows == 2
    assert user.subs == 1
    assert user.shares == 1


@pytest.mark.asyncio
async def test_message_history_limit(memory_db):
    """Test that message history respects per_user_history limit."""
    # Add 15 messages (limit is 10)
    for i in range(15):
        await memory_db.remember_event("test_user", message=f"Message {i}")
    
    user = await memory_db.get_user("test_user")
    
    # Should only keep last 10
    assert len(user.messages) == 10
    assert user.messages[0] == "Message 5"
    assert user.messages[-1] == "Message 14"


@pytest.mark.asyncio
async def test_background_info(memory_db):
    """Test background info generation."""
    await memory_db.remember_event(
        "test_user",
        background={"hobby": "gaming", "location": "Berlin"}
    )
    
    info = await memory_db.get_background_info("test_user")
    
    assert "hobby=gaming" in info
    assert "location=Berlin" in info


@pytest.mark.asyncio
async def test_background_info_truncation(memory_db):
    """Test that long background values are truncated."""
    long_value = "x" * 100
    await memory_db.remember_event(
        "test_user",
        background={"data": long_value}
    )
    
    info = await memory_db.get_background_info("test_user")
    
    # Should be truncated to 48 chars + ellipsis
    assert len(info) < len(long_value)
    assert "…" in info


@pytest.mark.asyncio
async def test_clean_old_users(memory_db):
    """Test that old user data is removed."""
    # Create an old user
    old_user = UserModel(
        uid="old_user",
        first_seen=time.time() - (100 * 86400),  # 100 days ago
        last_seen=time.time() - (100 * 86400)
    )
    await memory_db.save_user(old_user)
    
    # Create a recent user
    await memory_db.remember_event("recent_user", message="Hello")
    
    # Check both exist
    count_before = await memory_db.get_user_count()
    assert count_before == 2
    
    # Clean with 90-day decay
    removed = await memory_db.clean_old_users(decay_days=90)
    
    assert removed == 1
    
    # Old user should be gone
    count_after = await memory_db.get_user_count()
    assert count_after == 1
    
    # Recent user should still exist
    recent = await memory_db.get_user("recent_user")
    assert recent.uid == "recent_user"


@pytest.mark.asyncio
async def test_user_model_validation():
    """Test that UserModel validates data correctly."""
    # Valid user
    user = UserModel(
        uid="test_user",
        first_seen=time.time(),
        last_seen=time.time()
    )
    assert user.uid == "test_user"
    
    # Test default values
    assert user.likes == 0
    assert user.messages == []
    assert user.background == {}


@pytest.mark.asyncio
async def test_concurrent_access(memory_db):
    """Test that concurrent access is handled safely."""
    async def update_user(uid: str, count: int):
        for i in range(count):
            await memory_db.remember_event(uid, like_inc=1)
    
    # Run multiple concurrent updates
    await asyncio.gather(
        update_user("test_user", 10),
        update_user("test_user", 10),
        update_user("test_user", 10)
    )
    
    user = await memory_db.get_user("test_user")
    # Should have 30 likes total
    assert user.likes == 30
