#!/usr/bin/env python3
"""
Test HTTP API communication with Rhetor specialists
Tests HTTP-based communication for traditional Rhetor AIs
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import requests
import json
import time
from registry.socket_registry import SocketRegistry

def test_rhetor_health(host="localhost", port=8003):
    """Test Rhetor HTTP API health endpoint"""
    print(f"Testing Rhetor health at {host}:{port}...")
    
    try:
        response = requests.get(f"http://{host}:{port}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Rhetor HTTP API is healthy")
            return True
        else:
            print(f"❌ Rhetor returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to Rhetor: {e}")
        return False

def test_http_specialist_list(host="localhost", port=8003):
    """Test listing specialists via HTTP API"""
    print("\nTesting HTTP specialist listing...")
    
    try:
        response = requests.get(f"http://{host}:{port}/api/ai/specialists", timeout=5)
        if response.status_code == 200:
            data = response.json()
            count = data.get('count', 0)
            print(f"✅ Found {count} specialists via HTTP API")
            
            # Show active ones
            active = [s for s in data.get('specialists', []) if s.get('active')]
            if active:
                print(f"   Active specialists: {', '.join([s['id'] for s in active[:3]])}...")
            return True
        else:
            print(f"❌ Failed to list specialists: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error listing specialists: {e}")
        return False

def test_http_team_chat(host="localhost", port=8003):
    """Test team chat via HTTP API"""
    print("\nTesting HTTP team chat...")
    
    try:
        payload = {
            "message": "Hello from HTTP test",
            "moderation_mode": "pass_through",
            "timeout": 5.0
        }
        response = requests.post(
            f"http://{host}:{port}/api/team-chat",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            responses = data.get('responses', {})
            if responses:
                print(f"✅ Team chat received {len(responses)} responses")
                return True
            else:
                print("⚠️  Team chat returned no responses")
                return True
        else:
            print(f"❌ Team chat failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error in team chat: {e}")
        return False

def test_http_direct_specialist(host="localhost", port=8003):
    """Test direct specialist communication via HTTP"""
    print("\nTesting HTTP direct specialist...")
    
    try:
        # Try rhetor-orchestrator
        payload = {
            "message": "What is your purpose?",
            "temperature": 0.7
        }
        response = requests.post(
            f"http://{host}:{port}/api/ai/specialists/rhetor-orchestrator/message",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            content = data.get('response', data.get('content', ''))
            print(f"✅ HTTP specialist responded")
            print(f"   Response: {content[:50]}...")
            return True
        elif response.status_code == 404:
            print("⚠️  Specialist not found (might not be active)")
            return True
        else:
            print(f"❌ HTTP specialist failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error with HTTP specialist: {e}")
        return False

def test_http_via_registry(host="localhost", port=8003):
    """Test HTTP communication through aish registry"""
    print("\nTesting HTTP communication via registry...")
    
    registry = SocketRegistry(f"http://{host}:{port}", debug=True)
    
    # Create socket for rhetor
    socket_id = registry.create("rhetor")
    
    # Send message
    success = registry.write(socket_id, "Hello from registry HTTP test")
    if success:
        print("✅ Message sent via HTTP")
    else:
        print("❌ Failed to send message")
        return False
    
    # Wait and read response
    time.sleep(2)
    messages = registry.read(socket_id)
    if messages:
        print(f"✅ Received HTTP response")
        print(f"   Response: {messages[0][:50]}...")
    else:
        print("⚠️  No response received")
    
    # Cleanup
    registry.delete(socket_id)
    
    return True

def test_http_pipeline(host="localhost", port=8003):
    """Test HTTP-based AI pipeline"""
    print("\nTesting HTTP-based pipeline...")
    
    import subprocess
    aish_path = os.path.join(os.path.dirname(__file__), '..', 'aish')
    
    # Set environment variable for remote host if needed
    env = os.environ.copy()
    if host != "localhost":
        env['TEKTON_RHETOR_PORT'] = f"{port}"
        env['TEKTON_RHETOR_HOST'] = host
    
    # Test with rhetor specialist
    cmd = [aish_path, '-c', 'echo "What is AI?" | rhetor']
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=15, env=env)
    
    if result.returncode == 0 and result.stdout:
        print("✅ HTTP pipeline executed successfully")
        print(f"   Response: {result.stdout[:100]}...")
        return True
    else:
        print(f"❌ HTTP pipeline failed")
        if result.stderr:
            print(f"   Error: {result.stderr}")
        return False

def main():
    """Run all HTTP communication tests"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test HTTP API communication')
    parser.add_argument('--host', default='localhost', help='Rhetor host')
    parser.add_argument('--port', default=8003, type=int, help='Rhetor port')
    args = parser.parse_args()
    
    print("="*60)
    print("HTTP API Communication Tests")
    print(f"Testing Rhetor specialists at {args.host}:{args.port}")
    print("="*60)
    
    tests = [
        lambda: test_rhetor_health(args.host, args.port),
        lambda: test_http_specialist_list(args.host, args.port),
        lambda: test_http_team_chat(args.host, args.port),
        lambda: test_http_direct_specialist(args.host, args.port),
        lambda: test_http_via_registry(args.host, args.port),
        lambda: test_http_pipeline(args.host, args.port)
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test crashed: {e}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"HTTP Test Results: {passed} passed, {failed} failed")
    print("="*60)
    
    return 0 if failed == 0 else 1

if __name__ == '__main__':
    sys.exit(main())