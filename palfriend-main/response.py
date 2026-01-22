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
        prompt = f"User: {nick}\nBackground: {bg_info}\nChat history:\n{user_history}\nCurrent comment: {text}"
        
        try:
            fut = asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model=self.cfg["openai"]["model"],
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
            )
            response = await asyncio.wait_for(fut, timeout=self.timeout)
            reply = response.choices[0].message.content.strip()
            
            # Limit response length
            words = reply.split()
            if len(words) > 18:
                reply = " ".join(words[:18]) + "."
            
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
