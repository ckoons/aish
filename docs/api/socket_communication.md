# Socket Communication API Reference

## Overview

This document describes the socket communication API used by aish to communicate with AI specialists in the Tekton platform.

## Connection Details

- **Ports**: AI specialists listen on ports 45000-45999
- **Protocol**: TCP sockets with newline-delimited JSON
- **Timeout**: 30 seconds for responses, 2 seconds for connection
- **Discovery**: Use `ai-discover` tool or SocketRegistry

## Message Types

### Client → AI Messages

#### Chat Message
```json
{
  "type": "chat",
  "content": "Your message here",
  "context": {  // optional
    "session_id": "uuid",
    "user": "username",
    "previous_topic": "topic"
  }
}
```

#### Ping Message
```json
{
  "type": "ping",
  "timestamp": 1234567890,
  "source": "aish-client-id"
}
```

#### Info Request
```json
{
  "type": "info",
  "query": "capabilities|status|version"
}
```

### AI → Client Responses

#### Chat Response
```json
{
  "type": "chat_response",
  "ai_id": "athena-ai",
  "content": "AI response text",
  "timestamp": 1234567890.123,
  "processing_time": 0.456  // optional
}
```

#### Pong Response
```json
{
  "type": "pong",
  "ai_id": "athena-ai",
  "timestamp": 1234567890.123,
  "status": "ok"
}
```

#### Info Response
```json
{
  "type": "info_response",
  "ai_id": "athena-ai",
  "data": {
    "version": "0.1.0",
    "capabilities": ["knowledge-synthesis", "reasoning"],
    "status": "healthy"
  }
}
```

## Socket Classes

### LineBufferedSocket

Handles line-buffered reading and writing of JSON messages.

```python
from aish.src.utils.socket_buffer import LineBufferedSocket

# Create buffered socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('localhost', 45012))
buffered = LineBufferedSocket(sock, timeout=30.0, debug=True)

# Send message
message = {"type": "chat", "content": "Hello"}
buffered.write_message(message)

# Read response
response = buffered.read_message()
print(response['content'])

# Start heartbeat (optional)
buffered.start_heartbeat(interval=25.0)

# Close when done
buffered.close()
```

### SocketTimeoutDetector

Manages intelligent timeout detection.

```python
from aish.src.utils.socket_buffer import SocketTimeoutDetector

detector = SocketTimeoutDetector(
    connection_timeout=2.0,   # Network timeout
    response_timeout=30.0,    # AI processing timeout
    heartbeat_interval=25.0   # Expected heartbeat frequency
)

# Create connection with timeout
success, sock, error = detector.create_connection('localhost', 45012)
if not success:
    print(f"Connection failed: {error}")

# Check heartbeat status
alive, status = detector.check_heartbeat()
print(f"Connection {alive}: {status}")
```

### SocketRegistry

High-level interface for AI communication.

```python
from aish.src.registry.socket_registry import SocketRegistry

registry = SocketRegistry(debug=True)

# Discover available AIs
ais = registry.discover_ais()

# Create socket to AI
socket_id = registry.create('athena')

# Send message
registry.write(socket_id, "What is wisdom?")

# Read response
response = registry.read(socket_id)
print(response[0])

# List active sockets
active = registry.get_active_sockets()
```

## Error Handling

### Connection Errors
- `ConnectionRefusedError`: AI not running on specified port
- `timeout`: Connection attempt exceeded 2 seconds
- `socket.gaierror`: Invalid hostname

### Communication Errors
- `json.JSONDecodeError`: Invalid JSON in message
- `socket.timeout`: No response within 30 seconds
- `BrokenPipeError`: Connection lost during communication

### Example Error Handling
```python
try:
    response = buffered.read_message()
except socket.timeout:
    print("AI is taking too long to respond")
except json.JSONDecodeError as e:
    print(f"Invalid response format: {e}")
except Exception as e:
    print(f"Communication error: {e}")
```

## Best Practices

1. **Always use LineBufferedSocket** for reliable communication
2. **Enable debug mode** during development
3. **Handle timeouts gracefully** - AIs may take time to process
4. **Use heartbeats** for long-running connections
5. **Close sockets properly** to avoid resource leaks
6. **Use discovery** instead of hardcoding ports

## Debugging

Enable debug output:
```python
# Socket level debugging
buffered = LineBufferedSocket(sock, debug=True)

# Registry level debugging  
registry = SocketRegistry(debug=True)

# Run diagnostic
python tests/check_ai_ports.py
```

Debug output includes:
- Bytes sent/received
- Buffer state
- Message parsing
- Heartbeat activity
- Connection status