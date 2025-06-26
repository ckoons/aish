# Socket Registry Implementation Guide

## Quick Start

The file you'll be working on: `/aish/src/registry/socket_registry.py`

## Required Rhetor Endpoints

You'll need to implement these Rhetor endpoints first:

### 1. Create AI Socket
```python
POST /api/ai/socket/create
{
    "ai_name": "apollo",
    "model": "claude-3-sonnet",  # optional
    "prompt": "You are Apollo...",  # optional
    "context": {}  # optional
}

Response:
{
    "socket_id": "apollo-123",
    "websocket_url": "ws://localhost:8300/ws/socket/apollo-123"
}
```

### 2. WebSocket Connection
```python
ws://localhost:8300/ws/socket/{socket_id}

# Messages are JSON:
{
    "type": "write",
    "content": "Hello Apollo"
}

{
    "type": "read",
    "content": "Hello! I'm Apollo...",
    "headers": ["team-chat-from-apollo-123"]
}
```

## Implementation Steps

### Step 1: Update socket_registry.py create()
```python
async def create(self, ai_name: str, model: str = None, 
                prompt: str = None, context: Dict = None) -> str:
    # Call Rhetor API
    response = await self.http_client.post(
        f"{self.rhetor_endpoint}/api/ai/socket/create",
        json={
            "ai_name": ai_name,
            "model": model,
            "prompt": prompt,
            "context": context
        }
    )
    
    data = response.json()
    socket_id = data["socket_id"]
    
    # Store WebSocket URL for later
    self.sockets[socket_id] = {
        "ws_url": data["websocket_url"],
        "connection": None  # Lazy connect
    }
    
    return socket_id
```

### Step 2: Implement read/write via WebSocket
```python
async def write(self, socket_id: str, message: str):
    # Get or create WebSocket connection
    ws = await self._get_connection(socket_id)
    
    # Send message
    await ws.send_json({
        "type": "write",
        "content": message
    })
    
async def read(self, socket_id: str) -> List[str]:
    ws = await self._get_connection(socket_id)
    
    # Read available messages
    messages = []
    while ws.messages_available():
        msg = await ws.receive_json()
        if msg["type"] == "read":
            messages.append(msg["content"])
    
    return messages
```

### Step 3: Add team-chat support
```python
def __init__(self, rhetor_endpoint: str):
    super().__init__(rhetor_endpoint)
    # Pre-create special sockets
    self.create("team-chat-all", prompt="Broadcast to all AIs")
    self.create("rhetor", prompt="Rhetor's listening socket")
```

## Testing

### Test 1: Basic Echo
```python
# In aish shell
aish> echo "Hello" | apollo
Hello! I'm Apollo, how can I help you?
```

### Test 2: Pipeline
```python
aish> echo "Design a cache" | athena | apollo
[From Athena] Here's a cache design...
[From Apollo] Predicting performance...
```

### Test 3: Team Chat
```python
aish> team-chat "What's the best programming language?"
[From Apollo] For predictions, Python...
[From Athena] For knowledge systems, Prolog...
[From Hermes] For communication, Go...
```

## Common Issues

1. **Connection Management**: Use connection pooling
2. **Async Everywhere**: All I/O operations must be async
3. **Error Recovery**: Reconnect on WebSocket failure
4. **Headers**: Let Rhetor handle header addition/removal

## Next Steps After Basic Implementation

1. Add process management (list active sockets)
2. Implement socket groups for targeted broadcast
3. Add metrics/monitoring
4. Support for binary streams (audio/video)