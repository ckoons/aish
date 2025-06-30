# Conversation History

aish maintains a comprehensive history of your AI conversations, making it easy to track, search, and replay previous interactions.

## Overview

Every command and AI response is automatically recorded in two formats:
- **Text format** (`~/.aish_history`) - Human-readable, Unix-style history
- **JSON format** (`~/.aish/sessions/YYYY-MM-DD.json`) - Machine-parseable, detailed records

## Using History in aish

### View Recent History
```bash
aish> history
```
Shows the last 20 commands and responses.

### Replay Commands
```bash
aish> !1716
```
Replays command number 1716 from history.

### Example Session
```bash
aish> echo "What is wisdom?" | athena
[Response from Athena about wisdom...]

aish> echo "How do we apply wisdom?" | athena | apollo
[Athena's response processed by Apollo...]

aish> history
Recent conversation history:
------------------------------------------------------------
1: echo "What is wisdom?" | athena
   # athena: Wisdom is the quality of having experience, knowledge...
2: echo "How do we apply wisdom?" | athena | apollo
   # athena: We apply wisdom through careful consideration...
   # apollo: Building on Athena's insights, practical wisdom...
------------------------------------------------------------

aish> !1
Replaying: echo "What is wisdom?" | athena
[Response from Athena...]
```

## Using aish-history Command

Outside of the aish shell, use the `aish-history` command for advanced history management.

### Basic Usage
```bash
# View recent history (last 20 entries)
aish-history

# View last 50 entries
aish-history -n 50

# View all history
aish-history -n 0
```

### Search History
```bash
# Search for all interactions with Apollo
aish-history --search "apollo"

# Search for specific topics
aish-history --search "optimization"
```

### Replay Commands
```bash
# Get command for replay
aish-history --replay 1716

# Use in a script
COMMAND=$(aish-history --replay 1716)
aish -c "$COMMAND"
```

### JSON Export
```bash
# Export all history as JSON
aish-history --json

# Export with jq processing
aish-history --json | jq '.history[-5:]'  # Last 5 commands

# Export range
aish-history --json --start 100 --end 200

# Extract just commands
aish-history --json | jq -r '.history[].command'

# Find longest responses
aish-history --json | jq '.history | max_by(.responses | to_entries | .[].value | length)'
```

## History Format

### Text Format
```
1716: echo "what day was yesterday?" | numa
      # numa: Sunday June 29, 2025
1717: echo "analyze this code" | apollo | athena  
      # apollo: Code has 3 main functions...
      # athena: Architectural patterns suggest...
1718: team-chat "should we refactor?"
      # numa: Resource usage is optimal
      # apollo: Code clarity could improve
      # athena: Consider SOLID principles
```

### JSON Format
```json
{
  "session": "2025-06-30T10:30:00",
  "entries": [
    {
      "number": 1716,
      "timestamp": 1719750600.123,
      "command": "echo \"what day was yesterday?\" | numa",
      "responses": {
        "numa": "Sunday June 29, 2025"
      }
    }
  ]
}
```

## Configuration

### History Location
- Text history: `~/.aish_history`
- JSON sessions: `~/.aish/sessions/YYYY-MM-DD.json`

### Clear History
```bash
# Clear history (backs up to .aish_history.bak)
aish-history --clear
```

## Integration with Unix Tools

### Using with grep
```bash
# Find all team-chat commands
grep "team-chat" ~/.aish_history

# Find Apollo's responses about optimization
grep -A1 "apollo" ~/.aish_history | grep -i "optim"
```

### Using with awk
```bash
# Extract just command numbers and commands
awk -F: '/^[0-9]+:/ {print $1 ": " $2}' ~/.aish_history

# Count interactions per AI
awk -F: '/^      #/ {print $1}' ~/.aish_history | sed 's/.*# //' | sort | uniq -c
```

### Creating Workflows
```bash
# Save useful commands to a workflow
aish-history --search "successful" | grep "^[0-9]" > useful_commands.ai

# Replay a series of commands
for cmd in 1716 1720 1725; do
    aish -c "$(aish-history --replay $cmd)"
done
```

## Best Practices

1. **Regular Exports**: Periodically export JSON for long-term storage
   ```bash
   aish-history --json | gzip > aish_history_$(date +%Y%m%d).json.gz
   ```

2. **Search Before Asking**: Check if you've asked similar questions
   ```bash
   aish-history --search "error handling"
   ```

3. **Build Command Libraries**: Save useful pipelines
   ```bash
   aish-history --json | jq -r '.history[] | select(.responses | length > 2) | .command' > multi_ai_commands.txt
   ```

4. **Track AI Performance**: Analyze response patterns
   ```bash
   aish-history --json | jq '.history[].responses | keys[]' | sort | uniq -c | sort -nr
   ```

## Privacy Notes

- History is stored locally in your home directory
- No history is sent to external services
- Clear sensitive conversations with `aish-history --clear`
- JSON files can be encrypted if needed

## Troubleshooting

### History Not Recording
- Check file permissions on `~/.aish_history`
- Ensure `~/.aish/sessions/` directory exists
- Verify disk space is available

### Replay Not Working
- Ensure command number exists: `aish-history | grep "^NUMBER:"`
- Check for special characters that need escaping

### JSON Export Issues
- Verify session files exist in `~/.aish/sessions/`
- Check for corrupted JSON with `jq` validation