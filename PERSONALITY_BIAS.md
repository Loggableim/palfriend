# Personality-Bias Feature Guide

## Overview

The Personality-Bias feature allows PalFriend to have a configurable, evolving personality that influences how it responds to users. The personality can drift over time, evolve based on interactions, and maintain safety guardrails.

## Configuration

Add the following to your `settings.yaml`:

```yaml
personality_bias:
  enabled: 1  # Set to 0 to disable
  
  # Persona Profile
  persona_profile:
    name: "PalBot"
    backstory: "A friendly AI assistant who enjoys helping users."
    key_traits:
      - helpful
      - friendly
      - concise
  
  # Tone Weights (must sum to ~1.0)
  tone_weights:
    formal: 0.3
    casual: 0.5
    playful: 0.15
    sarcastic: 0.05
  
  # Topic-based stance overrides
  stance_overrides: {}
  
  # Volatility (drift rate per interaction, 0.0-1.0)
  volatility: 0.01
  
  # Evolution Rules
  evolution_rules:
    enabled: 1
    triggers:
      positive_interaction:
        magnitude: 0.02
        target_tone: playful
      negative_interaction:
        magnitude: 0.03
        target_tone: formal
      spam_detected:
        magnitude: 0.05
        target_tone: sarcastic
    clamps:
      formal: [0.1, 0.8]
      casual: [0.1, 0.8]
      playful: [0.0, 0.5]
      sarcastic: [0.0, 0.3]
  
  # Refusal Logic
  refusals:
    enabled: 1
    patterns:
      - trigger: ["spam", "offensive"]
        mode: brief_and_cold
      - trigger: ["inappropriate"]
        mode: polite_decline
    modes:
      brief_and_cold: "I'd rather not respond to that."
      polite_decline: "I appreciate your message, but I prefer not to engage with that topic."
  
  # Safety Overrides (highest priority)
  safety_overrides:
    forbidden_topics:
      - violence
      - hate_speech
      - illegal_activity
    always_refuse: 1
  
  # Inject Mode: prepend, append, or replace
  inject_mode: prepend
  
  # Persistence Settings
  persistence:
    scope: session  # "session" or "user"
    db_path: ./persona_state.db
    seed: null  # Set to an integer for deterministic testing
```

## Inject Modes

The `inject_mode` controls how the persona is added to the system prompt:

- **prepend**: Persona description comes before the base system prompt (recommended)
- **append**: Persona description comes after the base system prompt
- **replace**: Persona description replaces the base system prompt entirely

Example with `prepend`:
```
Persona: PalBot. A friendly AI assistant.
Key traits: helpful, friendly, concise
Current tone balance: casual (50.0%), formal (30.0%)

CRITICAL SAFETY RULE: Never engage with: violence, hate_speech, illegal_activity

[Original system prompt follows...]
```

## Evolution Semantics

### Volatility Drift

On each interaction, tone weights experience random drift based on the `volatility` parameter:
- `volatility: 0.0` = No drift (static personality)
- `volatility: 0.01` = Minimal drift (~1% per interaction)
- `volatility: 0.1` = Moderate drift (~10% per interaction)

Weights are always normalized to sum to 1.0 after drift.

### Evolution Triggers

When specific events occur, evolution rules shift the personality toward a target tone:

```python
# Positive interaction increases playful tone
positive_interaction:
  magnitude: 0.02  # +2% shift
  target_tone: playful

# Spam detection increases sarcastic tone
spam_detected:
  magnitude: 0.05  # +5% shift
  target_tone: sarcastic
```

### Clamps

Clamps prevent tones from going too high or too low:

```yaml
clamps:
  playful: [0.0, 0.5]  # Playful can be 0-50%
  sarcastic: [0.0, 0.3]  # Sarcastic capped at 30%
```

## Refusal Logic

The system can refuse to respond to certain patterns while maintaining safety:

### Pattern Matching

```yaml
patterns:
  - trigger: ["spam", "offensive"]  # Keywords to match
    mode: brief_and_cold            # Response mode
```

### Safety Priority

Safety overrides always take precedence:

1. Check forbidden topics (violence, hate_speech, etc.)
2. If matched, refuse with safety message
3. Otherwise, check refusal patterns
4. If matched, refuse with configured mode
5. Otherwise, generate normal response

## API Endpoints

### Get Persona State

```bash
GET /api/persona/state?scope_id=session
```

Response:
```json
{
  "success": true,
  "data": {
    "enabled": 1,
    "name": "PalBot",
    "backstory": "A friendly AI assistant.",
    "traits": ["helpful", "friendly", "concise"],
    "dominant_tone": "casual",
    "tone_weights": {
      "formal": 0.3,
      "casual": 0.5,
      "playful": 0.15,
      "sarcastic": 0.05
    },
    "stance_overrides": {},
    "evolution_history": [
      {
        "trigger": "positive_interaction",
        "magnitude": 0.02,
        "target_tone": "playful",
        "timestamp": "2024-01-20 10:30:45"
      }
    ]
  }
}
```

### Reset Persona

```bash
POST /api/persona/reset
Content-Type: application/json

{
  "scope_id": "session"
}
```

Response:
```json
{
  "success": true,
  "message": "Persona reset for session"
}
```

### Update Persona

```bash
PATCH /api/persona/update
Content-Type: application/json

{
  "scope_id": "session",
  "tone_weights": {
    "formal": 0.4,
    "casual": 0.4,
    "playful": 0.15,
    "sarcastic": 0.05
  },
  "stance_overrides": {
    "politics": "neutral"
  }
}
```

## Seed-Based Determinism

For testing, you can set a random seed to make personality drift reproducible:

```yaml
persistence:
  seed: 42  # Any integer
```

With a seed:
- Drift will be identical across runs
- Evolution remains deterministic
- Useful for automated testing and debugging

## Scoping

Personas can be scoped to:

- **session**: One persona shared across all users in a session
- **user**: Individual persona per user (user_id)

Set via:
```yaml
persistence:
  scope: session  # or "user"
```

## Integration Points

### Telemetry (To Be Implemented)

Future telemetry can track:

- **Refusal Rate**: How often refusal patterns trigger
  ```python
  telemetry.increment("persona.refusal", tags={"mode": "brief_and_cold"})
  ```

- **Tone Coherence**: Measure consistency of tone over time
  ```python
  telemetry.gauge("persona.tone.drift", value=drift_magnitude)
  ```

- **Evolution Events**: Log when personality shifts
  ```python
  telemetry.increment("persona.evolution", tags={"trigger": "positive_interaction"})
  ```

### Custom Triggers

To add custom evolution triggers, update the configuration:

```yaml
evolution_rules:
  triggers:
    gift_received:
      magnitude: 0.1
      target_tone: playful
    long_silence:
      magnitude: 0.05
      target_tone: formal
```

Then in your code:
```python
# After gift event
if response_engine.persona_store:
    scope_id = uid if response_engine.persona_store.scope == "user" else "session"
    state = response_engine.persona_store.get_state(scope_id)
    tone_weights = response_engine.persona_store.apply_evolution(
        scope_id, "gift_received", state["tone_weights"]
    )
    response_engine.persona_store.save_state(
        scope_id, tone_weights, state["stance_overrides"]
    )
```

## Testing

The personality system includes comprehensive tests:

```bash
# Run all personality tests
pytest tests/test_personality_config.py tests/test_persona_state.py tests/test_prompt_composer.py -v

# Test with deterministic seed
pytest tests/test_persona_state.py::test_apply_drift_deterministic -v
```

## Troubleshooting

### Personality Not Active

Check:
1. `personality_bias.enabled` is set to `1`
2. Database file is writable: `./persona_state.db`
3. Logs for initialization errors: `"Personality system initialized"`

### Drift Too Fast/Slow

Adjust `volatility`:
- Too fast: Reduce to 0.001-0.01
- Too slow: Increase to 0.05-0.1

### Evolution Not Working

Check:
1. `evolution_rules.enabled` is `1`
2. Trigger names match your events exactly
3. Target tones exist in `tone_weights`
4. Clamps aren't preventing change

### Refusals Not Triggering

Check:
1. `refusals.enabled` is `1`
2. Trigger patterns match text (case-insensitive substring match)
3. Mode exists in `refusals.modes`

## Best Practices

1. **Start Conservative**: Begin with low volatility (0.01) and small evolution magnitudes (0.02)
2. **Use Clamps**: Prevent extreme personalities with reasonable clamps
3. **Test with Seeds**: Use deterministic seeds during development
4. **Monitor Evolution**: Check `/api/persona/state` periodically
5. **Safety First**: Always keep `safety_overrides.always_refuse: 1`
6. **Session vs User**: Use session scope for consistent experience, user scope for personalization

## Example Configurations

### Formal Assistant

```yaml
tone_weights:
  formal: 0.7
  casual: 0.2
  playful: 0.05
  sarcastic: 0.05
volatility: 0.005  # Very stable
```

### Playful Companion

```yaml
tone_weights:
  formal: 0.1
  casual: 0.4
  playful: 0.4
  sarcastic: 0.1
volatility: 0.03  # More dynamic
```

### Professional with Evolution

```yaml
tone_weights:
  formal: 0.6
  casual: 0.3
  playful: 0.08
  sarcastic: 0.02
volatility: 0.01
evolution_rules:
  enabled: 1
  triggers:
    positive_interaction:
      magnitude: 0.01
      target_tone: casual
    negative_interaction:
      magnitude: 0.02
      target_tone: formal
```
