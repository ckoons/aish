# aish Quick Reference

## Basic Commands

```bash
# Send text to AI
echo "message" | ai_name

# Chain AIs
ai1 | ai2 | ai3

# Team chat
team-chat "message to all"

# Redirect output
ai_name > file.txt
ai_name >> file.txt  # append

# Read input
ai_name < file.txt

# Background execution (future)
ai_name &
```

## Built-in Commands

```bash
help              # Show help
exit              # Exit aish
!command          # Run shell command
ps -ai            # List AI sockets (future)
kill socket_id    # Terminate AI (future)
reset socket_id   # Reset AI context (future)
```

## Pipeline Examples

### Simple Query
```bash
echo "What is quantum computing?" | athena
```

### Multi-Stage Analysis
```bash
cat document.txt | athena | apollo | sophia > analysis.txt
```

### Parallel Processing
```bash
echo "problem" | tee >(apollo > pred.txt) >(athena > know.txt) | wait
```

### Team Consultation
```bash
team-chat "How should we architect this system?"
```

### Context Injection
```bash
cat context.txt requirements.txt | rhetor | synthesis
```

## AI Names (Tekton Components)

| AI Name | Purpose |
|---------|---------|
| apollo | Prediction & attention |
| athena | Knowledge & analysis |
| sophia | Learning & patterns |
| rhetor | LLM orchestration |
| hermes | Messaging & data |
| prometheus | Planning & strategy |
| ergon | Agent systems |
| synthesis | Code generation |

## Special Sockets

| Socket | Purpose |
|--------|---------|
| team-chat-all | Broadcast to all AIs |
| rhetor | Rhetor's listening socket |

## Headers (Automatic)

| Header | Purpose |
|--------|---------|
| [team-chat-from-X] | Source identification |
| [team-chat-to-Y] | Destination routing |
| [urgent] | Priority message |
| [error] | Error output |

## Configuration

### .aishrc file
```bash
# Aliases
alias think="apollo | athena | rhetor"
alias review="sophia | synthesis"

# Settings
export RHETOR_ENDPOINT="http://localhost:8300"
export AISH_DEBUG=1
```

## Tips

1. Use `|` liberally - it's the core of aish
2. Simple commands are often best
3. Let AIs decide who should answer (team-chat)
4. Everything is text until proven otherwise
5. When in doubt, pipe it through rhetor