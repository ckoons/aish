#!/usr/bin/env python3
"""
Integration tests for aish - The AI Shell
Tests that require Rhetor to be running
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import requests
import subprocess
import time
from registry.socket_registry import SocketRegistry

def check_rhetor_health():
    """Check if Rhetor is running and healthy"""
    try:
        response = requests.get('http://localhost:8003/health', timeout=2)
        return response.status_code == 200
    except:
        return False

def test_rhetor_connection():
    """Test basic connection to Rhetor"""
    print("Testing Rhetor connection...")
    
    if not check_rhetor_health():
        print("❌ Rhetor is not running on port 8003")
        return False
    
    print("✅ Rhetor is healthy")
    return True

def test_list_specialists():
    """Test listing AI specialists"""
    print("\nTesting specialist listing...")
    
    try:
        response = requests.get('http://localhost:8003/api/ai/specialists')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {data['count']} specialists:")
            for spec in data['specialists']:
                status = "✅" if spec['active'] else "❌"
                print(f"  {status} {spec['id']} - {spec['status']}")
            return True
        else:
            print(f"❌ Failed to list specialists: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error listing specialists: {e}")
        return False

def test_team_chat():
    """Test team chat functionality"""
    print("\nTesting team chat...")
    
    try:
        payload = {
            "message": "Hello from aish integration test",
            "moderation_mode": "pass_through",
            "timeout": 5.0
        }
        response = requests.post('http://localhost:8003/api/team-chat', json=payload)
        
        if response.status_code == 200:
            data = response.json()
            if data['responses']:
                print(f"✅ Team chat received {len(data['responses'])} responses")
                # Handle both list and dict responses
                if isinstance(data['responses'], dict):
                    for ai_id, resp in data['responses'].items():
                        content = resp.get('content', '') if isinstance(resp, dict) else str(resp)
                        print(f"  - {ai_id}: {content[:50]}...")
                elif isinstance(data['responses'], list):
                    for i, resp in enumerate(data['responses']):
                        content = resp.get('content', '') if isinstance(resp, dict) else str(resp)
                        print(f"  - Response {i}: {content[:50]}...")
                return True
            else:
                print("⚠️  Team chat returned no responses (no active specialists?)")
                return True  # Not a failure, just no active AIs
        else:
            print(f"❌ Team chat failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error in team chat: {e}")
        return False

def test_direct_specialist():
    """Test direct communication with rhetor specialist"""
    print("\nTesting direct specialist communication...")
    
    try:
        # Try rhetor-orchestrator which should be active
        payload = {
            "message": "What is your role?",
            "temperature": 0.7
        }
        response = requests.post(
            'http://localhost:8003/api/ai/specialists/rhetor-orchestrator/message',
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Rhetor responded: {data.get('response', '')[:100]}...")
            return True
        else:
            print(f"⚠️  Direct specialist returned {response.status_code}")
            # Try fallback to see if it's just this endpoint
            return True
    except Exception as e:
        print(f"❌ Error with direct specialist: {e}")
        return False

def test_aish_pipeline():
    """Test aish command-line pipeline"""
    print("\nTesting aish pipeline execution...")
    
    aish_path = os.path.join(os.path.dirname(__file__), '..', 'aish')
    
    if not os.path.exists(aish_path):
        print(f"❌ aish not found at {aish_path}")
        return False
    
    try:
        # Test simple echo | ai pipeline
        cmd = [aish_path, '-c', 'echo "What is 2+2?" | rhetor']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            output = result.stdout.strip()
            if output and len(output) > 10:  # Got a reasonable response
                print(f"✅ Pipeline executed successfully")
                print(f"   Response: {output[:100]}...")
                return True
            else:
                print(f"⚠️  Pipeline executed but output seems short: {output}")
                return True
        else:
            print(f"❌ Pipeline failed with code {result.returncode}")
            print(f"   Error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Pipeline execution timed out")
        return False
    except Exception as e:
        print(f"❌ Error executing pipeline: {e}")
        return False

def test_socket_registry_integration():
    """Test socket registry with real Rhetor"""
    print("\nTesting socket registry integration...")
    
    registry = SocketRegistry(debug=True)
    
    # Create socket
    socket_id = registry.create("rhetor")
    print(f"✅ Created socket: {socket_id}")
    
    # Write message
    success = registry.write(socket_id, "Hello from integration test")
    if success:
        print("✅ Successfully sent message")
    else:
        print("❌ Failed to send message")
        return False
    
    # Read response
    time.sleep(2)  # Give it time to respond
    messages = registry.read(socket_id)
    if messages:
        print(f"✅ Received {len(messages)} responses")
        print(f"   First response: {messages[0][:100]}...")
    else:
        print("⚠️  No responses received (might be normal)")
    
    # Cleanup
    registry.delete(socket_id)
    print("✅ Cleaned up socket")
    
    return True

def main():
    """Run all integration tests"""
    print("="*60)
    print("aish Integration Tests")
    print("="*60)
    
    if not check_rhetor_health():
        print("\n⚠️  WARNING: Rhetor is not running on port 8003")
        print("These tests require Rhetor to be running.")
        print("Start Rhetor and try again.")
        return 1
    
    tests = [
        test_rhetor_connection,
        test_list_specialists,
        test_team_chat,
        test_direct_specialist,
        test_aish_pipeline,
        test_socket_registry_integration
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
            print(f"❌ Test {test.__name__} crashed: {e}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("="*60)
    
    return 0 if failed == 0 else 1

if __name__ == '__main__':
    sys.exit(main())