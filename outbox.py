"""
Outbox batching module for grouping messages before sending.
"""

import asyncio
import logging
import time
from typing import Callable, List, Tuple

log = logging.getLogger("ChatPalBrain")


class OutboxBatcher:
    """
    Batches messages together based on priority, time window, and size limits.
    """
    
    def __init__(
        self,
        window_s: int,
        max_items: int,
        max_chars: int,
        sep: str,
        send_callback: Callable,
        speech_state,
        mic_state
    ) -> None:
        """
        Initialize outbox batcher.
        
        Args:
            window_s: Time window in seconds before flushing
            max_items: Maximum number of items before flushing
            max_chars: Maximum characters before flushing
            sep: Separator string between items
            send_callback: Async callback to send messages
            speech_state: SpeechState instance
            mic_state: MicState instance
        """
        self.window_s = window_s
        self.max_items = max_items
        self.max_chars = max_chars
        self.sep = sep
        self.send_callback = send_callback
        self.speech_state = speech_state
        self.mic_state = mic_state
        self.buffer: List[Tuple[int, str]] = []
        self.first_ts = None
        self._lock = asyncio.Lock()
    
    async def add(self, text: str, priority: int = 1) -> None:
        """
        Add a message to the batch.
        
        Args:
            text: Message text to add
            priority: Priority level (higher = more important)
        """
        if not text:
            return
        
        async with self._lock:
            # Add priority to the item
            self.buffer.append((priority, text.strip()))
            if self.first_ts is None:
                self.first_ts = time.time()
            
            # Sort by priority (higher priority first)
            self.buffer.sort(key=lambda x: x[0], reverse=True)
            
            # Check if we need to flush
            texts = [item[1] for item in self.buffer]
            joined = self.sep.join(texts)
            if len(joined) > self.max_chars or len(self.buffer) >= self.max_items:
                await self._flush_locked()
            else:
                log.info(f"Batch add (priority={priority}): {text}")
    
    async def worker(self) -> None:
        """
        Background worker that periodically flushes the batch.
        """
        while True:
            await asyncio.sleep(0.25)
            if self.mic_state.is_active() or self.speech_state.is_speaking():
                continue
            
            async with self._lock:
                if not self.buffer:
                    continue
                if (time.time() - (self.first_ts or time.time())) >= self.window_s:
                    await self._flush_locked()
    
    async def _flush_locked(self) -> None:
        """
        Flush the batch buffer (must be called while holding lock).
        """
        if not self.buffer:
            return
        
        # Extract texts in priority order
        texts = [item[1] for item in self.buffer]
        payload = self.sep.join(texts)
        self.buffer.clear()
        self.first_ts = None
        
        log.info(f"Batch flush → {payload}")
        await self.send_callback(payload)
