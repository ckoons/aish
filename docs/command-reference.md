# aish Command Reference

Complete reference for all aish commands and options.

## Command Line Options

```bash
aish [options] [script]
```

### Options

| Option | Long Form | Description |
|--------|-----------|-------------|
| `-c` | `--command` | Execute a single command and exit |
| `-d` | `--debug` | Enable debug output |
| `-l` | `--list-ais` | List available AI specialists |
| `-r` | `--rhetor` | Specify Rhetor endpoint |
| `-v` | `--version` | Show version information |
| `-h` | `--help` | Show help message |

### Examples

```bash
# Execute single command
aish -c 'echo "Hello" | apollo'

# Debug mode
aish -d -c 'team-chat "test"'

# Custom Rhetor endpoint
aish -r http://remote:8003 -c 'echo "test" | hermes'

# List AIs and exit
aish -l
```

## Pipeline Syntax

### Basic Pipeline

```bash
command | ai1 | ai2 | ai3
```

Data flows from left to right through each AI.

### Echo Input

```bash
echo "message" | ai-name
```

### File Input/Output

```bash
# Input from file
ai-name < input.txt

# Output to file
echo "message" | ai-name > output.txt

# Append to file
echo "message" | ai-name >> output.txt

# Full pipeline with files
cat input.py | apollo | athena > review.md
```

### Team Chat

Broadcast to all available AIs:

```bash
team-chat "message"
```

## Advanced Features (Sprint Implementation)

### Streaming Responses

Enable real-time streaming output:

```bash
echo "Generate a story" | apollo --stream
```

### Session Management

Maintain conversation context:

```bash
# Start a session
echo "My name is Casey" | apollo --session

# Continue with session ID
echo "What's my name?" | apollo --session sess_abc123

# Auto-session (new)
apollo --session --interactive
```

### Bulk Operations

Send to multiple AIs efficiently:

```bash
# Broadcast to specific AIs
apollo,athena,prometheus << "Analyze this code"

# Parallel execution block
{apollo|athena|prometheus} > results.txt

# Sequential with dependencies
apollo | {athena,hermes} | prometheus
```

### Capability-Based Routing

Route to best AI for a task:

```bash
@code-analysis << "Review this function"
@planning << "Design a microservice"
@optimization << "Improve performance"
```

### WebSocket Interactive Mode

Real-time interactive sessions:

```bash
aish --websocket apollo
apollo> Hello
apollo> [real-time streaming response...]
apollo> exit
```

## Interactive Mode Commands

When running `aish` without arguments:

| Command | Description |
|---------|-------------|
| `help` | Show help information |
| `list-ais`, `ais` | List available AI specialists |
| `exit` | Exit aish |
| `!command` | Execute shell command |
| `clear` | Clear screen |
| `history` | Show command history |

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TEKTON_RHETOR_PORT` | Rhetor service port | 8003 |
| `TEKTON_RHETOR_HOST` | Rhetor service host | localhost |
| `AISH_DEBUG` | Enable debug mode | 0 |
| `AISH_SESSION_DIR` | Session storage directory | ~/.aish/sessions |
| `AISH_HISTORY_FILE` | Command history file | ~/.aish_history |

## Special Syntax

### Multi-line Input

```bash
aish> apollo << EOF
> Line 1
> Line 2
> Line 3
> EOF
```

### Command Substitution

```bash
echo "Analyze: $(cat file.py)" | apollo
```

### Background Execution

```bash
apollo < large_file.txt &
```

## Pipeline Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `\|` | Pipe output to next command | `echo "test" \| apollo` |
| `>` | Redirect output to file | `apollo > out.txt` |
| `>>` | Append output to file | `apollo >> out.txt` |
| `<` | Read input from file | `apollo < in.txt` |
| `<<` | Here document / Bulk input | `apollo << "message"` |
| `&` | Background execution | `apollo &` |
| `;` | Sequential execution | `cmd1; cmd2` |
| `&&` | Execute if previous succeeds | `cmd1 && cmd2` |
| `\|\|` | Execute if previous fails | `cmd1 \|\| cmd2` |

## AI Name Resolution

aish intelligently resolves AI names:

1. **Exact match**: `apollo` → `apollo-ai`
2. **With suffix**: `apollo` → `apollo-ai`
3. **Prefix match**: `apol` → `apollo-ai`
4. **Component match**: `prometheus` → `prometheus-ai`
5. **Capability match**: `@planning` → best AI for planning

## Error Handling

### Exit Codes

| Code | Description |
|------|-------------|
| 0 | Success |
| 1 | General error |
| 2 | Connection error |
| 3 | AI not found |
| 4 | Syntax error |
| 5 | Timeout |

### Error Messages

```bash
# AI not found
aish: AI 'unknown-ai' not found. Available: apollo, athena...

# Connection error
aish: Cannot connect to Rhetor at localhost:8003

# Syntax error
aish: Syntax error near '|>'
```

## Performance Options

### Caching

```bash
# Enable response caching
export AISH_CACHE=1

# Set cache directory
export AISH_CACHE_DIR=~/.aish/cache
```

### Timeouts

```bash
# Set global timeout (seconds)
export AISH_TIMEOUT=30

# Per-command timeout
echo "test" | apollo --timeout 10
```

## Debugging

### Debug Levels

```bash
# Basic debug
aish -d

# Verbose debug
AISH_DEBUG=2 aish

# Trace level
AISH_DEBUG=3 aish
```

### Debug Output

```bash
[DEBUG] Created socket apollo-1234567890
[DEBUG] Writing to apollo: "Hello"
[DEBUG] Response from apollo: "Hi there!"
```

## Configuration File

Create `~/.aishrc`:

```bash
# Default settings
export TEKTON_RHETOR_PORT=8003
export AISH_DEBUG=0

# Aliases
alias review='apollo | athena'
alias plan='prometheus | telos'
alias doc='hermes | sophia'

# Functions
code_review() {
    cat "$1" | apollo | athena > "${1%.py}_review.md"
}
```

## Examples

### Code Review Pipeline
```bash
cat app.py | apollo --capability code-analysis | \
    athena --capability review | \
    prometheus --capability planning > review_and_plan.md
```

### Interactive Problem Solving
```bash
aish
aish> prometheus --session
prometheus> How do I design a scalable web service?
prometheus> What about database considerations?
prometheus> exit
```

### Batch Processing
```bash
for file in *.py; do
    echo "Analyzing $file" | apollo > "reviews/${file%.py}_review.txt"
done
```

### Team Collaboration
```bash
team-chat "We need to refactor the authentication system. Thoughts?" | \
    tee team_discussion.md
```

## Tips and Tricks

1. **Use tab completion** (when available) for AI names
2. **Create aliases** for common pipelines
3. **Use sessions** for context-aware conversations
4. **Enable streaming** for long responses
5. **Use capability routing** when unsure which AI to use
6. **Check AI availability** with `aish -l` before complex pipelines
7. **Use debug mode** to troubleshoot connection issues
8. **Save useful pipelines** as shell scripts