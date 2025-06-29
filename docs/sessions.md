# Session Management Guide

Learn how to use aish's session management features for stateful conversations with AI specialists.

## What Are Sessions?

Sessions allow AI specialists to maintain context across multiple interactions. Instead of treating each command as isolated, sessions remember previous exchanges, enabling more natural conversations.

## Basic Session Usage

### Starting a Session

Create a new session with an AI:

```bash
# Start an interactive session
aish
aish> apollo --session
apollo (session: sess_abc123)> Hello, I'm working on a Python web app
apollo> What kind of web app are you building?
apollo (session)> It's an e-commerce platform
apollo> I understand. For an e-commerce platform, you'll need...
```

### Session Commands

```bash
# Create a session and get its ID
echo "Hello" | apollo --session --get-id

# Continue an existing session
echo "What did we discuss?" | apollo --session sess_abc123

# End a session
apollo --session sess_abc123 --end

# List active sessions
aish --list-sessions
```

## Session Context Window

Sessions maintain a configurable context window:

```bash
# Default: 10 message pairs
echo "Start" | apollo --session

# Custom context window (20 messages)
echo "Start" | apollo --session --context-window 20

# Unlimited context (use carefully)
echo "Start" | apollo --session --context-window 0
```

## Multi-Stage Sessions

Use the same session across pipeline stages:

```bash
# Create session
SESSION_ID=$(echo "I need to refactor a login system" | apollo --session --get-id)

# Stage 1: Analysis
echo "Here's the current code: $(cat login.py)" | apollo --session $SESSION_ID > analysis.md

# Stage 2: Security review (context aware)
echo "What security issues should I address?" | apollo --session $SESSION_ID > security.md

# Stage 3: Implementation plan (knows full context)
echo "Create an implementation plan" | apollo --session $SESSION_ID > plan.md
```

## Session Persistence

Sessions can be saved and restored:

```bash
# Save session to file
aish --save-session sess_abc123 > my_session.json

# Restore session
aish --restore-session < my_session.json

# Export all sessions
aish --export-sessions > all_sessions.json
```

## Cross-AI Sessions

Share context between different AIs:

```bash
# Start with Apollo
SESSION=$(echo "Analyzing this architecture" | apollo --session --get-id)

# Share session with Athena
echo "Review Apollo's analysis" | athena --session $SESSION --shared

# Prometheus can see both perspectives
echo "Create a plan based on the discussion" | prometheus --session $SESSION --shared
```

## Interactive Session Mode

For extended conversations:

```bash
# Enter session mode
aish --session apollo

Welcome to session mode with apollo-ai
Session ID: sess_def456
Type 'exit' to end session, 'save' to save context

> Hello, I need help with database design
apollo> I'd be happy to help with database design. What kind of application...

> It's a social media platform
apollo> For a social media platform database, you'll need to consider...

> save
Session saved to ~/.aish/sessions/sess_def456.json

> exit
Session ended
```

## Session Management Commands

### In Interactive Mode

| Command | Description |
|---------|-------------|
| `save` | Save current session |
| `context` | Show session context |
| `clear` | Clear session history (keep session) |
| `info` | Show session information |
| `export` | Export session to file |
| `exit` | End session |

### Command Line Options

```bash
# Session-related flags
--session               # Enable session mode
--session-id ID        # Use specific session
--get-id               # Return session ID only
--context-window N     # Set context size
--shared              # Allow cross-AI context
--list-sessions       # List all active sessions
--end-session ID      # End specific session
--cleanup-sessions    # Remove expired sessions
```

## Session Configuration

### Environment Variables

```bash
# Session storage location
export AISH_SESSION_DIR=~/.aish/sessions

# Default context window
export AISH_DEFAULT_CONTEXT=10

# Session timeout (minutes)
export AISH_SESSION_TIMEOUT=60

# Maximum sessions per user
export AISH_MAX_SESSIONS=50
```

### Configuration File

Create `~/.aish/config.yaml`:

```yaml
sessions:
  storage:
    type: file  # or 'redis'
    path: ~/.aish/sessions
  defaults:
    context_window: 10
    timeout_minutes: 60
    auto_save: true
  limits:
    max_sessions: 50
    max_context_size: 100000  # tokens
```

## Advanced Session Features

### Session Templates

Create reusable session templates:

```bash
# Save a session as template
aish --save-template "code-review" sess_abc123

# Start new session from template
echo "Review this code" | apollo --session --template "code-review"
```

### Session Merging

Combine multiple sessions:

```bash
# Merge sessions
aish --merge-sessions sess_123,sess_456 --output sess_combined

# Continue with merged context
echo "Summarize our discussions" | apollo --session sess_combined
```

### Session Analytics

Track session usage:

```bash
# Session statistics
aish --session-stats

Active sessions: 5
Total messages: 1,234
Average context length: 8.5
Most active AI: apollo-ai (45%)

# Detailed session info
aish --session-info sess_abc123

Session: sess_abc123
AI: apollo-ai
Created: 2024-01-01 10:00:00
Messages: 15
Context used: 8/10
Last activity: 2 minutes ago
```

## Session Best Practices

### 1. Name Your Sessions

Use meaningful session IDs:

```bash
# Instead of auto-generated IDs
echo "Start" | apollo --session --session-id "project-refactor"
```

### 2. Regular Saves

Save important sessions:

```bash
# Auto-save every 5 messages
apollo --session --auto-save 5

# Manual save
> save checkpoint-1
```

### 3. Context Management

Monitor context usage:

```bash
# Check context before adding
> context
Using 8/10 context window
Oldest message: 15 minutes ago

# Clear old context if needed
> clear --keep-last 5
```

### 4. Session Hygiene

Clean up old sessions:

```bash
# Remove sessions older than 7 days
aish --cleanup-sessions --older-than 7d

# Remove all sessions for specific AI
aish --remove-sessions --ai apollo-ai
```

## Use Cases

### 1. Iterative Development

```bash
SESSION="feature-development"

# Initial design
echo "Design user authentication" | prometheus --session-id $SESSION

# Implementation
echo "Implement the design in Python" | apollo --session-id $SESSION

# Review
echo "Review the implementation" | athena --session-id $SESSION

# Refinement
echo "Address the review comments" | apollo --session-id $SESSION
```

### 2. Learning Sessions

```bash
# Tutorial session
aish --session hermes --session-id "learn-rust"

> Teach me Rust basics
hermes> I'll help you learn Rust! Let's start with...

> Show me variables and types
hermes> Building on what we just covered, variables in Rust...

> How does this relate to ownership?
hermes> Great question! Remember when I mentioned variables...
```

### 3. Debugging Sessions

```bash
# Debug session
DEBUG_SESSION="debug-memory-leak"

# Describe problem
echo "App has memory leak after 2 hours" | apollo --session-id $DEBUG_SESSION

# Provide code
echo "Here's the code: $(cat app.py)" | apollo --session-id $DEBUG_SESSION

# Interactive debugging
echo "Could it be the cache implementation?" | apollo --session-id $DEBUG_SESSION

# Get solution
echo "Provide the fix" | apollo --session-id $DEBUG_SESSION > fix.py
```

## Troubleshooting

### Session Not Found

```bash
# Check if session exists
aish --list-sessions | grep sess_abc123

# Restore from backup
aish --restore-session ~/.aish/sessions/backup/sess_abc123.json
```

### Context Limit Exceeded

```bash
# Increase context window
echo "Continue" | apollo --session sess_abc123 --extend-context 20

# Or prune old messages
aish --prune-session sess_abc123 --keep-recent 5
```

### Session Corruption

```bash
# Validate session
aish --validate-session sess_abc123

# Repair if possible
aish --repair-session sess_abc123

# Export valid parts
aish --export-session sess_abc123 --skip-corrupted
```

## Security Considerations

1. **Sessions may contain sensitive data** - Use appropriate storage
2. **Set expiration times** - Don't keep sessions forever
3. **Encrypt session storage** - Protect data at rest
4. **Audit session access** - Track who uses which sessions
5. **Clear sessions after use** - Don't leave sensitive context

## Future Features

Planned session enhancements:

- Multi-user shared sessions
- Session branching and merging
- Visual session history
- Session replay functionality
- Cross-platform session sync

Start using sessions today to have more meaningful, context-aware conversations with AI specialists!