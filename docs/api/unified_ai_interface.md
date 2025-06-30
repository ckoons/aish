# Unified AI Interface for aish

As of the latest update, aish now uses Tekton's Unified AI Interface for all AI communication. This provides a consistent, robust way to interact with AI specialists.

## Overview

The old socket-based implementation using `LineBufferedSocket` and `socket_buffer.py` has been replaced with Tekton's unified system. All AI discovery, connection management, and communication now goes through the shared interface.

## Key Components

### 1. Unified Registry

aish automatically discovers available AIs through the unified registry:

```python
# In socket_registry.py
from shared.ai.unified_registry import UnifiedAIRegistry
from shared.ai.socket_client import create_sync_client

# Automatic discovery
specialists = self.unified_registry.discover_sync()
```

### 2. Socket Client

All socket communication uses the shared client:

```python
# Old way (deprecated)
from utils.socket_buffer import LineBufferedSocket

# New way
from shared.ai.socket_client import create_sync_client
client = create_sync_client()
response = client.send_message(host, port, message)
```

## Usage in aish

The integration is transparent to users:

```bash
# Simple pipeline
echo "Hello" | apollo

# Multi-stage pipeline
echo "Analyze this" | apollo | athena

# Team chat
team-chat "What should we build?"
```

## Benefits

1. **Automatic Health Monitoring** - AIs are continuously monitored
2. **Performance Tracking** - Response times and success rates tracked
3. **Smart Routing** - Automatic fallback to healthy AIs
4. **Streaming Support** - Progressive responses (coming soon to aish)

## Configuration

No configuration needed! aish automatically uses the unified registry if Tekton is available, with graceful fallback to direct discovery.

## For Developers

See the main documentation:
- [Unified AI Interface Architecture](/Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/Architecture/UnifiedAIInterface.md)
- [Socket Client API](/Users/cskoons/projects/github/Tekton/shared/ai/socket_client.py)
- [Registry API](/Users/cskoons/projects/github/Tekton/shared/ai/unified_registry.py)

## Migration Notes

The following have been removed:
- `utils/socket_buffer.py` - Use shared socket client
- `LineBufferedSocket` class - Replaced by `AISocketClient`
- `SocketTimeoutDetector` - Built into unified client

All functionality has been preserved or enhanced in the new system.