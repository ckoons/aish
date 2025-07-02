# aish Architecture

## Overview

aish (AI Shell) is a thin client that provides seamless AI integration within any Unix shell environment. It acts as both a command-line tool and a transparent shell enhancement, routing AI requests to the Tekton platform while maintaining full shell compatibility.

## Core Design Principles

1. **Simplicity First**: One command (`aish`) serves as both the tool and the escape keyword
2. **Unix Philosophy**: Do one thing well - route AI commands to Tekton
3. **Zero Terminal Corruption**: Use shell functions/aliases, never manipulate terminal modes
4. **Thin Client**: Minimal local functionality, leverage Tekton for heavy lifting
5. **Shell Agnostic**: Works with bash, zsh, and other shells

## Architecture Components

### 1. aish Command (`/aish`)
The main entry point that serves multiple roles:
- **Direct AI Router**: `aish apollo "message"` routes to specific AI
- **Pipeline Component**: `echo "data" | aish athena` accepts piped input
- **Interactive Shell**: `aish` starts AI-enhanced REPL
- **Script Executor**: `aish script.ai` runs AI command scripts

### 2. aish-proxy (`/aish-proxy`)
Shell environment enhancer that:
- Sets up `AISH_ACTIVE=1` environment variable
- Adds aish to PATH for command availability
- Configures Rhetor endpoint connection
- Launches user's preferred shell with AI capabilities

### 3. Core Components (`/src/core/`)

#### shell.py
- Main REPL loop for interactive mode
- Command parsing and pipeline execution
- AI discovery and routing logic
- Integration with Rhetor API

#### proxy_shell.py
- Legacy subprocess-based implementation
- Fallback for compatibility
- Pattern matching for AI commands

#### history.py
- AI conversation history tracking
- Session management
- Context preservation

#### terminal_launcher.py
- Native terminal application launcher
- Platform-specific terminal detection
- Integration point for Tekton Terma

### 4. Communication Layer

```
User Input → aish command → Parse AI/Command → Route to Rhetor → AI Response
                                                        ↓
                                                  Tekton Platform
```

## Key Design Decisions

### 1. Single Command Pattern
**Decision**: Use `aish` as the only command, not individual AI names
**Rationale**: 
- Avoids namespace pollution (no hijacking "apollo", "athena", etc.)
- Clear distinction between shell and AI commands
- Future flexibility for command syntax evolution

### 2. Shell Hook Approach
**Decision**: Use shell initialization instead of PTY manipulation
**Rationale**:
- PTY manipulation is fragile and can corrupt terminals
- Shell hooks are stable and well-understood
- Maintains full shell feature compatibility (history, completion, etc.)

### 3. Thin Client Architecture
**Decision**: Keep aish minimal, delegate to Tekton
**Rationale**:
- Easier to maintain multiple implementations (Python/Rust/C)
- Centralized AI orchestration in Tekton
- Reduced client-side complexity

### 4. Pipeline Integration
**Decision**: Support Unix pipes as first-class feature
**Rationale**:
- Natural Unix workflow integration
- Enables AI command composition
- Follows "text as universal interface" principle

## Implementation Details

### Command Parsing Flow
1. Check if first argument is recognized AI name
2. Determine input source (args, stdin, or interactive)
3. Route to appropriate handler
4. Format and send to Rhetor
5. Return response to user

### Shell Integration
```bash
# In shell initialization
export AISH_ACTIVE=1
export PATH="/path/to/aish:$PATH"
export RHETOR_ENDPOINT="http://localhost:8003"
```

### AI Command Syntax
```bash
# Direct command
aish apollo "What is the weather?"

# Piped input
cat data.txt | aish athena

# Team broadcast
aish team-chat "Starting deployment"

# Chained AIs
echo "code" | aish apollo | aish athena
```

## Platform Integration

### Tekton Integration Points
1. **Rhetor**: AI communication hub (port 8003)
2. **Terma**: Terminal management and lifecycle
3. **Hermes**: Service orchestration
4. **Team Chat**: Multi-AI coordination

### Terminal Registration
When launched via Terma:
1. aish-proxy registers with Terma
2. Receives terminal ID and configuration
3. Reports health status periodically
4. Accepts commands from Terma

## Future Architecture Considerations

### Multi-Language Support
Current: Python implementation
Planned: Rust and C implementations
Selection: Via `AISH_IMPL` environment variable

### Enhanced Features
- Session persistence across terminals
- Streaming responses for long operations
- Bulk command execution
- Context sharing between terminals

### Security
- API key management for Rhetor
- Secure credential storage
- Audit logging for AI requests
- Rate limiting and quotas