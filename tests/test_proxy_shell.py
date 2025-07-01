#!/usr/bin/env python3
"""
Test script for aish Transparent Proxy
Verifies that the proxy correctly routes commands between AI and shell.
"""

import sys
import os
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_path))

from core.proxy_shell import TransparentAishProxy


def test_command_detection():
    """Test that AI vs shell command detection works correctly."""
    print("=== Testing Command Detection ===")
    
    proxy = TransparentAishProxy(debug=True)
    
    # Test cases: (command, should_be_ai)
    test_cases = [
        # Should be AI
        ('echo "test" | apollo', True),
        ('team-chat "hello world"', True),
        ('show me the git log', True),
        ('how do I fix this error?', True),
        ('ai: help me debug this', True),
        ('@ai analyze this code', True),
        ('what is the meaning of life?', True),
        
        # Should be shell
        ('ls -la', False),
        ('git status', False),
        ('cd /tmp', False),
        ('npm install', False),
        ('echo "hello world"', False),
        ('pwd', False),
        ('mkdir test', False),
        ('rm -rf /tmp/test', False),
    ]
    
    passed = 0
    failed = 0
    
    for command, expected_ai in test_cases:
        result = proxy.should_intercept(command)
        status = "PASS" if result == expected_ai else "FAIL"
        route = "AI" if result else "SHELL"
        expected_route = "AI" if expected_ai else "SHELL"
        
        print(f"  {status}: '{command}' -> {route} (expected {expected_route})")
        
        if result == expected_ai:
            passed += 1
        else:
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


def test_shell_passthrough():
    """Test that shell commands execute correctly."""
    print("\n=== Testing Shell Passthrough ===")
    
    proxy = TransparentAishProxy(debug=True)
    
    # Test simple commands that should work
    test_commands = [
        'echo "Hello from shell"',
        'pwd',
        'date',
        'uname',
    ]
    
    for command in test_commands:
        print(f"\nTesting: {command}")
        try:
            exit_code = proxy.run_single_command(command)
            print(f"  Exit code: {exit_code}")
        except Exception as e:
            print(f"  Error: {e}")


def test_builtin_commands():
    """Test built-in aish commands."""
    print("\n=== Testing Built-in Commands ===")
    
    proxy = TransparentAishProxy(debug=True)
    
    # Test built-in commands
    commands = [
        'aish-help',
        'aish-status',
    ]
    
    for command in commands:
        print(f"\nTesting: {command}")
        try:
            exit_code = proxy.run_single_command(command)
            print(f"  Exit code: {exit_code}")
        except Exception as e:
            print(f"  Error: {e}")


def test_ai_commands():
    """Test AI command routing (may fail if Rhetor not running)."""
    print("\n=== Testing AI Commands ===")
    print("Note: These tests require Rhetor to be running")
    
    proxy = TransparentAishProxy(debug=True)
    
    # Test AI commands (these might fail if Rhetor isn't running)
    ai_commands = [
        'team-chat "test message"',
        'show me available AIs',
    ]
    
    for command in ai_commands:
        print(f"\nTesting: {command}")
        try:
            exit_code = proxy.run_single_command(command)
            print(f"  Exit code: {exit_code}")
        except Exception as e:
            print(f"  Error: {e}")


def main():
    """Run all tests."""
    print("aish Transparent Proxy Test Suite")
    print("=" * 50)
    
    # Test command detection (core logic)
    detection_passed = test_command_detection()
    
    # Test shell passthrough
    test_shell_passthrough()
    
    # Test built-in commands
    test_builtin_commands()
    
    # Test AI commands (might fail without Rhetor)
    test_ai_commands()
    
    print("\n" + "=" * 50)
    if detection_passed:
        print("✅ Core proxy logic working - command detection passed!")
        print("🚀 Ready for terminal integration testing")
    else:
        print("❌ Command detection failed - needs fixing")
        return 1
    
    print("\nNext steps:")
    print("1. Start Rhetor: cd /path/to/Tekton/Rhetor && ./run_rhetor.sh")
    print("2. Test interactively: python tests/test_proxy_shell.py --interactive")
    print("3. Test single commands: python tests/test_proxy_shell.py --command 'ls -la'")
    
    return 0


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--interactive", action="store_true", help="Run interactive test")
    parser.add_argument("--command", help="Test single command")
    
    args = parser.parse_args()
    
    if args.interactive:
        # Interactive test mode
        proxy = TransparentAishProxy(debug=True)
        print("Starting interactive proxy test...")
        print("Try commands like: 'ls -la', 'echo \"test\" | apollo', 'aish-help'")
        proxy.run_interactive()
    elif args.command:
        # Single command test
        proxy = TransparentAishProxy(debug=True)
        exit_code = proxy.run_single_command(args.command)
        sys.exit(exit_code)
    else:
        # Run test suite
        sys.exit(main())