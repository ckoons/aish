# API Specifications - Tekton-aish Improvement Sprint

## Overview

This document provides detailed API specifications for all new endpoints and protocols introduced in the Tekton-aish Improvement Sprint.

## Table of Contents

1. [Streaming APIs](#streaming-apis)
2. [Session Management APIs](#session-management-apis)
3. [Bulk Operations API](#bulk-operations-api)
4. [Enhanced Discovery API](#enhanced-discovery-api)
5. [WebSocket Protocol](#websocket-protocol)
6. [Error Codes](#error-codes)

## Streaming APIs

### SSE Streaming Endpoint

Stream AI responses using Server-Sent Events.

**Endpoint**: `GET /api/v2/ai/{specialist_id}/stream`

**Request**:
```http
POST /api/v2/ai/apollo-ai/stream HTTP/1.1
Host: localhost:8003
Accept: text/event-stream
Content-Type: application/json

{
  "content": "Analyze this code for performance issues",
  "temperature": 0.7,
  "max_tokens": 2000
}
```

**Response**:
```http
HTTP/1.1 200 OK
Content-Type: text/event-stream
Cache-Control: no-cache

data: {"type": "start", "specialist_id": "apollo-ai", "request_id": "req_123"}

data: {"type": "content", "data": "Looking at", "specialist_id": "apollo-ai"}

data: {"type": "content", "data": " your code,", "specialist_id": "apollo-ai"}

data: {"type": "content", "data": " I found", "specialist_id": "apollo-ai"}

data: {"type": "done", "specialist_id": "apollo-ai", "tokens_used": 150}
```

**Event Types**:
- `start`: Stream initialization
- `content`: Content chunk
- `error`: Error occurred
- `done`: Stream complete

## Session Management APIs

### Create Session

Create a new conversational session with an AI specialist.

**Endpoint**: `POST /api/v2/sessions`

**Request**:
```json
{
  "specialist_id": "apollo-ai",
  "context_window": 10,
  "metadata": {
    "user_id": "user123",
    "project": "myproject"
  }
}
```

**Response**:
```json
{
  "id": "sess_abc123",
  "specialist_id": "apollo-ai",
  "context_window": 10,
  "created_at": "2024-01-01T12:00:00Z",
  "expires_at": "2024-01-01T13:00:00Z",
  "metadata": {
    "user_id": "user123",
    "project": "myproject"
  }
}
```

### Send Session Message

Send a message within an existing session.

**Endpoint**: `POST /api/v2/sessions/{session_id}/message`

**Request**:
```json
{
  "message": "Can you explain the previous issue in more detail?",
  "temperature": 0.7,
  "stream": false
}
```

**Response**:
```json
{
  "response": "Regarding the performance issue I mentioned...",
  "session_id": "sess_abc123",
  "message_count": 5,
  "tokens_used": 250,
  "context_used": 8
}
```

### Get Session Info

Retrieve session information and message history.

**Endpoint**: `GET /api/v2/sessions/{session_id}`

**Response**:
```json
{
  "id": "sess_abc123",
  "specialist_id": "apollo-ai",
  "created_at": "2024-01-01T12:00:00Z",
  "last_activity": "2024-01-01T12:30:00Z",
  "message_count": 10,
  "messages": [
    {
      "role": "user",
      "content": "Analyze this function",
      "timestamp": "2024-01-01T12:00:00Z"
    },
    {
      "role": "assistant",
      "content": "I'll analyze the function...",
      "timestamp": "2024-01-01T12:00:05Z"
    }
  ]
}
```

### Delete Session

End a session and clear its context.

**Endpoint**: `DELETE /api/v2/sessions/{session_id}`

**Response**:
```json
{
  "status": "deleted",
  "session_id": "sess_abc123"
}
```

## Bulk Operations API

### Execute Bulk Operations

Execute multiple AI operations in parallel or sequence.

**Endpoint**: `POST /api/v2/bulk`

**Request**:
```json
{
  "operations": [
    {
      "id": "op1",
      "ai": "apollo-ai",
      "message": "Analyze this code:\n```python\ndef process():\n    pass\n```",
      "temperature": 0.7
    },
    {
      "id": "op2",
      "ai": "athena-ai",
      "message": "Review the analysis from {op1}",
      "depends_on": ["op1"],
      "temperature": 0.8
    },
    {
      "id": "op3",
      "ai": "prometheus-ai",
      "message": "Create a plan based on {op1} and {op2}",
      "depends_on": ["op1", "op2"],
      "temperature": 0.6
    }
  ],
  "execution": "parallel",
  "timeout": 60
}
```

**Response**:
```json
{
  "request_id": "bulk_req_123",
  "status": "completed",
  "execution_time": 15.3,
  "results": {
    "op1": {
      "status": "success",
      "response": "The code analysis shows...",
      "ai": "apollo-ai",
      "execution_time": 5.1,
      "tokens_used": 350
    },
    "op2": {
      "status": "success",
      "response": "Based on the analysis...",
      "ai": "athena-ai",
      "execution_time": 8.2,
      "tokens_used": 420
    },
    "op3": {
      "status": "success",
      "response": "Here's a comprehensive plan...",
      "ai": "prometheus-ai",
      "execution_time": 12.5,
      "tokens_used": 680
    }
  },
  "total_tokens": 1450
}
```

**Execution Modes**:
- `parallel`: Execute independent operations concurrently
- `sequential`: Execute all operations in order

## Enhanced Discovery API

### List AIs with Capabilities

Discover available AIs with detailed capability information.

**Endpoint**: `GET /api/v2/discovery/ais`

**Query Parameters**:
- `capability`: Filter by capability (e.g., "code-analysis")
- `min_score`: Minimum capability score (0-1)
- `status`: Filter by status (active, inactive, all)

**Response**:
```json
{
  "ais": [
    {
      "id": "apollo-ai",
      "name": "Apollo",
      "status": "active",
      "model": "claude-3-opus",
      "connection": {
        "host": "localhost",
        "port": 45007,
        "protocol": "tcp"
      },
      "capabilities": {
        "primary": ["code-analysis", "debugging", "optimization"],
        "scores": {
          "code-analysis": 0.95,
          "debugging": 0.90,
          "planning": 0.70,
          "creative-writing": 0.30
        }
      },
      "performance": {
        "avg_response_time": 1.2,
        "success_rate": 0.98,
        "context_window": 100000,
        "max_tokens": 4000
      },
      "cost": {
        "per_1k_tokens": 0.002,
        "currency": "USD"
      },
      "features": {
        "streaming": true,
        "sessions": true,
        "websocket": true
      }
    }
  ],
  "total": 18,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Find Best AI for Capability

Find the best AI for a specific capability.

**Endpoint**: `GET /api/v2/discovery/best`

**Query Parameters**:
- `capability`: Required capability
- `threshold`: Minimum score (default: 0.7)

**Response**:
```json
{
  "capability": "code-analysis",
  "best_match": {
    "id": "apollo-ai",
    "score": 0.95,
    "is_primary": true
  },
  "alternatives": [
    {
      "id": "athena-ai",
      "score": 0.85,
      "is_primary": false
    }
  ]
}
```

## WebSocket Protocol

### Connection Establishment

**Endpoint**: `ws://localhost:8003/ws/ai/{specialist_id}`

**Connection Headers**:
```http
GET /ws/ai/apollo-ai HTTP/1.1
Host: localhost:8003
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Sec-WebSocket-Version: 13
Authorization: Bearer <token>
```

### Message Format

All WebSocket messages use JSON-RPC 2.0 format.

#### Client Messages

**Chat Request**:
```json
{
  "jsonrpc": "2.0",
  "method": "chat",
  "params": {
    "message": "Analyze this function",
    "temperature": 0.7,
    "session_id": "sess_abc123"
  },
  "id": 1
}
```

**Stream Request**:
```json
{
  "jsonrpc": "2.0",
  "method": "stream",
  "params": {
    "message": "Generate a detailed report",
    "temperature": 0.8
  },
  "id": 2
}
```

#### Server Messages

**Chat Response**:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "content": "Here's my analysis...",
    "tokens_used": 150,
    "session_id": "sess_abc123"
  },
  "id": 1
}
```

**Stream Chunk**:
```json
{
  "jsonrpc": "2.0",
  "method": "stream.chunk",
  "params": {
    "content": "The analysis shows",
    "chunk_index": 0
  }
}
```

**Stream Complete**:
```json
{
  "jsonrpc": "2.0",
  "method": "stream.complete",
  "params": {
    "total_chunks": 25,
    "tokens_used": 450
  }
}
```

**Error**:
```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32603,
    "message": "Internal error",
    "data": {
      "specialist_id": "apollo-ai",
      "details": "Model temporarily unavailable"
    }
  },
  "id": 1
}
```

### WebSocket Commands

- `ping`: Keep-alive ping (expects `pong` response)
- `subscribe`: Subscribe to events
- `unsubscribe`: Unsubscribe from events

## Error Codes

### HTTP Status Codes

- `200`: Success
- `201`: Created (sessions)
- `400`: Bad Request
- `401`: Unauthorized
- `404`: Not Found
- `429`: Rate Limited
- `500`: Internal Server Error
- `503`: Service Unavailable

### WebSocket Error Codes (JSON-RPC)

- `-32700`: Parse error
- `-32600`: Invalid Request
- `-32601`: Method not found
- `-32602`: Invalid params
- `-32603`: Internal error
- `-32000`: Session expired
- `-32001`: AI unavailable
- `-32002`: Context limit exceeded

### Error Response Format

```json
{
  "error": {
    "code": "SESSION_EXPIRED",
    "message": "The session has expired",
    "details": {
      "session_id": "sess_abc123",
      "expired_at": "2024-01-01T13:00:00Z"
    }
  }
}
```

## Rate Limiting

All endpoints implement rate limiting:

```http
HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1704124800
Retry-After: 3600

{
  "error": {
    "code": "RATE_LIMITED",
    "message": "Rate limit exceeded",
    "retry_after": 3600
  }
}
```

## Versioning

API versioning is handled via URL path:

- Current stable: `/api/v1/`
- New features: `/api/v2/`
- Experimental: `/api/experimental/`

Clients should check capabilities endpoint to determine feature availability:

```json
GET /api/capabilities

{
  "version": "2.0",
  "features": {
    "streaming": true,
    "sessions": true,
    "bulk_operations": true,
    "websocket": true,
    "enhanced_discovery": true
  },
  "api_versions": ["v1", "v2"],
  "deprecations": {
    "v1/team-chat": "Use v2/bulk instead"
  }
}
```