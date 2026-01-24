"""
Audio device management and playback module for TTS output.
"""

import asyncio
import logging
import time
from typing import Optional, Dict, Any

import numpy as np
import sounddevice as sd
import soundfile as sf

log = logging.getLogger("ChatPalBrain")


class AudioManager:
    """
    Manages audio device selection and playback for TTS output.
    Supports routing audio to specific output devices (e.g., Virtual Audio Cable).
    """
    
    def __init__(self, cfg: Dict[str, Any]) -> None:
        """
        Initialize AudioManager.
        
        Args:
            cfg: Configuration dictionary with 'audio' section
        """
        self.cfg = cfg
        audio_cfg = cfg.get("audio", {})
        
        # Output device configuration
        self.output_device = audio_cfg.get("output_device", None)
        if self.output_device == "":
            self.output_device = None
        
        # Playback settings
        self.sample_rate = int(audio_cfg.get("sample_rate", 44100))
        self.channels = int(audio_cfg.get("channels", 1))
        
        # State
        self._playing = False
        self._play_lock = asyncio.Lock()
        
        log.info(f"AudioManager initialized (device={self.output_device}, rate={self.sample_rate})")
    
    def list_devices(self) -> list:
        """
        List all available audio devices.
        
        Returns:
            List of device dictionaries with name, index, and channel info
        """
        try:
            devices = sd.query_devices()
            return [
                {
                    "index": i,
                    "name": dev["name"],
                    "max_output_channels": dev["max_output_channels"],
                    "default_samplerate": dev["default_samplerate"]
                }
                for i, dev in enumerate(devices)
                if dev["max_output_channels"] > 0
            ]
        except Exception as e:
            log.error(f"Failed to list audio devices: {e}")
            return []
    
    async def play_audio(self, audio_data: np.ndarray, sample_rate: int) -> None:
        """
        Play audio data to the configured output device.
        
        Args:
            audio_data: Audio samples as numpy array
            sample_rate: Sample rate of the audio
        """
        async with self._play_lock:
            try:
                self._playing = True
                
                # Prepare audio data
                if audio_data.ndim == 1:
                    # Mono to stereo if needed
                    if self.channels == 2:
                        audio_data = np.stack([audio_data, audio_data], axis=1)
                elif audio_data.ndim == 2:
                    # Ensure correct number of channels
                    if audio_data.shape[1] != self.channels:
                        if self.channels == 1:
                            # Stereo to mono
                            audio_data = np.mean(audio_data, axis=1)
                        else:
                            # Mono to stereo
                            audio_data = np.stack([audio_data[:, 0], audio_data[:, 0]], axis=1)
                
                # Play audio
                device = self.output_device
                if device is not None:
                    try:
                        # Try to parse as integer device index
                        device = int(device)
                    except (ValueError, TypeError):
                        # Keep as string device name
                        pass
                
                # Use blocking play for simplicity
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: sd.play(audio_data, samplerate=sample_rate, device=device, blocking=True)
                )
                
                log.info(f"Audio playback completed ({len(audio_data)/sample_rate:.2f}s)")
            except Exception as e:
                log.error(f"Audio playback error: {e}")
            finally:
                self._playing = False
    
    async def play_file(self, file_path: str) -> None:
        """
        Play an audio file to the configured output device.
        
        Args:
            file_path: Path to the audio file
        """
        try:
            # Load audio file
            audio_data, sample_rate = sf.read(file_path, dtype='float32')
            await self.play_audio(audio_data, sample_rate)
        except Exception as e:
            log.error(f"Failed to play audio file {file_path}: {e}")
    
    def is_playing(self) -> bool:
        """
        Check if audio is currently playing.
        
        Returns:
            True if audio is playing, False otherwise
        """
        return self._playing
    
    def set_output_device(self, device: Optional[str]) -> None:
        """
        Set the output device.
        
        Args:
            device: Device name or index (None for default)
        """
        self.output_device = device
        log.info(f"Audio output device set to: {device}")
