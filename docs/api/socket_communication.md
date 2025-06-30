# Socket Communication API Reference [DEPRECATED]

**⚠️ DEPRECATED: This document describes the old socket communication system. Please see [Unified AI Interface](./unified_ai_interface.md) for the current implementation.**

This document is kept for historical reference only.

## Overview

This document describes the socket communication API that was used by aish to communicate with AI specialists in the Tekton platform.

## Deprecation Notice

As of the latest update, aish has migrated to Tekton's Unified AI Interface. The old implementation using:
- `LineBufferedSocket` class
- `socket_buffer.py` module  
- Direct socket connections
- Manual timeout detection

Has been replaced with:
- `shared.ai.socket_client.AISocketClient` - Unified socket client
- `shared.ai.unified_registry.UnifiedAIRegistry` - Centralized registry
- Automatic health monitoring
- Built-in retry logic

## Migration

If you have code using the old socket communication:

```python
# Old way (deprecated)
from utils.socket_buffer import LineBufferedSocket
detector = SocketTimeoutDetector()
success, sock, error = detector.create_connection(host, port)
buffered_socket = LineBufferedSocket(sock)

# New way
from shared.ai.socket_client import create_sync_client
client = create_sync_client()
response = client.send_message(host, port, message)
```

## Original Documentation

[The rest of this file contains the original socket communication documentation for historical reference...]

## Connection Details

- **Ports**: AI specialists listen on ports 45000-45999
- **Protocol**: TCP sockets with newline-delimited JSON

[Rest of original content preserved for historical reference]