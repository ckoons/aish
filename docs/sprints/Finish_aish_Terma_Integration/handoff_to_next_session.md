# Handoff: Terma Integration Sprint - Current State & Next Steps

**Date**: July 1, 2025
**Previous Session**: Casey & Claude - Terma Replacement Implementation
**Next Session Goal**: Complete Terma frontend-backend integration and finalize aish-proxy setup

## Current State Summary

### What We've Accomplished

1. **Complete Terma Replacement** ✅
   - Removed all old PTY/WebSocket terminal code from `app.py`
   - Added native terminal endpoints to `app.py` from `terminal_service.py`
   - Terma now launches native terminals (Terminal.app, iTerm2, Warp)
   - API endpoints working: `/api/terminals/launch`, `/api/terminals/types`, etc.

2. **UI Integration** ✅
   - Added Dashboard and Launch Terminal tabs to Terma component
   - Launch button sends POST to `/api/terminals/launch`
   - Fixed CSS tab switching
   - Removed legacy JavaScript special handling for Terma

3. **Made Terma Launch Without aish-proxy** ✅
   - Modified `terminal_launcher_impl.py` to gracefully handle missing aish-proxy
   - Falls back to regular shell (bash/zsh) when aish-proxy not found
   - Shows status "running (without aish-proxy)" in API response

### Current Issues

1. **aish-proxy Location**
   - Currently in `/Users/cskoons/projects/github/aish/aish-proxy`
   - Needs to move to `/Users/cskoons/projects/github/Tekton/shared/aish/`
   - Terminal launcher looks for it with hardcoded paths

2. **Terminal Launch Behavior**
   - Terminals launch in `/Users/cskoons/projects` (hardcoded)
   - Should launch in user's home directory
   - Doesn't preserve user's shell preferences

3. **Frontend-Backend Integration**
   - Launch button works but needs refinement
   - Dashboard doesn't auto-refresh to show new terminals
   - No MCP endpoint for terminal launching yet

## Next Steps for Completion

### 1. Move aish-proxy to Tekton/shared/aish

```bash
# Create the shared directory
mkdir -p /Users/cskoons/projects/github/Tekton/shared/aish

# Move aish-proxy and related files
mv /Users/cskoons/projects/github/aish/aish-proxy /Users/cskoons/projects/github/Tekton/shared/aish/
mv /Users/cskoons/projects/github/aish/src/core/proxy_shell.py /Users/cskoons/projects/github/Tekton/shared/aish/

# Update imports in aish-proxy to find proxy_shell.py in new location
```

### 2. Update Terminal Launcher Paths

In `/Users/cskoons/projects/github/Tekton/Terma/terma/core/terminal_launcher_impl.py`:

```python
def _find_aish_proxy(self) -> str:
    """Find the aish-proxy executable."""
    locations = [
        # Add Tekton shared location first
        Path(__file__).parent.parent.parent.parent.parent / "shared" / "aish" / "aish-proxy",
        # Remove hardcoded home paths
        shutil.which("aish-proxy"),  # System PATH
    ]
```

### 3. Fix Terminal Launch Behavior

Update `launch_terminal` request in UI to use proper defaults:

```javascript
body: JSON.stringify({
    app: terminalType,
    template: shellType === 'aish' ? 'aish-dev' : null,
    working_dir: null,  // Let backend use user's home
    env: {
        "SHELL": null  // Let backend detect user's shell
    }
})
```

Update backend to:
- Use `os.path.expanduser("~")` for working_dir if not specified
- Detect user's shell from `os.environ.get('SHELL', '/bin/bash')`
- Pass user's shell to aish-proxy so it can wrap it

### 4. Add MCP Endpoint

In `/Users/cskoons/projects/github/Tekton/Terma/terma/api/app.py`, add to MCP router:

```python
@mcp_router.post("/tools/launch_terminal")
async def mcp_launch_terminal(request: dict):
    """MCP tool for launching terminals."""
    # Convert MCP request to LaunchTerminalRequest
    # Call existing launch_terminal function
    # Return MCP-formatted response
```

### 5. Frontend Polish

- Add auto-refresh to Dashboard when switching tabs
- Show better status messages during launch
- Add error handling for when Terma service is down
- Consider adding a "Copy aish command" button for manual terminal launch

## Key Files to Work With

### Backend (Tekton)
- `/Tekton/Terma/terma/api/app.py` - Main API with terminal endpoints
- `/Tekton/Terma/terma/core/terminal_launcher_impl.py` - Terminal launching logic
- `/Tekton/Terma/terma/api/fastmcp_endpoints.py` - Add MCP tool here

### Frontend (Hephaestus)
- `/Tekton/Hephaestus/ui/components/terma/terma-component.html` - UI component

### aish-proxy (to be moved)
- `/aish/aish-proxy` - Shell wrapper executable
- `/aish/src/core/proxy_shell.py` - Proxy implementation

## Testing Steps

1. **Test aish-proxy after move**:
   ```bash
   cd /Tekton/shared/aish
   ./aish-proxy  # Should start interactive shell
   ```

2. **Test terminal launch with proper directory**:
   ```bash
   curl -X POST http://localhost:8004/api/terminals/launch \
     -H "Content-Type: application/json" \
     -d '{"working_dir": null}'
   # Should open in user's home directory
   ```

3. **Test MCP endpoint**:
   ```bash
   curl -X POST http://localhost:8004/api/mcp/v2/tools/launch_terminal \
     -H "Content-Type: application/json" \
     -d '{"purpose": "Development work"}'
   ```

## Questions/Considerations for Casey

1. **Shell Detection**: Should we use `$SHELL` environment variable or check user's `/etc/passwd` entry?

2. **aish-proxy Arguments**: What arguments should aish-proxy accept to wrap the user's shell properly?

3. **Terminal Templates**: Should templates override the user's shell or just set environment variables?

4. **MCP Tool Name**: Is `launch_terminal` the right name for the MCP tool, or should it be more specific?

5. **Installation**: Should we create a setup script that symlinks aish-proxy to `/usr/local/bin`?

## Cleanup Tasks (Low Priority)

In `/Users/cskoons/projects/github/aish/`:
- Delete `examples/terma_integration_demo.py` (outdated)
- Delete `src/terma_service.py` (duplicate of Tekton version)
- Move `tests/test_terma_v2_api.py` to `/Tekton/Terma/tests/`

---

## Session Summary for Next Claude

You're picking up after we successfully replaced Terma's web terminals with native terminal launching. The system works but needs polish:

1. **Move aish-proxy** from aish project to Tekton/shared/aish
2. **Fix paths** in terminal launcher to find aish-proxy in new location  
3. **Improve launch behavior** - use user's home dir and shell preferences
4. **Add MCP endpoint** for AI tools to launch terminals
5. **Polish the UI** - auto-refresh, better error handling

The architecture is solid, just needs these finishing touches to be production-ready. Casey wants terminals to feel native - launching in the right directory with the user's normal shell environment, just enhanced with AI capabilities through aish-proxy.

Good luck! 🚀