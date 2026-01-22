"""
Speech and microphone state management module.
"""

import asyncio
import logging
import time
from typing import Optional

import numpy as np
import sounddevice as sd

log = logging.getLogger("ChatPalBrain")


class SpeechState:
    """
    Manages the state of speech output (speaking/idle).
    """
    
    def __init__(self) -> None:
        """Initialize speech state tracking."""
        self._started = asyncio.Event()
        self._ended = asyncio.Event()
        self._ended.set()
    
    def mark_started(self) -> None:
        """Mark that speech has started."""
        self._ended.clear()
        self._started.set()
        log.info("ChatPal meldet: SpeechStarted")
    
    def mark_ended(self) -> None:
        """Mark that speech has ended."""
        self._started.clear()
        self._ended.set()
        log.info("ChatPal meldet: SpeechEnded")
    
    async def wait_idle(self) -> None:
        """Wait until speech is idle."""
        await self._ended.wait()
    
    async def wait_started(self, timeout: Optional[float] = None) -> bool:
        """
        Wait for speech to start.
        
        Args:
            timeout: Optional timeout in seconds
        
        Returns:
            True if speech started, False if timeout occurred
        """
        if timeout is None:
            await self._started.wait()
            return True
        try:
            await asyncio.wait_for(self._started.wait(), timeout)
            return True
        except asyncio.TimeoutError:
            return False
    
    async def wait_ended(self, timeout: Optional[float] = None) -> bool:
        """
        Wait for speech to end.
        
        Args:
            timeout: Optional timeout in seconds
        
        Returns:
            True if speech ended, False if timeout occurred
        """
        if timeout is None:
            await self._ended.wait()
            return True
        try:
            await asyncio.wait_for(self._ended.wait(), timeout)
            return True
        except asyncio.TimeoutError:
            return False
    
    def is_speaking(self) -> bool:
        """
        Check if currently speaking.
        
        Returns:
            True if speaking, False otherwise
        """
        return self._started.is_set() and not self._ended.is_set()


class MicState:
    """
    Manages the state of microphone input (active/idle).
    """
    
    def __init__(self) -> None:
        """Initialize microphone state tracking."""
        self._active = False
        self._active_event = asyncio.Event()
        self._idle_event = asyncio.Event()
        self._idle_event.set()
        self.last_active_ts = 0.0
        self.last_idle_ts = time.time()
    
    def mark_active(self) -> None:
        """Mark that microphone is active."""
        if not self._active:
            self._active = True
            self._active_event.set()
            self._idle_event.clear()
            self.last_active_ts = time.time()
            log.info("Mic Status: aktiv")
    
    def mark_idle(self) -> None:
        """Mark that microphone is idle."""
        if self._active:
            self._active = False
            self._idle_event.set()
            self._active_event.clear()
            self.last_idle_ts = time.time()
            log.info("Mic Status: idle")
    
    async def wait_idle(self) -> None:
        """Wait until microphone is idle."""
        await self._idle_event.wait()
    
    def is_active(self) -> bool:
        """
        Check if microphone is active.
        
        Returns:
            True if active, False otherwise
        """
        return self._active


class MicrophoneMonitor:
    """
    Monitors microphone input and detects voice activity.
    """
    
    def __init__(self, cfg: dict, mic_state: MicState, level_cb=None) -> None:
        """
        Initialize microphone monitor.
        
        Args:
            cfg: Configuration dictionary
            mic_state: MicState instance to update
            level_cb: Optional callback for level updates
        """
        self.cfg = cfg
        self.mic_state = mic_state
        self.stream = None
        self.running = False
        self.threshold = float(cfg["microphone"].get("silence_threshold", 0.02))
        self.attack_ms = int(cfg["microphone"].get("attack_ms", 120))
        self.release_ms = int(cfg["microphone"].get("release_ms", 1200))
        self.device = cfg["microphone"].get("device", "")
        self._last_above = 0.0
        self._last_below = time.time()
        self._level = 0.0
        self._level_cb = level_cb
        self._attack_reached = False
    
    def _callback(self, indata, frames, time_info, status) -> None:
        """
        Audio callback for processing microphone input.
        
        Args:
            indata: Input audio data
            frames: Number of frames
            time_info: Timing information
            status: Status flags
        """
        try:
            data = np.asarray(indata, dtype=np.float32)
            if data.ndim > 1:
                data = np.mean(data, axis=1)
            rms = float(np.sqrt(np.mean(np.square(data)))) if data.size else 0.0
            self._level = rms
            
            if self._level_cb:
                try:
                    self._level_cb(rms)
                except Exception:
                    pass
            
            now = time.time()
            if rms >= self.threshold:
                if not self._attack_reached:
                    self._attack_reached = True
                    self._last_above = now
                if (now - self._last_above) * 1000 >= self.attack_ms:
                    self.mic_state.mark_active()
                self._last_below = now
            else:
                if (now - self._last_below) * 1000 >= self.release_ms:
                    self.mic_state.mark_idle()
                    self._attack_reached = False
        except Exception:
            pass
    
    def start(self) -> None:
        """Start monitoring microphone input."""
        if self.running:
            return
        self.running = True
        kwargs = {"channels": 1, "dtype": "float32", "callback": self._callback}
        if self.device:
            try:
                dev_index = int(self.device)
                kwargs["device"] = dev_index
            except ValueError:
                kwargs["device"] = self.device
        self.stream = sd.InputStream(**kwargs)
        self.stream.start()
        log.info("Mic Monitor gestartet")
    
    def stop(self) -> None:
        """Stop monitoring microphone input."""
        if not self.running:
            return
        try:
            self.stream.stop()
            self.stream.close()
        except Exception:
            pass
        self.running = False
        log.info("Mic Monitor gestoppt")
    
    def set_device(self, device: str) -> None:
        """
        Change microphone device.
        
        Args:
            device: Device name or index
        """
        self.device = device
        try:
            self.stop()
        except Exception:
            pass
        try:
            self.start()
        except Exception:
            pass
    
    @property
    def level(self) -> float:
        """
        Get current microphone level.
        
        Returns:
            Current RMS level
        """
        return self._level
