"""
Line-buffered socket utilities for reliable JSON message handling.

This module provides utilities for reading newline-delimited JSON messages
from sockets, handling partial reads and message boundaries correctly.
"""

import json
import socket
import time
import threading
from typing import Optional, Dict, Any, Tuple


class LineBufferedSocket:
    """
    A wrapper around socket that handles line-buffered reading of JSON messages.
    
    This class accumulates partial reads until a complete newline-delimited
    message is received, then parses and returns the JSON object.
    """
    
    def __init__(self, sock: socket.socket, timeout: float = 30.0, debug: bool = False,
                 heartbeat_handler: Optional['SocketTimeoutDetector'] = None):
        """
        Initialize the line-buffered socket wrapper.
        
        Args:
            sock: The underlying socket
            timeout: Read timeout in seconds
            debug: Enable debug logging
            heartbeat_handler: Optional heartbeat detector for tracking keepalives
        """
        self.socket = sock
        self.timeout = timeout
        self.debug = debug
        self.buffer = b""
        self.socket.settimeout(timeout)
        self.heartbeat_handler = heartbeat_handler
        
    def read_message(self) -> Optional[Dict[str, Any]]:
        """
        Read a complete JSON message from the socket.
        
        Returns:
            Parsed JSON message or None if connection closed
            
        Raises:
            socket.timeout: If no data received within timeout
            json.JSONDecodeError: If message is not valid JSON
        """
        while True:
            # Check if we have a complete message in the buffer
            if b'\n' in self.buffer:
                line, self.buffer = self.buffer.split(b'\n', 1)
                if line:
                    try:
                        message = json.loads(line.decode('utf-8'))
                        if self.debug:
                            print(f"[DEBUG] Received message: {message}")
                        
                        # Handle heartbeat messages
                        if message.get('type') == 'ping' or message.get('type') == 'heartbeat':
                            if self.heartbeat_handler:
                                self.heartbeat_handler.record_heartbeat()
                            if self.debug:
                                print("[DEBUG] Heartbeat received")
                            # Continue reading for actual messages
                            continue
                            
                        return message
                    except json.JSONDecodeError as e:
                        if self.debug:
                            print(f"[DEBUG] JSON decode error: {e}, line: {line}")
                        # Skip invalid JSON and continue
                        continue
            
            # Read more data
            try:
                chunk = self.socket.recv(4096)
                if not chunk:
                    # Connection closed
                    if self.debug:
                        print("[DEBUG] Socket connection closed")
                    return None
                    
                self.buffer += chunk
                if self.debug:
                    print(f"[DEBUG] Read {len(chunk)} bytes, buffer size: {len(self.buffer)}")
                    
            except socket.timeout:
                if self.debug:
                    print(f"[DEBUG] Socket timeout after {self.timeout}s")
                raise
                
    def write_message(self, message: Dict[str, Any]) -> bool:
        """
        Write a JSON message to the socket.
        
        Args:
            message: Dictionary to send as JSON
            
        Returns:
            True if successful, False otherwise
        """
        try:
            data = json.dumps(message).encode('utf-8') + b'\n'
            self.socket.sendall(data)
            if self.debug:
                print(f"[DEBUG] Sent message: {message}")
            return True
        except Exception as e:
            if self.debug:
                print(f"[DEBUG] Error sending message: {e}")
            return False
            
    def close(self):
        """Close the underlying socket."""
        try:
            self.socket.close()
        except:
            pass
    
    def start_heartbeat(self, interval: float = 25.0, source_id: str = "aish-client"):
        """
        Start sending periodic heartbeat messages.
        
        Args:
            interval: Heartbeat interval in seconds
            source_id: Identifier for this client
        """
        def send_heartbeat():
            while True:
                try:
                    if self.socket.fileno() == -1:  # Socket closed
                        break
                    
                    heartbeat = {
                        "type": "ping",
                        "timestamp": int(time.time()),
                        "source": source_id
                    }
                    
                    self.write_message(heartbeat)
                    if self.debug:
                        print(f"[DEBUG] Sent heartbeat at {heartbeat['timestamp']}")
                    
                    time.sleep(interval)
                except Exception as e:
                    if self.debug:
                        print(f"[DEBUG] Heartbeat thread error: {e}")
                    break
        
        # Start heartbeat thread
        heartbeat_thread = threading.Thread(target=send_heartbeat, daemon=True)
        heartbeat_thread.start()
        
        if self.debug:
            print(f"[DEBUG] Started heartbeat thread with {interval}s interval")


class SocketTimeoutDetector:
    """
    Intelligent timeout detection that distinguishes between:
    - Network failures (immediate)
    - AI processing delays (reasonable timeout)
    - Dead connections (no heartbeat)
    """
    
    def __init__(self, 
                 connection_timeout: float = 2.0,
                 response_timeout: float = 30.0,
                 heartbeat_interval: float = 25.0,
                 debug: bool = False):
        """
        Initialize the timeout detector.
        
        Args:
            connection_timeout: Timeout for initial connection
            response_timeout: Timeout for AI response
            heartbeat_interval: Expected heartbeat interval
            debug: Enable debug logging
        """
        self.connection_timeout = connection_timeout
        self.response_timeout = response_timeout
        self.heartbeat_interval = heartbeat_interval
        self.debug = debug
        self.last_heartbeat = time.time()
        
    def create_connection(self, host: str, port: int) -> Tuple[bool, Optional[socket.socket], str]:
        """
        Create a socket connection with intelligent timeout.
        
        Returns:
            (success, socket_or_none, error_message)
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.connection_timeout)
        
        try:
            sock.connect((host, port))
            sock.settimeout(self.response_timeout)  # Switch to response timeout
            return True, sock, ""
        except socket.timeout:
            sock.close()
            return False, None, f"Connection timeout after {self.connection_timeout}s - network issue"
        except Exception as e:
            sock.close()
            return False, None, f"Connection failed: {e}"
            
    def check_heartbeat(self) -> Tuple[bool, str]:
        """
        Check if heartbeat is overdue.
        
        Returns:
            (is_alive, status_message)
        """
        elapsed = time.time() - self.last_heartbeat
        if elapsed > self.heartbeat_interval * 2:
            return False, f"No heartbeat for {elapsed:.1f}s - connection may be dead"
        elif elapsed > self.heartbeat_interval * 1.5:
            return True, f"Heartbeat delayed ({elapsed:.1f}s) - AI may be busy"
        else:
            return True, "Connection healthy"
            
    def record_heartbeat(self):
        """Record that a heartbeat was received."""
        self.last_heartbeat = time.time()
        if self.debug:
            print(f"[DEBUG] Heartbeat recorded at {self.last_heartbeat}")