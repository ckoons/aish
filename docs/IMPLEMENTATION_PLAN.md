# aish Implementation Plan

## Current Status

### Completed ✅
1. Basic command routing (`aish apollo "message"`)
2. Pipeline support (`echo "data" | aish athena`)
3. Shell integration via aish-proxy
4. Team chat functionality
5. AI discovery from Rhetor
6. Command history tracking
7. Safe terminal integration (no corruption)

### In Progress 🚧
1. Moving to Tekton/shared/aish
2. Terma integration for terminal management
3. MCP endpoint exposure
4. Session persistence

### Planned 📋
1. Streaming responses
2. Multi-language implementations
3. Enhanced context management
4. Rich terminal UI

## Phase 1: Tekton Integration (Current)

### 1.1 Move aish to Tekton/shared/aish
```bash
# File structure in Tekton
Tekton/shared/aish/
├── aish              # Main command
├── aish-proxy        # Shell enhancer  
├── aish-history      # History tool
├── src/              # Python package
│   └── core/         # Core modules
├── docs/             # Documentation
└── requirements.txt  # Dependencies
```

### 1.2 Update Import Paths
- Modify imports to work from Tekton location
- Update PATH additions in aish-proxy
- Ensure Rhetor endpoint discovery

### 1.3 Terma Integration
- Register terminal on launch
- Accept commands from Terma
- Report health status
- Handle terminal lifecycle

### 1.4 MCP Endpoints
```python
# In Terma MCP
@mcp_router.post("/tools/launch_terminal")
async def launch_terminal_with_aish(request):
    config = TerminalConfig(
        shell_args=["--aish"],  # Use aish-proxy
        env={"TERMA_ID": terminal_id}
    )
    return launcher.launch_terminal(config)
```

## Phase 2: Enhanced Features

### 2.1 Streaming Responses
- Implement WebSocket client in aish
- Progressive response display
- Interruption handling (Ctrl+C)
- Progress indicators

### 2.2 Session Management
```python
# Session persistence
class AishSession:
    def __init__(self, session_id):
        self.id = session_id
        self.context = {}
        self.history = []
        
    def save(self):
        # Persist to ~/.aish/sessions/
        
    def restore(self):
        # Load previous context
```

### 2.3 Context Sharing
- Cross-terminal context sync
- Conversation branching
- Context summarization
- Explicit context commands

## Phase 3: Multi-Language Implementation

### 3.1 Language Variants
```
aish (wrapper) → checks AISH_IMPL → launches appropriate version
                                  ├── aish-py (Python)
                                  ├── aish-rs (Rust)
                                  └── aish-c (C)
```

### 3.2 Rust Implementation
```rust
// aish-rs/src/main.rs
use clap::Parser;
use reqwest;

#[derive(Parser)]
struct Args {
    ai_name: Option<String>,
    message: Vec<String>,
}

async fn route_to_ai(ai: &str, message: &str) -> Result<String> {
    // HTTP client to Rhetor
}
```

### 3.3 C Implementation
```c
// aish-c/src/main.c
#include <stdio.h>
#include <curl/curl.h>

int main(int argc, char *argv[]) {
    if (argc > 1) {
        route_to_ai(argv[1], argv[2]);
    }
    return 0;
}
```

## Phase 4: Advanced Features

### 4.1 Rich Terminal UI
- Color support for AI responses
- Markdown rendering in terminal
- Progress bars and spinners
- Interactive selection menus

### 4.2 Command Completion
```bash
# Bash completion
_aish_completions() {
    local cur="${COMP_WORDS[COMP_CWORD]}"
    local ais="apollo athena rhetor sophia hermes"
    COMPREPLY=($(compgen -W "${ais}" -- ${cur}))
}
complete -F _aish_completions aish
```

### 4.3 Plugin System
```python
# Plugin interface
class AishPlugin:
    def pre_process(self, command: str) -> str:
        """Modify command before execution"""
        
    def post_process(self, response: str) -> str:
        """Modify response before display"""
```

## Testing Strategy

### Unit Tests
- Command parsing
- Input detection
- AI routing logic
- History management

### Integration Tests
- Rhetor communication
- Pipeline execution
- Error handling
- Shell compatibility

### System Tests
- Terminal launching via Terma
- Cross-terminal sessions
- Performance under load
- Multi-language consistency

## Migration Path

### For Users
```bash
# Before: Individual AI commands
apollo "question"

# After: Unified aish command  
aish apollo "question"

# Migration helper
alias apollo='aish apollo'
```

### For Developers
1. Update documentation
2. Deprecation warnings
3. Migration scripts
4. Compatibility layer

## Performance Considerations

### Startup Time
- Lazy import heavy dependencies
- Cache AI discovery results
- Minimize initialization

### Response Latency
- Connection pooling to Rhetor
- Local response caching
- Async I/O where possible

### Resource Usage
- Minimal memory footprint
- No background processes
- Clean subprocess handling

## Security Implementation

### API Authentication
```python
# Future: API key management
api_key = os.environ.get('AISH_API_KEY')
if not api_key:
    api_key = load_from_keyring()
```

### Audit Logging
- Log all AI requests
- Track usage per user
- Rate limiting implementation

### Secure Communication
- HTTPS to Rhetor
- Certificate validation
- Encrypted credential storage