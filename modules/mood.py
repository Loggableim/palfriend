"""
Mood System for the bot to track emotional states and adjust responses.
"""

import logging
from enum import Enum
from typing import Dict, Any

log = logging.getLogger("MoodManager")


class Mood(Enum):
    """Possible mood states for the bot."""
    NEUTRAL = "neutral"
    HAPPY = "happy"
    HYPE = "hype"
    ANNOYED = "annoyed"
    TIRED = "tired"


class MoodManager:
    """
    Manages the bot's emotional state based on events and interactions.
    """
    
    # Mood score thresholds
    MOOD_THRESHOLDS = {
        Mood.HYPE: 80,
        Mood.HAPPY: 40,
        Mood.NEUTRAL: -20,
        Mood.ANNOYED: -50,
        Mood.TIRED: -100
    }
    
    # Event type to mood change mapping
    EVENT_MODIFIERS = {
        "gift": 15,
        "follow": 10,
        "like": 5,
        "share": 8,
        "join": 3,
        "leave": -2,
        "spam": -10,
        "timeout": -15,
        "long_session": -5,
        "positive_chat": 7,
        "negative_chat": -8
    }
    
    def __init__(self, initial_mood: Mood = Mood.NEUTRAL):
        """
        Initialize mood manager.
        
        Args:
            initial_mood: Starting mood state
        """
        self.current_mood = initial_mood
        self.mood_score = 0  # Numeric score determining mood state
        log.info(f"MoodManager initialized with mood: {self.current_mood.value}")
    
    def update_mood(self, event_type: str, value: int = None) -> Mood:
        """
        Update mood based on an event.
        
        Args:
            event_type: Type of event (e.g., 'gift', 'spam', 'follow')
            value: Optional custom mood change value (overrides default)
        
        Returns:
            Updated mood state
        """
        # Use provided value or lookup default modifier
        modifier = value if value is not None else self.EVENT_MODIFIERS.get(event_type, 0)
        
        self.mood_score += modifier
        
        # Clamp mood score to reasonable bounds
        self.mood_score = max(-100, min(100, self.mood_score))
        
        # Determine new mood based on score
        old_mood = self.current_mood
        self.current_mood = self._calculate_mood_from_score()
        
        if old_mood != self.current_mood:
            log.info(f"Mood changed: {old_mood.value} -> {self.current_mood.value} (score: {self.mood_score})")
        
        return self.current_mood
    
    def _calculate_mood_from_score(self) -> Mood:
        """
        Calculate mood state from current score.
        
        Returns:
            Mood enum value
        """
        if self.mood_score >= self.MOOD_THRESHOLDS[Mood.HYPE]:
            return Mood.HYPE
        elif self.mood_score >= self.MOOD_THRESHOLDS[Mood.HAPPY]:
            return Mood.HAPPY
        elif self.mood_score >= self.MOOD_THRESHOLDS[Mood.NEUTRAL]:
            return Mood.NEUTRAL
        elif self.mood_score >= self.MOOD_THRESHOLDS[Mood.ANNOYED]:
            return Mood.ANNOYED
        else:
            return Mood.TIRED
    
    def get_prompt_modifier(self) -> str:
        """
        Get a text modifier to inject into the system prompt.
        
        Returns:
            String describing the current mood to guide response generation
        """
        mood_descriptions = {
            Mood.HYPE: "You're feeling SUPER energetic and excited! Use lots of enthusiasm, emojis, and exclamation marks! 🎉",
            Mood.HAPPY: "You're in a great mood! Be friendly, upbeat, and positive. 😊",
            Mood.NEUTRAL: "You're feeling balanced and calm. Respond naturally and conversationally.",
            Mood.ANNOYED: "You're feeling a bit irritated. Keep responses shorter and more direct, with occasional sass.",
            Mood.TIRED: "You're exhausted and drained. Keep responses brief and less enthusiastic. Maybe mention being tired."
        }
        return mood_descriptions.get(self.current_mood, "")
    
    def get_mood(self) -> Mood:
        """
        Get the current mood state.
        
        Returns:
            Current Mood enum value
        """
        return self.current_mood
    
    def get_mood_score(self) -> int:
        """
        Get the current numeric mood score.
        
        Returns:
            Mood score integer
        """
        return self.mood_score
    
    def reset_mood(self) -> None:
        """Reset mood to neutral state."""
        self.mood_score = 0
        self.current_mood = Mood.NEUTRAL
        log.info("Mood reset to NEUTRAL")
