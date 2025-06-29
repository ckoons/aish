#!/usr/bin/env python3
"""
Test script for aish socket registry implementation
"""

import sys
sys.path.insert(0, 'src')

from registry.socket_registry import SocketRegistry

def test_socket_registry():
    print("Testing aish socket registry implementation...")
    
    # Create registry with debug mode (will use env var or default)
    registry = SocketRegistry(debug=True)
    print(f"✓ Created socket registry (endpoint: {registry.rhetor_endpoint})")
    
    # Test 1: Create socket (using rhetor which is active)
    socket_id = registry.create("rhetor", prompt="You are Rhetor, the LLM orchestrator")
    print(f"✓ Created socket: {socket_id}")
    
    # Test 2: Write to socket
    success = registry.write(socket_id, "Hello Rhetor! What specialists are currently active?")
    print(f"✓ Write to socket: {'Success' if success else 'Failed'}")
    
    # Test 3: Read from socket
    messages = registry.read(socket_id)
    print(f"✓ Read from socket: {len(messages)} messages")
    if messages:
        print(f"  Response: {messages[0][:100]}...")
    
    # Test 4: List sockets
    sockets = registry.list_sockets()
    print(f"✓ Listed sockets: {len(sockets)} active")
    
    # Test 5: Reset socket
    success = registry.reset(socket_id)
    print(f"✓ Reset socket: {'Success' if success else 'Failed'}")
    
    # Test 6: Delete socket
    success = registry.delete(socket_id)
    print(f"✓ Delete socket: {'Success' if success else 'Failed'}")
    
    print("\nAll tests completed!")

if __name__ == "__main__":
    test_socket_registry()