"""
Tests for Phase 6: Message Batching (outbox.py)
"""
import time
from outbox import OutboxBatcher


def test_outbox_add_and_flush():
    """Test basic add and flush operations."""
    batcher = OutboxBatcher(batch_window=10)
    
    batcher.add("Message 1")
    batcher.add("Message 2")
    
    batch = batcher.flush()
    
    assert len(batch) == 2
    assert "Message 1" in batch
    assert "Message 2" in batch


def test_outbox_priority():
    """Test that high priority messages come first."""
    batcher = OutboxBatcher(batch_window=10)
    
    batcher.add("Normal", priority=False)
    batcher.add("Important", priority=True)
    batcher.add("Another normal", priority=False)
    
    batch = batcher.flush()
    
    # High priority should be first
    assert batch[0] == "Important"


def test_outbox_deduplication():
    """Test that duplicate messages are removed."""
    batcher = OutboxBatcher(batch_window=10)
    
    batcher.add("Hello")
    batcher.add("Hello")  # Duplicate
    batcher.add("World")
    
    batch = batcher.flush()
    
    # Should only have 2 unique messages
    assert len(batch) == 2
    assert "Hello" in batch
    assert "World" in batch


def test_outbox_max_batch_size():
    """Test that batch size is limited."""
    batcher = OutboxBatcher(batch_window=10)
    
    # Add more than max batch size (10)
    for i in range(15):
        batcher.add(f"Message {i}")
    
    batch = batcher.flush()
    
    # Should be limited to 10
    assert len(batch) <= 10


def test_outbox_empty_flush():
    """Test that flushing empty batcher returns empty list."""
    batcher = OutboxBatcher(batch_window=10)
    
    batch = batcher.flush()
    
    assert batch == []


def test_outbox_size():
    """Test size tracking."""
    batcher = OutboxBatcher(batch_window=10)
    
    assert batcher.size() == 0
    
    batcher.add("Message 1")
    assert batcher.size() == 1
    
    batcher.add("Message 2", priority=True)
    assert batcher.size() == 2
    
    batcher.flush()
    assert batcher.size() == 0


def test_outbox_clears_after_flush():
    """Test that batcher is empty after flush."""
    batcher = OutboxBatcher(batch_window=10)
    
    batcher.add("Message 1")
    batcher.add("Message 2")
    
    batch1 = batcher.flush()
    assert len(batch1) == 2
    
    # Second flush should be empty
    batch2 = batcher.flush()
    assert len(batch2) == 0
