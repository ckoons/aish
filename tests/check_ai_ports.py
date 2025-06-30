#!/usr/bin/env python3
"""Quick diagnostic to check which AI ports are actually listening."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import socket
import json
from src.registry.socket_registry import SocketRegistry

print("Checking AI port availability using ai-discover...")
print("-" * 60)

# Use dynamic discovery
registry = SocketRegistry(debug=False)
ais = registry.discover_ais()

if not ais:
    print("No AIs discovered! Is Tekton running?")
    sys.exit(1)

# Check each discovered AI
successful = 0
failed = 0

for ai_id, ai_info in ais.items():
    # Skip duplicates (e.g., 'athena' and 'athena-ai')
    if not ai_id.endswith('-ai'):
        continue
        
    name = ai_info.get('name', ai_id)
    port = ai_info.get('port')
    
    if not port:
        print(f"⚠️  {name:15} - No port specified (API-only)")
        continue
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1.0)
    
    try:
        sock.connect(('localhost', port))
        print(f"✓ {name:15} port {port:5} - LISTENING", end="")
        
        # Try to send a ping
        try:
            ping = json.dumps({"type": "ping"}) + "\n"
            sock.send(ping.encode())
            sock.settimeout(2.0)
            response = sock.recv(1024)
            if response:
                resp_str = response.decode().strip()
                try:
                    resp_json = json.loads(resp_str)
                    if resp_json.get('status') == 'ok':
                        print(" [ping: OK]")
                    else:
                        print(f" [ping response: {resp_str[:30]}...]")
                except:
                    print(f" [raw response: {resp_str[:30]}...]")
            else:
                print(" [no ping response]")
        except Exception as e:
            print(f" [ping failed: {str(e)[:30]}]")
        
        successful += 1
        sock.close()
    except Exception as e:
        print(f"✗ {name:15} port {port:5} - NOT LISTENING ({str(e)[:30]})")
        failed += 1

print("\n" + "-" * 60)
print(f"Summary: {successful} listening, {failed} not listening")
print("\nNote: All AI specialists should be on ports 45000+")
print("      Component HTTP APIs are on ports 8000-8088")