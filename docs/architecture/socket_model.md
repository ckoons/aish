# aish Socket Model Architecture

## Overview

The aish socket model treats AI instances as file descriptors, enabling Unix-style composition and pipeline operations.

## Core Abstractions

### AI Socket
```python
class AISocket:
    socket_id: str      # "apollo-123"
    input: Stream       # What the AI reads
    output: Stream      # What the AI writes
    error: Stream       # Error/debug output
    registry_ref: str   # Reference in Rhetor
```

### Socket Lifecycle

```
create() → socket_id
   ↓
write(socket_id, message)
   ↓
read(socket_id) → response  
   ↓
delete(socket_id) OR reset(socket_id)
```

## Header Protocol

All messages are automatically wrapped with headers for routing:

### Input Headers (added by write)
- `[team-chat-to-apollo-123]` - Directed message
- `[broadcast]` - All AIs
- `[priority-high]` - Urgent processing

### Output Headers (added by read)  
- `[team-chat-from-apollo-123]` - Source identification
- `[thinking]` - Internal monologue
- `[error]` - Error messages

## Pipeline Wiring

When creating a pipeline `A | B | C`:

```
1. Create sockets: a_sock, b_sock, c_sock
2. Wire: a.output → b.input
3. Wire: b.output → c.input  
4. Execute: write(a_sock) → ... → read(c_sock)
```

## Implementation via Rhetor

Rhetor provides the actual AI management:

```python
# In Rhetor
@router.post("/api/ai/socket/create")
async def create_ai_socket(config: AIConfig) -> SocketID

@router.websocket("/ws/socket/{socket_id}")
async def socket_connection(websocket: WebSocket, socket_id: str)
```

## Special Sockets

### team-chat-all
- Broadcast socket
- Writes go to all registered AIs
- Reads collect from all AIs

### rhetor
- Rhetor's own listening socket
- Receives all unrouted messages
- Can delegate to other AIs

## Error Handling

- Socket not found: Empty read, logged error
- Write to closed: Message dropped, error logged  
- Malformed header: Treated as content
- Network failure: Automatic reconnect

## Performance Considerations

- Sockets are lazy - created on first use
- Buffered I/O for efficiency
- Async operations throughout
- Connection pooling to Rhetor

## Security Model

- Sockets are capabilities - having the ID grants access
- No authentication within aish (relies on Rhetor)
- Headers are trusted (don't parse untrusted headers)

## Future: Distributed Sockets

```bash
# Remote AI execution
aish> echo "analyze" | ssh server2 apollo

# Becomes
create_remote_socket("apollo", "server2")
```

The socket abstraction remains identical whether local or remote.