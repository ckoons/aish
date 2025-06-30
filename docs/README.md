# aish Documentation

Welcome to the aish documentation. This directory contains comprehensive documentation for the AI Shell.

## Recent Updates (June 2025)

### Phase 1 Complete: Socket Communication Improvements
- **Line-buffered sockets** - Fixed message truncation issues
- **Intelligent timeouts** - Distinguish network vs processing delays  
- **Dynamic discovery** - No more hardcoded ports, uses `ai-discover`
- **MCP integration** - Unified communication with Tekton platform

See [Phase 1 Documentation](development/phase1_socket_improvements.md) for details.

## Documentation Structure

### [Architecture](architecture/)
- System design and core concepts
- Socket management model
- Pipeline execution engine
- Integration with Rhetor/Tekton

### [API Reference](api/)
- [Socket Communication API](api/socket_communication.md) - NEW
- [MCP Integration](api/mcp_integration.md) - NEW
- Python API documentation
- Shell command reference
- Configuration options
- Extension interfaces

### [Tutorials](tutorials/)
- Getting started guide
- Basic pipeline examples
- Advanced orchestration patterns
- Integration with existing tools

### [Reference](reference/)
- Complete command reference
- Pipeline syntax specification
- Configuration file formats
- Troubleshooting guide

### [Development](development/)
- [Phase 1 Socket Improvements](development/phase1_socket_improvements.md) - NEW
- [Claude Handoff Guide](CLAUDE_HANDOFF.md) - NEW
- Contributing guidelines
- Development setup
- Testing procedures
- Release process

## Quick Links

- [Installation Guide](tutorials/installation.md)
- [Your First AI Pipeline](tutorials/first-pipeline.md)
- [Command Reference](reference/commands.md)
- [API Documentation](api/python-api.md)

## Philosophy

aish embodies the Unix philosophy for AI orchestration:
- Everything is a socket
- Small, composable tools
- Text streams as universal interface
- Simple syntax, powerful capabilities