#!/usr/bin/env python3
"""
Test core aish features one by one.
"""

import subprocess
import time
import json
from pathlib import Path


def run_aish_command(cmd):
    """Run an aish command and return output."""
    result = subprocess.run(
        ['./aish', '-c', cmd],
        capture_output=True,
        text=True,
        cwd=str(Path(__file__).parent.parent)
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def test_single_ai():
    """Test single AI communication."""
    print("\n1. Testing Single AI (echo | athena)")
    print("-" * 50)
    
    code, out, err = run_aish_command('echo "Hello Athena" | athena')
    
    if code == 0 and out and "Knowledge" in out:
        print("✅ PASSED - Athena responded")
        print(f"   Response preview: {out[:100]}...")
        return True
    else:
        print("❌ FAILED")
        print(f"   Exit code: {code}")
        print(f"   Output: {out[:100]}")
        print(f"   Error: {err}")
        return False


def test_pipeline():
    """Test pipeline communication."""
    print("\n2. Testing Pipeline (echo | apollo | athena)")
    print("-" * 50)
    
    code, out, err = run_aish_command('echo "What is clean code?" | apollo | athena')
    
    if code == 0 and out:
        # Check if we got a response (not an error message)
        if "Failed to write" in out:
            print("❌ FAILED - Pipeline not working")
            print(f"   Error: {out}")
            return False
        else:
            print("✅ PASSED - Pipeline executed")
            print(f"   Response preview: {out[:100]}...")
            return True
    else:
        print("❌ FAILED")
        print(f"   Exit code: {code}")
        print(f"   Output: {out[:100]}")
        print(f"   Error: {err}")
        return False


def test_team_chat():
    """Test team chat."""
    print("\n3. Testing Team Chat")
    print("-" * 50)
    
    code, out, err = run_aish_command('team-chat "What should we optimize?"')
    
    if code == 0:
        if "No responses yet" in out:
            print("⚠️  Team chat returned but no AI responses")
            print("   This might be a Tekton/Rhetor issue")
            return False
        elif out:
            print("✅ PASSED - Team chat got responses")
            print(f"   Response preview: {out[:200]}...")
            # Count how many AIs responded
            ai_count = out.count("[team-chat-from-")
            print(f"   Number of AIs that responded: {ai_count}")
            return True
        else:
            print("❌ FAILED - No output")
            return False
    else:
        print("❌ FAILED")
        print(f"   Exit code: {code}")
        print(f"   Error: {err}")
        return False


def test_history_recording():
    """Test if history is being recorded."""
    print("\n4. Testing History Recording")
    print("-" * 50)
    
    # Check session file
    session_file = Path.home() / '.aish' / 'sessions' / f"{time.strftime('%Y-%m-%d')}.json"
    
    if session_file.exists():
        print("✅ Session file exists")
        
        # Read and check content
        with open(session_file) as f:
            data = json.load(f)
        
        entries = data.get('entries', [])
        print(f"   Total entries today: {len(entries)}")
        
        if entries:
            # Show last entry
            last = entries[-1]
            print(f"   Last command: {last.get('command', 'N/A')[:50]}...")
            print(f"   Timestamp: {time.ctime(last.get('timestamp', 0))}")
            responses = last.get('responses', {})
            print(f"   Responses from: {', '.join(responses.keys()) if responses else 'None'}")
            return True
        else:
            print("   ⚠️  No entries in session file")
            return False
    else:
        print("❌ Session file not found")
        return False


def test_history_command():
    """Test aish-history command."""
    print("\n5. Testing aish-history Command")
    print("-" * 50)
    
    result = subprocess.run(
        ['./aish-history', '--json'],
        capture_output=True,
        text=True,
        cwd=str(Path(__file__).parent.parent)
    )
    
    if result.returncode == 0:
        try:
            data = json.loads(result.stdout)
            entries = data.get('history', [])
            print(f"✅ JSON export works - {len(entries)} total entries")
            
            # Show recent commands
            if entries:
                recent = entries[-3:]
                print("   Recent commands:")
                for entry in recent:
                    cmd = entry.get('command', 'N/A')
                    print(f"     #{entry.get('number')}: {cmd[:50]}...")
            
            return True
        except:
            print("❌ Invalid JSON from aish-history")
            return False
    else:
        print(f"❌ aish-history failed: {result.stderr}")
        return False


def main():
    """Run all feature tests."""
    print("aish Feature Test Suite")
    print("=" * 60)
    print("Testing each feature individually to identify issues")
    
    tests = [
        ("Single AI", test_single_ai),
        ("Pipeline", test_pipeline),
        ("Team Chat", test_team_chat),
        ("History Recording", test_history_recording),
        ("History Command", test_history_command)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n{name} test crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print("-" * 60)
    
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{name:20} {status}")
    
    passed = sum(1 for _, r in results if r)
    print(f"\nTotal: {passed}/{len(tests)} passed")
    
    # Recommendations
    print("\nRECOMMENDATIONS:")
    if not results[1][1]:  # Pipeline failed
        print("- Pipeline feature needs debugging in aish")
    if not results[2][1]:  # Team chat failed
        print("- Team chat might need fixes in Tekton/Rhetor")
    if not results[3][1]:  # History recording failed
        print("- History recording needs to be verified")
    
    return passed == len(tests)


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)