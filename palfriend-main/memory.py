"""
Memory module for storing and managing user interaction history and data.
"""

import json
import logging
import os
import time
from collections import deque
from typing import Any, Dict

log = logging.getLogger("ChatPalBrain")


def load_memory(path: str, decay_days: int) -> Dict[str, Any]:
    """
    Load memory from file and remove stale user data based on decay period.
    
    Args:
        path: Path to memory file
        decay_days: Number of days after which user data is considered stale
    
    Returns:
        Dictionary containing user memory data
    """
    if not os.path.isfile(path):
        return {"users": {}, "created": time.time()}
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            mem = json.load(f)
        
        # Remove stale user data
        decay_sec = decay_days * 86400
        now = time.time()
        mem["users"] = {
            uid: u
            for uid, u in mem.get("users", {}).items()
            if now - u.get("last_seen", 0) < decay_sec
        }
        
        log.info(f"Loaded memory with {len(mem['users'])} users")
        return mem
    except json.JSONDecodeError as e:
        log.error(f"Memory file corrupt: {e}. Creating new memory.")
        return {"users": {}, "created": time.time()}
    except Exception as e:
        log.error(f"Error loading memory: {e}. Creating new memory.")
        return {"users": {}, "created": time.time()}


def save_memory(mem: Dict[str, Any], path: str) -> None:
    """
    Save memory to file using atomic write operation.
    
    Args:
        mem: Memory dictionary to save
        path: Path to memory file
    """
    try:
        tmp = f"{path}.tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(mem, f, indent=2, ensure_ascii=False)
        os.replace(tmp, path)
    except Exception as e:
        log.error(f"Failed to save memory: {e}")


def get_user(memory: Dict[str, Any], uid: str, per_user_history: int) -> Dict[str, Any]:
    """
    Get or create a user record in memory.
    
    Args:
        memory: Main memory dictionary
        uid: User unique ID
        per_user_history: Maximum number of messages to keep per user
    
    Returns:
        User data dictionary
    """
    u = memory["users"].get(uid)
    if not u:
        u = {
            "first_seen": time.time(),
            "last_seen": time.time(),
            "nickname": "",
            "likes": 0,
            "gifts": 0,
            "follows": 0,
            "subs": 0,
            "shares": 0,
            "joins": 0,
            "messages": deque(maxlen=per_user_history),
            "last_greet": 0.0,
            "background": {}
        }
        memory["users"][uid] = u
    return u


def remember_event(
    memory: Dict[str, Any],
    mem_cfg: Dict[str, Any],
    uid: str,
    nickname: str = "",
    *,
    like_inc: int = 0,
    gift_inc: int = 0,
    follow: bool = False,
    sub: bool = False,
    share: bool = False,
    join: bool = False,
    message: str = None,
    background: Dict[str, Any] = None
) -> None:
    """
    Record a user event in memory.
    
    Args:
        memory: Main memory dictionary
        mem_cfg: Memory configuration
        uid: User unique ID
        nickname: User's display name
        like_inc: Number of likes to add
        gift_inc: Number of gifts to add
        follow: Whether user followed
        sub: Whether user subscribed
        share: Whether user shared
        join: Whether user joined
        message: Message text to store
        background: Background information to update
    """
    if not mem_cfg.get("enabled", 1):
        return
    
    u = get_user(memory, uid, mem_cfg.get("per_user_history", 10))
    u["last_seen"] = time.time()
    
    if nickname:
        u["nickname"] = nickname
    if like_inc:
        u["likes"] = int(u.get("likes", 0)) + int(like_inc)
    if gift_inc:
        u["gifts"] = int(u.get("gifts", 0)) + int(gift_inc)
    if follow:
        u["follows"] = int(u.get("follows", 0)) + 1
    if sub:
        u["subs"] = int(u.get("subs", 0)) + 1
    if share:
        u["shares"] = int(u.get("shares", 0)) + 1
    if join:
        u["joins"] = int(u.get("joins", 0)) + 1
    if message:
        try:
            u["messages"].append(message)
        except Exception:
            u["messages"] = deque([message], maxlen=mem_cfg.get("per_user_history", 10))
    if background:
        u["background"].update(background)
    
    try:
        save_memory(memory, mem_cfg.get("file", "memory.json"))
    except Exception:
        pass


def get_background_info(memory: Dict[str, Any], uid: str) -> str:
    """
    Get formatted background information for a user.
    
    Args:
        memory: Main memory dictionary
        uid: User unique ID
    
    Returns:
        Formatted background information string
    """
    u = memory["users"].get(uid, {})
    bg = u.get("background", {})
    if not bg:
        return ""
    
    parts = []
    for k, v in bg.items():
        if v is None:
            continue
        ks = str(k).strip()
        vs = str(v).strip()
        if not ks or not vs:
            continue
        truncated = vs[:48]
        if len(vs) > 48:
            truncated += "…"
        parts.append(f"{ks}={truncated}")
    
    return ", ".join(parts)
