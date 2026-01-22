"""
Utility functions for text processing and general helpers.
"""

import asyncio
import time
from typing import Dict, Any


def trim_text(text: str, max_length: int) -> str:
    """
    Trim text to maximum length, adding ellipsis if needed.
    
    Args:
        text: Text to trim
        max_length: Maximum allowed length
    
    Returns:
        Trimmed text with ellipsis if truncated
    """
    text = text.strip()
    if len(text) <= max_length:
        return text
    return text[: max_length - 1] + "…"


class TokenBucket:
    """
    Token bucket rate limiter for controlling request frequency.
    """
    
    def __init__(self, capacity: int, rate_per_sec: float) -> None:
        """
        Initialize token bucket.
        
        Args:
            capacity: Maximum number of tokens
            rate_per_sec: Rate at which tokens are refilled per second
        """
        self.capacity = max(1, capacity)
        self.tokens = float(capacity)
        self.rate = float(rate_per_sec)
        self.updated = time.time()
        self._lock = asyncio.Lock()
    
    async def take(self) -> None:
        """
        Take a token from the bucket, waiting if necessary.
        """
        async with self._lock:
            while True:
                now = time.time()
                elapsed = now - self.updated
                self.updated = now
                self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
                
                if self.tokens >= 1.0:
                    self.tokens -= 1.0
                    return
                
                # Calculate wait time and sleep
                need = (1.0 - self.tokens) / self.rate
                await asyncio.sleep(max(0.01, need))
