# Test Configuration

This directory contains tests for the PalFriend 7-phase architecture.

## Test Structure

- `test_settings.py` - Phase 1: Settings Management
- `test_memory.py` - Phase 2: Memory System
- `test_events.py` - Phase 4: Event Processing
- `test_response.py` - Phase 5: Response Generation
- `test_outbox.py` - Phase 6: Message Batching
- `test_utils.py` - Phase 7: Utility Functions

## Running Tests

### Run all tests
```bash
pytest
```

### Run specific test file
```bash
pytest tests/test_settings.py
```

### Run with coverage
```bash
pytest --cov=. --cov-report=html
```

### Run with verbose output
```bash
pytest -v
```

## Test Requirements

Required packages for testing:
- pytest
- pytest-asyncio (for async tests)
- pytest-cov (for coverage reports)

Install with:
```bash
pip install pytest pytest-asyncio pytest-cov
```

## Writing New Tests

1. Create test file with `test_` prefix
2. Name test functions with `test_` prefix
3. Use descriptive test names
4. Include docstrings explaining what is tested
5. Use assertions to verify expected behavior

Example:
```python
def test_feature_name():
    """Test that feature works correctly."""
    result = some_function()
    assert result == expected_value
```

## CI/CD Integration

Tests are automatically run in GitHub Actions on:
- Push to main, develop, or copilot/** branches
- Pull requests to main or develop

See `.github/workflows/ci.yml` for CI configuration.
