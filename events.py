"""
Event handling and deduplication for TikTok live events.
"""

import asyncio
import hashlib
import logging
import time
from typing import Dict, Set

log = logging.getLogger("ChatPalBrain")


class EventDeduper:
    """
    Deduplicates events within a time-to-live window.
    """
    
    def __init__(self, ttl: int) -> None:
        """
        Initialize event deduplicator.
        
        Args:
            ttl: Time-to-live in seconds for event signatures
        """
        self.ttl = ttl
        self._store: Dict[str, float] = {}
        self._lock = asyncio.Lock()
    
    async def seen(self, signature: str) -> bool:
        """
        Check if an event signature has been seen recently.
        
        Args:
            signature: Event signature hash
        
        Returns:
            True if event was seen recently, False otherwise
        """
        now = time.time()
        async with self._lock:
            # Remove expired entries periodically
            if len(self._store) > 1000:
                expired = {k for k, v in self._store.items() if v < now}
                for k in expired:
                    del self._store[k]
            
            if signature in self._store:
                return True
            
            self._store[signature] = now + self.ttl
            
            # Keep max size to prevent memory issues
            if len(self._store) > 5000:
                # Remove oldest entries
                sorted_items = sorted(self._store.items(), key=lambda x: x[1])
                to_remove = len(self._store) - 4000
                for k, _ in sorted_items[:to_remove]:
                    del self._store[k]
            
            return False


def make_signature(prefix: str, *parts) -> str:
    """
    Create a unique signature for an event.
    
    Args:
        prefix: Event type prefix
        *parts: Additional parts to include in signature
    
    Returns:
        SHA1 hash of the signature (used for deduplication, not cryptography)
    
    Note:
        SHA1 is used here for fast event deduplication, not for security purposes.
        The hash is not used for authentication or data integrity verification.
    """
    raw = prefix + "|" + "|".join(str(p) for p in parts)
    # SHA1 used for non-cryptographic deduplication only
    return hashlib.sha1(raw.encode("utf-8", errors="ignore"), usedforsecurity=False).hexdigest()  # nosec B324


def touch_viewer(viewers: Dict[str, Dict], uid: str, nick: str = "") -> Dict:
    """
    Update or create viewer tracking information.
    
    Args:
        viewers: Dictionary of active viewers
        uid: User unique ID
        nick: User nickname
    
    Returns:
        Updated viewer dictionary
    """
    now = time.time()
    v = viewers.get(uid, {"nick": nick or uid, "joined": now, "last_active": now, "greeted": False})
    if nick:
        v["nick"] = nick
    v["last_active"] = now
    viewers[uid] = v
    return v


def should_consider_present(viewers: Dict[str, Dict], uid: str, active_ttl_seconds: int) -> bool:
    """
    Check if a viewer should be considered present based on recent activity.
    
    Args:
        viewers: Dictionary of active viewers
        uid: User unique ID
        active_ttl_seconds: Time in seconds to consider viewer active
    
    Returns:
        True if viewer is considered present, False otherwise
    """
    v = viewers.get(uid)
    if not v:
        return False
    return (time.time() - v["last_active"]) <= active_ttl_seconds


async def schedule_greeting(
    uid: str,
    viewers: Dict[str, Dict],
    greet_tasks: Dict[str, asyncio.Task],
    pending_joins: Set[str],
    memory_db,  # MemoryDB instance
    cfg: Dict
) -> None:
    """
    Schedule a greeting for a user after a delay.
    
    Args:
        uid: User unique ID
        viewers: Dictionary of active viewers
        greet_tasks: Dictionary of active greeting tasks
        pending_joins: Set of pending join greetings
        memory_db: MemoryDB instance
        cfg: Main configuration
    """
    if not int(cfg.get("join_rules", {}).get("enabled", 1)):
        return
    
    delay = int(cfg.get("join_rules", {}).get("greet_after_seconds", 30))
    try:
        await asyncio.sleep(delay)
        v = viewers.get(uid)
        if not v:
            return
        if v.get("greeted"):
            return
        
        user = await memory_db.get_user(uid)
        gcool = int(cfg.get("comment", {}).get("greeting_cooldown", 360))
        if time.time() - user.last_greet < gcool:
            return
        
        if not should_consider_present(
            viewers,
            uid,
            int(cfg.get("join_rules", {}).get("active_ttl_seconds", 45))
        ):
            return
        
        v["greeted"] = True
        # Update last_greet time
        user.last_greet = time.time()
        await memory_db.save_user(user)
        pending_joins.add(v["nick"])
        log.info(f"Greet queued (pending summary): {v['nick']}")
    except Exception as e:
        log.error(f"Greet task error uid={uid}: {e}")
    finally:
        greet_tasks.pop(uid, None)
