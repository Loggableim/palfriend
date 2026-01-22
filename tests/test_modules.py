"""
Tests for the new modules: RAG, Mood, and Relationships.
"""
import pytest
import tempfile
import os
import shutil
from modules.mood import MoodManager, Mood
from modules.relationships import RelationshipManager, FriendshipLevel


class TestMoodManager:
    """Tests for the MoodManager class."""
    
    def test_mood_initialization(self):
        """Test that mood manager initializes correctly."""
        mood_mgr = MoodManager()
        assert mood_mgr.get_mood() == Mood.NEUTRAL
        assert mood_mgr.get_mood_score() == 0
    
    def test_mood_update_positive(self):
        """Test positive mood updates."""
        mood_mgr = MoodManager()
        
        # Add some positive events
        mood_mgr.update_mood("gift", None)  # +15
        mood_mgr.update_mood("follow", None)  # +10
        mood_mgr.update_mood("like", None)  # +5
        
        # Should be at 30, which is still NEUTRAL (needs 40 for HAPPY)
        assert mood_mgr.get_mood_score() == 30
        assert mood_mgr.get_mood() == Mood.NEUTRAL
        
        # Add more to reach HAPPY
        mood_mgr.update_mood("follow", None)  # +10
        assert mood_mgr.get_mood_score() == 40
        assert mood_mgr.get_mood() == Mood.HAPPY
    
    def test_mood_update_negative(self):
        """Test negative mood updates."""
        mood_mgr = MoodManager()
        
        # Add negative events
        mood_mgr.update_mood("spam", None)  # -10
        mood_mgr.update_mood("timeout", None)  # -15
        mood_mgr.update_mood("spam", None)  # -10
        
        # Should be at -35, which is ANNOYED (threshold is -20 to -50)
        assert mood_mgr.get_mood_score() == -35
        assert mood_mgr.get_mood() == Mood.ANNOYED
    
    def test_mood_clamping(self):
        """Test that mood score is clamped to [-100, 100]."""
        mood_mgr = MoodManager()
        
        # Try to go beyond 100
        for _ in range(10):
            mood_mgr.update_mood("gift", None)  # +15 each
        
        assert mood_mgr.get_mood_score() <= 100
        
        # Try to go below -100
        mood_mgr.reset_mood()
        for _ in range(10):
            mood_mgr.update_mood("timeout", None)  # -15 each
        
        assert mood_mgr.get_mood_score() >= -100
    
    def test_mood_reset(self):
        """Test mood reset functionality."""
        mood_mgr = MoodManager()
        
        # Change mood
        mood_mgr.update_mood("gift", None)
        mood_mgr.update_mood("follow", None)
        
        # Reset
        mood_mgr.reset_mood()
        
        assert mood_mgr.get_mood() == Mood.NEUTRAL
        assert mood_mgr.get_mood_score() == 0
    
    def test_get_prompt_modifier(self):
        """Test that prompt modifiers are returned."""
        mood_mgr = MoodManager()
        
        # Get modifier for NEUTRAL
        modifier = mood_mgr.get_prompt_modifier()
        assert isinstance(modifier, str)
        assert len(modifier) > 0
        
        # Change to HYPE and get modifier
        for _ in range(10):
            mood_mgr.update_mood("gift", None)
        
        modifier = mood_mgr.get_prompt_modifier()
        assert "energetic" in modifier.lower() or "excited" in modifier.lower()


class TestRelationshipManager:
    """Tests for the RelationshipManager class."""
    
    def setup_method(self):
        """Create a temporary database for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_relationships.db")
    
    def teardown_method(self):
        """Clean up temporary database."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test that relationship manager initializes correctly."""
        rel_mgr = RelationshipManager(db_path=self.db_path)
        assert os.path.exists(self.db_path)
    
    def test_add_xp_new_user(self):
        """Test adding XP to a new user."""
        rel_mgr = RelationshipManager(db_path=self.db_path)
        
        xp = rel_mgr.add_xp("user123", 10, "TestUser")
        assert xp == 10
    
    def test_add_xp_existing_user(self):
        """Test adding XP to an existing user."""
        rel_mgr = RelationshipManager(db_path=self.db_path)
        
        rel_mgr.add_xp("user123", 10, "TestUser")
        xp = rel_mgr.add_xp("user123", 15, "TestUser")
        
        assert xp == 25
    
    def test_get_user_xp(self):
        """Test retrieving user XP."""
        rel_mgr = RelationshipManager(db_path=self.db_path)
        
        rel_mgr.add_xp("user123", 30)
        xp = rel_mgr.get_user_xp("user123")
        
        assert xp == 30
    
    def test_get_user_xp_nonexistent(self):
        """Test getting XP for a user that doesn't exist."""
        rel_mgr = RelationshipManager(db_path=self.db_path)
        
        xp = rel_mgr.get_user_xp("nonexistent")
        assert xp == 0
    
    def test_friendship_levels(self):
        """Test that friendship levels are assigned correctly."""
        rel_mgr = RelationshipManager(db_path=self.db_path)
        
        # Stranger (0-49)
        rel_mgr.add_xp("user1", 0)
        assert rel_mgr.get_user_level("user1") == FriendshipLevel.STRANGER
        
        rel_mgr.add_xp("user1", 25)
        assert rel_mgr.get_user_level("user1") == FriendshipLevel.STRANGER
        
        # Regular (50-199)
        rel_mgr.add_xp("user2", 50)
        assert rel_mgr.get_user_level("user2") == FriendshipLevel.REGULAR
        
        rel_mgr.add_xp("user2", 100)
        assert rel_mgr.get_user_level("user2") == FriendshipLevel.REGULAR
        
        # Friend (200-499)
        rel_mgr.add_xp("user3", 200)
        assert rel_mgr.get_user_level("user3") == FriendshipLevel.FRIEND
        
        # Bestie (500+)
        rel_mgr.add_xp("user4", 500)
        assert rel_mgr.get_user_level("user4") == FriendshipLevel.BESTIE
    
    def test_get_user_info(self):
        """Test getting comprehensive user info."""
        rel_mgr = RelationshipManager(db_path=self.db_path)
        
        rel_mgr.add_xp("user123", 75)
        info = rel_mgr.get_user_info("user123")
        
        assert info["xp"] == 75
        assert info["level"] == "Regular"
        assert "progress_percent" in info
    
    def test_award_interaction_xp(self):
        """Test awarding XP for specific interaction types."""
        rel_mgr = RelationshipManager(db_path=self.db_path)
        
        # Award message XP
        xp = rel_mgr.award_interaction_xp("user123", "message")
        assert xp == 2
        
        # Award question XP
        xp = rel_mgr.award_interaction_xp("user123", "question")
        assert xp == 7  # 2 + 5
        
        # Award gift XP
        xp = rel_mgr.award_interaction_xp("user123", "gift")
        assert xp == 27  # 7 + 20


# RAG tests would require actual chromadb which may not be available in test environment
# For now, we'll skip comprehensive RAG tests and rely on integration testing
