# aish Tests

This directory contains tests for aish - The AI Shell.

## Test Structure

- `test_functional.py` - Unit tests that don't require Rhetor
- `test_integration.py` - Integration tests that require Rhetor to be running
- `test_pipeline.py` - Manual test script for basic functionality
- `test_basic.sh` - Quick bash script for smoke testing
- `run_tests.py` - Main test runner

## Running Tests

### Quick Test
```bash
# From the tests directory
./test_basic.sh
```

### All Tests
```bash
# Run all tests (functional + integration)
./run_tests.py

# Or with Python
python run_tests.py
```

### Specific Test Suites
```bash
# Only functional tests (no Rhetor needed)
./run_tests.py --functional

# Only integration tests (requires Rhetor)
./run_tests.py --integration

# Quick smoke test
./run_tests.py --quick
```

## Test Requirements

### Functional Tests
- Python 3.6+
- No external services required

### Integration Tests
- Rhetor must be running on port 8003
- At least one AI specialist should be active

## What's Tested

### Functional Tests
- Pipeline parsing (echo | ai | ai)
- Socket registry operations
- Command parsing
- Team chat syntax

### Integration Tests
- Rhetor connection
- AI specialist listing
- Team chat API
- Direct specialist communication
- Full pipeline execution
- Socket registry with real Rhetor

## Adding New Tests

1. **Functional Tests**: Add to `test_functional.py`
2. **Integration Tests**: Add to `test_integration.py`
3. **Update test runner** if adding new test files

## Continuous Integration

These tests can be integrated into CI/CD:
```yaml
# Example GitHub Actions
- name: Run aish tests
  run: |
    cd tests
    python run_tests.py --functional
    # Integration tests would need Rhetor service
```