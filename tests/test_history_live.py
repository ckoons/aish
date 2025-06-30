#!/usr/bin/env python3
"""
Test history with live AIs without changing HOME directory.
"""

import sys
import os
import subprocess
import time
import json
from pathlib import Path

# Add src directory to path
aish_root = Path(__file__).resolve().parent.parent
src_path = aish_root / 'src'
sys.path.insert(0, str(src_path))

from core.history import AIHistory


def test_history_via_subprocess():
    """Test history by running aish as subprocess."""
    print("\n=== Testing History via aish Subprocess ===")
    
    # Get current history state
    history_file = Path.home() / '.aish_history'
    original_size = history_file.stat().st_size if history_file.exists() else 0
    
    print(f"\n1. Original history size: {original_size} bytes")
    
    # Run aish commands
    test_commands = [
        'echo "What is the meaning of life?" | athena',
        'echo "How do we build better software?" | apollo | athena',
        'team-chat "What should we optimize today?"'
    ]
    
    print("\n2. Running test commands...")
    for i, cmd in enumerate(test_commands, 1):
        print(f"\n   Command {i}: {cmd[:50]}...")
        
        # Run command via aish -c
        result = subprocess.run(
            ['./aish', '-c', cmd],
            capture_output=True,
            text=True,
            cwd=str(aish_root)
        )
        
        if result.returncode == 0:
            output = result.stdout.strip()
            if output:
                print(f"   ✓ Got response ({len(output)} chars)")
                print(f"     Preview: {output[:100]}...")
            else:
                print("   ⚠️  No output")
        else:
            print(f"   ✗ Command failed: {result.stderr}")
    
    # Give it a moment to write history
    time.sleep(0.5)
    
    # Check history was updated
    print("\n3. Checking history file...")
    new_size = history_file.stat().st_size if history_file.exists() else 0
    print(f"   New history size: {new_size} bytes")
    print(f"   Growth: {new_size - original_size} bytes")
    
    if new_size > original_size:
        print("   ✓ History file grew")
        
        # Read recent history
        history = AIHistory()
        recent = history.get_history(20)
        
        print("\n4. Recent history entries:")
        print("   " + "-" * 50)
        
        # Find our test commands
        found_commands = 0
        for line in recent[-30:]:  # Check last 30 lines
            line = line.strip()
            if any(test_cmd in line for test_cmd in ["meaning of life", "better software", "optimize today"]):
                print(f"   {line}")
                found_commands += 1
            elif line.startswith("#") and found_commands > 0:
                print(f"   {line}")
        
        print("   " + "-" * 50)
        
        # Test JSON export
        print("\n5. Testing JSON export...")
        json_data = history.export_json()
        data = json.loads(json_data)
        
        if 'history' in data and len(data['history']) > 0:
            print(f"   ✓ JSON export works ({len(data['history'])} entries)")
            
            # Show last entry
            last_entry = data['history'][-1]
            print(f"   Last entry: Command #{last_entry['number']}")
            print(f"   Command: {last_entry['command'][:50]}...")
            print(f"   Responses: {len(last_entry.get('responses', {}))} AIs")
        else:
            print("   ⚠️  No JSON history found")
        
        return True
    else:
        print("   ✗ History file did not grow")
        return False


def test_aish_history_command():
    """Test the aish-history command."""
    print("\n=== Testing aish-history Command ===")
    
    aish_history_path = Path(__file__).parent.parent / 'aish-history'
    
    # Test basic command
    print("\n1. Testing basic history view...")
    result = subprocess.run(
        [str(aish_history_path), '-n', '5'],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("   ✓ Command succeeded")
        if result.stdout:
            print("   Output preview:")
            for line in result.stdout.strip().split('\n')[:5]:
                print(f"     {line}")
    else:
        print(f"   ✗ Command failed: {result.stderr}")
    
    # Test JSON export
    print("\n2. Testing JSON export...")
    result = subprocess.run(
        [str(aish_history_path), '--json'],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        try:
            data = json.loads(result.stdout)
            print(f"   ✓ Valid JSON with {len(data.get('history', []))} entries")
        except:
            print("   ✗ Invalid JSON output")
    else:
        print(f"   ✗ Command failed: {result.stderr}")
    
    return True


def main():
    """Run live history tests."""
    print("Live History Test Suite")
    print("=" * 60)
    print("Testing history with real AI communication")
    print("This test uses your actual ~/.aish_history file")
    
    tests = [
        ("History via Subprocess", test_history_via_subprocess),
        ("aish-history Command", test_aish_history_command)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            print(f"\nRunning: {test_name}")
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n{test_name} failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary:")
    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        print(f"  {test_name}: {status}")
    
    total_passed = sum(1 for _, result in results if result)
    print(f"\nTotal: {total_passed}/{len(tests)} tests passed")
    
    print("\nNOTE: This test used your real ~/.aish_history file")
    print("Your conversation history has been preserved.")
    
    return total_passed == len(tests)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)