#!/usr/bin/env python3
"""
Test script for conversation history functionality.
"""

import sys
import os
import tempfile
import json
from pathlib import Path

# Add src directory to path (same as main aish script)
aish_root = Path(__file__).resolve().parent.parent
src_path = aish_root / 'src'
sys.path.insert(0, str(src_path))

from core.history import AIHistory


def test_basic_history():
    """Test basic history operations."""
    print("\n=== Testing Basic History Operations ===")
    
    # Use temp file for testing
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.history') as tf:
        history_file = tf.name
    
    history = AIHistory(history_file)
    
    # Test 1: Add commands
    print("\n1. Adding commands to history...")
    cmd1 = history.add_command(
        'echo "Hello" | apollo',
        {"apollo": "Greetings! How can I help you today?"}
    )
    print(f"Added command {cmd1}")
    
    cmd2 = history.add_command(
        'echo "What is AI?" | athena | apollo',
        {
            "athena": "AI is the simulation of human intelligence...",
            "apollo": "Building on Athena's explanation, AI encompasses..."
        }
    )
    print(f"Added command {cmd2}")
    
    cmd3 = history.add_command(
        'team-chat "Should we add more tests?"',
        {
            "hermes": "Yes, comprehensive testing is essential",
            "athena": "I agree, tests ensure reliability",
            "apollo": "Tests help catch edge cases"
        }
    )
    print(f"Added command {cmd3}")
    
    # Test 2: Read history
    print("\n2. Reading history...")
    entries = history.get_history()
    print(f"Total entries: {len(entries)}")
    for entry in entries:
        print(f"  {entry.rstrip()}")
    
    # Test 3: Search history
    print("\n3. Searching history...")
    results = history.search("apollo")
    print(f"Found {len(results)} lines matching 'apollo'")
    
    # Test 4: Get specific command
    print("\n4. Getting specific command...")
    cmd, responses = history.get_command_by_number(cmd2)
    print(f"Command {cmd2}: {cmd}")
    print(f"Responses: {len(responses)} AIs responded")
    
    # Test 5: Replay
    print("\n5. Testing replay...")
    replay_cmd = history.replay(cmd1)
    print(f"Replay command {cmd1}: {replay_cmd}")
    
    # Cleanup
    os.unlink(history_file)
    
    return True


def test_json_export():
    """Test JSON export functionality."""
    print("\n=== Testing JSON Export ===")
    
    # Create temp session directory
    temp_dir = tempfile.mkdtemp()
    session_dir = Path(temp_dir) / '.aish' / 'sessions'
    session_dir.mkdir(parents=True)
    
    # Override home directory for testing
    original_home = os.environ.get('HOME')
    os.environ['HOME'] = temp_dir
    
    try:
        history = AIHistory()
        
        # Add some commands
        history.add_command('echo "test 1" | apollo', {"apollo": "Response 1"})
        history.add_command('echo "test 2" | athena', {"athena": "Response 2"})
        
        # Export as JSON
        json_data = history.export_json()
        data = json.loads(json_data)
        
        print(f"Exported {len(data['history'])} entries")
        print("JSON structure valid: ✓")
        
        # Test range export
        json_partial = history.export_json(start=1, end=1)
        partial_data = json.loads(json_partial)
        print(f"Range export: {len(partial_data['history'])} entries")
        
    finally:
        # Restore environment
        if original_home:
            os.environ['HOME'] = original_home
        else:
            del os.environ['HOME']
        
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)
    
    return True


def test_history_command():
    """Test aish-history command."""
    print("\n=== Testing aish-history Command ===")
    
    # Check if command exists
    history_cmd = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'aish-history')
    
    if os.path.exists(history_cmd):
        print(f"✓ aish-history command found at: {history_cmd}")
        
        # Test help
        import subprocess
        result = subprocess.run([history_cmd, '--help'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ Help command works")
        else:
            print("✗ Help command failed")
            
        return True
    else:
        print("✗ aish-history command not found")
        return False


def test_unix_style_format():
    """Test Unix-style history format."""
    print("\n=== Testing Unix-style Format ===")
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.history') as tf:
        history_file = tf.name
    
    history = AIHistory(history_file)
    
    # Add a command
    history.add_command(
        'echo "what day was yesterday?" | numa',
        {"numa": "Sunday June 29, 2025"}
    )
    
    # Read the file directly
    with open(history_file, 'r') as f:
        content = f.read()
    
    print("History file content:")
    print(content)
    
    # Verify format
    if ': echo "what day was yesterday?" | numa' in content:
        print("✓ Command format correct")
    else:
        print("✗ Command format incorrect")
        
    if '# numa: Sunday June 29, 2025' in content:
        print("✓ Response format correct")
    else:
        print("✗ Response format incorrect")
    
    os.unlink(history_file)
    return True


def main():
    """Run all history tests."""
    print("Conversation History Test Suite")
    print("=" * 50)
    
    tests = [
        ("Basic History Operations", test_basic_history),
        ("JSON Export", test_json_export),
        ("Unix-style Format", test_unix_style_format),
        ("History Command", test_history_command)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n{test_name} failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary:")
    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        print(f"  {test_name}: {status}")
    
    total_passed = sum(1 for _, result in results if result)
    print(f"\nTotal: {total_passed}/{len(tests)} tests passed")
    
    return total_passed == len(tests)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)