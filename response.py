"""
Response generation and relevance scoring module.
"""

import asyncio
import logging
import re
from functools import lru_cache
from typing import Dict, Any, Optional

import openai

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
    
    def __init__(self, cfg: Dict[str, Any], memory_db) -> None:
        """
        Initialize response engine.
        
        Args:
            cfg: Configuration dictionary
            memory_db: MemoryDB instance for user history
        """
        self.cfg = cfg
        self.memory_db = memory_db
        self.openai_client = openai.OpenAI(api_key=cfg["openai"]["api_key"])
        self.system_prompt = cfg.get("system_prompt", "")
        cache_size = int(cfg.get("openai", {}).get("cache_size", 128))
        self.reply_to_comment = lru_cache(maxsize=cache_size)(self._reply_to_comment_impl)
        self.timeout = float(cfg.get("openai", {}).get("request_timeout", 10.0))
        
        # Initialize new features
        try:
            from modules.rag import RAGEngine
            from modules.mood import MoodManager, Mood
            from modules.relationships import RelationshipManager
            
            self.rag_engine = RAGEngine(persist_directory="./chroma_db")
            self.mood_manager = MoodManager(initial_mood=Mood.NEUTRAL)
            self.relationship_manager = RelationshipManager(db_path="./relationships.db")
            log.info("Enhanced features initialized: RAG, Mood, and Relationships")
        except Exception as e:
            log.warning(f"Failed to initialize enhanced features: {e}. Continuing without them.")
            self.rag_engine = None
            self.mood_manager = None
            self.relationship_manager = None
        
        # Initialize personality system
        try:
            from modules.persona_state import PersonaStateStore
            from modules.prompt_composer import PromptComposer
            
            personality_config = cfg.get("personality_bias", {})
            if personality_config.get("enabled", 0):
                db_path = personality_config.get("persistence", {}).get("db_path", "./persona_state.db")
                self.persona_store = PersonaStateStore(personality_config, db_path)
                self.prompt_composer = PromptComposer(cfg)
                log.info("Personality system initialized")
            else:
                self.persona_store = None
                self.prompt_composer = None
                log.info("Personality system disabled")
        except Exception as e:
            log.warning(f"Failed to initialize personality system: {e}. Continuing without it.")
            self.persona_store = None
            self.prompt_composer = None
    
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
        # Check for refusal first (personality-based)
        if self.prompt_composer:
            refusal = self.prompt_composer.check_refusal(text)
            if refusal:
                log.info(f"Refusal triggered for user {uid}")
                return refusal
        
        user = await self.memory_db.get_user(uid)
        user_history = "\n".join(user.messages)
        bg_info = await self.memory_db.get_background_info(uid)
        
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
        
        # Build system prompt with personality if enabled
        if self.persona_store and self.prompt_composer:
            try:
                # Get current persona state
                scope_id = uid if self.persona_store.scope == "user" else "session"
                state = self.persona_store.get_state(scope_id)
                tone_weights = state["tone_weights"]
                stance_overrides = state["stance_overrides"]
                
                # Apply volatility drift
                volatility = self.cfg.get("personality_bias", {}).get("volatility", 0.01)
                tone_weights = self.persona_store.apply_drift(tone_weights, volatility)
                
                # Compose system prompt with personality
                enhanced_system_prompt = self.prompt_composer.compose_prompt(
                    tone_weights, stance_overrides, 
                    context={"mood": mood_modifier, "friendship": friendship_level, "rag": rag_context}
                )
                
                # Save updated state
                self.persona_store.save_state(scope_id, tone_weights, stance_overrides)
            except Exception as e:
                log.warning(f"Failed to apply personality: {e}. Using default prompt.")
                enhanced_system_prompt = self.system_prompt
        else:
            # Construct enhanced system prompt without personality (legacy behavior)
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
            
            # Update persona evolution based on interaction
            if self.persona_store and self.prompt_composer:
                try:
                    scope_id = uid if self.persona_store.scope == "user" else "session"
                    state = self.persona_store.get_state(scope_id)
                    tone_weights = state["tone_weights"]
                    
                    # Trigger evolution based on interaction type
                    tone_weights = self.persona_store.apply_evolution(scope_id, "positive_interaction", tone_weights)
                    
                    # Save updated state
                    self.persona_store.save_state(scope_id, tone_weights, state["stance_overrides"])
                except Exception as e:
                    log.warning(f"Failed to update persona evolution: {e}")
            
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
    
    def get_persona_state(self, uid: str = "session") -> Optional[Dict[str, Any]]:
        """
        Get current persona state for a user/session.
        
        Args:
            uid: User ID or "session" for session-scoped persona
        
        Returns:
            Persona state summary or None if personality system not enabled
        """
        if not self.persona_store or not self.prompt_composer:
            return None
        
        try:
            scope_id = uid if self.persona_store.scope == "user" else "session"
            state = self.persona_store.get_state(scope_id)
            summary = self.prompt_composer.get_persona_summary(
                state["tone_weights"], 
                state["stance_overrides"]
            )
            summary["evolution_history"] = self.persona_store.get_evolution_history(scope_id, limit=5)
            return summary
        except Exception as e:
            log.error(f"Failed to get persona state: {e}")
            return None
    
    def reset_persona(self, uid: str = "session") -> bool:
        """
        Reset persona state to defaults.
        
        Args:
            uid: User ID or "session" for session-scoped persona
        
        Returns:
            True if reset successful, False otherwise
        """
        if not self.persona_store:
            return False
        
        try:
            scope_id = uid if self.persona_store.scope == "user" else "session"
            self.persona_store.reset_state(scope_id)
            log.info(f"Reset persona state for {scope_id}")
            return True
        except Exception as e:
            log.error(f"Failed to reset persona: {e}")
            return False
