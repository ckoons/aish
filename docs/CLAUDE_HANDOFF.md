# Claude AI Handoff Documentation

## For Future Claude Instances

This document provides essential context for any Claude instance working on the aish project.

## Project Overview

aish (AI Shell) is an interactive shell that extends Unix philosophy to AI orchestration:
- **Philosophy**: "AIs are just sockets. They read input, write output."
- **Syntax**: Unix-style pipelines for AI communication
- **Integration**: Works with Tekton's AI specialist platform

## Recent Work (June 2025 Sprint)

### Phase 1 Completed: Socket Communication Improvements

**What was done:**
1. Fixed socket buffering issues that caused message truncation
2. Implemented line-buffered socket reading for reliable communication
3. Added intelligent timeout detection (connection vs processing vs dead)
4. Integrated with Tekton's MCP tools for unified AI communication

**Key files created/modified:**
- `src/utils/socket_buffer.py` - New LineBufferedSocket and SocketTimeoutDetector
- `src/registry/socket_registry.py` - Updated to use buffered sockets
- `tests/test_socket_buffering.py` - Comprehensive socket tests
- `tests/test_phase1_integration.py` - Integration tests

### Current Architecture

```
aish (shell) 
  ↓
SocketRegistry (manages connections)
  ↓
LineBufferedSocket (handles protocol)
  ↓
AI Specialists (ports 45000+)
```

**Protocol**: Newline-delimited JSON
```json
Request:  {"type": "chat", "content": "message"}\n
Response: {"type": "chat_response", "content": "reply", "ai_id": "athena-ai"}\n
```

## Important Context

### Casey's Preferences
1. **No auto-restart** - Makes errors visible for debugging
2. **Discuss before implementing** - Present ideas and get approval
3. **Test everything** - Manual testing before automation
4. **Simple and robust** - Avoid over-engineering
5. **No hardcoded values** - Use discovery mechanisms

### AI Specialist Ports
- All AI specialists are on ports 45000+ (NOT 9001-9004)
- Use `ai-discover` for dynamic discovery
- Component HTTP APIs are on ports 8000-8088

### Testing Philosophy
- Build functional tests for both ends
- Use dynamic discovery in tests
- Make errors visible and debuggable
- Test with real AIs, not mocks

## Next Sprint Items (Phase 2)

### High Priority:
1. **Conversation History** (in progress)
   - Unix-style format: `1716: echo "query" | ai # Response: ...`
   - Storage in ~/.aish_history
   - `aish-history` command with JSON export via `jc`

2. **SSE Streaming** 
   - Progressive output display
   - Add to both aish and Rhetor
   - Heartbeat support

### Medium Priority:
3. **WebSocket Support**
   - After SSE is working
   - For bidirectional streaming
   - Optional protocol selection

4. **Session Management**
   - Stateful conversations
   - Integration with Engram (later)

## Common Commands

```bash
# Check AI availability
ai-discover list

# Test socket connections
python tests/check_ai_ports.py

# Run integration tests
python tests/test_phase1_integration.py

# Check Tekton status
tekton-status

# Debug mode
AISH_DEBUG=1 aish
```

## Known Issues

1. **Engram Integration**: Deferred to later sprint
2. **Streaming**: Not yet implemented (Phase 2)
3. **Session Persistence**: Basic implementation only

## Code Patterns

### Socket Communication
```python
# Always use dynamic discovery
registry = SocketRegistry(debug=True)
ai_info = registry._get_ai_info('athena')

# Use LineBufferedSocket for reliability
buffered = LineBufferedSocket(sock, timeout=30.0, debug=True)
buffered.write_message({"type": "chat", "content": "message"})
response = buffered.read_message()
```

### Error Handling
```python
# Distinguish timeout types
if error == "Connection timeout after 2.0s":
    # Network issue
elif error == "No heartbeat for 60s":
    # Dead connection
else:
    # AI processing
```

## Documentation Locations

- `/docs/api/` - API references
- `/docs/development/` - Development guides
- `/docs/architecture/` - System design
- `/tests/README_*.md` - Test documentation

## Contact

- Casey Koons - Project owner, handles all GitHub operations
- Tekton platform - Related AI infrastructure project

Remember: Always discuss approaches before implementing!