#!/usr/bin/env python3
"""
Quick test runner to verify basic functionality
"""

import subprocess
import sys
import os

def run_test(test_name, test_file):
    """Run a test file and return results"""
    print(f"\n{'='*60}")
    print(f"Running {test_name}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            [sys.executable, test_file], 
            capture_output=True, 
            text=True,
            timeout=120  # 2 minute timeout for all tests
        )
        
        if result.returncode == 0:
            # Extract test summary from output
            output_lines = result.stdout.strip().split('\n')
            for line in output_lines[-5:]:
                if 'Ran' in line or 'OK' in line or 'FAILED' in line:
                    print(f"✅ {line}")
            return True
        else:
            print(f"❌ {test_name} failed")
            # Show last few lines of output
            if result.stdout:
                output_lines = result.stdout.strip().split('\n')
                for line in output_lines[-10:]:
                    print(f"   {line}")
            if result.stderr:
                print(f"   Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"❌ {test_name} timed out after 2 minutes")
        return False
    except Exception as e:
        print(f"❌ {test_name} crashed: {e}")
        return False

def main():
    """Run quick check of all tests"""
    test_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(os.path.dirname(test_dir))  # Change to aish root
    
    print("Quick Test Check for aish")
    print("This will run basic validation of test suites")
    
    tests = [
        ("Functional Tests", os.path.join(test_dir, "test_functional.py")),
        ("Integration Tests", os.path.join(test_dir, "test_integration.py")),
        ("Socket Tests", os.path.join(test_dir, "test_socket_communication.py")),
    ]
    
    results = []
    for test_name, test_file in tests:
        if os.path.exists(test_file):
            results.append((test_name, run_test(test_name, test_file)))
        else:
            print(f"❌ {test_name}: File not found")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} test suites passed")
    
    # Return appropriate exit code
    return 0 if passed == total else 1

if __name__ == '__main__':
    sys.exit(main())