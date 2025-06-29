# Architectural Decisions - Tekton-aish Improvement Sprint

## Overview

This document captures key architectural decisions for implementing streaming, sessions, bulk operations, enhanced discovery, and WebSocket support across Tekton and aish.

## Decision 1: Streaming Architecture

### Options Considered
1. **Server-Sent Events (SSE)** - Unidirectional, HTTP-based streaming
2. **WebSocket Streaming** - Bidirectional, persistent connection
3. **HTTP/2 Server Push** - Modern but limited client support
4. **Long Polling** - Compatible but inefficient

### Decision: Dual Approach (SSE + WebSocket)
- **SSE for simple streaming** - When only server-to-client flow needed
- **WebSocket for interactive sessions** - When bidirectional communication required

### Rationale
- SSE is simpler and works over standard HTTP
- WebSocket enables full duplex for interactive use cases
- Both can coexist without conflict
- Provides flexibility for different client capabilities

### Implementation
```python
# SSE Endpoint
GET /api/ai/specialists/{id}/stream
Accept: text/event-stream

# WebSocket Endpoint  
ws://localhost:8003/ws/ai/{specialist_id}
```

## Decision 2: Session Storage Architecture

### Options Considered
1. **In-Memory (Redis)** - Fast but requires external service
2. **SQLite** - Embedded but potential concurrency issues
3. **File System** - Simple but doesn't scale
4. **PostgreSQL** - Robust but heavyweight

### Decision: Redis with SQLite Fallback
- **Primary**: Redis for active sessions
- **Fallback**: SQLite for environments without Redis
- **Archive**: Optional PostgreSQL for long-term storage

### Rationale
- Redis provides millisecond latency for active sessions
- SQLite fallback ensures zero-dependency operation
- Modular design allows easy addition of backends

### Implementation
```python
class SessionStore:
    def __init__(self):
        try:
            self.backend = RedisSessionBackend()
        except ConnectionError:
            self.backend = SQLiteSessionBackend()
```

## Decision 3: Bulk Operations Design

### Options Considered
1. **Batch Array** - Single request with multiple operations
2. **GraphQL-style** - Complex query language
3. **Parallel Endpoints** - Multiple concurrent HTTP requests
4. **Message Queue** - Async job processing

### Decision: Batch Array with Dependency Graph
```json
POST /api/ai/bulk
{
  "operations": [
    {"id": "op1", "ai": "apollo", "message": "analyze this"},
    {"id": "op2", "ai": "athena", "message": "review op1", "depends_on": ["op1"]}
  ],
  "execution": "parallel"  // or "sequential"
}
```

### Rationale
- Simple JSON structure easy to generate and parse
- Dependency graph enables complex workflows
- Parallel/sequential modes provide flexibility
- Compatible with existing single-operation APIs

## Decision 4: Capability Metadata Schema

### Options Considered
1. **Simple Tags** - List of capability strings
2. **Numeric Scores** - 0-1 scale for each capability
3. **Hierarchical Taxonomy** - Nested capability tree
4. **Vector Embeddings** - ML-based similarity

### Decision: Hybrid Scoring System
```json
{
  "capabilities": {
    "primary": ["code-analysis", "debugging"],
    "scores": {
      "code-analysis": 0.95,
      "planning": 0.7,
      "creative-writing": 0.3
    },
    "context_window": 100000,
    "avg_response_time": 1.2,
    "success_rate": 0.98
  }
}
```

### Rationale
- Combines human-readable tags with numeric scores
- Enables both exact matching and fuzzy selection
- Performance metrics inform routing decisions
- Extensible for future ML-based routing

## Decision 5: WebSocket Protocol

### Options Considered
1. **Raw WebSocket** - Maximum flexibility
2. **Socket.io** - Built-in reconnection and rooms
3. **GraphQL Subscriptions** - Type-safe but complex
4. **gRPC Streaming** - Efficient but requires HTTP/2

### Decision: JSON-RPC over WebSocket
```json
// Client -> Server
{
  "jsonrpc": "2.0",
  "method": "chat",
  "params": {"message": "Hello"},
  "id": 1
}

// Server -> Client  
{
  "jsonrpc": "2.0",
  "result": {"content": "Hi there!", "streaming": true},
  "id": 1
}
```

### Rationale
- JSON-RPC provides structure without complexity
- Supports request/response and notifications
- Easy to implement in any language
- Well-defined error handling

## Decision 6: Backward Compatibility

### Strategy
1. **Version all endpoints** - `/api/v1/` vs `/api/v2/`
2. **Feature detection** - Clients check capabilities
3. **Graceful degradation** - Stream endpoints fall back to batch
4. **Migration period** - 6 months dual support

### Implementation
```python
# Client detects streaming support
capabilities = requests.get("/api/capabilities").json()
if "streaming" in capabilities:
    response = requests.get("/api/v2/ai/stream", stream=True)
else:
    response = requests.post("/api/v1/ai/message")
```

## Decision 7: Error Handling

### Streaming Errors
- Use SSE error events for recoverable errors
- Close stream for fatal errors
- Include error context in event data

### Session Errors
- Automatic session recovery on connection loss
- Checkpoint sessions periodically
- Clear error messages for session limits

### Bulk Operation Errors
- Partial success allowed
- Each operation reports individual status
- Dependency failures cascade appropriately

## Decision 8: Security Considerations

### Authentication
- Reuse existing Tekton auth tokens
- WebSocket auth via initial handshake
- Session tokens expire after inactivity

### Rate Limiting
- Per-client limits on streams
- Bulk operation size limits
- WebSocket message rate limits

### Data Privacy
- Sessions encrypted at rest
- No logging of message content
- Automatic session expiry

## Performance Targets

1. **Streaming Latency**
   - First byte: < 100ms
   - Sustained rate: > 50 tokens/second

2. **Session Operations**
   - Create: < 10ms
   - Retrieve: < 5ms
   - Update: < 10ms

3. **Bulk Execution**
   - Overhead: < 5% vs individual requests
   - Parallelism: Up to 20 concurrent operations

4. **WebSocket**
   - Connection time: < 50ms
   - Message latency: < 10ms
   - Concurrent connections: 10,000+

## Future Considerations

1. **Multi-Region Support**
   - Session replication across regions
   - Geo-distributed AI routing

2. **Advanced Routing**
   - ML-based capability matching
   - Dynamic load balancing
   - Cost-aware routing

3. **Extended Protocols**
   - Binary streaming for audio/video
   - Compression for large contexts
   - Multiplexing for efficiency