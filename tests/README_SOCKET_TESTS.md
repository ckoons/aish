# Socket Communication Test Documentation

## Overview

This document describes the socket communication tests for aish, which now use Tekton's Unified AI Interface.

## Test Files

### test_socket_communication.py

Tests the core socket communication functionality using the unified interface.

**What it tests:**
- Direct socket connections to AI specialists
- SocketRegistry communication
- Dynamic AI discovery
- Message sending and receiving
- Team chat functionality

**Key test cases:**
1. `test_socket_discovery()` - Discover available AI specialists
2. `test_direct_socket_connection()` - Direct socket communication
3. `test_socket_registry_communication()` - Registry-based messaging

### test_socket_registry.py (formerly test_pipeline.py)

Tests the SocketRegistry implementation in detail.

**What it tests:**
- Registry initialization
- Socket creation and management
- Message queuing
- AI discovery caching
- Error handling

### test_http_communication.py

Tests HTTP-based communication with Rhetor specialists.

**What it tests:**
- HTTP API endpoints
- Specialist messaging via REST
- Team chat via HTTP
- Error handling for HTTP requests

### test_all_protocols.py

Orchestrates running both socket and HTTP protocol tests.

**What it does:**
- Runs socket communication tests
- Runs HTTP communication tests
- Provides unified test results

### test_integration.py

End-to-end integration tests with the Rhetor platform.

**What it tests:**
- Complete aish integration with Rhetor
- Multi-AI pipelines
- Team chat functionality
- Real AI responses

### test_functional.py

Unit tests for core aish components.

**What it tests:**
- PipelineParser functionality
- SocketRegistry methods (mocked)
- AIShell command execution (mocked)
- No external dependencies required

### test_aish_features.py

Black-box testing of aish features using subprocess.

**What it tests:**
- Single AI communication
- Pipeline execution
- Team chat
- Conversation history
- Command-line interface

### check_ai_ports.py

Diagnostic tool for checking AI availability.

**What it does:**
- Uses ai-discover to find all AIs
- Checks which ports are listening
- Tests ping response for each AI
- Reports connection status

**Usage:**
```bash
python tests/check_ai_ports.py
```

## Running Tests

### Prerequisites
1. Tekton platform running (`tekton-launch`)
2. AI specialists active (`tekton-status`)
3. aish environment set up
4. Unified registry populated (`python3 $TEKTON_ROOT/shared/ai/migrate_registry.py`)

### Quick Test
```bash
# Check AI availability first
python tests/check_ai_ports.py

# Run all tests quickly
python tests/test_quick_check.py

# Run specific test suites
python tests/test_socket_communication.py
python tests/test_functional.py
python tests/test_integration.py
```

### Test Output

**Successful output includes:**
- "✓" checkmarks for passed tests
- Response previews from AIs
- Timing information
- Summary of passed/failed tests

**Debug mode:**
```bash
# Set environment variable for verbose output
AISH_DEBUG=1 python tests/test_socket_communication.py
```

## Unified AI Interface

All tests now use Tekton's Unified AI Interface:

```python
# The SocketRegistry automatically uses the unified interface
from registry.socket_registry import SocketRegistry

registry = SocketRegistry(debug=True)
# Discovers AIs via unified registry
ais = registry.discover_ais()
```

Benefits:
- Automatic health monitoring
- Performance tracking
- Consistent discovery
- Better error handling

## Test Scenarios

### 1. Basic Communication
- Send message to AI
- Receive response
- Verify response format

### 2. Error Conditions
- AI not running
- Network timeout
- Connection refused
- Invalid responses

### 3. Performance Tests
- Multiple AI pipelines
- Concurrent connections
- Team chat broadcasts

### 4. Protocol Tests
- Socket protocol (newline-delimited JSON)
- HTTP REST API
- Message routing

## Troubleshooting Tests

### Test Fails: No AIs Found
```
No AI specialists discovered
```
**Solution**: 
1. Ensure Tekton is running
2. Run migration: `python3 $TEKTON_ROOT/shared/ai/migrate_registry.py`
3. Check with: `ai-discover list`

### Test Fails: Connection Refused
```
Connection refused to localhost:45012
```
**Solution**: Start the specific AI or all AIs with `tekton-launch`

### Test Fails: Import Error
```
ImportError: No module named 'shared.ai.unified_registry'
```
**Solution**: Ensure TEKTON_ROOT is in Python path or run from correct directory

## Adding New Tests

### Template for new socket test:
```python
def test_new_feature():
    """Test description."""
    # Setup
    registry = SocketRegistry(debug=True)
    
    # Execute
    socket_id = registry.create('apollo')
    success = registry.write(socket_id, "test message")
    
    # Verify
    assert success
    responses = registry.read(socket_id)
    assert len(responses) > 0
    assert "expected" in responses[0]
    
    # Cleanup
    registry.delete(socket_id)
    return True
```

### Best Practices:
1. Use unified registry for discovery
2. Handle timeouts gracefully
3. Clean up resources
4. Provide helpful error messages
5. Use debug mode for troubleshooting

## CI/CD Integration

Tests can be run in CI with:
```bash
# Run all tests
python tests/run_tests.py

# Run specific test categories
python tests/test_functional.py  # No external deps
python tests/test_integration.py # Requires Rhetor
```

Expected exit codes:
- 0: All tests passed
- 1: One or more tests failed
- 2: Setup/environment error

## Test Status

All tests have been updated to work with the Unified AI Interface. No references to old `socket_buffer.py` or `LineBufferedSocket` remain.