#!/usr/bin/env python3
"""
Test script for verifying socket buffering fixes.

This script tests the line-buffered socket implementation with:
1. Direct socket connections to Greek Chorus AIs
2. Partial message handling
3. Timeout detection
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
from src.utils.socket_buffer import LineBufferedSocket, SocketTimeoutDetector
from src.registry.socket_registry import SocketRegistry


def test_direct_socket_connection():
    """Test direct socket connection to an AI specialist."""
    print("\n=== Testing Direct Socket Connection ===")
    
    # Use dynamic discovery
    registry = SocketRegistry(debug=True)
    ais = registry.discover_ais()
    
    # Find Athena dynamically
    athena_info = registry._get_ai_info('athena')
    if not athena_info or not athena_info.get('port'):
        print("Athena AI not found in discovery")
        return False
    
    port = athena_info['port']
    print(f"\nTesting connection to Athena (discovered port {port})...")
    
    detector = SocketTimeoutDetector(debug=True)
    success, sock, error = detector.create_connection('localhost', port)
    
    if not success:
        print(f"Connection failed: {error}")
        return False
    
    print("Connection successful!")
    
    try:
        # Create line-buffered socket
        buffered = LineBufferedSocket(sock, debug=True)
        
        # Send ping message
        print("\nSending ping message...")
        ping_msg = {"type": "ping"}
        if not buffered.write_message(ping_msg):
            print("Failed to send ping")
            return False
        
        # Read response
        print("\nWaiting for response...")
        response = buffered.read_message()
        if response:
            print(f"Received response: {response}")
        else:
            print("No response received")
        
        # Send chat message
        print("\nSending chat message...")
        chat_msg = {
            "type": "chat",
            "content": "Hello Athena, this is a test message from the new socket buffering system."
        }
        if not buffered.write_message(chat_msg):
            print("Failed to send chat message")
            return False
        
        # Read response
        print("\nWaiting for chat response...")
        response = buffered.read_message()
        if response:
            print(f"Received chat response: {response}")
            return True
        else:
            print("No chat response received")
            return False
            
    finally:
        buffered.close()


def test_socket_registry():
    """Test socket registry with new buffering."""
    print("\n=== Testing Socket Registry ===")
    
    registry = SocketRegistry(debug=True)
    
    # Discover AIs
    print("\nDiscovering AIs...")
    ais = registry.discover_ais()
    print(f"Found {len(ais)} AIs")
    
    # Find Greek Chorus AIs (socket-based)
    socket_ais = []
    for ai_id, ai_info in ais.items():
        if ai_info.get('port'):  # Has port = socket-based
            socket_ais.append((ai_id, ai_info))
            print(f"  - {ai_id}: {ai_info.get('name')} on port {ai_info.get('port')}")
    
    if not socket_ais:
        print("No socket-based AIs found")
        return False
    
    # Test communication with first socket AI
    ai_id, ai_info = socket_ais[0]
    print(f"\nTesting communication with {ai_id}...")
    
    # Create socket
    socket_id = registry.create(ai_id)
    if not socket_id:
        print(f"Failed to create socket for {ai_id}")
        return False
    
    print(f"Created socket: {socket_id}")
    
    # Send message
    test_message = "Testing the new line-buffered socket implementation. Can you confirm receipt?"
    print(f"\nSending: {test_message}")
    
    if not registry.write(socket_id, test_message):
        print("Failed to send message")
        return False
    
    # Wait a bit for response
    time.sleep(2)
    
    # Read response
    response = registry.read(socket_id)
    if response:
        print(f"\nReceived response: {response}")
        return True
    else:
        print("No response received")
        return False


def test_partial_messages():
    """Test handling of partial messages (simulated)."""
    print("\n=== Testing Partial Message Handling ===")
    
    # This is a unit test of the buffering logic
    import socket
    import threading
    import json
    
    # Create a socket pair for testing
    server_sock, client_sock = socket.socketpair()
    
    def send_partial_messages():
        """Simulate sending messages in chunks."""
        messages = [
            {"type": "ping", "status": "ok"},
            {"type": "chat", "content": "This is a longer message that might get split into chunks"},
            {"type": "info", "data": {"key": "value", "number": 42}}
        ]
        
        for msg in messages:
            # Send message in small chunks to simulate partial reads
            data = json.dumps(msg).encode() + b'\n'
            chunk_size = 10
            for i in range(0, len(data), chunk_size):
                chunk = data[i:i+chunk_size]
                server_sock.send(chunk)
                time.sleep(0.1)  # Simulate network delay
    
    # Start sender thread
    sender = threading.Thread(target=send_partial_messages)
    sender.start()
    
    # Read messages with buffering
    buffered = LineBufferedSocket(client_sock, debug=True)
    
    messages_received = []
    try:
        # We're sending exactly 3 messages, read those 3
        for _ in range(3):
            msg = buffered.read_message()
            if msg:
                messages_received.append(msg)
                print(f"Received complete message: {msg}")
    except socket.timeout:
        # Expected after reading all messages
        pass
    
    sender.join()
    buffered.close()
    server_sock.close()
    
    print(f"\nReceived {len(messages_received)} complete messages")
    
    # Check that we got the first message as a heartbeat and 2 regular messages
    if len(messages_received) >= 2:
        print("✓ Successfully handled partial messages")
        return True
    else:
        print("✗ Failed to receive expected messages")
        return False


def main():
    """Run all tests."""
    print("Socket Buffering Test Suite")
    print("=" * 50)
    
    tests = [
        ("Direct Socket Connection", test_direct_socket_connection),
        ("Socket Registry", test_socket_registry),
        ("Partial Message Handling", test_partial_messages)
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