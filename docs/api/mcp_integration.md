# MCP (Model Context Protocol) Integration

## Overview

This document describes how aish integrates with Tekton's MCP tools for unified AI communication.

## MCP Tools Location

The MCP implementation is in the Tekton repository:
- `Tekton/Rhetor/rhetor/core/mcp/tools_integration_unified.py`

## Key Components

### MCPToolsIntegrationUnified

Provides unified interface for AI communication with dual routing:
- **Socket-based**: Direct TCP for AI specialists (ports 45000+)
- **API-based**: HTTP/REST for Rhetor services

### SendMessageToSpecialist

The primary method for AI communication:

```python
async def send_message_to_specialist(
    specialist_id: str,      # e.g., 'athena-ai'
    message: str,           # Message content
    context: Dict = None    # Optional context
) -> Dict[str, Any]:
    # Returns:
    # {
    #   "success": bool,
    #   "response": str,
    #   "specialist_id": str,
    #   "type": "socket" | "api",
    #   "error": str  # if success=False
    # }
```

## Integration Points

### From aish Side

aish can use MCP tools via the Rhetor API:

```python
import httpx

# Send message via MCP
async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8003/api/mcp/send",
        json={
            "specialist_id": "athena-ai",
            "message": "What is wisdom?",
            "context": {"session_id": "123"}
        }
    )
    result = response.json()
```

### Direct Socket Alternative

aish can also communicate directly via sockets:

```python
from src.registry.socket_registry import SocketRegistry

registry = SocketRegistry()
socket_id = registry.create('athena')
registry.write(socket_id, "What is wisdom?")
response = registry.read(socket_id)
```

## Routing Logic

MCP automatically routes based on AI configuration:

1. **Check AI Discovery**
   ```python
   ai_info = await discovery.get_ai_info(specialist_id)
   ```

2. **Determine Route**
   ```python
   if 'connection' in ai_info and ai_info['connection'].get('port'):
       # Use socket for specialists with ports
       return await self._send_via_socket(ai_info, message)
   else:
       # Use API for others
       return await self._send_via_api(specialist_id, message)
   ```

## Error Handling

MCP provides consistent error responses:

```python
# Connection timeout
{
    "success": False,
    "error": "Connection timeout - specialist may be unavailable",
    "response": None
}

# AI not found
{
    "success": False,
    "error": "Specialist athena-ai not found",
    "response": None
}

# Processing error
{
    "success": False,
    "error": "Socket error: [details]",
    "response": None
}
```

## Testing MCP Integration

### Test Script Location
`Tekton/tests/test_mcp_integration.py`

### Running Tests
```bash
cd /Users/cskoons/projects/github/Tekton
python tests/test_mcp_integration.py
```

### Test Coverage
- Socket-based routing
- API-based routing
- Error handling
- Context passing
- Timeout scenarios

## Future Enhancements

### Planned
1. **GetSpecialistConversationHistory** - Retrieve chat history
2. **ConfigureOrchestration** - Dynamic routing rules
3. **Streaming Support** - SSE/WebSocket integration

### Under Consideration
- Connection pooling
- Automatic retry with backoff
- Load balancing across instances
- Priority queuing

## Best Practices

1. **Use MCP for Tekton Integration**
   - Provides unified interface
   - Handles routing automatically
   - Consistent error handling

2. **Use Direct Sockets for aish-only**
   - Lower latency
   - More control
   - Direct heartbeat management

3. **Always Include Context**
   ```python
   context = {
       "session_id": "uuid",
       "user": "username",
       "timestamp": time.time()
   }
   ```

4. **Handle All Response Types**
   ```python
   if response['success']:
       content = response['response']
   else:
       error = response['error']
   ```