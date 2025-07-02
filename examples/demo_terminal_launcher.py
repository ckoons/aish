#!/usr/bin/env python3
"""
Demo of Terminal Launcher capabilities
Shows how native terminals can be launched with AI enhancement.
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_path))

from core.terminal_launcher import TerminalLauncher, TerminalConfig, TerminalTemplates


def demo_launcher_capabilities():
    """Demonstrate the terminal launcher features."""
    print("🚀 Terminal Launcher Demo")
    print("=" * 50)
    
    # Initialize launcher
    launcher = TerminalLauncher()
    
    print(f"Platform: {launcher.platform}")
    print(f"Default terminal: {launcher.get_default_terminal()}")
    print()
    
    # Show what would happen with different launches
    print("Launch Scenarios:")
    print("-" * 30)
    
    # Scenario 1: Default launch
    print("\n1. Default Terminal Launch")
    config = TerminalConfig()
    print(f"   Would launch: {launcher.get_default_terminal()}")
    print(f"   Shell: {launcher.aish_path}")
    print(f"   Directory: {config.working_dir or 'current'}")
    
    # Scenario 2: Development template
    print("\n2. Development Template")
    dev_config = TerminalTemplates.get_template("development")
    if dev_config:
        print(f"   Would launch: {launcher.get_default_terminal()}")
        print(f"   Purpose: Development Terminal")
        print(f"   Directory: {dev_config.working_dir}")
        print(f"   Environment:")
        for k, v in dev_config.env.items():
            print(f"     {k}={v}")
    
    # Scenario 3: AI Workspace
    print("\n3. AI Workspace Template")
    ai_config = TerminalTemplates.get_template("ai_workspace")
    if ai_config:
        print(f"   Would launch: {launcher.get_default_terminal()}")
        print(f"   Purpose: {ai_config.purpose}")
        print(f"   Special env: TEKTON_AI_WORKSPACE=true")
    
    # Scenario 4: Custom configuration
    print("\n4. Custom Configuration")
    custom = TerminalConfig(
        name="API Debug Terminal",
        purpose="Debug the Tekton API server",
        working_dir="/tmp",
        env={
            "DEBUG": "true",
            "LOG_LEVEL": "verbose"
        }
    )
    print(f"   Would launch: {launcher.get_default_terminal()}")
    print(f"   Purpose: {custom.purpose}")
    print(f"   Directory: {custom.working_dir}")
    print(f"   Debug mode: enabled")
    
    print("\n" + "=" * 50)
    print("✅ Terminal launcher ready!")
    print("\nThe launcher can:")
    print("  • Detect and use available terminals")
    print("  • Launch with aish-proxy for AI enhancement")
    print("  • Apply configuration templates")
    print("  • Pass context to AI system")
    print("  • Track terminals by PID")
    
    print("\n🎯 Next: Integration with Tekton as Terma service")


def show_command_examples():
    """Show example commands."""
    print("\n📝 Example Commands:")
    print("-" * 30)
    
    commands = [
        ("List terminals", "./aish-terminal terminals"),
        ("Launch default", "./aish-terminal launch"),
        ("Launch with template", "./aish-terminal launch --template development"),
        ("Launch with purpose", './aish-terminal launch --purpose "Fix bug #123"'),
        ("Launch specific app", "./aish-terminal launch --app Terminal.app"),
    ]
    
    for desc, cmd in commands:
        print(f"\n{desc}:")
        print(f"  $ {cmd}")


if __name__ == "__main__":
    demo_launcher_capabilities()
    show_command_examples()