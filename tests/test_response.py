"""
Tests for Phase 5: Response Generation (response.py)
"""
import pytest
from response import Relevance


def test_relevance_scoring_question():
    """Test that questions get high relevance scores."""
    config = {
        "keywords_bonus": ["why", "how", "what", "when", "where", "who"],
        "ignore_if_startswith": ["!"],
        "ignore_contains": []
    }
    
    rel = Relevance(config)
    
    # Question should score high
    score = rel.score("Why is the sky blue?")
    assert score > 0.5
    
    # Statement should score lower
    score = rel.score("The sky is blue.")
    assert score <= 0.5


def test_relevance_ignore_commands():
    """Test that commands are ignored."""
    config = {
        "keywords_bonus": [],
        "ignore_if_startswith": ["!", "/"],
        "ignore_contains": []
    }
    
    rel = Relevance(config)
    
    assert rel.is_ignored("!help")
    assert rel.is_ignored("/command")
    assert not rel.is_ignored("Hello")


def test_relevance_ignore_urls():
    """Test that URLs are ignored."""
    config = {
        "keywords_bonus": [],
        "ignore_if_startswith": [],
        "ignore_contains": ["http://", "https://"]
    }
    
    rel = Relevance(config)
    
    assert rel.is_ignored("Check out http://example.com")
    assert rel.is_ignored("Visit https://example.com")
    assert not rel.is_ignored("Hello world")


def test_relevance_greeting_detection():
    """Test greeting detection."""
    config = {
        "keywords_bonus": [],
        "ignore_if_startswith": [],
        "ignore_contains": []
    }
    
    rel = Relevance(config)
    
    assert rel.is_greeting("Hello everyone!")
    assert rel.is_greeting("Hi there")
    assert rel.is_greeting("hey")
    assert not rel.is_greeting("How are you?")


def test_relevance_thanks_detection():
    """Test thank you detection."""
    config = {
        "keywords_bonus": [],
        "ignore_if_startswith": [],
        "ignore_contains": []
    }
    
    rel = Relevance(config)
    
    assert rel.is_thanks("Thanks!")
    assert rel.is_thanks("thanks")
    assert rel.is_thanks("thx")
    assert not rel.is_thanks("Hello")


def test_relevance_length_bonus():
    """Test that longer messages get bonus."""
    config = {
        "keywords_bonus": [],
        "ignore_if_startswith": [],
        "ignore_contains": []
    }
    
    rel = Relevance(config)
    
    short_score = rel.score("Hi")
    long_score = rel.score("This is a longer message with more words")
    
    # Longer message should score higher
    assert long_score > short_score


def test_relevance_fuzzy_spam_detection():
    """Test fuzzy spam detection."""
    config = {
        "keywords_bonus": [],
        "ignore_if_startswith": [],
        "ignore_contains": []
    }
    
    rel = Relevance(config)
    
    # Test common spam variations with typos
    assert rel.is_ignored("F0llow me")
    assert rel.is_ignored("Folow me")
    assert rel.is_ignored("Follow mee")
    assert rel.is_ignored("Check out my channel")
    assert not rel.is_ignored("I follow your advice")


def test_relevance_sentiment_positive():
    """Test sentiment analysis for positive messages."""
    config = {
        "keywords_bonus": [],
        "ignore_if_startswith": [],
        "ignore_contains": []
    }
    
    rel = Relevance(config)
    
    # Skip if sentiment analyzer not available
    if not rel.sentiment_analyzer:
        pytest.skip("vaderSentiment not installed")
    
    sentiment = rel.get_sentiment("I love this! This is amazing!")
    assert sentiment > 0.3  # Should be positive


def test_relevance_sentiment_negative():
    """Test sentiment analysis for negative messages."""
    config = {
        "keywords_bonus": [],
        "ignore_if_startswith": [],
        "ignore_contains": []
    }
    
    rel = Relevance(config)
    
    # Skip if sentiment analyzer not available
    if not rel.sentiment_analyzer:
        pytest.skip("vaderSentiment not installed")
    
    sentiment = rel.get_sentiment("I hate this. This is terrible.")
    assert sentiment < -0.3  # Should be negative


def test_relevance_sentiment_neutral():
    """Test sentiment analysis for neutral messages."""
    config = {
        "keywords_bonus": [],
        "ignore_if_startswith": [],
        "ignore_contains": []
    }
    
    rel = Relevance(config)
    
    # Skip if sentiment analyzer not available
    if not rel.sentiment_analyzer:
        pytest.skip("vaderSentiment not installed")
    
    sentiment = rel.get_sentiment("The weather is nice today.")
    assert -0.3 <= sentiment <= 0.3  # Should be neutral


def test_relevance_apply_sentiment_positive():
    """Test applying positive sentiment to tone weights."""
    config = {
        "keywords_bonus": [],
        "ignore_if_startswith": [],
        "ignore_contains": []
    }
    
    rel = Relevance(config)
    
    tone_weights = {
        "happy": 0.3,
        "tired": 0.3,
        "neutral": 0.4
    }
    
    adjusted = rel.apply_sentiment(0.5, tone_weights)
    
    # Happy should increase
    assert adjusted["happy"] > tone_weights["happy"]
    # Weights should still sum to ~1.0
    assert abs(sum(adjusted.values()) - 1.0) < 0.01


def test_relevance_apply_sentiment_negative():
    """Test applying negative sentiment to tone weights."""
    config = {
        "keywords_bonus": [],
        "ignore_if_startswith": [],
        "ignore_contains": []
    }
    
    rel = Relevance(config)
    
    tone_weights = {
        "happy": 0.3,
        "gloomy": 0.3,
        "neutral": 0.4
    }
    
    adjusted = rel.apply_sentiment(-0.5, tone_weights)
    
    # Gloomy should increase
    assert adjusted["gloomy"] > tone_weights["gloomy"]
    # Weights should still sum to ~1.0
    assert abs(sum(adjusted.values()) - 1.0) < 0.01
