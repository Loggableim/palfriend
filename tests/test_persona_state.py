"""
Tests for PersonaStateStore module.
"""
import os
import tempfile
import pytest
from modules.persona_state import PersonaStateStore


@pytest.fixture
def test_config():
    """Create test configuration."""
    return {
        "enabled": 1,
        "tone_weights": {
            "formal": 0.3,
            "casual": 0.5,
            "playful": 0.15,
            "sarcastic": 0.05
        },
        "stance_overrides": {},
        "volatility": 0.05,
        "evolution_rules": {
            "enabled": 1,
            "triggers": {
                "positive_interaction": {"magnitude": 0.02, "target_tone": "playful"},
                "negative_interaction": {"magnitude": 0.03, "target_tone": "formal"}
            },
            "clamps": {
                "formal": [0.1, 0.8],
                "casual": [0.1, 0.8],
                "playful": [0.0, 0.5],
                "sarcastic": [0.0, 0.3]
            }
        },
        "persistence": {
            "scope": "session",
            "seed": 42
        }
    }


@pytest.fixture
def temp_db():
    """Create temporary database."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    yield db_path
    if os.path.exists(db_path):
        os.unlink(db_path)


def test_persona_store_initialization(test_config, temp_db):
    """Test PersonaStateStore initialization."""
    store = PersonaStateStore(test_config, temp_db)
    assert store is not None
    assert store.db_path == temp_db
    assert store.scope == "session"
    assert store.seed == 42


def test_get_default_state(test_config, temp_db):
    """Test getting default state when none saved."""
    store = PersonaStateStore(test_config, temp_db)
    state = store.get_state("test_scope")
    
    assert "tone_weights" in state
    assert "stance_overrides" in state
    assert state["tone_weights"] == test_config["tone_weights"]


def test_save_and_load_state(test_config, temp_db):
    """Test saving and loading persona state."""
    store = PersonaStateStore(test_config, temp_db)
    
    # Modify state
    tone_weights = {"formal": 0.4, "casual": 0.4, "playful": 0.15, "sarcastic": 0.05}
    stance_overrides = {"politics": "neutral"}
    
    # Save
    store.save_state("test_scope", tone_weights, stance_overrides)
    
    # Load
    loaded = store.get_state("test_scope")
    
    assert loaded["tone_weights"] == tone_weights
    assert loaded["stance_overrides"] == stance_overrides


def test_apply_drift_deterministic(test_config, temp_db):
    """Test drift with deterministic seed."""
    store = PersonaStateStore(test_config, temp_db)
    
    initial_weights = test_config["tone_weights"].copy()
    
    # Apply drift twice with same seed
    drifted1 = store.apply_drift(initial_weights, 0.05)
    
    # Reset store with same seed
    store2 = PersonaStateStore(test_config, temp_db)
    drifted2 = store2.apply_drift(initial_weights, 0.05)
    
    # Should be identical due to seed
    assert drifted1 == drifted2


def test_apply_drift_normalization(test_config, temp_db):
    """Test that drift maintains normalized weights."""
    store = PersonaStateStore(test_config, temp_db)
    
    initial_weights = test_config["tone_weights"].copy()
    drifted = store.apply_drift(initial_weights, 0.1)
    
    # Check normalization (sum should be 1.0)
    total = sum(drifted.values())
    assert abs(total - 1.0) < 0.01


def test_apply_evolution_positive(test_config, temp_db):
    """Test positive interaction evolution."""
    store = PersonaStateStore(test_config, temp_db)
    
    initial_weights = test_config["tone_weights"].copy()
    evolved = store.apply_evolution("test_scope", "positive_interaction", initial_weights)
    
    # Playful should increase
    assert evolved["playful"] > initial_weights["playful"]
    
    # Should remain normalized
    total = sum(evolved.values())
    assert abs(total - 1.0) < 0.01


def test_apply_evolution_with_clamps(test_config, temp_db):
    """Test evolution respects clamps."""
    store = PersonaStateStore(test_config, temp_db)
    
    # Start with weights near clamp limits
    weights = {"formal": 0.7, "casual": 0.15, "playful": 0.1, "sarcastic": 0.05}
    
    # Apply many positive evolutions
    for _ in range(20):
        weights = store.apply_evolution("test_scope", "positive_interaction", weights)
    
    # Check clamps are respected
    assert weights["playful"] <= 0.5  # Max clamp


def test_reset_state(test_config, temp_db):
    """Test resetting persona state."""
    store = PersonaStateStore(test_config, temp_db)
    
    # Save modified state
    modified_weights = {"formal": 0.5, "casual": 0.3, "playful": 0.15, "sarcastic": 0.05}
    store.save_state("test_scope", modified_weights, {})
    
    # Verify it was saved
    state = store.get_state("test_scope")
    assert state["tone_weights"] == modified_weights
    
    # Reset
    store.reset_state("test_scope")
    
    # Should return to defaults
    state = store.get_state("test_scope")
    assert state["tone_weights"] == test_config["tone_weights"]


def test_evolution_history(test_config, temp_db):
    """Test evolution history logging."""
    store = PersonaStateStore(test_config, temp_db)
    
    initial_weights = test_config["tone_weights"].copy()
    
    # Apply several evolutions
    weights = initial_weights
    for trigger in ["positive_interaction", "positive_interaction", "negative_interaction"]:
        weights = store.apply_evolution("test_scope", trigger, weights)
    
    # Get history
    history = store.get_evolution_history("test_scope", limit=10)
    
    assert len(history) == 3
    # Check that we have both types of interactions
    triggers = [h["trigger"] for h in history]
    assert "positive_interaction" in triggers
    assert "negative_interaction" in triggers
    assert triggers.count("positive_interaction") == 2
    assert "timestamp" in history[0]
    assert "magnitude" in history[0]


def test_no_drift_with_zero_volatility(test_config, temp_db):
    """Test that zero volatility means no drift."""
    store = PersonaStateStore(test_config, temp_db)
    
    initial_weights = test_config["tone_weights"].copy()
    drifted = store.apply_drift(initial_weights, 0.0)
    
    # Should be unchanged
    assert drifted == initial_weights


def test_evolution_disabled(test_config, temp_db):
    """Test evolution when disabled."""
    config = test_config.copy()
    config["evolution_rules"]["enabled"] = 0
    
    store = PersonaStateStore(config, temp_db)
    
    initial_weights = test_config["tone_weights"].copy()
    evolved = store.apply_evolution("test_scope", "positive_interaction", initial_weights)
    
    # Should be unchanged
    assert evolved == initial_weights


def test_unknown_trigger(test_config, temp_db):
    """Test evolution with unknown trigger."""
    store = PersonaStateStore(test_config, temp_db)
    
    initial_weights = test_config["tone_weights"].copy()
    evolved = store.apply_evolution("test_scope", "unknown_trigger", initial_weights)
    
    # Should be unchanged
    assert evolved == initial_weights


def test_interpolate_weights_disabled(test_config, temp_db):
    """Test interpolation when disabled."""
    config = test_config.copy()
    config["interpolation"] = {"enabled": False}
    
    store = PersonaStateStore(config, temp_db)
    
    current = {"formal": 0.8, "casual": 0.1, "playful": 0.1}
    target = {"formal": 0.1, "casual": 0.8, "playful": 0.1}
    
    # Should return target immediately when disabled
    result = store.interpolate_weights("test_scope", target, current)
    assert result == target


def test_interpolate_weights_gradual(test_config, temp_db):
    """Test gradual interpolation over time."""
    import time
    
    config = test_config.copy()
    config["interpolation"] = {"enabled": True, "duration_seconds": 1.0}  # 1 second for testing
    
    store = PersonaStateStore(config, temp_db)
    
    current = {"formal": 0.8, "casual": 0.1, "playful": 0.1}
    target = {"formal": 0.1, "casual": 0.8, "playful": 0.1}
    
    # First call should return current
    result1 = store.interpolate_weights("test_scope", target, current)
    assert result1 == current
    
    # Wait a bit
    time.sleep(0.5)  # Half duration
    
    # Should be somewhere between current and target
    result2 = store.interpolate_weights("test_scope", target, result1)
    assert result2["formal"] < current["formal"]
    assert result2["formal"] > target["formal"]
    assert result2["casual"] > current["casual"]
    assert result2["casual"] < target["casual"]
    
    # Wait until completion
    time.sleep(0.6)
    
    # Should be at target now
    result3 = store.interpolate_weights("test_scope", target, result2)
    assert abs(result3["formal"] - target["formal"]) < 0.01
    assert abs(result3["casual"] - target["casual"]) < 0.01


def test_interpolate_weights_target_change(test_config, temp_db):
    """Test interpolation when target changes mid-transition."""
    config = test_config.copy()
    config["interpolation"] = {"enabled": True, "duration_seconds": 10.0}
    
    store = PersonaStateStore(config, temp_db)
    
    current = {"formal": 0.8, "casual": 0.1, "playful": 0.1}
    target1 = {"formal": 0.1, "casual": 0.8, "playful": 0.1}
    target2 = {"formal": 0.3, "casual": 0.3, "playful": 0.4}
    
    # Start interpolation to target1
    result1 = store.interpolate_weights("test_scope", target1, current)
    assert result1 == current
    
    # Change target to target2
    result2 = store.interpolate_weights("test_scope", target2, result1)
    
    # Should restart interpolation with new target
    assert "test_scope" in store._interpolation_state
    assert store._interpolation_state["test_scope"]["target"] == target2
