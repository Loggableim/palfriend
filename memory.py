"""
Memory module with SQLite backend for storing and managing user interaction history and data.
"""

import asyncio
import json
import logging
import os
import time
import warnings
from typing import Any, Dict, Optional, List

import aiosqlite
from pydantic import BaseModel, Field

log = logging.getLogger("ChatPalBrain")


async def extract_and_store_entities(text: str, uid: str, memory_db, openai_client) -> None:
    """
    Extract entities (Names, Locations, Facts) from user message using LLM.
    
    This enables the bot to remember personal details like "I have a dog named Max"
    and use them in future interactions.
    
    Args:
        text: User message text
        uid: User ID
        memory_db: MemoryDB instance
        openai_client: OpenAI client instance
    """
    try:
        # Use LLM to extract structured information
        prompt = f"""Extract any personal information, names, locations, or facts from this message.
        
Message: "{text}"

Return a JSON object with keys for any entities found (e.g., {{"pet": "dog named Max", "location": "Berlin", "hobby": "gaming"}}).
If no entities found, return {{}}.
Only return the JSON, no other text."""
        
        response = await asyncio.to_thread(
            openai_client.chat.completions.create,
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a data extraction assistant. Extract personal information from user messages."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            max_tokens=150
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Try to parse JSON response
        # Remove markdown code blocks if present
        if result_text.startswith("```"):
            result_text = result_text.split("```")[1]
            if result_text.startswith("json"):
                result_text = result_text[4:]
        
        entities = json.loads(result_text)
        
        if entities:
            # Update user background with extracted entities
            await memory_db.update_background(uid, entities)
            log.info(f"Extracted entities for user {uid}: {entities}")
    except json.JSONDecodeError as e:
        log.debug(f"Failed to parse entity extraction response: {e}")
    except Exception as e:
        log.warning(f"Entity extraction failed: {e}")


class UserModel(BaseModel):
    """Pydantic model for user data with strict typing."""
    uid: str
    first_seen: float
    last_seen: float
    nickname: str = ""
    likes: int = 0
    gifts: int = 0
    follows: int = 0
    subs: int = 0
    shares: int = 0
    joins: int = 0
    messages: List[str] = Field(default_factory=list)
    last_greet: float = 0.0
    background: Dict[str, Any] = Field(default_factory=dict)


class MemoryDB:
    """Async SQLite database for user memory management."""
    
    def __init__(self, db_path: str = "memory.db", per_user_history: int = 10):
        """
        Initialize memory database.
        
        Args:
            db_path: Path to SQLite database file
            per_user_history: Maximum number of messages to keep per user
        """
        self.db_path = db_path
        self.per_user_history = per_user_history
        self._conn: Optional[aiosqlite.Connection] = None
        self._lock = asyncio.Lock()
    
    async def initialize(self) -> None:
        """Initialize database connection and create tables."""
        self._conn = await aiosqlite.connect(self.db_path)
        self._conn.row_factory = aiosqlite.Row
        
        await self._conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                uid TEXT PRIMARY KEY,
                first_seen REAL NOT NULL,
                last_seen REAL NOT NULL,
                nickname TEXT DEFAULT '',
                likes INTEGER DEFAULT 0,
                gifts INTEGER DEFAULT 0,
                follows INTEGER DEFAULT 0,
                subs INTEGER DEFAULT 0,
                shares INTEGER DEFAULT 0,
                joins INTEGER DEFAULT 0,
                messages TEXT DEFAULT '[]',
                last_greet REAL DEFAULT 0.0,
                background TEXT DEFAULT '{}'
            )
        """)
        
        await self._conn.commit()
        log.info(f"MemoryDB initialized at {self.db_path}")
    
    async def close(self) -> None:
        """Close database connection."""
        if self._conn:
            await self._conn.close()
            self._conn = None
    
    async def get_user(self, uid: str) -> UserModel:
        """
        Get or create a user record.
        
        Args:
            uid: User unique ID
        
        Returns:
            UserModel object
        """
        async with self._lock:
            return await self._get_user_unlocked(uid)
    
    async def _get_user_unlocked(self, uid: str) -> UserModel:
        """
        Get or create a user record (internal method, assumes lock is held).
        
        Args:
            uid: User unique ID
        
        Returns:
            UserModel object
        """
        cursor = await self._conn.execute(
            "SELECT * FROM users WHERE uid = ?", (uid,)
        )
        row = await cursor.fetchone()
        
        if row:
            # Convert row to dict and parse JSON fields
            user_dict = dict(row)
            user_dict['messages'] = json.loads(user_dict['messages'])
            user_dict['background'] = json.loads(user_dict['background'])
            return UserModel(**user_dict)
        else:
            # Create new user
            now = time.time()
            new_user = UserModel(
                uid=uid,
                first_seen=now,
                last_seen=now
            )
            await self._save_user(new_user)
            return new_user
    
    async def _save_user(self, user: UserModel) -> None:
        """
        Save user to database (internal method, assumes lock is held).
        
        Args:
            user: UserModel to save
        """
        await self._conn.execute("""
            INSERT OR REPLACE INTO users (
                uid, first_seen, last_seen, nickname, likes, gifts,
                follows, subs, shares, joins, messages, last_greet, background
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user.uid,
            user.first_seen,
            user.last_seen,
            user.nickname,
            user.likes,
            user.gifts,
            user.follows,
            user.subs,
            user.shares,
            user.joins,
            json.dumps(user.messages),
            user.last_greet,
            json.dumps(user.background)
        ))
        await self._conn.commit()
    
    async def save_user(self, user: UserModel) -> None:
        """
        Save user to database (public method with locking).
        
        Args:
            user: UserModel to save
        """
        async with self._lock:
            await self._save_user(user)
    
    async def remember_event(
        self,
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
        async with self._lock:
            user = await self._get_user_unlocked(uid)
            user.last_seen = time.time()
            
            if nickname:
                user.nickname = nickname
            if like_inc:
                user.likes += like_inc
            if gift_inc:
                user.gifts += gift_inc
            if follow:
                user.follows += 1
            if sub:
                user.subs += 1
            if share:
                user.shares += 1
            if join:
                user.joins += 1
            if message:
                # Maintain max history
                user.messages.append(message)
                if len(user.messages) > self.per_user_history:
                    user.messages = user.messages[-self.per_user_history:]
            if background:
                user.background.update(background)
            
            await self._save_user(user)
    
    async def update_background(self, uid: str, entities: Dict[str, Any]) -> None:
        """
        Update user background with extracted entities.
        
        Args:
            uid: User unique ID
            entities: Dictionary of extracted entities/facts
        """
        async with self._lock:
            user = await self._get_user_unlocked(uid)
            user.background.update(entities)
            await self._save_user(user)
    
    async def get_background_info(self, uid: str) -> str:
        """
        Get formatted background information for a user.
        
        Args:
            uid: User unique ID
        
        Returns:
            Formatted background information string
        """
        user = await self.get_user(uid)
        bg = user.background
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
    
    async def clean_old_users(self, decay_days: int) -> int:
        """
        Remove users who haven't been seen in decay_days.
        
        Args:
            decay_days: Number of days after which user data is considered stale
        
        Returns:
            Number of users removed
        """
        decay_sec = decay_days * 86400
        cutoff = time.time() - decay_sec
        
        async with self._lock:
            cursor = await self._conn.execute(
                "SELECT COUNT(*) FROM users WHERE last_seen < ?", (cutoff,)
            )
            count_row = await cursor.fetchone()
            count = count_row[0] if count_row else 0
            
            await self._conn.execute(
                "DELETE FROM users WHERE last_seen < ?", (cutoff,)
            )
            await self._conn.commit()
            
            return count
    
    async def get_user_count(self) -> int:
        """
        Get total number of users in database.
        
        Returns:
            Number of users
        """
        cursor = await self._conn.execute("SELECT COUNT(*) FROM users")
        row = await cursor.fetchone()
        return row[0] if row else 0


# Legacy function wrappers for backward compatibility
def load_memory(path: str, decay_days: int) -> Dict[str, Any]:
    """
    Legacy function for loading memory from JSON (deprecated).
    
    Args:
        path: Path to memory file
        decay_days: Number of days after which user data is considered stale
    
    Returns:
        Dictionary containing user memory data
    """
    warnings.warn(
        "load_memory() is deprecated. Use MemoryDB() constructor and get_user() instead.",
        DeprecationWarning,
        stacklevel=2
    )
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
    Legacy function for saving memory to JSON (deprecated).
    
    Args:
        mem: Memory dictionary to save
        path: Path to memory file
    """
    warnings.warn(
        "save_memory() is deprecated. MemoryDB saves automatically.",
        DeprecationWarning,
        stacklevel=2
    )
    try:
        tmp = f"{path}.tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(mem, f, indent=2, ensure_ascii=False)
        os.replace(tmp, path)
    except Exception as e:
        log.error(f"Failed to save memory: {e}")


def get_user(memory: Dict[str, Any], uid: str, per_user_history: int) -> Dict[str, Any]:
    """
    Legacy function for getting user (deprecated).
    
    Args:
        memory: Main memory dictionary
        uid: User unique ID
        per_user_history: Maximum number of messages to keep per user
    
    Returns:
        User data dictionary
    """
    warnings.warn(
        "get_user() is deprecated. Use MemoryDB.get_user() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    from collections import deque
    
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
    Legacy function for recording events (deprecated).
    
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
    warnings.warn(
        "remember_event() is deprecated. Use MemoryDB.remember_event() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    from collections import deque
    
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
        except (AttributeError, KeyError):
            u["messages"] = deque([message], maxlen=mem_cfg.get("per_user_history", 10))
    if background:
        u["background"].update(background)
    
    try:
        save_memory(memory, mem_cfg.get("file", "memory.json"))
    except (IOError, OSError) as e:
        log.error(f"Failed to save memory: {e}")


def get_background_info(memory: Dict[str, Any], uid: str) -> str:
    """
    Legacy function for getting background info (deprecated).
    
    Args:
        memory: Main memory dictionary
        uid: User unique ID
    
    Returns:
        Formatted background information string
    """
    warnings.warn(
        "get_background_info() is deprecated. Use MemoryDB.get_background_info() instead.",
        DeprecationWarning,
        stacklevel=2
    )
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
