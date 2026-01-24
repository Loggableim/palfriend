"""
TTS (Text-to-Speech) module with Fish Audio provider and caching.
"""

import asyncio
import hashlib
import logging
import os
import time
from pathlib import Path
from typing import Dict, Any, Optional

import aiosqlite
import numpy as np
import soundfile as sf
from dotenv import load_dotenv

log = logging.getLogger("ChatPalBrain")

# Load environment variables
load_dotenv()


class FishAudioProvider:
    """
    Fish Audio TTS provider with API integration.
    """
    
    def __init__(self, cfg: Dict[str, Any]) -> None:
        """
        Initialize Fish Audio provider.
        
        Args:
            cfg: Configuration dictionary with 'tts' section
        """
        tts_cfg = cfg.get("tts", {})
        
        # API configuration
        self.api_key = os.getenv("FISH_AUDIO_API_KEY") or tts_cfg.get("fish_audio_api_key", "")
        if not self.api_key:
            log.warning("Fish Audio API key not found. Set FISH_AUDIO_API_KEY in .env or tts.fish_audio_api_key in settings.yaml")
        
        # Voice configuration
        self.voice_id = os.getenv("FISH_AUDIO_VOICE_ID") or tts_cfg.get("fish_audio_voice_id", "")
        
        # Generation settings
        self.format = tts_cfg.get("format", "wav")
        self.sample_rate = int(tts_cfg.get("sample_rate", 44100))
        
        log.info(f"FishAudioProvider initialized (voice_id={self.voice_id[:8] if self.voice_id else 'not set'}...)")
    
    async def synthesize(self, text: str) -> Optional[bytes]:
        """
        Synthesize speech from text using Fish Audio API.
        
        Args:
            text: Text to synthesize
        
        Returns:
            Audio data as bytes, or None on error
        """
        if not self.api_key:
            log.error("Cannot synthesize: Fish Audio API key not configured")
            return None
        
        if not self.voice_id:
            log.error("Cannot synthesize: Fish Audio voice ID not configured")
            return None
        
        try:
            # Import Fish Audio SDK
            try:
                from fish_audio_sdk import Session, TTSRequest
            except ImportError:
                log.error("fish-audio-sdk not installed. Run: pip install fish-audio-sdk")
                return None
            
            # Create session and synthesize
            session = Session(self.api_key)
            
            # Create TTS request
            request = TTSRequest(
                text=text,
                reference_id=self.voice_id,
                format=self.format,
            )
            
            # Synthesize speech
            audio_data = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: session.tts(request)
            )
            
            log.info(f"Synthesized {len(text)} chars -> {len(audio_data) if audio_data else 0} bytes")
            return audio_data
        except Exception as e:
            log.error(f"Fish Audio synthesis error: {e}")
            return None


class TTSManager:
    """
    Manages TTS providers, caching, and audio generation.
    """
    
    def __init__(self, cfg: Dict[str, Any], cache_dir: str = "data/audio_cache") -> None:
        """
        Initialize TTS Manager.
        
        Args:
            cfg: Configuration dictionary
            cache_dir: Directory for audio file cache
        """
        self.cfg = cfg
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Database for cache metadata
        self.db_path = "data/tts_cache.db"
        self.db: Optional[aiosqlite.Connection] = None
        
        # Initialize provider
        self.provider = FishAudioProvider(cfg)
        
        # Cache settings
        tts_cfg = cfg.get("tts", {})
        self.cache_enabled = bool(int(tts_cfg.get("cache_enabled", 1)))
        self.max_cache_age_days = int(tts_cfg.get("max_cache_age_days", 30))
        
        log.info(f"TTSManager initialized (cache={'enabled' if self.cache_enabled else 'disabled'})")
    
    async def initialize(self) -> None:
        """Initialize database and create tables."""
        try:
            self.db = await aiosqlite.connect(self.db_path)
            await self.db.execute("""
                CREATE TABLE IF NOT EXISTS tts_cache (
                    text_hash TEXT PRIMARY KEY,
                    text TEXT NOT NULL,
                    voice_id TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    created_at INTEGER NOT NULL,
                    access_count INTEGER DEFAULT 0,
                    last_accessed INTEGER NOT NULL
                )
            """)
            await self.db.commit()
            log.info("TTS cache database initialized")
        except Exception as e:
            log.error(f"Failed to initialize TTS cache database: {e}")
    
    async def close(self) -> None:
        """Close database connection."""
        if self.db:
            await self.db.close()
    
    def _generate_hash(self, text: str, voice_id: str) -> str:
        """
        Generate a hash for text and voice combination.
        
        Args:
            text: Text to hash
            voice_id: Voice ID to include in hash
        
        Returns:
            Hex string hash
        """
        content = f"{text}|{voice_id}".encode("utf-8")
        return hashlib.sha256(content).hexdigest()
    
    async def _get_cached_audio(self, text: str, voice_id: str) -> Optional[str]:
        """
        Get cached audio file path if available.
        
        Args:
            text: Text to look up
            voice_id: Voice ID used
        
        Returns:
            File path if cached, None otherwise
        """
        if not self.cache_enabled or not self.db:
            return None
        
        text_hash = self._generate_hash(text, voice_id)
        
        try:
            async with self.db.execute(
                "SELECT file_path FROM tts_cache WHERE text_hash = ?",
                (text_hash,)
            ) as cursor:
                row = await cursor.fetchone()
                
                if row:
                    file_path = row[0]
                    if os.path.exists(file_path):
                        # Update access stats
                        await self.db.execute(
                            "UPDATE tts_cache SET access_count = access_count + 1, last_accessed = ? WHERE text_hash = ?",
                            (int(time.time()), text_hash)
                        )
                        await self.db.commit()
                        log.info(f"Cache HIT: {text[:50]}...")
                        return file_path
                    else:
                        # File deleted, remove from cache
                        await self.db.execute("DELETE FROM tts_cache WHERE text_hash = ?", (text_hash,))
                        await self.db.commit()
        except Exception as e:
            log.error(f"Cache lookup error: {e}")
        
        log.info(f"Cache MISS: {text[:50]}...")
        return None
    
    async def _cache_audio(self, text: str, voice_id: str, audio_data: bytes) -> str:
        """
        Cache audio data to file and database.
        
        Args:
            text: Original text
            voice_id: Voice ID used
            audio_data: Audio data to cache
        
        Returns:
            Path to cached file
        """
        text_hash = self._generate_hash(text, voice_id)
        file_path = self.cache_dir / f"{text_hash}.wav"
        
        try:
            # Write audio data to file
            with open(file_path, "wb") as f:
                f.write(audio_data)
            
            # Store in database
            now = int(time.time())
            
            if self.db:
                await self.db.execute(
                    """
                    INSERT OR REPLACE INTO tts_cache 
                    (text_hash, text, voice_id, file_path, created_at, access_count, last_accessed)
                    VALUES (?, ?, ?, ?, ?, 1, ?)
                    """,
                    (text_hash, text, voice_id, str(file_path), now, now)
                )
                await self.db.commit()
            
            log.info(f"Cached audio: {file_path}")
            return str(file_path)
        except Exception as e:
            log.error(f"Failed to cache audio: {e}")
            return ""
    
    async def synthesize_to_file(self, text: str) -> Optional[str]:
        """
        Synthesize text to audio file (cached or new).
        
        Args:
            text: Text to synthesize
        
        Returns:
            Path to audio file, or None on error
        """
        voice_id = self.provider.voice_id
        
        # Check cache first
        cached_path = await self._get_cached_audio(text, voice_id)
        if cached_path:
            return cached_path
        
        # Synthesize new audio
        audio_data = await self.provider.synthesize(text)
        if not audio_data:
            return None
        
        # Cache if enabled
        if self.cache_enabled:
            file_path = await self._cache_audio(text, voice_id, audio_data)
            return file_path
        else:
            # Save to temporary file with timestamp
            # Note: These files should be cleaned up periodically or after use
            temp_path = self.cache_dir / f"temp_{int(time.time() * 1000)}.wav"
            with open(temp_path, "wb") as f:
                f.write(audio_data)
            return str(temp_path)
    
    async def clean_temp_files(self) -> int:
        """
        Clean temporary audio files (created when caching is disabled).
        
        Returns:
            Number of files removed
        """
        try:
            removed = 0
            temp_pattern = "temp_*.wav"
            
            for temp_file in self.cache_dir.glob(temp_pattern):
                try:
                    # Remove files older than 1 hour
                    if (time.time() - temp_file.stat().st_mtime) > 3600:
                        temp_file.unlink()
                        removed += 1
                except Exception:
                    pass
            
            if removed > 0:
                log.info(f"Cleaned {removed} temporary audio files")
            return removed
        except Exception as e:
            log.error(f"Temp file cleanup error: {e}")
            return 0
    
    async def clean_old_cache(self) -> int:
        """
        Clean old cached audio files.
        
        Returns:
            Number of entries removed
        """
        if not self.cache_enabled or not self.db:
            return 0
        
        try:
            cutoff = int(time.time()) - (self.max_cache_age_days * 86400)
            
            # Get old entries
            async with self.db.execute(
                "SELECT text_hash, file_path FROM tts_cache WHERE last_accessed < ?",
                (cutoff,)
            ) as cursor:
                rows = await cursor.fetchall()
            
            removed = 0
            for text_hash, file_path in rows:
                # Delete file
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                except Exception:
                    pass
                
                # Remove from database
                await self.db.execute("DELETE FROM tts_cache WHERE text_hash = ?", (text_hash,))
                removed += 1
            
            await self.db.commit()
            log.info(f"Cleaned {removed} old cache entries")
            return removed
        except Exception as e:
            log.error(f"Cache cleaning error: {e}")
            return 0
