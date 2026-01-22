"""
Relationship Manager for tracking user friendship levels with the bot.
Uses SQLite to persist user XP and levels.
"""

import logging
import sqlite3
from typing import Dict, Optional
from enum import Enum

log = logging.getLogger("RelationshipManager")


class FriendshipLevel(Enum):
    """Friendship level tiers."""
    STRANGER = ("Stranger", 0, 49)
    REGULAR = ("Regular", 50, 199)
    FRIEND = ("Friend", 200, 499)
    BESTIE = ("Bestie", 500, float('inf'))
    
    def __init__(self, display_name: str, min_xp: int, max_xp: float):
        self.display_name = display_name
        self.min_xp = min_xp
        self.max_xp = max_xp


class RelationshipManager:
    """
    Manages parasocial friendship levels based on user interactions.
    """
    
    # XP rewards for different interaction types
    XP_REWARDS = {
        "message": 2,
        "question": 5,
        "greeting": 3,
        "thanks": 4,
        "gift": 20,
        "follow": 15,
        "share": 10
    }
    
    def __init__(self, db_path: str = "./relationships.db"):
        """
        Initialize relationship manager with SQLite database.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._init_database()
        log.info(f"RelationshipManager initialized with database: {db_path}")
    
    def _init_database(self) -> None:
        """Create database table if it doesn't exist."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_relationships (
                    user_id TEXT PRIMARY KEY,
                    username TEXT,
                    xp INTEGER DEFAULT 0,
                    last_interaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            conn.close()
            log.debug("Database initialized successfully")
        except Exception as e:
            log.error(f"Failed to initialize database: {e}")
            raise
    
    def add_xp(self, user_id: str, amount: int, username: str = None) -> int:
        """
        Add XP to a user's friendship level.
        
        Args:
            user_id: Unique identifier for the user
            amount: Amount of XP to add
            username: Optional username for display
        
        Returns:
            New total XP for the user
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if user exists
            cursor.execute("SELECT xp FROM user_relationships WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            
            if result:
                # Update existing user
                new_xp = result[0] + amount
                cursor.execute("""
                    UPDATE user_relationships 
                    SET xp = ?, last_interaction = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                """, (new_xp, user_id))
            else:
                # Insert new user
                new_xp = amount
                cursor.execute("""
                    INSERT INTO user_relationships (user_id, username, xp)
                    VALUES (?, ?, ?)
                """, (user_id, username or user_id, new_xp))
            
            conn.commit()
            conn.close()
            
            log.debug(f"Added {amount} XP to user {user_id}. Total: {new_xp}")
            return new_xp
        except Exception as e:
            log.error(f"Failed to add XP: {e}")
            return 0
    
    def get_user_xp(self, user_id: str) -> int:
        """
        Get a user's current XP.
        
        Args:
            user_id: Unique identifier for the user
        
        Returns:
            User's XP amount
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT xp FROM user_relationships WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else 0
        except Exception as e:
            log.error(f"Failed to get user XP: {e}")
            return 0
    
    def get_user_level(self, user_id: str) -> FriendshipLevel:
        """
        Get a user's current friendship level.
        
        Args:
            user_id: Unique identifier for the user
        
        Returns:
            FriendshipLevel enum value
        """
        xp = self.get_user_xp(user_id)
        
        for level in FriendshipLevel:
            if level.min_xp <= xp <= level.max_xp:
                return level
        
        return FriendshipLevel.STRANGER
    
    def get_user_info(self, user_id: str) -> Dict[str, any]:
        """
        Get comprehensive user relationship info.
        
        Args:
            user_id: Unique identifier for the user
        
        Returns:
            Dictionary with user's XP, level, and progress
        """
        xp = self.get_user_xp(user_id)
        level = self.get_user_level(user_id)
        
        # Calculate progress to next level
        next_level_xp = None
        progress_percent = 0
        
        levels_list = list(FriendshipLevel)
        current_index = levels_list.index(level)
        
        if current_index < len(levels_list) - 1:
            next_level = levels_list[current_index + 1]
            next_level_xp = next_level.min_xp
            xp_in_current = xp - level.min_xp
            xp_needed = next_level_xp - level.min_xp
            progress_percent = int((xp_in_current / xp_needed) * 100) if xp_needed > 0 else 0
        
        return {
            "user_id": user_id,
            "xp": xp,
            "level": level.display_name,
            "next_level_xp": next_level_xp,
            "progress_percent": progress_percent
        }
    
    def award_interaction_xp(self, user_id: str, interaction_type: str, username: str = None) -> int:
        """
        Award XP for a specific interaction type.
        
        Args:
            user_id: Unique identifier for the user
            interaction_type: Type of interaction (from XP_REWARDS keys)
            username: Optional username for display
        
        Returns:
            New total XP for the user
        """
        xp_amount = self.XP_REWARDS.get(interaction_type, 1)
        return self.add_xp(user_id, xp_amount, username)
