#!/usr/bin/env python3
"""
Test script for Terminal Launcher
Verifies platform detection, terminal discovery, and launch capabilities.
"""

import sys
import os
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_path))

from core.terminal_launcher import TerminalLauncher, TerminalConfig, TerminalTemplates


def test_platform_detection():
    """Test that platform and terminal detection works."""
    print("=== Testing Platform & Terminal Detection ===")
    
    try:
        launcher = TerminalLauncher()
        
        print(f"Platform detected: {launcher.platform}")
        print(f"aish-proxy path: {launcher.aish_path}")
        print(f"\nAvailable terminals ({len(launcher.available_terminals)}):")
        
        for app_id, display_name in launcher.available_terminals:
            default = " [DEFAULT]" if app_id == launcher.get_default_terminal() else ""
            print(f"  • {app_id:<20} - {display_name}{default}")
        
        print(f"\nDefault terminal: {launcher.get_default_terminal()}")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_terminal_templates():
    """Test terminal configuration templates."""
    print("\n=== Testing Terminal Templates ===")
    
    templates = ["default", "development", "ai_workspace", "data_science"]
    
    for template_name in templates:
        template = TerminalTemplates.get_template(template_name)
        if template:
            print(f"\nTemplate: {template_name}")
            print(f"  Name: {template.name}")
            print(f"  Working dir: {template.working_dir or '(current)'}")
            print(f"  Purpose: {template.purpose or '(none)'}")
            print(f"  Environment:")
            for k, v in template.env.items():
                print(f"    {k} = {v}")
        else:
            print(f"\nTemplate '{template_name}' not found!")
    
    return True


def test_launch_simulation():
    """Test launch configuration (without actually launching)."""
    print("\n=== Testing Launch Configuration ===")
    
    try:
        launcher = TerminalLauncher()
        
        # Test different configurations
        configs = [
            TerminalConfig(name="Test 1"),
            TerminalConfig(name="Test 2", working_dir="/tmp"),
            TerminalConfig(name="Test 3", purpose="AI development session"),
            TerminalTemplates.get_template("ai_workspace"),
        ]
        
        for i, config in enumerate(configs):
            if config:
                print(f"\nConfiguration {i + 1}:")
                print(f"  Name: {config.name}")
                print(f"  App: {config.app or launcher.get_default_terminal()}")
                print(f"  Working dir: {config.working_dir or os.getcwd()}")
                print(f"  Purpose: {config.purpose or '(none)'}")
                
                # Show what command would be built (simplified)
                aish_cmd = launcher.aish_path
                if config.shell_args:
                    aish_cmd += " " + " ".join(config.shell_args)
                print(f"  Shell command: {aish_cmd}")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False


def interactive_test():
    """Interactive test to actually launch a terminal."""
    print("\n=== Interactive Terminal Launch Test ===")
    print("This will actually launch a terminal window.")
    
    response = input("\nDo you want to launch a test terminal? [y/N] ")
    if response.lower() != 'y':
        print("Skipping interactive test")
        return
    
    try:
        launcher = TerminalLauncher()
        
        # Show options
        print("\nSelect terminal to launch:")
        print("0. Default terminal")
        for i, (app_id, display_name) in enumerate(launcher.available_terminals):
            print(f"{i + 1}. {display_name}")
        
        choice = input("\nChoice [0]: ").strip() or "0"
        
        config = TerminalConfig()
        if choice != "0":
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(launcher.available_terminals):
                    config.app = launcher.available_terminals[idx][0]
            except ValueError:
                pass
        
        # Add some context
        config.purpose = "aish terminal launcher test"
        config.env["AISH_TEST"] = "true"
        
        print(f"\nLaunching {config.app or launcher.get_default_terminal()}...")
        pid = launcher.launch_terminal(config)
        
        print(f"✅ Terminal launched with PID: {pid}")
        
        # Show how to manage it
        print("\nManagement commands:")
        print(f"  Show terminal:      python -m core.terminal_launcher show --pid {pid}")
        print(f"  Terminate terminal: python -m core.terminal_launcher terminate --pid {pid}")
        print(f"  List terminals:     python -m core.terminal_launcher list")
        
    except Exception as e:
        print(f"❌ Launch failed: {e}")


def main():
    """Run all tests."""
    print("Terminal Launcher Test Suite")
    print("=" * 50)
    
    # Run tests
    tests_passed = 0
    tests_total = 3
    
    if test_platform_detection():
        tests_passed += 1
    
    if test_terminal_templates():
        tests_passed += 1
    
    if test_launch_simulation():
        tests_passed += 1
    
    print("\n" + "=" * 50)
    print(f"Tests passed: {tests_passed}/{tests_total}")
    
    if tests_passed == tests_total:
        print("✅ All tests passed!")
        
        # Offer interactive test
        interactive_test()
    else:
        print("❌ Some tests failed")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())