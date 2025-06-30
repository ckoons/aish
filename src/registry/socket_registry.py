"""
Socket Registry - Manages AI socket connections
"""

from typing import Dict, Optional, Any, List
from collections import deque
from datetime import datetime
import requests
import json
import os
import subprocess
import time

class SocketRegistry:
    """Registry for AI sockets managed by Rhetor"""
    
    def __init__(self, rhetor_endpoint: str = None, debug: bool = False):
        if rhetor_endpoint:
            self.rhetor_endpoint = rhetor_endpoint
        else:
            # Check environment variable, then use default
            port = os.environ.get('TEKTON_RHETOR_PORT', '8003')
            self.rhetor_endpoint = f"http://localhost:{port}"
        
        self.debug = debug
        self.sockets: Dict[str, Any] = {}
        self.message_queues: Dict[str, deque] = {}
        self.max_queue_size = 1000
        
        # Cache for discovered AIs
        self._ai_cache = {}
        self._cache_time = 0
        self._cache_ttl = 300  # 5 minutes
    
    def create(self, ai_name: str, model: str = None, prompt: str = None, context: Dict = None) -> str:
        """
        Create a new AI instance with socket
        Returns socket_id
        """
        # Generate unique socket ID
        timestamp = int(datetime.now().timestamp() * 1000000)
        socket_id = f"{ai_name}-{timestamp}"
        
        # Initialize socket info
        self.sockets[socket_id] = {
            'ai_name': ai_name,
            'model': model or 'default',
            'prompt': prompt,
            'context': context or {},
            'created_at': datetime.now().isoformat()
        }
        
        # Initialize message queue for this socket
        self.message_queues[socket_id] = deque(maxlen=self.max_queue_size)
        
        # For now, just track locally
        # Note: Specialists are pre-created in Rhetor, we don't need to create them
        if self.debug:
            print(f"Created socket {socket_id} for {ai_name}")
        
        return socket_id
    
    def read(self, socket_id: str) -> list:
        """
        Read messages from AI socket
        Auto-adds [team-chat-from-X] headers
        """
        # Handle broadcast reads
        if socket_id == "team-chat-all":
            messages = []
            for sid, queue in self.message_queues.items():
                if queue:
                    ai_name = self.sockets[sid]['ai_name']
                    while queue:
                        msg = queue.popleft()
                        # Add source header
                        messages.append(f"[team-chat-from-{ai_name}] {msg}")
            return messages
        
        # Read from specific socket
        if socket_id not in self.message_queues:
            return []
        
        queue = self.message_queues[socket_id]
        messages = []
        
        # Get all messages from queue
        while queue:
            msg = queue.popleft()
            ai_name = self.sockets[socket_id]['ai_name']
            # Add source header
            messages.append(f"[team-chat-from-{ai_name}] {msg}")
        
        return messages
    
    def write(self, socket_id: str, message: str) -> bool:
        """
        Write message to AI socket
        Auto-adds [team-chat-to-X] headers
        """
        # Handle broadcast writes
        if socket_id == "team-chat-all":
            return self._write_team_chat(message)
        
        # Write to specific socket
        return self._write_to_socket(socket_id, message)
    
    def _write_to_socket(self, socket_id: str, message: str) -> bool:
        """Internal method to write to a specific socket"""
        if socket_id not in self.sockets:
            return False
        
        socket_info = self.sockets[socket_id]
        ai_name = socket_info['ai_name']
        
        # Add destination header
        message_with_header = f"[team-chat-to-{ai_name}] {message}"
        
        try:
            # Resolve AI name dynamically
            ai_info = self._get_ai_info(ai_name)
            if not ai_info:
                if self.debug:
                    print(f"Could not resolve AI name '{ai_name}'")
                return self._write_via_team_chat(socket_id, ai_name, message)
            
            # Check if this is a Greek Chorus AI (has socket info)
            if 'socket' in ai_info and 'host' in ai_info and 'port' in ai_info:
                return self._write_via_socket(socket_id, ai_info, message)
            
            # Fall back to Rhetor specialist endpoint
            specialist_id = ai_info.get('id', ai_name)
            payload = {
                "message": message,
                "temperature": 0.7
            }
            
            response = requests.post(
                f"{self.rhetor_endpoint}/api/ai/specialists/{specialist_id}/message",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                # Extract the response content
                ai_response = result.get('response', result.get('content', ''))
                
                # Add to message queue for this socket
                if socket_id in self.message_queues:
                    self.message_queues[socket_id].append(ai_response)
                
                return True
            elif response.status_code == 404:
                # Specialist not found, fallback to team chat
                if self.debug:
                    print(f"Specialist {specialist_id} not found, using team chat fallback")
                return self._write_via_team_chat(socket_id, ai_name, message)
            else:
                if self.debug:
                    print(f"Error from Rhetor: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            if self.debug:
                print(f"Error calling Rhetor: {e}")
            return False
    
    def _write_via_team_chat(self, socket_id: str, ai_name: str, message: str) -> bool:
        """Fallback to team chat for a specific AI"""
        try:
            payload = {
                "message": f"[To {ai_name}] {message}",
                "moderation_mode": "pass_through",
                "timeout": 10.0
            }
            
            response = requests.post(
                f"{self.rhetor_endpoint}/api/team-chat",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                responses = result.get('responses', {})
                
                # Look for response from our specific specialist
                specialist_id = self.resolve_ai_name(ai_name) or f"{ai_name}-ai"
                
                if specialist_id in responses:
                    ai_response = responses[specialist_id].get('content', '')
                    if socket_id in self.message_queues:
                        self.message_queues[socket_id].append(ai_response)
                    return True
                elif responses:
                    # Get first response if our specialist didn't respond
                    first_key = list(responses.keys())[0]
                    ai_response = responses[first_key].get('content', '')
                    if socket_id in self.message_queues:
                        self.message_queues[socket_id].append(ai_response)
                    return True
                    
            return False
            
        except Exception as e:
            if self.debug:
                print(f"Error in team chat fallback: {e}")
            return False
    
    def _write_team_chat(self, message: str) -> bool:
        """Send message to all AIs using team-chat endpoint"""
        try:
            # Get list of active AI names
            specialists = [f"{socket['ai_name']}-ai" for socket in self.sockets.values()]
            
            if not specialists:
                if self.debug:
                    print("No active specialists for team chat")
                return False
            
            # Use Rhetor's team-chat API with the correct endpoint and format
            payload = {
                "message": message,
                "moderation_mode": "pass_through",
                "timeout": 10.0
            }
            
            response = requests.post(
                f"{self.rhetor_endpoint}/api/team-chat",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                responses = result.get('responses', {})
                
                # Add responses to appropriate queues
                for socket_id, socket_info in self.sockets.items():
                    ai_id = f"{socket_info['ai_name']}-ai"
                    if ai_id in responses:
                        self.message_queues[socket_id].append(responses[ai_id])
                
                return True
            else:
                if self.debug:
                    print(f"Error from Rhetor team-chat: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            if self.debug:
                print(f"Error calling Rhetor team-chat: {e}")
            return False
    
    def delete(self, socket_id: str) -> bool:
        """Delete AI instance and clean up socket"""
        if socket_id not in self.sockets:
            return False
        
        # Get AI name for context deletion
        ai_name = self.sockets[socket_id]['ai_name']
        
        # TODO: Delete specialist from Rhetor when API is ready
        if self.debug:
            print(f"Would delete specialist {ai_name} from Rhetor")
        
        # Clean up local state
        del self.sockets[socket_id]
        if socket_id in self.message_queues:
            del self.message_queues[socket_id]
        
        return True
    
    def reset(self, socket_id: str) -> bool:
        """Reset AI context while keeping socket alive"""
        if socket_id not in self.sockets:
            return False
        
        # Clear local context
        self.sockets[socket_id]['context'] = {}
        
        # Clear message queue
        if socket_id in self.message_queues:
            self.message_queues[socket_id].clear()
        
        # TODO: Reset specialist in Rhetor when API is ready
        ai_name = self.sockets[socket_id]['ai_name']
        if self.debug:
            print(f"Would reset specialist {ai_name} in Rhetor")
        
        return True
    
    def list_sockets(self) -> Dict[str, Any]:
        """List all registered sockets"""
        return self.sockets.copy()
    
    def get_socket(self, socket_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific socket"""
        return self.sockets.get(socket_id)
    
    def get_active_sockets(self) -> List[str]:
        """Get list of active socket IDs"""
        return list(self.sockets.keys())
    
    def discover_ais(self, force_refresh: bool = False) -> Dict[str, Any]:
        """Discover available AI specialists using ai-discover tool"""
        # Check cache
        if not force_refresh and self._ai_cache and (time.time() - self._cache_time) < self._cache_ttl:
            return self._ai_cache
        
        # Try ai-discover from multiple locations
        ai_discover_configs = [
            {'cmd': 'ai-discover', 'cwd': None},  # In PATH
            {'cmd': 'python', 'args': ['scripts/ai-discover'], 'cwd': '/Users/cskoons/projects/github/Tekton'},  # From Tekton dir
            {'cmd': '../Tekton/scripts/ai-discover', 'cwd': None},  # Relative to aish
        ]
        
        for config in ai_discover_configs:
            try:
                cmd = [config['cmd']]
                if 'args' in config:
                    cmd.extend(config['args'])
                cmd.extend(['--json', 'list'])
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=10,
                    cwd=config.get('cwd')
                )
                
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    # Handle both formats: direct array or {"ais": [...]}
                    ais = data.get('ais', data) if isinstance(data, dict) else data
                    # Create lookup dict by various names
                    self._ai_cache = {}
                    for ai in ais:
                        # Index by id, name, and component
                        ai_id = ai.get('id', ai.get('name', ''))
                        if ai_id:
                            # Extract all fields including connection info
                            ai_info = {
                                'id': ai_id,
                                'name': ai.get('name', ai_id),
                                'component': ai.get('component', ''),
                                'status': ai.get('status', 'unknown'),
                                'capabilities': ai.get('capabilities', [])
                            }
                            # Add connection info if available
                            if 'connection' in ai:
                                ai_info['host'] = ai['connection'].get('host', 'localhost')
                                ai_info['port'] = ai['connection'].get('port')
                                ai_info['socket'] = True  # Mark as socket-based
                            
                            self._ai_cache[ai_id] = ai_info
                            # Also index by short name (without -ai suffix)
                            if ai_id.endswith('-ai'):
                                short_name = ai_id[:-3]
                                self._ai_cache[short_name] = ai_info
                            # Index by component name
                            if 'component' in ai and ai['component']:
                                self._ai_cache[ai['component']] = ai_info
                    self._cache_time = time.time()
                    if self.debug:
                        print(f"Discovered {len(ais)} AIs via {config['cmd']}")
                    return self._ai_cache
            except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError) as e:
                if self.debug:
                    print(f"ai-discover with {config['cmd']} failed: {e}")
                continue
        
        # Fallback to direct API
        try:
            response = requests.get(f"{self.rhetor_endpoint}/api/ai/specialists", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self._ai_cache = {}
                seen_ids = set()
                for spec in data.get('specialists', []):
                    spec_id = spec['id']
                    if spec_id not in seen_ids:
                        seen_ids.add(spec_id)
                        ai_info = {
                            'id': spec_id,
                            'name': spec.get('name', spec_id),
                            'component': spec.get('component_id', ''),
                            'status': spec.get('status', 'unknown'),
                            'capabilities': spec.get('capabilities', [])
                        }
                        self._ai_cache[spec_id] = ai_info
                        # Also index by component name if different
                        if 'component_id' in spec and spec['component_id'] != spec_id:
                            self._ai_cache[spec['component_id']] = ai_info
                self._cache_time = time.time()
                return self._ai_cache
        except Exception as e:
            if self.debug:
                print(f"Failed to discover AIs: {e}")
        
        # Return empty if all discovery fails
        return {}
    
    def resolve_ai_name(self, name: str) -> Optional[str]:
        """Resolve a user-provided AI name to a specialist ID"""
        # Refresh discovery if cache is empty
        if not self._ai_cache:
            self.discover_ais()
        
        # Direct lookup
        if name in self._ai_cache:
            return self._ai_cache[name]['id']
        
        # Try with -ai suffix
        with_suffix = f"{name}-ai"
        if with_suffix in self._ai_cache:
            return with_suffix
        
        # Try prefix match
        for ai_id, ai_info in self._ai_cache.items():
            if ai_id.startswith(name):
                return ai_info['id']
        
        # Try component match
        for ai_id, ai_info in self._ai_cache.items():
            if ai_info.get('component', '').lower() == name.lower():
                return ai_info['id']
        
        # Force refresh and try again
        self.discover_ais(force_refresh=True)
        if name in self._ai_cache:
            return self._ai_cache[name]['id']
        
        # Not found
        if self.debug:
            available = [ai['id'] for ai in self._ai_cache.values()]
            print(f"AI '{name}' not found. Available: {', '.join(available[:5])}")
        
        return None
    
    def _get_ai_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Get full AI info for a name"""
        # Refresh discovery if cache is empty
        if not self._ai_cache:
            self.discover_ais()
        
        # Direct lookup
        if name in self._ai_cache:
            return self._ai_cache[name]
        
        # Try with -ai suffix
        with_suffix = f"{name}-ai"
        if with_suffix in self._ai_cache:
            return self._ai_cache[with_suffix]
        
        # Try prefix match
        for ai_id, ai_info in self._ai_cache.items():
            if ai_id.startswith(name):
                return ai_info
        
        return None
    
    def _write_via_socket(self, socket_id: str, ai_info: Dict[str, Any], message: str) -> bool:
        """Write to AI via direct socket connection using line-buffered protocol"""
        from ..utils.socket_buffer import LineBufferedSocket, SocketTimeoutDetector
        
        detector = SocketTimeoutDetector(debug=self.debug)
        host = ai_info.get('host', 'localhost')
        port = ai_info.get('port')
        
        if not port:
            if self.debug:
                print(f"No port specified for {ai_info['id']}")
            return False
        
        # Create connection with intelligent timeout
        success, sock, error_msg = detector.create_connection(host, port)
        if not success:
            if self.debug:
                print(f"Connection to {ai_info['id']} failed: {error_msg}")
            return False
        
        try:
            # Use line-buffered socket for reliable communication
            buffered_socket = LineBufferedSocket(sock, timeout=30.0, debug=self.debug)
            
            # Send message
            request = {
                "type": "chat",
                "content": message
            }
            
            if not buffered_socket.write_message(request):
                if self.debug:
                    print(f"Failed to send message to {ai_info['id']}")
                buffered_socket.close()
                return False
            
            # Read response with proper buffering
            response = buffered_socket.read_message()
            buffered_socket.close()
            
            if response:
                # Extract content from response
                ai_response = response.get('content', response.get('response', ''))
                
                # Add to message queue
                if socket_id in self.message_queues:
                    self.message_queues[socket_id].append(ai_response)
                
                if self.debug:
                    print(f"Socket response from {ai_info['id']}: {ai_response[:50]}...")
                
                return True
            else:
                if self.debug:
                    print(f"No response from {ai_info['id']}")
                return False
                
        except Exception as e:
            if self.debug:
                print(f"Socket communication with {ai_info['id']} failed: {e}")
            try:
                sock.close()
            except:
                pass
            return False