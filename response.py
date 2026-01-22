"""
Response generation and relevance scoring module.
"""

import asyncio
import logging
import re
from functools import lru_cache
from typing import Dict, Any, Optional

import openai

from memory import get_background_info
from modules.rag import RAGEngine
from modules.mood import MoodManager, Mood
from modules.relationships import RelationshipManager

log = logging.getLogger("ChatPalBrain")


class Relevance:
    """
    Scores comment relevance and identifies special message types.
    """
    
    def __init__(self, conf: Dict[str, Any]) -> None:
        """
        Initialize relevance scorer.
        
        Args:
            conf: Comment configuration dictionary
        """
        self.kw_bonus = set(k.lower() for k in conf.get("keywords_bonus", []))
        self.ignore_sw = tuple(s.lower() for s in conf.get("ignore_if_startswith", []))
        self.ignore_contains = set(c.lower() for c in conf.get("ignore_contains", []))
        self.url_re = re.compile(r"https?://|\bdiscord\.gg\b", re.I)
        self.greetings_re = re.compile(
            r"\b(?:hallo|hi|hey|servus|moin|gruss|gru[eü]ß|guten morgen|guten abend|hello)\b",
            re.I | re.UNICODE
        )
        self.thanks_re = re.compile(r"\b(?:danke|thx|thanks|ty|merci)\b", re.I | re.UNICODE)
    
    def is_ignored(self, text: str) -> bool:
        """
        Check if text should be ignored.
        
        Args:
            text: Text to check
        
        Returns:
            True if text should be ignored, False otherwise
        """
        low = text.lower().strip()
        if low.startswith(self.ignore_sw):
            return True
        if any(c in low for c in self.ignore_contains):
            return True
        if self.url_re.search(low):
            return True
        return False
    
    def is_greeting(self, text: str) -> bool:
        """
        Check if text is a greeting.
        
        Args:
            text: Text to check
        
        Returns:
            True if text contains a greeting, False otherwise
        """
        return bool(self.greetings_re.search(text))
    
    def is_thanks(self, text: str) -> bool:
        """
        Check if text is a thank you message.
        
        Args:
            text: Text to check
        
        Returns:
            True if text contains thanks, False otherwise
        """
        return bool(self.thanks_re.search(text))
    
    def score(self, text: str) -> float:
        """
        Calculate relevance score for text.
        
        Args:
            text: Text to score
        
        Returns:
            Relevance score between 0.0 and 1.0
        """
        low = text.lower().strip()
        score = 0.0
        
        if "?" in low:
            score += 0.6
        
        # Use word set intersection for faster keyword matching
        words = set(low.split())
        if words & self.kw_bonus:
            score += 0.35
        
        if len(low) >= 7:
            score += 0.1
        
        if any(p in low for p in [":", ";", "!"]):
            score += 0.05
        
        return min(1.0, score)


class ResponseEngine:
    """
    Generates AI-powered responses to user comments.
    """
    
    def __init__(self, cfg: Dict[str, Any], memory: Dict[str, Any]) -> None:
        """
        Initialize response engine.
        
        Args:
            cfg: Configuration dictionary
            memory: Memory dictionary for user history
        """
        self.cfg = cfg
        self.memory = memory
        self.openai_client = openai.OpenAI(api_key=cfg["openai"]["api_key"])
        self.system_prompt = cfg.get("system_prompt", "")
        cache_size = int(cfg.get("openai", {}).get("cache_size", 128))
        self.reply_to_comment = lru_cache(maxsize=cache_size)(self._reply_to_comment_impl)
        self.timeout = float(cfg.get("openai", {}).get("request_timeout", 10.0))
        
        # Initialize new features
        try:
            self.rag_engine = RAGEngine(persist_directory="./chroma_db")
            self.mood_manager = MoodManager(initial_mood=Mood.NEUTRAL)
            self.relationship_manager = RelationshipManager(db_path="./relationships.db")
            log.info("Enhanced features initialized: RAG, Mood, and Relationships")
        except Exception as e:
            log.warning(f"Failed to initialize enhanced features: {e}. Continuing without them.")
            self.rag_engine = None
            self.mood_manager = None
            self.relationship_manager = None
    
    def _make_cache_key(self, nick: str, text: str, uid: str) -> tuple:
        """
        Create cache key from normalized inputs.
        
        Args:
            nick: User nickname
            text: Comment text
            uid: User ID
        
        Returns:
            Cache key tuple
        """
        return (nick, text.lower().strip(), uid)
    
    async def _reply_to_comment_impl(self, nick: str, text: str, uid: str) -> Optional[str]:
        """
        Generate a reply to a user comment using OpenAI.
        
        Args:
            nick: User nickname
            text: Comment text
            uid: User ID
        
        Returns:
            Generated reply text or None if failed
        """
        user_history = "\n".join(self.memory["users"].get(uid, {}).get("messages", []))
        bg_info = get_background_info(self.memory, uid)
        
        # Fetch RAG context if available
        rag_context = ""
        if self.rag_engine:
            try:
                contexts = self.rag_engine.get_context(text, uid, n_results=3)
                if contexts:
                    rag_context = "\nRelevant past interactions:\n" + "\n".join(
                        [f"- {ctx['text']}" for ctx in contexts]
                    )
            except Exception as e:
                log.warning(f"Failed to get RAG context: {e}")
        
        # Get user's friendship level if available
        friendship_level = "Stranger"
        if self.relationship_manager:
            try:
                level_info = self.relationship_manager.get_user_info(uid)
                friendship_level = level_info['level']
            except Exception as e:
                log.warning(f"Failed to get friendship level: {e}")
        
        # Get mood modifier if available
        mood_modifier = ""
        if self.mood_manager:
            try:
                mood_modifier = f"\n{self.mood_manager.get_prompt_modifier()}"
            except Exception as e:
                log.warning(f"Failed to get mood modifier: {e}")
        
        # Construct enhanced system prompt
        enhanced_system_prompt = self.system_prompt
        if mood_modifier or friendship_level != "Stranger" or rag_context:
            mood_value = self.mood_manager.get_mood().value if self.mood_manager else 'neutral'
            enhanced_system_prompt += f"\n\nCurrent Mood: {mood_value}"
            enhanced_system_prompt += f"{mood_modifier}"
            enhanced_system_prompt += f"\nUser Relationship Level: {friendship_level}"
            enhanced_system_prompt += rag_context
        
        prompt = f"User: {nick}\nBackground: {bg_info}\nChat history:\n{user_history}\nCurrent comment: {text}"
        
        try:
            fut = asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model=self.cfg["openai"]["model"],
                messages=[
                    {"role": "system", "content": enhanced_system_prompt},
                    {"role": "user", "content": prompt}
                ],
            )
            response = await asyncio.wait_for(fut, timeout=self.timeout)
            reply = response.choices[0].message.content.strip()
            
            # Limit response length
            words = reply.split()
            if len(words) > 18:
                reply = " ".join(words[:18]) + "."
            
            # Save interaction to RAG if available
            if self.rag_engine:
                try:
                    self.rag_engine.add_memory(uid, text, "user")
                    self.rag_engine.add_memory(uid, reply, "assistant")
                except Exception as e:
                    log.warning(f"Failed to save to RAG: {e}")
            
            # Update friendship XP if available
            if self.relationship_manager:
                try:
                    # Determine interaction type
                    interaction_type = "message"
                    if "?" in text:
                        interaction_type = "question"
                    elif self.is_greeting(text):
                        interaction_type = "greeting"
                    elif self.is_thanks(text):
                        interaction_type = "thanks"
                    
                    self.relationship_manager.award_interaction_xp(uid, interaction_type, nick)
                except Exception as e:
                    log.warning(f"Failed to update relationship XP: {e}")
            
            # Update mood based on interaction if available
            if self.mood_manager:
                try:
                    # Positive interaction
                    self.mood_manager.update_mood("positive_chat")
                except Exception as e:
                    log.warning(f"Failed to update mood: {e}")
            
            return reply
        except asyncio.TimeoutError:
            log.error(f"OpenAI Timeout nach {self.timeout}s")
            return None
        except openai.APIError as e:
            log.error(f"OpenAI API Fehler: {e}")
            return None
        except Exception as e:
            log.error(f"OpenAI Fehler: {e}")
            return None
    
    def is_greeting(self, text: str) -> bool:
        """Helper to check if text is a greeting."""
        greetings_re = re.compile(
            r"\b(?:hallo|hi|hey|servus|moin|gruss|gru[eü]ß|guten morgen|guten abend|hello)\b",
            re.I | re.UNICODE
        )
        return bool(greetings_re.search(text))
    
    def is_thanks(self, text: str) -> bool:
        """Helper to check if text is a thanks message."""
        thanks_re = re.compile(r"\b(?:danke|thx|thanks|ty|merci)\b", re.I | re.UNICODE)
        return bool(thanks_re.search(text))
