# Next Steps for aish Implementation

## Immediate Priority: Make This Work

```bash
$ ./aish
aish> echo "Hello" | apollo
```

That's it. If you can make that single command work, everything else follows.

## Implementation Order

### 1. Rhetor Socket Endpoint (30 min)
In `/Tekton/Rhetor/rhetor/api/`, add:
- `POST /api/ai/socket/create`
- `WebSocket /ws/socket/{socket_id}`

### 2. Wire Up Socket Registry (30 min)
In `/aish/src/registry/socket_registry.py`:
- Make `create()` call Rhetor
- Make `write()` send to WebSocket
- Make `read()` receive from WebSocket

### 3. Execute Pipeline (30 min)
In `/aish/src/core/shell.py`:
- Update `_execute_pipeline()` to actually run
- Parse → Create sockets → Write → Read → Display

### 4. Test with Team Chat
- Start Rhetor
- Open Hephaestus UI
- Run: `aish> team-chat "Hello everyone"`
- See messages in Team Chat panel!

## Success Criteria

You know it's working when:
1. `echo "test" | apollo` returns AI response
2. `team-chat "test"` shows in Hephaestus UI
3. `apollo | athena` chains responses
4. No crashes, clean errors

## Where to Find Help

- Casey and previous Claude for guidance
- `/aish/docs/` for all documentation
- `/Tekton/Rhetor/` for backend code
- Just ask if stuck!

Remember: Simple. Works. Hard to screw up.