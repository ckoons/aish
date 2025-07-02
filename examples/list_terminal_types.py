#!/usr/bin/env python3
"""
List all terminal types and show Tekton connection status
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_path))

from core.terminal_launcher import TerminalLauncher
from core.proxy_shell import TransparentAishProxy


def main():
    print("🖥️  Terminal Types & Tekton Connection Status")
    print("=" * 60)
    
    # Terminal detection
    print("\n📟 Available Terminal Types:")
    print("-" * 30)
    
    launcher = TerminalLauncher()
    
    # Show platform
    print(f"Platform: {launcher.platform}")
    print(f"\nDetected terminals:")
    
    for i, (app_id, display_name) in enumerate(launcher.available_terminals):
        is_default = " ⭐ DEFAULT" if app_id == launcher.get_default_terminal() else ""
        print(f"  {i+1}. {app_id:<20} - {display_name}{is_default}")
    
    # Terminal capabilities by platform
    print("\n📋 Terminal Capabilities:")
    print("-" * 30)
    
    if launcher.platform == "darwin":
        print("macOS terminals:")
        print("  • Terminal.app     - Native Apple terminal (AppleScript control)")
        print("  • iTerm2.app       - Advanced features, split panes")
        print("  • WarpPreview.app  - Modern AI-powered terminal")
        print("  • Alacritty.app    - GPU-accelerated performance")
    else:
        print("Linux terminals:")
        print("  • gnome-terminal   - GNOME default (most common)")
        print("  • konsole          - KDE terminal emulator")  
        print("  • xterm            - Classic X11 terminal (fallback)")
        print("  • alacritty        - Cross-platform GPU terminal")
    
    # Check Tekton connection
    print("\n🔗 Tekton Connection Status:")
    print("-" * 30)
    
    try:
        proxy = TransparentAishProxy(debug=False)
        
        print(f"Rhetor endpoint: {proxy.rhetor_endpoint}")
        
        # Try to discover AIs
        ais = proxy.registry.discover_ais(force_refresh=True)
        
        if ais:
            print(f"✅ Connected to Tekton!")
            print(f"   Found {len(ais)} AI specialists")
            
            # Show a few examples
            ai_names = sorted(set(ai['id'] for ai in ais.values()))[:5]
            print(f"   Examples: {', '.join(ai_names)}...")
        else:
            print("❌ No AI specialists found")
            print("   Is Rhetor running? (cd Tekton/Rhetor && ./run_rhetor.sh)")
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        print("   Check if Tekton services are running")
    
    # Show how terminals integrate with Tekton
    print("\n🚀 Terminal + Tekton Integration:")
    print("-" * 30)
    print("When you launch a terminal with aish-proxy:")
    print("  1. Native terminal opens (Terminal.app, gnome-terminal, etc.)")
    print("  2. aish-proxy runs as the shell")
    print("  3. Normal commands work as always (ls, git, npm, etc.)")
    print("  4. AI commands route to Tekton specialists:")
    print("     • echo 'analyze this' | apollo")
    print("     • team-chat 'ready to deploy?'")
    print("     • show me the error logs")
    
    print("\n✨ Ready to launch AI-enhanced terminals!")


if __name__ == "__main__":
    main()