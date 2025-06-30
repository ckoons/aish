# aish - The AI Shell

An interactive shell for orchestrating AI systems using Unix pipeline syntax.

## Overview

`aish` extends the Unix philosophy to AI orchestration. Just as `bash` pipes processes, `aish` pipes AI models:

```bash
$ echo "analyze this code" | apollo | athena | sophia > analysis.txt
```

## Quick Start

```bash
# Interactive mode
$ aish
aish> echo "Hello" | apollo
aish> team-chat "What should we build?"

# Script mode
$ aish script.ai

# One-liner
$ aish -c "echo 'test' | rhetor | apollo"
```

## Features

- **Unix Pipeline Syntax** - Familiar `|`, `>`, `<` operators
- **AI Process Management** - Create, pipe, and manage AI instances
- **Unified AI Interface** - Integrated with Tekton's AI registry and health monitoring
- **Team Chat** - Multi-AI collaboration built-in
- **Automatic Discovery** - AIs are discovered and monitored automatically

## Installation

```bash
git clone https://github.com/Tekton/aish.git
cd aish
./install.sh
```

## Documentation

See the `/docs` directory for detailed documentation:

### User Documentation
- [Getting Started](docs/getting-started.md) - Installation and first steps
- [Command Reference](docs/command-reference.md) - Complete command syntax
- [Pipeline Guide](docs/pipeline-guide.md) - Building AI pipelines
- [Architecture](docs/architecture/) - System design and concepts

### Advanced Features
- [Session Management](docs/sessions.md) - Stateful conversations
- [Streaming Guide](docs/streaming.md) - Real-time AI responses
- [API Reference](docs/api/) - Programming interfaces

### Development
- [Development Guide](docs/development/) - Contributing guidelines
- [Unified AI Interface](docs/api/unified_ai_interface.md) - AI communication system
- [Sprint Planning](docs/sprints/) - Current development sprints

## Examples

```bash
# Parallel AI processing
echo "problem" | tee >(apollo > pred.txt) >(athena > know.txt) | wait

# AI pipeline with context
cat context.txt | rhetor | team-chat "solve this"

# Remote AI execution
echo "analyze" | ssh server1 apollo
```

## Philosophy

AIs are just sockets. They read input, write output. Nothing more.

## Integration with Tekton

aish now uses Tekton's Unified AI Interface for robust AI discovery and communication. This provides:
- Automatic health monitoring of AI specialists
- Performance tracking and smart routing
- Seamless fallback handling
- Future streaming support

See [Unified AI Interface](docs/api/unified_ai_interface.md) for details.

## License

MIT License - See LICENSE file for details.