#!/usr/bin/env python3
"""
Simple test script to verify TTS and Audio module initialization.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.audio import AudioManager
from modules.tts import TTSManager


async def test_initialization():
    """Test basic initialization of modules."""
    print("Testing module initialization...")
    
    # Test configuration
    cfg = {
        "audio": {
            "output_device": None,
            "sample_rate": 44100,
            "channels": 1,
        },
        "tts": {
            "enabled": 1,
            "provider": "fish_audio",
            "fish_audio_api_key": "test_key",
            "fish_audio_voice_id": "test_voice_id",
            "format": "wav",
            "sample_rate": 44100,
            "cache_enabled": 1,
            "max_cache_age_days": 30,
        }
    }
    
    # Test AudioManager
    print("  Initializing AudioManager...")
    audio_mgr = AudioManager(cfg)
    print(f"  ✓ AudioManager initialized (device={audio_mgr.output_device})")
    
    # Test device listing
    devices = audio_mgr.list_devices()
    print(f"  ✓ Found {len(devices)} audio output devices")
    if devices:
        print("    Example devices:")
        for dev in devices[:3]:
            print(f"      - {dev['name']} (index={dev['index']})")
    
    # Test TTSManager
    print("  Initializing TTSManager...")
    tts_mgr = TTSManager(cfg, cache_dir="/tmp/test_cache")
    await tts_mgr.initialize()
    print("  ✓ TTSManager initialized")
    print(f"    Cache enabled: {tts_mgr.cache_enabled}")
    print(f"    Cache dir: {tts_mgr.cache_dir}")
    
    # Close resources
    await tts_mgr.close()
    print("  ✓ TTSManager closed")
    
    print("\n✅ All tests passed!")
    return True


def main():
    """Main entry point"""
    print("=" * 60)
    print("PalFriend TTS Module Test")
    print("=" * 60)
    print()
    
    try:
        success = asyncio.run(test_initialization())
        return 0 if success else 1
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
