"""
Tests for PromptComposer module.
"""
import pytest
from modules.prompt_composer import PromptComposer


@pytest.fixture
def test_config():
    """Create test configuration."""
    return {
        "system_prompt": "You are a helpful assistant.",
        "personality_bias": {
            "enabled": 1,
            "persona_profile": {
                "name": "TestBot",
                "backstory": "A friendly test assistant.",
                "key_traits": ["helpful", "concise", "friendly"]
            },
            "tone_weights": {
                "formal": 0.3,
                "casual": 0.5,
                "playful": 0.15,
                "sarcastic": 0.05
            },
            "stance_overrides": {"politics": "neutral"},
            "inject_mode": "prepend",
            "refusals": {
                "enabled": 1,
                "patterns": [
                    {"trigger": ["spam", "offensive"], "mode": "brief_and_cold"},
                    {"trigger": ["inappropriate"], "mode": "polite_decline"}
                ],
                "modes": {
                    "brief_and_cold": "I'd rather not respond to that.",
                    "polite_decline": "I appreciate your message, but I prefer not to engage with that topic."
                }
            },
            "safety_overrides": {
                "forbidden_topics": ["violence", "hate_speech"],
                "always_refuse": 1
            }
        }
    }


def test_prompt_composer_initialization(test_config):
    """Test PromptComposer initialization."""
    composer = PromptComposer(test_config)
    assert composer is not None
    assert composer.enabled == 1
    assert composer.base_system_prompt == "You are a helpful assistant."


def test_compose_prompt_prepend(test_config):
    """Test prompt composition with prepend mode."""
    composer = PromptComposer(test_config)
    
    tone_weights = test_config["personality_bias"]["tone_weights"]
    stance_overrides = test_config["personality_bias"]["stance_overrides"]
    
    prompt = composer.compose_prompt(tone_weights, stance_overrides)
    
    # Should contain persona info before base prompt
    assert "TestBot" in prompt
    assert "A friendly test assistant" in prompt
    assert "You are a helpful assistant" in prompt
    assert prompt.index("TestBot") < prompt.index("You are a helpful assistant")


def test_compose_prompt_append(test_config):
    """Test prompt composition with append mode."""
    test_config["personality_bias"]["inject_mode"] = "append"
    composer = PromptComposer(test_config)
    
    tone_weights = test_config["personality_bias"]["tone_weights"]
    stance_overrides = test_config["personality_bias"]["stance_overrides"]
    
    prompt = composer.compose_prompt(tone_weights, stance_overrides)
    
    # Should contain base prompt before persona info
    assert "TestBot" in prompt
    assert "You are a helpful assistant" in prompt
    assert prompt.index("You are a helpful assistant") < prompt.index("TestBot")


def test_compose_prompt_replace(test_config):
    """Test prompt composition with replace mode."""
    test_config["personality_bias"]["inject_mode"] = "replace"
    composer = PromptComposer(test_config)
    
    tone_weights = test_config["personality_bias"]["tone_weights"]
    stance_overrides = test_config["personality_bias"]["stance_overrides"]
    
    prompt = composer.compose_prompt(tone_weights, stance_overrides)
    
    # Should contain persona but not base prompt
    assert "TestBot" in prompt
    assert "You are a helpful assistant" not in prompt


def test_compose_prompt_includes_safety(test_config):
    """Test that safety overrides are always included."""
    composer = PromptComposer(test_config)
    
    tone_weights = test_config["personality_bias"]["tone_weights"]
    stance_overrides = test_config["personality_bias"]["stance_overrides"]
    
    prompt = composer.compose_prompt(tone_weights, stance_overrides)
    
    # Should contain safety rules
    assert "CRITICAL SAFETY RULE" in prompt
    assert "violence" in prompt
    assert "hate_speech" in prompt


def test_compose_prompt_disabled(test_config):
    """Test prompt composition when personality is disabled."""
    test_config["personality_bias"]["enabled"] = 0
    composer = PromptComposer(test_config)
    
    tone_weights = test_config["personality_bias"]["tone_weights"]
    stance_overrides = test_config["personality_bias"]["stance_overrides"]
    
    prompt = composer.compose_prompt(tone_weights, stance_overrides)
    
    # Should just return base prompt
    assert prompt == "You are a helpful assistant."


def test_check_refusal_spam(test_config):
    """Test refusal for spam."""
    composer = PromptComposer(test_config)
    
    refusal = composer.check_refusal("This is spam spam spam")
    
    assert refusal is not None
    assert refusal == "I'd rather not respond to that."


def test_check_refusal_inappropriate(test_config):
    """Test refusal for inappropriate content."""
    composer = PromptComposer(test_config)
    
    refusal = composer.check_refusal("This is inappropriate content")
    
    assert refusal is not None
    assert refusal == "I appreciate your message, but I prefer not to engage with that topic."


def test_check_refusal_normal(test_config):
    """Test no refusal for normal content."""
    composer = PromptComposer(test_config)
    
    refusal = composer.check_refusal("Hello, how are you?")
    
    assert refusal is None


def test_check_safety_refusal(test_config):
    """Test safety refusal for forbidden topics."""
    composer = PromptComposer(test_config)
    
    refusal = composer.check_refusal("Let's talk about violence")
    
    assert refusal is not None
    assert "cannot engage" in refusal.lower()


def test_check_safety_priority(test_config):
    """Test that safety overrides take priority over regular refusals."""
    composer = PromptComposer(test_config)
    
    # Contains both spam and violence
    refusal = composer.check_refusal("spam about violence")
    
    # Should use safety refusal
    assert "cannot engage" in refusal.lower()


def test_check_refusal_disabled(test_config):
    """Test refusal when disabled."""
    test_config["personality_bias"]["refusals"]["enabled"] = 0
    composer = PromptComposer(test_config)
    
    refusal = composer.check_refusal("This is spam")
    
    # Should not refuse when disabled (unless safety)
    assert refusal is None


def test_get_persona_summary(test_config):
    """Test getting persona summary."""
    composer = PromptComposer(test_config)
    
    tone_weights = test_config["personality_bias"]["tone_weights"]
    stance_overrides = test_config["personality_bias"]["stance_overrides"]
    
    summary = composer.get_persona_summary(tone_weights, stance_overrides)
    
    assert summary["enabled"] == 1
    assert summary["name"] == "TestBot"
    assert summary["backstory"] == "A friendly test assistant."
    assert summary["traits"] == ["helpful", "concise", "friendly"]
    assert summary["dominant_tone"] == "casual"
    assert summary["tone_weights"] == tone_weights
    assert summary["stance_overrides"] == stance_overrides


def test_compose_prompt_with_tone_weights(test_config):
    """Test that tone weights are reflected in prompt."""
    composer = PromptComposer(test_config)
    
    tone_weights = test_config["personality_bias"]["tone_weights"]
    stance_overrides = {}
    
    prompt = composer.compose_prompt(tone_weights, stance_overrides)
    
    # Should mention dominant tones
    assert "casual" in prompt.lower()


def test_compose_prompt_with_stance_overrides(test_config):
    """Test that stance overrides are reflected in prompt."""
    composer = PromptComposer(test_config)
    
    tone_weights = test_config["personality_bias"]["tone_weights"]
    stance_overrides = {"politics": "neutral", "sports": "enthusiastic"}
    
    prompt = composer.compose_prompt(tone_weights, stance_overrides)
    
    # Should mention stances
    assert "politics" in prompt.lower()
    assert "sports" in prompt.lower()
