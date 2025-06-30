# aish Phase 4 Sprint Plan

## Timeline: 7 Days

### Day 1-2: SSE Client Implementation
**Goal**: Add streaming support to aish shell

#### Tasks:
1. Create SSE client in `utils/streaming.py`
2. Integrate with socket_registry
3. Update shell.py for progressive display
4. Handle disconnections gracefully

#### Key Files:
- `src/utils/streaming.py` (new)
- `src/registry/socket_registry.py` (update)
- `src/core/shell.py` (update display logic)

### Day 3: Stream Wrapper Design
**Goal**: Unified streaming interface

#### Tasks:
1. Design abstract stream interface
2. Implement SSE stream wrapper
3. Prepare for WebSocket wrapper
4. Add heartbeat/keepalive logic

#### Key Files:
- `src/utils/stream_wrapper.py` (new)
- `src/utils/heartbeat.py` (extract from socket_buffer.py)

### Day 4-5: Pipeline Improvements
**Goal**: Fix timeouts and add context

#### Tasks:
1. Debug apollo timeout issue
2. Implement context passing protocol
3. Add parallel pipeline support
4. Test with complex pipelines

#### Key Files:
- `src/core/shell.py` (_execute_pipe_stages)
- `src/parser/pipeline.py` (context support)
- `src/registry/socket_registry.py` (context handling)

### Day 6: History Enhancements
**Goal**: Make history streaming-aware

#### Tasks:
1. Track partial responses during streaming
2. Record streaming metadata
3. Update history format for streams
4. Test replay with streaming commands

#### Key Files:
- `src/core/history.py`
- `src/core/shell.py` (history integration)

### Day 7: Integration & Testing
**Goal**: Ensure everything works together

#### Tasks:
1. End-to-end streaming tests
2. Pipeline integration tests
3. History with streaming tests
4. Performance benchmarking
5. Update documentation

## Streaming Display Strategy

### Progressive Output
```
aish> echo "Explain quantum computing" | athena
[Streaming...] Quantum computing is a revolutionary approach to computation that
leverages the principles of quantum mechanics. Unlike classical computers that use
bits representing 0 or 1, quantum computers use quantum bits or 'qubits' which can
exist in superposition...
[Complete - 2.3s]
```

### Parallel Pipeline Display
```
aish> echo "Analyze this" | apollo & athena & hermes
[apollo   ] Starting analysis of code structure...
[athena   ] From a knowledge perspective...
[hermes   ] Coordinating responses...
[Complete - 3 AIs responded]
```

## Risk Mitigation

1. **SSE Compatibility**: May need fallback for non-streaming
2. **Terminal Control**: Progressive display needs careful handling
3. **History Complexity**: Streaming adds recording challenges
4. **Performance**: Streaming overhead on client side

## Definition of Done

- [ ] SSE streaming shows progressive output
- [ ] Pipelines work without timeouts
- [ ] Context passes between stages
- [ ] History captures streaming sessions
- [ ] All tests passing
- [ ] Documentation updated

## Future Enhancements

- WebSocket for bidirectional streaming
- Advanced terminal UI (progress bars, etc.)
- Streaming transformations in pipelines
- Real-time collaborative sessions