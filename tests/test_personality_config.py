"""
Tests for personality bias configuration and integration.
"""
import json
import os
import tempfile
import pytest
from settings import load_settings, save_settings, DEFAULT_SETTINGS


def test_personality_bias_in_defaults():
    """Test that personality_bias is in DEFAULT_SETTINGS."""
    assert "personality_bias" in DEFAULT_SETTINGS
    pb = DEFAULT_SETTINGS["personality_bias"]
    
    # Check structure
    assert "enabled" in pb
    assert "persona_profile" in pb
    assert "tone_weights" in pb
    assert "stance_overrides" in pb
    assert "volatility" in pb
    assert "evolution_rules" in pb
    assert "refusals" in pb
    assert "safety_overrides" in pb
    assert "inject_mode" in pb
    assert "persistence" in pb


def test_personality_bias_persona_profile():
    """Test persona profile structure."""
    profile = DEFAULT_SETTINGS["personality_bias"]["persona_profile"]
    
    assert "name" in profile
    assert "backstory" in profile
    assert "key_traits" in profile
    assert isinstance(profile["key_traits"], list)


def test_personality_bias_tone_weights():
    """Test tone weights structure."""
    tone_weights = DEFAULT_SETTINGS["personality_bias"]["tone_weights"]
    
    # Check that weights sum to approximately 1.0
    total = sum(tone_weights.values())
    assert abs(total - 1.0) < 0.01, f"Tone weights sum to {total}, expected ~1.0"
    
    # Check all weights are non-negative
    for tone, weight in tone_weights.items():
        assert weight >= 0, f"Negative weight for {tone}: {weight}"


def test_personality_bias_evolution_rules():
    """Test evolution rules structure."""
    rules = DEFAULT_SETTINGS["personality_bias"]["evolution_rules"]
    
    assert "enabled" in rules
    assert "triggers" in rules
    assert "clamps" in rules
    
    # Check triggers structure
    triggers = rules["triggers"]
    for trigger_name, trigger_config in triggers.items():
        assert "magnitude" in trigger_config
        assert "target_tone" in trigger_config


def test_personality_bias_refusals():
    """Test refusals structure."""
    refusals = DEFAULT_SETTINGS["personality_bias"]["refusals"]
    
    assert "enabled" in refusals
    assert "patterns" in refusals
    assert "modes" in refusals
    
    # Check patterns structure
    patterns = refusals["patterns"]
    assert isinstance(patterns, list)
    for pattern in patterns:
        assert "trigger" in pattern
        assert "mode" in pattern


def test_personality_bias_safety_overrides():
    """Test safety overrides structure."""
    safety = DEFAULT_SETTINGS["personality_bias"]["safety_overrides"]
    
    assert "forbidden_topics" in safety
    assert "always_refuse" in safety
    assert isinstance(safety["forbidden_topics"], list)


def test_personality_bias_persistence():
    """Test persistence config structure."""
    persistence = DEFAULT_SETTINGS["personality_bias"]["persistence"]
    
    assert "scope" in persistence
    assert "db_path" in persistence
    assert "seed" in persistence
    assert persistence["scope"] in ["session", "user"]


def test_personality_bias_inject_mode():
    """Test inject_mode is valid."""
    inject_mode = DEFAULT_SETTINGS["personality_bias"]["inject_mode"]
    assert inject_mode in ["prepend", "append", "replace"]


def test_personality_bias_load_and_save():
    """Test that personality_bias persists through save/load."""
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        
        # Create custom settings (not loading first)
        settings = DEFAULT_SETTINGS.copy()
        settings["personality_bias"]["enabled"] = 1
        settings["personality_bias"]["persona_profile"]["name"] = "TestBot"
        settings["personality_bias"]["volatility"] = 0.05
        
        # Save
        save_settings(settings)
        
        # Load again
        loaded = load_settings()
        
        # Verify changes persisted
        assert loaded["personality_bias"]["enabled"] == 1
        assert loaded["personality_bias"]["persona_profile"]["name"] == "TestBot"
        assert loaded["personality_bias"]["volatility"] == 0.05
