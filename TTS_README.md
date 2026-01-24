# Fish Audio TTS Integration

This document describes the Fish Audio TTS integration in PalFriend.

## Overview

PalFriend now supports local Text-to-Speech (TTS) using the Fish Audio API as an alternative to sending text to Animaze. This provides:

- **Independent Audio Generation**: Generate speech using Fish Audio's API
- **Audio Routing**: Route audio to specific output devices (e.g., Virtual Audio Cable)
- **Caching**: Reduce API costs and latency by caching generated audio
- **Voice Management**: Fetch and manage available Fish Audio voices

## Setup

### 1. Install Dependencies

The required dependencies are already in `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 2. Configure API Key

Copy `.env.example` to `.env` and add your Fish Audio API key:

```bash
cp .env.example .env
```

Edit `.env`:
```
FISH_AUDIO_API_KEY=your_api_key_here
FISH_AUDIO_VOICE_ID=your_voice_id_here
```

Get your API key from [fish.audio](https://fish.audio).

### 3. Fetch Available Voices

Run the voice fetcher script to get the list of available voices:

```bash
python scripts/fetch_voices.py
```

This will save all available voices to `data/voices.json`. Choose a voice ID and set it in your `.env` file.

### 4. Configure Settings

Update your `settings.yaml` to enable TTS:

```yaml
tts:
  enabled: 1                    # Enable TTS (1=on, 0=off)
  provider: fish_audio          # TTS provider
  fish_audio_api_key: ""        # Optional: can use .env instead
  fish_audio_voice_id: ""       # Optional: can use .env instead
  format: wav                   # Audio format
  sample_rate: 44100            # Sample rate
  cache_enabled: 1              # Enable audio caching
  max_cache_age_days: 30        # Cache retention period

audio:
  output_device: ""             # Output device (empty=default, or device name/index)
  sample_rate: 44100            # Audio sample rate
  channels: 1                   # Audio channels (1=mono, 2=stereo)
```

### 5. Configure Output Device (Optional)

To route audio to a Virtual Audio Cable or other device:

1. List available audio devices:
   ```python
   python -c "from modules.audio import AudioManager; m = AudioManager({'audio': {}}); print([d['name'] for d in m.list_devices()])"
   ```

2. Set the device name or index in `settings.yaml`:
   ```yaml
   audio:
     output_device: "Cable Input"  # or device index like "5"
   ```

## Architecture

### Modules

- **`modules/audio.py`**: AudioManager class for device management and playback
- **`modules/tts.py`**: TTSManager and FishAudioProvider classes with SQLite caching
- **`scripts/fetch_voices.py`**: Utility to fetch and save the voice list
- **`data/`**: Storage for voice list and audio cache

### How It Works

1. When TTS is enabled (`tts.enabled: 1`), the system uses local TTS instead of Animaze WebSocket
2. Text is sent to the Fish Audio API for synthesis
3. Generated audio is cached in SQLite database and filesystem
4. Audio is played through the configured output device
5. Speech state is managed manually (`speech.mark_started()`, `speech.mark_ended()`)
6. Animaze can listen to the audio output device as microphone input for lipsync

### Fallback Mode

If TTS initialization fails or is disabled (`tts.enabled: 0`), the system falls back to the original Animaze WebSocket mode.

## Testing

Test the TTS modules:

```bash
python scripts/test_tts.py
```

## Cache Management

- Audio files are cached in `data/audio_cache/`
- Metadata is stored in `data/tts_cache.db`
- Old cache entries are cleaned automatically after `max_cache_age_days`
- Manual cleanup: Delete `data/audio_cache/` and `data/tts_cache.db`

## Troubleshooting

### "Fish Audio API key not found"
- Ensure `.env` file exists with `FISH_AUDIO_API_KEY` set
- Or set `tts.fish_audio_api_key` in `settings.yaml`

### "Fish Audio voice ID not found"
- Run `python scripts/fetch_voices.py` to see available voices
- Set `FISH_AUDIO_VOICE_ID` in `.env` or `tts.fish_audio_voice_id` in `settings.yaml`

### "PortAudio library not found"
- Linux: `sudo apt-get install libportaudio2`
- macOS: `brew install portaudio`
- Windows: Usually included with Python sounddevice package

### No audio output
- Check `audio.output_device` setting
- Verify the device is available: Run the device list command above
- Check system audio settings

### Audio playback issues
- Verify sample rate matches device capabilities
- Try different audio channels (1 or 2)
- Check if Virtual Audio Cable is installed and configured

## Notes

- The system controls audio playback independently of Animaze's TTS
- Configure Animaze to use the output device (e.g., "Cable Output") as microphone input
- Caching significantly reduces API calls and improves response time
- The cache database uses SQLite with async support (aiosqlite)
