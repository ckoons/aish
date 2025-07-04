# Handoff: aish-Tekton Integration Sprint

**Date**: July 2, 2025  
**Current Claude**: Completed aish implementation  
**Next Claude**: Tekton integration specialist  
**Casey**: Overseeing integration, handling GitHub

## Sprint Status: Day 1 Complete ✅

### What We Accomplished Today

1. **Redesigned aish Architecture** 
   - Abandoned PTY manipulation (caused terminal corruption)
   - Implemented safe shell hook approach
   - Single command pattern: `aish` is the universal escape

2. **Working aish Implementation**
   ```bash
   # All these work now:
   aish apollo "question"          # Direct AI command
   echo "data" | aish athena      # Piped input
   aish team-chat "message"       # Team broadcast
   aish                           # Interactive shell
   ```

3. **Clean Documentation**
   - Architecture documented
   - Design decisions captured (including failures)
   - Implementation plan created
   - User guide updated

## For the New Claude: Your Mission

### Context You Need
1. **Read these first**:
   - `/Users/cskoons/projects/github/aish/docs/ARCHITECTURE.md`
   - `/Users/cskoons/projects/github/aish/docs/DESIGN_DECISIONS.md`
   - The original sprint plan in this directory

2. **Key Design Decision**: 
   - `aish` is the ONLY command we create
   - No namespace pollution (no "apollo", "athena" commands)
   - Shell does all parsing, we just route to AIs

3. **Casey's Guidance**:
   - He has terminal emulator expertise (built and sold them)
   - Prefers simple, working solutions over complex experiments
   - Will handle GitHub commits - don't touch git
   - Ask questions when you have alternatives

### Your Tekton Integration Tasks

#### 1. Move aish to Tekton/shared/aish
```bash
# Target structure:
Tekton/shared/aish/
├── aish              # Main command (copy from aish project)
├── aish-proxy        # Shell enhancer (copy from aish project)
├── aish-history      # History tool (copy from aish project)
├── src/              # Python package (copy from aish project)
├── requirements.txt  # Dependencies
└── README.md         # Integration notes
```

**Important**: Update import paths and PATH references after moving

#### 2. Update Terma Terminal Launcher

Current issue in `/Tekton/Terma/terma/core/terminal_launcher_impl.py`:
```python
# Line 74-86: Hardcoded paths to find aish-proxy
locations = [
    Path.home() / "projects" / "github" / "aish" / "aish-proxy",
    # ... other hardcoded paths
]
```

Change to:
```python
locations = [
    Path(__file__).parent.parent.parent.parent.parent / "shared" / "aish" / "aish-proxy",
    shutil.which("aish-proxy"),  # System PATH
]
```

#### 3. Fix Terminal Launch Behavior

Current: Terminals launch in hardcoded directory  
Need: Launch in user's home directory with their shell

Update in terminal launcher:
- Use `os.path.expanduser("~")` for working directory
- Detect user's shell from `$SHELL` environment variable
- Pass shell preference to aish-proxy

#### 4. Add MCP Endpoint for Terminal Launching

In `/Tekton/Terma/terma/api/fastmcp_endpoints.py`, add:
```python
@mcp_router.post("/tools/launch_terminal")
async def mcp_launch_terminal(request: dict):
    """Launch a terminal with aish integration."""
    # Implementation details in original handoff doc
```

#### 5. Test Integration

1. Launch terminal via Terma UI
2. Verify `aish` command is available
3. Test AI routing works
4. Confirm clean exit

### Architecture Context

**aish side** (this Claude completed):
- Thin client that routes to Tekton
- Uses `aish` as single command
- Safe shell integration

**Tekton side** (your work):
- Terma manages terminal lifecycle
- aish registers as Terma terminal instance
- Bidirectional communication planned
- MCP endpoints for external control

### Key Files You'll Work With

1. **Copy these from aish to Tekton**:
   - `/aish/aish` → `/Tekton/shared/aish/aish`
   - `/aish/aish-proxy` → `/Tekton/shared/aish/aish-proxy`
   - `/aish/src/` → `/Tekton/shared/aish/src/`

2. **Modify in Tekton**:
   - `/Tekton/Terma/terma/core/terminal_launcher_impl.py`
   - `/Tekton/Terma/terma/api/app.py` (if needed)
   - `/Tekton/Terma/terma/api/fastmcp_endpoints.py`

3. **Test via**:
   - Hephaestus UI: http://localhost:8080
   - Navigate to Terma component
   - Click "Launch Terminal"

### Communication Plan

- Casey will coordinate between Claudes
- The current Claude (me) will answer questions about aish design
- You focus on Tekton integration
- Ask before making major changes

### Success Criteria

✅ aish files moved to Tekton/shared/aish  
✅ Terminal launcher finds aish-proxy in new location  
✅ Terminals launch with user's preferences  
✅ MCP endpoint works  
✅ UI can launch aish-enabled terminals  
✅ No terminal corruption!

## Important Notes

1. **Terminal Safety**: We spent hours fixing terminal corruption. The current approach is safe - don't change to PTY manipulation!

2. **Single Command**: `aish` is the only command. This was a deliberate decision after much discussion.

3. **Test Carefully**: Always have a kill command ready if testing terminals:
   ```bash
   ps aux | grep aish | grep -v grep | awk '{print $2}' | xargs kill -9
   ```

4. **Casey's Workflow**: He reviews everything before committing. Don't use git commands.

Good luck! The aish side is solid, now we need clean Tekton integration.

---
Current Claude available for aish questions  
Casey coordinating the integration