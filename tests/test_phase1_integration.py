#!/usr/bin/env python3
"""
Phase 1 Integration Test - Complete test of socket fixes and MCP integration.

This script performs end-to-end testing of:
1. Socket buffering improvements
2. MCP SendMessageToSpecialist 
3. Intelligent timeout detection
"""

import sys
import os
import time
import subprocess

# Add paths
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'Tekton'))

from src.core.shell import AIShell


def test_aish_ai_specialists():
    """Test aish communication with AI specialists."""
    print("\n=== Testing aish with AI Specialists ===")
    
    shell = AIShell(debug=True)
    
    # Test 1: Simple echo to Athena
    print("\n1. Testing simple echo to Athena...")
    result = shell.execute_pipeline('echo "Hello Athena, are you receiving this clearly?" | athena')
    print(f"Result: {result}")
    
    if result and "error" not in result.lower():
        print("✓ Successfully communicated with Athena")
    else:
        print("✗ Failed to communicate with Athena")
        return False
    
    # Test 2: Pipeline through multiple AIs
    print("\n2. Testing pipeline through multiple AIs...")
    result = shell.execute_pipeline('echo "What makes great software?" | apollo | athena')
    print(f"Result: {result}")
    
    if result and "error" not in result.lower():
        print("✓ Successfully piped through multiple AIs")
    else:
        print("✗ Failed to pipe through multiple AIs")
        return False
    
    # Test 3: Team chat
    print("\n3. Testing team chat...")
    result = shell.execute_pipeline('team-chat "What should we optimize in our codebase?"')
    print(f"Result: {result[:200]}..." if result else "No result")
    
    if result and "error" not in result.lower():
        print("✓ Successfully performed team chat")
    else:
        print("✗ Failed team chat")
        return False
    
    return True


def test_aish_with_long_messages():
    """Test aish with messages that would cause buffering issues."""
    print("\n=== Testing Long Message Handling ===")
    
    shell = AIShell(debug=True)
    
    # Create a long message that would exceed single recv buffer
    long_message = "Please analyze this long text: " + "x" * 5000
    
    print(f"\nSending {len(long_message)} byte message to Apollo...")
    result = shell.execute_pipeline(f'echo "{long_message}" | apollo')
    
    if result and "error" not in result.lower():
        print("✓ Successfully handled long message")
        return True
    else:
        print("✗ Failed to handle long message")
        return False


def test_timeout_detection():
    """Test intelligent timeout detection."""
    print("\n=== Testing Timeout Detection ===")
    
    from src.utils.socket_buffer import SocketTimeoutDetector
    
    detector = SocketTimeoutDetector(debug=True)
    
    # Test 1: Quick connection timeout
    print("\n1. Testing connection timeout (non-existent host)...")
    success, sock, error = detector.create_connection("192.168.255.255", 9999)
    
    if not success and "timeout" in error.lower():
        print(f"✓ Correctly detected connection timeout: {error}")
    else:
        print("✗ Failed to detect connection timeout properly")
        return False
    
    # Test 2: Heartbeat tracking
    print("\n2. Testing heartbeat tracking...")
    detector.record_heartbeat()
    
    # Check immediately - should be healthy
    alive, status = detector.check_heartbeat()
    if alive and "healthy" in status.lower():
        print(f"✓ Initial heartbeat status: {status}")
    else:
        print(f"✗ Unexpected initial status: {status}")
        return False
    
    # Simulate delay
    detector.last_heartbeat = time.time() - 35  # 35 seconds ago
    alive, status = detector.check_heartbeat()
    
    if alive and "delayed" in status.lower():
        print(f"✓ Detected delayed heartbeat: {status}")
    else:
        print(f"✗ Failed to detect delayed heartbeat: {status}")
        return False
    
    # Simulate dead connection
    detector.last_heartbeat = time.time() - 60  # 60 seconds ago
    alive, status = detector.check_heartbeat()
    
    if not alive and "dead" in status.lower():
        print(f"✓ Detected dead connection: {status}")
    else:
        print(f"✗ Failed to detect dead connection: {status}")
        return False
    
    return True


def test_mcp_integration():
    """Test MCP tools integration from aish side."""
    print("\n=== Testing MCP Integration from aish ===")
    
    # This would require MCP server to be running
    # For now, we'll test that the integration points exist
    
    try:
        from Rhetor.rhetor.core.mcp.tools_integration_unified import MCPToolsIntegrationUnified
        print("✓ MCP tools integration module loads correctly")
        
        # Check that SendMessageToSpecialist is implemented
        integration = MCPToolsIntegrationUnified()
        if hasattr(integration, 'send_message_to_specialist'):
            print("✓ SendMessageToSpecialist method exists")
        else:
            print("✗ SendMessageToSpecialist method missing")
            return False
            
        if hasattr(integration, '_send_via_socket') and hasattr(integration, '_send_via_api'):
            print("✓ Dual routing methods implemented")
        else:
            print("✗ Dual routing methods missing")
            return False
            
        return True
    except Exception as e:
        print(f"✗ Failed to load MCP integration: {e}")
        return False


def run_full_integration_test():
    """Run a full integration test scenario."""
    print("\n=== Full Integration Test ===")
    
    shell = AIShell(debug=True)
    
    # Complex scenario: Ask multiple AIs to collaborate
    print("\nScenario: Multi-AI collaboration on code review")
    
    commands = [
        'echo "Review this Python function: def add(a, b): return a + b" | apollo',
        'echo "What design patterns could improve our socket handling?" | athena',
        'team-chat "How can we improve our error handling strategy?"'
    ]
    
    for i, cmd in enumerate(commands, 1):
        print(f"\n{i}. Executing: {cmd}")
        result = shell.execute_pipeline(cmd)
        
        if result and "error" not in result.lower():
            print(f"✓ Command {i} succeeded")
            print(f"   Response preview: {result[:100]}...")
        else:
            print(f"✗ Command {i} failed")
            return False
    
    return True


def main():
    """Run all Phase 1 tests."""
    print("Phase 1 Integration Test Suite")
    print("=" * 60)
    print("Testing socket buffering, MCP integration, and timeout detection")
    
    tests = [
        ("AI Specialist Communication", test_aish_ai_specialists),
        ("Long Message Handling", test_aish_with_long_messages),
        ("Timeout Detection", test_timeout_detection),
        ("MCP Integration", test_mcp_integration),
        ("Full Integration", run_full_integration_test)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            print(f"\nRunning: {test_name}")
            print("-" * 40)
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n{test_name} failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Phase 1 Test Summary:")
    print("-" * 60)
    
    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        print(f"  {test_name}: {status}")
    
    total_passed = sum(1 for _, result in results if result)
    print(f"\nTotal: {total_passed}/{len(tests)} tests passed")
    
    if total_passed == len(tests):
        print("\n🎉 Phase 1 Complete! All tests passed.")
        print("\nReady for Phase 2: Streaming Support (SSE/WebSocket)")
    else:
        print("\n⚠️  Some tests failed. Please review and fix before proceeding.")
    
    return total_passed == len(tests)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)