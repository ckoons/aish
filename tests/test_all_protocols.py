#!/usr/bin/env python3
"""
Test all communication protocols (socket and HTTP)
Comprehensive test suite for aish communication methods
"""

import sys
import os
import argparse
import subprocess

def run_test(test_script, args=[]):
    """Run a test script and return pass/fail"""
    cmd = [sys.executable, test_script] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0

def main():
    """Run all protocol tests"""
    parser = argparse.ArgumentParser(description='Test all aish communication protocols')
    parser.add_argument('--host', default='localhost', help='Remote host for testing')
    parser.add_argument('--rhetor-port', default=8003, type=int, help='Rhetor HTTP API port')
    parser.add_argument('--socket-only', action='store_true', help='Only test socket communication')
    parser.add_argument('--http-only', action='store_true', help='Only test HTTP communication')
    args = parser.parse_args()
    
    test_dir = os.path.dirname(__file__)
    
    print("="*60)
    print("aish Communication Protocol Tests")
    print(f"Host: {args.host}")
    print("="*60)
    
    tests_run = 0
    tests_passed = 0
    
    # Test socket communication
    if not args.http_only:
        print("\n🔌 SOCKET PROTOCOL TESTS")
        print("-"*60)
        socket_args = []
        if args.host != 'localhost':
            socket_args.extend(['--host', args.host])
        
        if run_test(os.path.join(test_dir, 'test_socket_communication.py'), socket_args):
            tests_passed += 1
            print("\n✅ Socket tests PASSED")
        else:
            print("\n❌ Socket tests FAILED")
        tests_run += 1
    
    # Test HTTP communication
    if not args.socket_only:
        print("\n\n🌐 HTTP PROTOCOL TESTS")
        print("-"*60)
        http_args = []
        if args.host != 'localhost':
            http_args.extend(['--host', args.host])
        if args.rhetor_port != 8003:
            http_args.extend(['--port', str(args.rhetor_port)])
        
        if run_test(os.path.join(test_dir, 'test_http_communication.py'), http_args):
            tests_passed += 1
            print("\n✅ HTTP tests PASSED")
        else:
            print("\n❌ HTTP tests FAILED")
        tests_run += 1
    
    # Summary
    print("\n" + "="*60)
    print("OVERALL TEST RESULTS")
    print("="*60)
    print(f"Protocol suites run: {tests_run}")
    print(f"Protocol suites passed: {tests_passed}")
    print(f"Protocol suites failed: {tests_run - tests_passed}")
    
    if tests_passed == tests_run:
        print("\n🎉 All protocol tests passed!")
    else:
        print("\n⚠️  Some protocol tests failed")
    
    print("\nUsage examples:")
    print("  # Test remote host")
    print("  ./test_all_protocols.py --host tekton.example.com")
    print("  # Test only sockets")
    print("  ./test_all_protocols.py --socket-only")
    print("  # Test only HTTP with custom port")
    print("  ./test_all_protocols.py --http-only --rhetor-port 8080")
    
    return 0 if tests_passed == tests_run else 1

if __name__ == '__main__':
    sys.exit(main())