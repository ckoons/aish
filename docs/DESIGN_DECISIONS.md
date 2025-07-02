# aish Design Decisions

## Overview

This document captures the key design decisions made during aish development, including failed approaches and lessons learned.

## Major Design Decisions

### 1. Command Interface Design

**Decision**: Single `aish` command as universal AI escape

**Alternatives Considered**:
- Individual AI commands (apollo, athena, etc.)
- Special prefix (ai:apollo, @apollo)
- Shell operators (>|, |>)

**Rationale**:
- Namespace safety - no conflicts with existing commands
- User clarity - one thing to remember
- Future flexibility - can evolve syntax within aish
- Corporate friendly - companies named "Apollo" won't complain

**Trade-offs**:
- Slightly more verbose (`aish apollo` vs `apollo`)
- Worth it for clarity and safety

### 2. Terminal Integration Approach

**Decision**: Shell initialization hooks instead of PTY manipulation

**Failed Approach**: PTY-based transparent proxy
- Attempted to intercept keystrokes
- Manipulated terminal modes (raw, cbreak)
- Created PTY pairs for bidirectional filtering

**Why It Failed**:
- Terminal mode manipulation corrupted user terminals
- Complex edge cases (arrow keys, history, tab completion)
- Signal handling issues (Ctrl+C, Ctrl+D, SIGWINCH)
- Poor user experience with hung terminals

**Successful Approach**: Shell hooks
- Source initialization file with functions
- Add aish to PATH
- Let shell handle ALL terminal interaction
- Process commands after shell parsing

**Lessons Learned**:
- "Acting like a terminal" requires implementing a full terminal emulator
- Shell hooks are simple, reliable, and well-tested
- Never fight the shell - work with it

### 3. Architecture Pattern

**Decision**: Thin client connecting to Tekton platform

**Rationale**:
- Separation of concerns - aish routes, Tekton orchestrates
- Multiple implementation languages possible
- Centralized AI management
- Easier updates and maintenance

**Implementation**:
- Minimal local state (just history)
- All AI logic in Rhetor/Tekton
- Simple HTTP/WebSocket communication
- Stateless client design

### 4. Input/Output Handling

**Decision**: Support both direct and piped input uniformly

**Design**:
```python
if not sys.stdin.isatty():
    # Piped input
    input_data = sys.stdin.read()
elif args.message:
    # Command line args
    input_data = ' '.join(args.message)
else:
    # Interactive input
    input_data = sys.stdin.read()
```

**Benefits**:
- Natural Unix pipeline integration
- Flexible input methods
- Consistent behavior

### 5. AI Discovery and Routing

**Decision**: Static list of known AIs with runtime discovery

**Implementation**:
- Hardcoded AI names for command parsing
- Runtime discovery from Rhetor for availability
- Graceful degradation if AI unavailable

**Trade-offs**:
- Must update aish for new AIs (acceptable)
- Fast command parsing
- Clear error messages

### 6. Error Handling Philosophy

**Decision**: Fail quietly with clear messages

**Principles**:
- No stack traces for user errors
- Clear, actionable error messages
- Debug mode for development
- Follow Unix conventions (exit codes)

### 7. Shell Compatibility

**Decision**: Support bash and zsh with same codebase

**Approach**:
- Detect shell type at runtime
- Use common subset of features
- Shell-specific initialization only where necessary
- Test on both shells

### 8. Configuration Management

**Decision**: Environment variables over config files

**Variables**:
- `AISH_ACTIVE` - Indicates aish is available
- `RHETOR_ENDPOINT` - AI backend location
- `AISH_DEBUG` - Enable debug output
- `AISH_KEYWORD` - (Future) Alternative to 'aish'

**Benefits**:
- No configuration file management
- Easy to override per-session
- Standard Unix approach

## Failed Experiments

### 1. PTY Proxy Implementations
- `pty_proxy_shell.py` - Full PTY manipulation
- `simple_pty_proxy.py` - Minimal PTY approach
- `working_pty_proxy.py` - Terminal mode experiments

**Lesson**: Terminal emulation is complex; use existing shells

### 2. Command Interception
- Tried intercepting at keystroke level
- Attempted to parse partial commands
- Buffer management for line editing

**Lesson**: Let the shell parse commands completely

### 3. Individual AI Commands
- Created `apollo`, `athena` as separate commands
- Added to PATH dynamically
- Namespace collision issues

**Lesson**: One command is cleaner and safer

## Design Principles

### Simplicity
- Minimum viable functionality
- Clear, single purpose
- No feature creep

### Reliability
- Never corrupt user's terminal
- Always provide escape route
- Fail gracefully

### Compatibility
- Work with existing tools
- Follow Unix conventions
- Respect user's environment

### Extensibility
- Clean interfaces for Tekton integration
- Multiple language implementations
- Plugin architecture (future)

## Future Design Considerations

### Streaming Responses
- WebSocket for real-time AI responses
- Progress indicators for long operations
- Interruption handling

### Context Management
- Session persistence
- Cross-terminal context sharing
- Conversation branching

### Enhanced UI
- Rich terminal UI (colors, formatting)
- Interactive mode improvements
- Command completion for AI names