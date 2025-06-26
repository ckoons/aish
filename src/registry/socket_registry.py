"""
Socket Registry - Manages AI socket connections
"""

from typing import Dict, Optional, Any, List
from collections import deque
from datetime import datetime
import requests
import json
import asyncio
import aiohttp

class SocketRegistry:
    """Registry for AI sockets managed by Rhetor"""
    
    def __init__(self, rhetor_endpoint: str = "http://localhost:8003"):
        self.rhetor_endpoint = rhetor_endpoint
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
        
        # Create context in Rhetor
        try:
            simple_context = {
                "role": ai_name,
                "task": "aish-pipeline", 
                "data": context or {}
            }
            response = requests.post(
                f"{self.rhetor_endpoint}/contexts/{ai_name}",
                json=simple_context
            )
            if response.status_code != 200:
                print(f"Warning: Failed to create context in Rhetor: {response.text}")
        except Exception as e:
            print(f"Warning: Could not connect to Rhetor: {e}")
        
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
            success = True
            for sid in self.sockets:
                if not self._write_to_socket(sid, message):
                    success = False
            return success
        
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
            # Call Rhetor's completion API
            payload = {
                "message": message,
                "context_id": socket_id,
                "system_prompt": socket_info.get('prompt', ''),
                "component_name": ai_name,
                "provider_id": "ollama",  # Default provider
                "model_id": socket_info.get('model', 'llama3.3')
            }
            
            response = requests.post(
                f"{self.rhetor_endpoint}/complete",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                # Extract the actual response message
                ai_response = result.get('response', result.get('content', ''))
                
                # Add to message queue for this socket
                if socket_id in self.message_queues:
                    self.message_queues[socket_id].append(ai_response)
                
                return True
            else:
                print(f"Error from Rhetor: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"Error calling Rhetor: {e}")
            return False
    
    def delete(self, socket_id: str) -> bool:
        """Delete AI instance and clean up socket"""
        if socket_id not in self.sockets:
            return False
        
        # Get AI name for context deletion
        ai_name = self.sockets[socket_id]['ai_name']
        
        # Delete context from Rhetor
        try:
            response = requests.delete(f"{self.rhetor_endpoint}/contexts/{ai_name}")
            if response.status_code not in [200, 204, 404]:
                print(f"Warning: Failed to delete context from Rhetor: {response.text}")
        except Exception as e:
            print(f"Warning: Could not delete context from Rhetor: {e}")
        
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
        
        # Reset context in Rhetor
        ai_name = self.sockets[socket_id]['ai_name']
        try:
            # Delete and recreate context
            requests.delete(f"{self.rhetor_endpoint}/contexts/{ai_name}")
            
            simple_context = {
                "role": ai_name,
                "task": "aish-pipeline",
                "data": {}
            }
            response = requests.post(
                f"{self.rhetor_endpoint}/contexts/{ai_name}",
                json=simple_context
            )
            if response.status_code != 200:
                print(f"Warning: Failed to reset context in Rhetor: {response.text}")
        except Exception as e:
            print(f"Warning: Could not reset context in Rhetor: {e}")
        
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