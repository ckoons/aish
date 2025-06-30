# Socket Communication Test Documentation

## Overview

This document describes the socket communication tests added in Phase 1 of the aish-Tekton integration.

## Test Files

### test_socket_buffering.py

Tests the core socket improvements including line-buffered reading and partial message handling.

**What it tests:**
- Direct socket connections to AI specialists
- Line-buffered message reading
- Partial message reassembly
- SocketRegistry communication
- Dynamic port discovery

**Key test cases:**
1. `test_direct_socket_connection()` - Raw socket communication with ping/chat
2. `test_socket_registry()` - High-level registry interface
3. `test_partial_messages()` - Message fragmentation handling

### test_phase1_integration.py

End-to-end integration tests for Phase 1 improvements.

**What it tests:**
- aish shell with AI specialists
- Long message handling (>4KB)
- Timeout detection
- MCP tools integration
- Multi-AI pipelines

**Key test cases:**
1. `test_aish_ai_specialists()` - Basic AI communication
2. `test_aish_with_long_messages()` - Buffer overflow scenarios
3. `test_timeout_detection()` - Intelligent timeout handling
4. `test_mcp_integration()` - Tekton MCP tools
5. `run_full_integration_test()` - Complex multi-AI scenarios

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

### Quick Test
```bash
# Check AI availability first
python tests/check_ai_ports.py

# Run socket tests
python tests/test_socket_buffering.py

# Run full integration
python tests/test_phase1_integration.py
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
AISH_DEBUG=1 python tests/test_socket_buffering.py
```

## Test Scenarios

### 1. Basic Communication
- Send message to AI
- Receive response
- Verify JSON format

### 2. Error Conditions
- AI not running
- Network timeout
- Invalid JSON
- Connection refused

### 3. Performance Tests
- Large messages (>4KB)
- Multiple concurrent connections
- Rapid message sequences

### 4. Protocol Tests
- Ping/pong heartbeat
- Message types (chat, info)
- Context passing

## Troubleshooting Tests

### Test Fails: Connection Refused
```
✗ athena port 45012 - NOT LISTENING
```
**Solution**: Start Tekton platform or specific AI

### Test Fails: Timeout
```
[DEBUG] Socket timeout after 30.0s
```
**Solution**: Check if AI is processing or hung

### Test Fails: JSON Decode
```
[DEBUG] JSON decode error: Expecting value: line 1 column 1
```
**Solution**: Check AI response format

## Adding New Tests

### Template for new socket test:
```python
def test_new_feature():
    """Test description."""
    # Setup
    registry = SocketRegistry(debug=True)
    
    # Execute
    socket_id = registry.create('ai-name')
    registry.write(socket_id, "test message")
    
    # Verify
    response = registry.read(socket_id)
    assert response is not None
    assert "expected" in response[0]
    
    return True
```

### Best Practices:
1. Use dynamic discovery (no hardcoded ports)
2. Handle timeouts gracefully
3. Clean up resources (close sockets)
4. Provide helpful error messages
5. Use debug mode for detailed output

## CI/CD Integration

Tests can be run in CI with:
```bash
python tests/run_tests.py --socket-tests
```

Expected exit codes:
- 0: All tests passed
- 1: One or more tests failed
- 2: Setup/environment error