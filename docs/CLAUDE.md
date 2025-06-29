# Claude Development Guide for aish

Hi Claude! This guide will help you understand and work on aish effectively.

## Project Vision

aish is implementing a 50-year-old dream: making AI orchestration as simple as Unix pipes. When complete, developers will write:

```bash
problem | think | solve > solution.txt
```

Instead of thousands of lines of orchestration code.

## Current Status

- ✅ Basic pipeline execution working
- ✅ Socket registry implemented
- ✅ Both HTTP (Rhetor) and Socket (Greek Chorus) protocols supported
- ✅ Team chat functionality
- ✅ Dynamic AI discovery
- ✅ Test suite (functional, integration, socket tests)
- 🚧 Upcoming: Streaming, Sessions, Bulk Operations, WebSocket (see Sprint docs)

## Key Concepts You Must Understand

### 1. AIs Are Just Sockets
- No complex abstractions
- Read input, write output
- Headers handle routing: `[team-chat-from-apollo-123]`

### 2. Everything Is A Stream
```bash
audio.mp3 | whisper | apollo | text-to-speech > response.mp3
image.png | vision | athena | markdown > analysis.md
```

### 3. Rhetor Is The Backend
- Manages actual AI instances
- Provides socket-like interface
- Running on http://localhost:8300

## Code Architecture

```
aish/
├── aish                    # Entry point (like /bin/bash)
├── src/
│   ├── core/
│   │   └── shell.py       # Main REPL loop
│   ├── parser/
│   │   └── pipeline.py    # Parse "ai1 | ai2" syntax
│   ├── registry/
│   │   └── socket_registry.py  # YOUR MAIN WORK AREA
│   └── runners/           # Future: execute pipelines
```

## Implementation Priority

### Phase 1: Basic Socket Operations (YOUR FOCUS)
Make these commands work:
```bash
echo "test" | apollo              # Simple pipe
apollo | athena                   # AI-to-AI pipe
team-chat "message"              # Broadcast
```

### Phase 2: File Operations
```bash
apollo > output.txt              # Redirect output
apollo < input.txt               # Read input
apollo >> log.txt                # Append
```

### Phase 3: Process Management
```bash
ps -ai                          # List AI processes
kill apollo-123                 # Terminate AI
apollo &                        # Background AI
```

## Rhetor Integration

Rhetor will provide REST/WebSocket endpoints for:
```python
# Create AI instance
POST /api/ai/create
{
    "name": "apollo",
    "model": "claude-3",
    "prompt": "You are Apollo...",
    "context": {}
}

# Read/Write will use WebSocket
ws://localhost:8300/ws/ai/{socket_id}
```

## Testing Your Implementation

1. Start Rhetor:
   ```bash
   cd /Users/cskoons/projects/github/Tekton/Rhetor
   ./run_rhetor.sh
   ```

2. Run aish:
   ```bash
   cd /Users/cskoons/projects/github/aish
   ./aish
   aish> echo "Hello" | apollo
   ```

3. Check Team Chat UI in Hephaestus to see multi-AI communication

## Design Principles

1. **Fail Silent, Not Loud** - Like Unix tools
2. **Text Is Universal** - Everything converts to/from text
3. **Composable** - Small tools that combine
4. **No Magic** - If it seems complex, it's wrong

## Common Patterns

### Pipeline Execution
```python
# Parse pipeline
stages = parse("echo 'test' | apollo | athena")

# Create sockets
sockets = [create_ai(stage) for stage in stages]

# Wire them together
for i in range(len(sockets)-1):
    pipe(sockets[i].output, sockets[i+1].input)

# Execute
run_pipeline(sockets)
```

### Header Management
```python
def read(socket_id):
    raw_message = socket.read()
    return f"[team-chat-from-{socket_id}] {raw_message}"

def write(socket_id, message):
    header = f"[team-chat-to-{socket_id}] "
    socket.write(header + message)
```

## Questions To Ask

- "Should this work like Unix tool X?" (Usually yes)
- "Is this the simplest solution?" (If no, rethink)
- "Would a 1970s Unix hacker understand this?" (Goal)

## Current Sprint: Tekton-aish Improvement Sprint

See `/docs/sprints/Tekton_aish_Improvement_Sprint/` for detailed plans:
- **SprintPlan.md**: 14-day implementation timeline
- **ArchitecturalDecisions.md**: Key design choices
- **ImplementationPlan.md**: Detailed code changes
- **APISpecifications.md**: New API contracts
- **TestingStrategy.md**: Comprehensive test plans
- **TestingImprovements.md**: Test infrastructure upgrades

### Sprint Goals
1. **Streaming**: Real-time AI responses (SSE + WebSocket)
2. **Sessions**: Stateful conversations with context
3. **Bulk Operations**: Efficient multi-AI execution
4. **Enhanced Discovery**: Capability-based AI selection
5. **WebSocket**: Interactive bidirectional communication

## Testing

### Running Tests
```bash
# Quick check all tests
python tests/test_quick_check.py

# Individual test suites
python tests/test_functional.py      # No dependencies
python tests/test_integration.py     # Requires Rhetor
python tests/test_socket_communication.py
```

### Test Status
- All current tests passing ✅
- See `tests/README_TEST_STATUS.md` for details
- Sprint will add streaming, session, bulk, and WebSocket tests

## Resources

- Unix Philosophy: "Write programs that do one thing and do it well"
- Rhetor Docs: `/Tekton/MetaData/TektonDocumentation/Architecture/Rhetor_AI_Communication_Protocol.md`
- Team Chat UI: `/Tekton/Hephaestus/ui/components/rhetor/rhetor-component.html`
- User Docs: `/docs/getting-started.md`, `/docs/command-reference.md`, `/docs/pipeline-guide.md`
- Sprint Docs: `/docs/sprints/Tekton_aish_Improvement_Sprint/`

Remember: You're not building an AI framework. You're building a shell that happens to pipe AIs instead of processes. Keep it simple!

---

Casey and the previous Claude are here to help. Good luck!