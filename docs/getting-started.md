# Getting Started with aish

Welcome to aish - The AI Shell! This guide will help you get up and running quickly.

## Installation

### Prerequisites
- Python 3.8 or higher
- Tekton platform running locally or accessible remotely
- Network access to AI services (Rhetor on port 8003)

### Quick Install

1. **Clone the repository**
   ```bash
   git clone https://github.com/cskoons/aish.git
   cd aish
   ```

2. **Create a symlink in your PATH**
   ```bash
   ln -s $(pwd)/aish ~/utils/aish
   # Or add to /usr/local/bin if you prefer
   sudo ln -s $(pwd)/aish /usr/local/bin/aish
   ```

3. **Verify installation**
   ```bash
   aish --version
   aish --help
   ```

## First Steps

### 1. Check Available AIs

List all available AI specialists:

```bash
aish -l
# or
aish --list-ais
```

You should see a list like:
```
Available AI Specialists (18):
------------------------------------------------------------
Active:
  apollo-ai     - code-analysis, static-analysis, metrics
  athena-ai     - knowledge-synthesis, query-resolution
  hermes-ai     - messaging, communication
  ...
```

### 2. Your First AI Command

Send a simple message to an AI:

```bash
aish -c 'echo "Hello, AI!" | apollo'
```

### 3. Interactive Mode

Start an interactive session:

```bash
aish
aish> echo "What is Python?" | athena
aish> help
aish> exit
```

## Basic Concepts

### AI Pipelines

aish treats AIs like Unix commands that can be piped together:

```bash
# Single AI
echo "Analyze this code: def add(a,b): return a+b" | apollo

# Chain multiple AIs
echo "Plan a web app" | prometheus | apollo | athena > plan.md

# Save output
echo "Explain quantum computing" | athena > quantum.txt
```

### Team Chat

Broadcast a message to all available AIs:

```bash
aish -c 'team-chat "What are the best practices for error handling?"'
```

### Input Methods

1. **Echo pipeline**
   ```bash
   echo "Your message" | ai-name
   ```

2. **File input**
   ```bash
   cat code.py | apollo
   ```

3. **Direct command**
   ```bash
   aish -c 'apollo < input.txt'
   ```

## Configuration

### Environment Variables

- `TEKTON_RHETOR_PORT`: Rhetor service port (default: 8003)
- `TEKTON_RHETOR_HOST`: Rhetor service host (default: localhost)
- `AISH_DEBUG`: Enable debug output (set to 1)

### Configuration File

Create `~/.aishrc` for persistent settings:

```bash
# ~/.aishrc
export TEKTON_RHETOR_PORT=8003
export AISH_DEBUG=0

# Aliases for common pipelines
alias code-review='apollo | athena'
alias plan='prometheus | telos'
```

## Common Use Cases

### 1. Code Review
```bash
cat mycode.py | apollo | athena > review.md
```

### 2. Documentation Generation
```bash
echo "Document this API endpoint: POST /users" | hermes > api-docs.md
```

### 3. Problem Solving
```bash
echo "How do I optimize database queries?" | @optimization > tips.md
```

### 4. Interactive Development
```bash
aish
aish> echo "Design a REST API for a todo app" | prometheus
aish> # Copy the output, refine it
aish> echo "Add authentication to: [previous output]" | apollo
```

## Troubleshooting

### Connection Issues

If you get connection errors:

1. **Check Rhetor is running**
   ```bash
   curl http://localhost:8003/health
   ```

2. **Verify AI discovery**
   ```bash
   ai-discover list
   ```

3. **Enable debug mode**
   ```bash
   aish -d -c 'echo "test" | apollo'
   ```

### No AI Response

If an AI doesn't respond:

1. Check if the AI is active: `aish -l`
2. Try a different AI
3. Use team-chat to find available AIs
4. Check the Tekton logs

### Performance Issues

For slow responses:

1. Use streaming mode (when available): `--stream`
2. Try bulk operations for multiple AIs
3. Check network latency to Rhetor

## Next Steps

Now that you're up and running:

1. Read the [Command Reference](./command-reference.md) for all available commands
2. Learn about [Building Pipelines](./pipeline-guide.md)
3. Explore [Advanced Features](./sessions.md) like sessions
4. Try the [examples](../examples/) directory

## Getting Help

- **Built-in help**: Type `help` in aish
- **Command help**: `aish --help`
- **Debug mode**: `aish -d` for verbose output
- **GitHub Issues**: Report bugs or request features

Welcome to the future of AI orchestration!