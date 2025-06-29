#!/usr/bin/env python3
"""
Test runner for aish - The AI Shell
Runs both functional and integration tests
"""

import sys
import os
import subprocess
import argparse

def run_functional_tests():
    """Run functional tests that don't require Rhetor"""
    print("="*60)
    print("Running Functional Tests")
    print("="*60)
    
    test_file = os.path.join(os.path.dirname(__file__), 'test_functional.py')
    result = subprocess.run([sys.executable, test_file], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)
    
    return result.returncode

def run_integration_tests():
    """Run integration tests that require Rhetor"""
    print("\n" + "="*60)
    print("Running Integration Tests")
    print("="*60)
    
    test_file = os.path.join(os.path.dirname(__file__), 'test_integration.py')
    result = subprocess.run([sys.executable, test_file])
    
    return result.returncode

def run_protocol_tests():
    """Run socket and HTTP protocol tests"""
    print("\n" + "="*60)
    print("Running Protocol Tests")
    print("="*60)
    
    test_file = os.path.join(os.path.dirname(__file__), 'test_all_protocols.py')
    result = subprocess.run([sys.executable, test_file])
    
    return result.returncode

def run_quick_check():
    """Quick smoke test to verify basic functionality"""
    print("="*60)
    print("Quick Functionality Check")
    print("="*60)
    
    aish_path = os.path.join(os.path.dirname(__file__), '..', 'aish')
    
    # Test 1: Check aish help
    print("\n1. Testing aish help...")
    result = subprocess.run([aish_path, '--help'], capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ aish help works")
    else:
        print("❌ aish help failed")
    
    # Test 2: Check version
    print("\n2. Testing aish version...")
    result = subprocess.run([aish_path, '--version'], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✅ aish version: {result.stdout.strip()}")
    else:
        print("❌ aish version failed")
    
    # Test 3: Simple echo (no AI needed)
    print("\n3. Testing simple echo command...")
    result = subprocess.run([aish_path, '-c', 'echo "Hello aish"'], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✅ Echo works: {result.stdout.strip()}")
    else:
        print("❌ Echo failed")
    
    return 0

def main():
    parser = argparse.ArgumentParser(description='Run aish tests')
    parser.add_argument('--functional', action='store_true', help='Run only functional tests')
    parser.add_argument('--integration', action='store_true', help='Run only integration tests')
    parser.add_argument('--protocols', action='store_true', help='Run protocol tests (socket + HTTP)')
    parser.add_argument('--quick', action='store_true', help='Run quick smoke test')
    parser.add_argument('--all', action='store_true', help='Run all tests including protocols')
    
    args = parser.parse_args()
    
    # Default to functional + integration if nothing specified
    if not any([args.functional, args.integration, args.protocols, args.quick, args.all]):
        args.functional = True
        args.integration = True
    
    exit_code = 0
    
    if args.quick:
        exit_code |= run_quick_check()
    
    if args.functional or args.all:
        exit_code |= run_functional_tests()
    
    if args.integration or args.all:
        exit_code |= run_integration_tests()
    
    if args.protocols or args.all:
        exit_code |= run_protocol_tests()
    
    return exit_code

if __name__ == '__main__':
    sys.exit(main())