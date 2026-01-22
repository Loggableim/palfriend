"""
Settings module for handling configuration loading, saving, and management.
Supports both JSON (legacy) and YAML formats for better readability.
"""

import json
import logging
import os
from typing import Any, Dict

import yaml

log = logging.getLogger("ChatPalBrain")

SETTINGS_FILE_JSON = "settings.json"
SETTINGS_FILE_YAML = "settings.yaml"

DEFAULT_SETTINGS: Dict[str, Any] = {
    "tiktok": {"unique_id": "@PupCid", "session_id": ""},
    "animaze": {"host": "localhost", "port": 9000, "retry_max_attempts": 5, "retry_base_delay": 1.0},
    "openai": {"api_key": "", "model": "gpt-4o-mini", "cache_size": 128, "request_timeout": 10.0},
    "style": {"max_line_length": 140},
    "comment": {
        "enabled": 1,
        "global_cooldown": 6,
        "per_user_cooldown": 15,
        "min_length": 3,
        "max_replies_per_min": 20,
        "reply_threshold": 0.6,
        "respond_to_greetings": 1,
        "greeting_cooldown": 360,
        "respond_to_thanks": 1,
        "ignore_if_startswith": ["!"],
        "ignore_contains": ["http://", "https://", "discord.gg"],
        "keywords_bonus": [
            "warum", "wieso", "wie", "wann", "wo", "wer", "was", "welche", "welcher", "welches",
            "why", "how", "when", "where", "who", "what", "which", "how much", "how many"
        ],
        "greetings": ["hallo", "hi", "hey", "servus", "moin", "gruss", "grüß", "guten morgen", "guten abend", "hello"],
        "thanks": ["danke", "thx", "thanks", "ty", "merci"]
    },
    "batch_window": 25,
    "like_threshold": 20,
    "memory": {"enabled": 1, "file": "memory.json", "per_user_history": 100, "decay_days": 90},
    "dedupe_ttl": 600,
    "system_prompt": "Neutraler Assistent: präzise, kurze Antworten (max 25 Wörter) basierend auf Chat-Kontext und Memory.",
    "microphone": {
        "enabled": 1,
        "device": "",
        "silence_threshold": 0.02,
        "attack_ms": 120,
        "release_ms": 1200,
        "flush_delay_ms": 400
    },
    "join_rules": {
        "enabled": 1,
        "greet_after_seconds": 30,
        "active_ttl_seconds": 45,
        "min_idle_since_last_output_sec": 25,
        "greet_global_cooldown_sec": 180
    },
    "outbox": {"window_seconds": 8, "max_items": 8, "max_chars": 320, "separator": " • "},
    "speech": {"wait_start_timeout_ms": 1200, "max_speech_ms": 15000, "post_gap_ms": 250},
    "event_priority": {"gift": 3, "follow": 2, "subscribe": 3, "share": 2, "like": 1, "join": 1}
}


def _merge_settings(base: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively merge two configuration dictionaries.
    
    Args:
        base: Base configuration dictionary (will be modified)
        updates: Updates to merge into base
    
    Returns:
        Merged configuration dictionary
    """
    for key, value in updates.items():
        if isinstance(value, dict):
            base[key] = _merge_settings(base.get(key, {}), value)
        else:
            base.setdefault(key, value)
    return base


def load_settings() -> Dict[str, Any]:
    """
    Load settings from file, preferring YAML over JSON.
    Falls back to defaults if file doesn't exist or is corrupt.
    
    Returns:
        Configuration dictionary with all settings
    """
    # Try YAML first (preferred format)
    if os.path.isfile(SETTINGS_FILE_YAML):
        try:
            with open(SETTINGS_FILE_YAML, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f)
            log.info(f"Loaded settings from {SETTINGS_FILE_YAML}")
            merged = _merge_settings(json.loads(json.dumps(DEFAULT_SETTINGS)), cfg)
            save_settings(merged)
            return merged
        except yaml.YAMLError as e:
            log.error(f"YAML settings file corrupt: {e}. Trying JSON fallback.")
        except Exception as e:
            log.error(f"Error loading YAML settings: {e}. Trying JSON fallback.")
    
    # Try JSON fallback (legacy format)
    if os.path.isfile(SETTINGS_FILE_JSON):
        try:
            with open(SETTINGS_FILE_JSON, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            log.info(f"Loaded settings from {SETTINGS_FILE_JSON}")
            merged = _merge_settings(json.loads(json.dumps(DEFAULT_SETTINGS)), cfg)
            # Migrate to YAML
            save_settings(merged)
            return merged
        except json.JSONDecodeError as e:
            log.error(f"JSON settings file corrupt: {e}. Using defaults.")
        except Exception as e:
            log.error(f"Error loading JSON settings: {e}. Using defaults.")
    
    # Use defaults if no valid file found
    log.info("No valid settings file found, using defaults")
    save_settings(DEFAULT_SETTINGS)
    return json.loads(json.dumps(DEFAULT_SETTINGS))


def save_settings(cfg: Dict[str, Any]) -> None:
    """
    Save settings to YAML file.
    
    Args:
        cfg: Configuration dictionary to save
    """
    try:
        with open(SETTINGS_FILE_YAML, "w", encoding="utf-8") as f:
            yaml.dump(cfg, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        log.info(f"Settings saved to {SETTINGS_FILE_YAML}")
    except Exception as e:
        log.error(f"Failed to save settings: {e}")
