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
- **Distributed Execution** - Run AIs across multiple machines
- **Team Chat** - Multi-AI collaboration built-in
- **Socket-Based** - Everything is a file descriptor

## Installation

```bash
git clone https://github.com/Tekton/aish.git
cd aish
./install.sh
```

## Documentation

See the `/docs` directory for detailed documentation:
- [Architecture](docs/architecture/) - System design and concepts
- [API Reference](docs/api/) - Programming interfaces
- [Tutorials](docs/tutorials/) - Getting started guides
- [Development](docs/development/) - Contributing guidelines

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

## License

MIT License - See LICENSE file for details.