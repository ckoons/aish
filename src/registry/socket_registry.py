"""
Socket Registry - Manages AI socket connections
"""

from typing import Dict, Optional, Any, List
from collections import deque
from datetime import datetime
import requests
import json
import os

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
            # Map short names to full specialist IDs
            specialist_map = {
                'apollo': 'apollo-coordinator',
                'athena': 'athena-analyst',
                'hermes': 'hermes-messenger',
                'prometheus': 'prometheus-strategist',
                'rhetor': 'rhetor-orchestrator',
                'engram': 'engram-memory',
                'sophia': 'sophia-researcher'
            }
            
            specialist_id = specialist_map.get(ai_name, f"{ai_name}-coordinator")
            
            # Try the direct specialist endpoint first
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
                specialist_map = {
                    'apollo': 'apollo-coordinator',
                    'athena': 'athena-analyst',
                    'hermes': 'hermes-messenger',
                    'prometheus': 'prometheus-strategist',
                    'rhetor': 'rhetor-orchestrator',
                    'engram': 'engram-memory',
                    'sophia': 'sophia-researcher'
                }
                
                specialist_id = specialist_map.get(ai_name, f"{ai_name}-coordinator")
                
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