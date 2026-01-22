"""
Tests for Phase 1: Settings Management (settings.py)
"""
import os
import tempfile
import pytest
from settings import load_settings, save_settings, DEFAULT_SETTINGS


def test_default_settings_structure():
    """Test that default settings have all required keys."""
    assert "tiktok" in DEFAULT_SETTINGS
    assert "animaze" in DEFAULT_SETTINGS
    assert "openai" in DEFAULT_SETTINGS
    assert "comment" in DEFAULT_SETTINGS
    assert "memory" in DEFAULT_SETTINGS


def test_load_settings_creates_default():
    """Test that load_settings creates default settings when file doesn't exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        settings = load_settings()
        assert settings is not None
        assert "tiktok" in settings
        assert settings["tiktok"]["unique_id"] == "@PupCid"


def test_save_and_load_settings():
    """Test that settings can be saved and loaded."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "test_settings.yaml")
        os.environ["SETTINGS_FILE_YAML"] = test_file
        
        # Create test settings
        test_settings = DEFAULT_SETTINGS.copy()
        test_settings["tiktok"]["unique_id"] = "@TestUser"
        
        # Save
        save_settings(test_settings)
        
        # Load
        loaded = load_settings()
        assert loaded["tiktok"]["unique_id"] == "@TestUser"


def test_settings_yaml_format():
    """Test that settings are saved in YAML format."""
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        settings = load_settings()
        save_settings(settings)
        
        # Check that YAML file exists
        assert os.path.exists("settings.yaml")
