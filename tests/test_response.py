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
    assert rel.is_thanks("Thank you")
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
