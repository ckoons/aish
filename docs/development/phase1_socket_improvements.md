# Phase 1 Socket Improvements Documentation

## Overview

This document describes the socket communication improvements implemented in Phase 1 of the aish-Tekton integration sprint (June 2025).

## Key Improvements

### 1. Line-Buffered Socket Implementation

The core issue was that the original socket implementation used a single `recv(4096)` call, which could fail when:
- Messages exceeded 4096 bytes
- Messages arrived in multiple packets
- Network delays caused partial reads

**Solution**: Implemented `LineBufferedSocket` class in `src/utils/socket_buffer.py` that:
- Accumulates data until a complete newline-delimited message is received
- Handles partial reads gracefully
- Supports heartbeat/ping messages
- Provides debug logging for troubleshooting

### 2. Intelligent Timeout Detection

Implemented `SocketTimeoutDetector` class that distinguishes between:
- **Connection timeouts** (2 seconds) - Network unreachable
- **Response timeouts** (30 seconds) - AI processing time
- **Dead connections** (>50 seconds without heartbeat) - Connection lost

### 3. Dynamic Port Discovery

Replaced hardcoded ports with dynamic discovery using `ai-discover`:
- No more hardcoded port numbers
- Adapts to whatever AIs are running
- Supports both short names (`athena`) and full IDs (`athena-ai`)

## Socket Protocol

All AI specialists use newline-delimited JSON protocol:

### Request Format
```json
{
  "type": "chat|ping|info",
  "content": "message text",
  "context": {}  // optional
}
```

### Response Format
```json
{
  "type": "chat_response|pong|info_response",
  "ai_id": "specialist-ai",
  "content": "response text",
  "timestamp": 1234567890.123
}
```

### Message Flow
1. Client connects to AI port (45000+)
2. Client sends JSON message + newline
3. AI processes and responds with JSON + newline
4. For long operations, heartbeats keep connection alive

## API Changes

### SocketRegistry Updates

The `_write_via_socket` method now uses `LineBufferedSocket`:
```python
# Old implementation
response_data = client_socket.recv(4096).decode().strip()

# New implementation
buffered_socket = LineBufferedSocket(sock, timeout=30.0, debug=self.debug)
response = buffered_socket.read_message()
```

### Heartbeat Support

Added automatic heartbeat handling:
```python
# Start heartbeat thread (25-second intervals)
buffered_socket.start_heartbeat(interval=25.0, source_id="aish-client")

# Heartbeats are automatically filtered in read_message()
if message.get('type') in ['ping', 'heartbeat']:
    # Record heartbeat and continue reading
```

## Testing

### Test Files
- `test_socket_buffering.py` - Core socket improvements
- `test_phase1_integration.py` - Full integration testing
- `check_ai_ports.py` - Diagnostic tool

### Running Tests
```bash
# Check which AIs are listening
python tests/check_ai_ports.py

# Test socket improvements
python tests/test_socket_buffering.py

# Full integration test
python tests/test_phase1_integration.py
```

## Troubleshooting

### Debug Mode
Enable debug output for detailed logging:
```python
registry = SocketRegistry(debug=True)
```

### Common Issues

1. **Connection Refused**
   - Check AI is running: `tekton-status`
   - Verify port with: `ai-discover list`

2. **Timeout Errors**
   - AI may be processing - wait for response
   - Check heartbeat status in debug logs

3. **JSON Decode Errors**
   - Verify message format is newline-delimited
   - Check for partial reads in debug output

## Future Improvements

- SSE streaming for progressive responses
- WebSocket support for bidirectional streaming
- Connection pooling for performance
- Automatic reconnection with backoff