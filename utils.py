"""
Utility functions for text processing and general helpers.
"""

import asyncio
import time
from typing import Dict, Any, List, Optional
import logging

log = logging.getLogger("ChatPalUtils")


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
    return text[:max_length - 1] + "…"


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


def fuzzy_match(text: str, pattern: str, max_distance: int = 2) -> bool:
    """
    Check if text fuzzy matches a pattern using Levenshtein distance.
    
    This allows detecting spam/trigger words even with typos or intentional variations
    like "F0llow", "Folow me", "Follow mee" all matching "Follow me".
    
    Args:
        text: Text to check
        pattern: Pattern to match against
        max_distance: Maximum Levenshtein distance to consider a match
    
    Returns:
        True if text fuzzy matches pattern within max_distance, False otherwise
    """
    try:
        import Levenshtein
        
        # Normalize both strings for comparison
        text_lower = text.lower().strip()
        pattern_lower = pattern.lower().strip()
        
        # Check if pattern appears as substring (exact match)
        if pattern_lower in text_lower:
            return True
        
        # Split text into words and check each word against pattern
        words = text_lower.split()
        for word in words:
            distance = Levenshtein.distance(word, pattern_lower)
            if distance <= max_distance:
                return True
        
        # Also check entire text against pattern
        distance = Levenshtein.distance(text_lower, pattern_lower)
        if distance <= max_distance:
            return True
        
        return False
    except ImportError:
        log.warning("python-Levenshtein not installed, falling back to exact match")
        # Fallback to simple substring match if Levenshtein not available
        return pattern.lower() in text.lower()


class TokenBuffer:
    """
    Token-aware context buffer that manages message history with automatic summarization.
    
    Uses tiktoken to track token count and triggers LLM summarization when approaching
    the token limit, preserving long-term context while freeing tokens.
    """
    
    def __init__(self, max_tokens: int = 4000, model: str = "gpt-3.5-turbo"):
        """
        Initialize token buffer.
        
        Args:
            max_tokens: Maximum number of tokens to maintain in buffer
            model: Model name for token encoding (used by tiktoken)
        """
        self.max_tokens = max_tokens
        self.model = model
        self.messages: List[str] = []
        self._encoding = None
        
        try:
            import tiktoken
            self._encoding = tiktoken.encoding_for_model(model)
            log.info(f"TokenBuffer initialized with tiktoken for {model}")
        except Exception as e:
            log.warning(f"Failed to initialize tiktoken: {e}. Using character approximation.")
            self._encoding = None
    
    def _count_tokens(self, text: str) -> int:
        """
        Count tokens in text.
        
        Args:
            text: Text to count tokens for
        
        Returns:
            Number of tokens
        """
        if self._encoding:
            return len(self._encoding.encode(text))
        else:
            # Fallback: approximate 1 token = 4 characters
            return len(text) // 4
    
    def add_message(self, message: str) -> None:
        """
        Add a message to the buffer.
        
        Args:
            message: Message text to add
        """
        self.messages.append(message)
    
    def get_total_tokens(self) -> int:
        """
        Get total tokens in buffer.
        
        Returns:
            Total number of tokens
        """
        return sum(self._count_tokens(msg) for msg in self.messages)
    
    def needs_summarization(self) -> bool:
        """
        Check if buffer needs summarization.
        
        Returns:
            True if current token count exceeds 80% of max_tokens
        """
        return self.get_total_tokens() > (self.max_tokens * 0.8)
    
    def get_messages_for_summarization(self) -> List[str]:
        """
        Get oldest 50% of messages for summarization.
        
        Returns:
            List of messages to summarize
        """
        split_point = len(self.messages) // 2
        return self.messages[:split_point]
    
    def replace_with_summary(self, summary: str) -> None:
        """
        Replace oldest 50% of messages with a summary.
        
        Args:
            summary: Summary text to replace old messages with
        """
        split_point = len(self.messages) // 2
        summary_message = f"SUMMARY: {summary}"
        self.messages = [summary_message] + self.messages[split_point:]
        log.info(f"Replaced {split_point} messages with summary. Buffer now has {len(self.messages)} entries.")
    
    def get_all_messages(self) -> List[str]:
        """
        Get all messages in buffer.
        
        Returns:
            List of all messages
        """
        return self.messages.copy()
    
    def clear(self) -> None:
        """Clear all messages from buffer."""
        self.messages.clear()
