#!/usr/bin/env python3
"""
Demo script to show the transparent proxy in action
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_path))

from core.proxy_shell import TransparentAishProxy


def demo_command_routing():
    """Demonstrate how commands are routed."""
    print("🚀 aish Transparent Proxy Demo")
    print("=" * 50)
    
    proxy = TransparentAishProxy(debug=False)  # Less verbose for demo
    
    demo_commands = [
        # Shell commands (pass through)
        ('ls -la | head -5', '📁 Shell: List directory'),
        ('echo "Hello, World!"', '📁 Shell: Echo command'),
        ('pwd', '📁 Shell: Print working directory'),
        
        # AI commands (intercept)
        ('echo "analyze this code" | apollo', '🤖 AI: Pipeline to Apollo'),
        ('team-chat "what should we build?"', '🤖 AI: Team chat'),
        ('show me the git log', '🤖 AI: Natural language'),
        ('how do I fix this error?', '🤖 AI: Question'),
        
        # Built-in commands
        ('aish-status', '⚙️  Built-in: Show status'),
    ]
    
    for command, description in demo_commands:
        print(f"\n{description}")
        print(f"Command: {command}")
        print("-" * 30)
        
        try:
            exit_code = proxy.run_single_command(command)
            print(f"Exit code: {exit_code}")
        except Exception as e:
            print(f"Error: {e}")
        
        print()
    
    print("=" * 50)
    print("✅ Demo complete!")
    print("\nThe proxy successfully:")
    print("  • Passes shell commands through transparently")
    print("  • Intercepts AI commands for processing")
    print("  • Handles built-in aish commands")
    print("  • Maintains full shell compatibility")
    print("\n🎯 Ready for terminal integration!")


if __name__ == "__main__":
    demo_command_routing()