#!/usr/bin/env python3
"""
Utility script to fetch and save the complete list of Fish Audio voices.
"""

import json
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def fetch_voices():
    """Fetch all available Fish Audio voices and save to data/voices.json"""
    
    # Get API key
    api_key = os.getenv("FISH_AUDIO_API_KEY")
    if not api_key:
        print("ERROR: FISH_AUDIO_API_KEY not found in environment")
        print("Please set it in .env file or export it")
        return False
    
    try:
        # Import Fish Audio SDK
        try:
            from fish_audio_sdk import Session
        except ImportError:
            print("ERROR: fish-audio-sdk not installed")
            print("Run: pip install fish-audio-sdk")
            return False
        
        print("Fetching voices from Fish Audio API...")
        
        # Create session
        session = Session(api_key)
        
        # Fetch voices
        # Note: The actual API method may vary depending on the SDK version
        # This is a placeholder implementation
        try:
            voices = session.list_voices()
            
            if not voices:
                print("No voices found")
                return False
            
            # Convert to JSON-serializable format
            voices_data = []
            for voice in voices:
                voice_info = {
                    "id": getattr(voice, "id", ""),
                    "name": getattr(voice, "name", ""),
                    "description": getattr(voice, "description", ""),
                    "language": getattr(voice, "language", ""),
                    "tags": getattr(voice, "tags", []),
                }
                voices_data.append(voice_info)
            
            # Save to file
            data_dir = Path("data")
            data_dir.mkdir(exist_ok=True)
            
            output_path = data_dir / "voices.json"
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(voices_data, f, indent=2, ensure_ascii=False)
            
            print(f"✓ Saved {len(voices_data)} voices to {output_path}")
            
            # Print some examples
            print("\nExample voices:")
            for i, voice in enumerate(voices_data[:5]):
                print(f"  {i+1}. {voice['name']} ({voice['id'][:16]}...)")
                if voice.get('description'):
                    print(f"     {voice['description']}")
            
            if len(voices_data) > 5:
                print(f"  ... and {len(voices_data) - 5} more")
            
            return True
        except AttributeError as e:
            # If list_voices doesn't exist, provide alternative
            print(f"ERROR: Unable to list voices: {e}")
            print("\nThe Fish Audio SDK may not support voice listing yet.")
            print("You can manually find voice IDs at: https://fish.audio/voices")
            print("or check the Fish Audio documentation for the correct API method.")
            return False
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point"""
    print("=" * 60)
    print("Fish Audio Voice Fetcher")
    print("=" * 60)
    print()
    
    success = fetch_voices()
    
    print()
    if success:
        print("✓ Voice list updated successfully")
        print("\nTo use a voice:")
        print("1. Open data/voices.json")
        print("2. Find the voice ID you want")
        print("3. Set FISH_AUDIO_VOICE_ID in .env or tts.fish_audio_voice_id in settings.yaml")
        return 0
    else:
        print("✗ Failed to fetch voices")
        print("\nTroubleshooting:")
        print("1. Verify your API key is correct")
        print("2. Check your internet connection")
        print("3. Visit https://fish.audio for documentation")
        return 1


if __name__ == "__main__":
    sys.exit(main())
