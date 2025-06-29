#!/usr/bin/env python3
"""
Functional tests for aish - The AI Shell
Tests basic functionality without requiring Rhetor to be running
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from registry.socket_registry import SocketRegistry
from parser.pipeline import PipelineParser
from core.shell import AIShell
import unittest
from unittest.mock import patch, MagicMock
import subprocess

class TestPipelineParser(unittest.TestCase):
    """Test the pipeline parser"""
    
    def setUp(self):
        self.parser = PipelineParser()
    
    def test_parse_echo_pipe(self):
        """Test parsing echo | ai command"""
        result = self.parser.parse('echo "Hello" | apollo')
        self.assertEqual(result['type'], 'pipeline')
        self.assertEqual(len(result['stages']), 2)
        self.assertEqual(result['stages'][0]['type'], 'echo')
        self.assertEqual(result['stages'][0]['content'], 'Hello')
        self.assertEqual(result['stages'][1]['type'], 'ai')
        self.assertEqual(result['stages'][1]['name'], 'apollo')
    
    def test_parse_team_chat(self):
        """Test parsing team-chat command"""
        result = self.parser.parse('team-chat "Hello team"')
        self.assertEqual(result['type'], 'team-chat')
        self.assertEqual(result['message'], 'Hello team')
    
    def test_parse_multi_pipe(self):
        """Test parsing multi-stage pipeline"""
        result = self.parser.parse('echo "test" | apollo | athena | hermes')
        self.assertEqual(result['type'], 'pipeline')
        self.assertEqual(len(result['stages']), 4)
        ai_names = [s['name'] for s in result['stages'] if s['type'] == 'ai']
        self.assertEqual(ai_names, ['apollo', 'athena', 'hermes'])
    
    def test_parse_redirect(self):
        """Test parsing output redirect"""
        result = self.parser.parse('apollo > output.txt')
        self.assertEqual(result['type'], 'redirect')
        self.assertEqual(result['command'], 'apollo')
        self.assertEqual(result['output'], 'output.txt')

class TestSocketRegistry(unittest.TestCase):
    """Test the socket registry"""
    
    def setUp(self):
        self.registry = SocketRegistry(debug=False)
    
    def test_create_socket(self):
        """Test creating a socket"""
        socket_id = self.registry.create("apollo")
        self.assertIsNotNone(socket_id)
        self.assertTrue(socket_id.startswith("apollo-"))
        self.assertIn(socket_id, self.registry.sockets)
    
    def test_list_sockets(self):
        """Test listing sockets"""
        # Create a few sockets
        id1 = self.registry.create("apollo")
        id2 = self.registry.create("athena")
        
        sockets = self.registry.list_sockets()
        self.assertEqual(len(sockets), 2)
        self.assertIn(id1, sockets)
        self.assertIn(id2, sockets)
    
    def test_delete_socket(self):
        """Test deleting a socket"""
        socket_id = self.registry.create("apollo")
        success = self.registry.delete(socket_id)
        self.assertTrue(success)
        self.assertNotIn(socket_id, self.registry.sockets)
    
    def test_reset_socket(self):
        """Test resetting a socket"""
        socket_id = self.registry.create("apollo", context={"test": "data"})
        success = self.registry.reset(socket_id)
        self.assertTrue(success)
        self.assertEqual(self.registry.sockets[socket_id]['context'], {})
    
    def test_write_and_read_flow(self):
        """Test basic write and read flow without external dependencies"""
        # Create a socket
        socket_id = self.registry.create("test-ai")
        
        # Manually add a message to the queue (simulating a response)
        self.registry.message_queues[socket_id].append("Test response")
        
        # Read the message
        messages = self.registry.read(socket_id)
        
        # Verify the message includes the header
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0], "[team-chat-from-test-ai] Test response")
        
    def test_team_chat_broadcast(self):
        """Test team chat functionality"""
        # Create multiple sockets
        socket1 = self.registry.create("ai1")
        socket2 = self.registry.create("ai2")
        
        # Add messages to their queues
        self.registry.message_queues[socket1].append("Response from AI1")
        self.registry.message_queues[socket2].append("Response from AI2")
        
        # Read team chat
        messages = self.registry.read("team-chat-all")
        
        # Should get messages from both AIs
        self.assertEqual(len(messages), 2)
        self.assertIn("[team-chat-from-ai1] Response from AI1", messages)
        self.assertIn("[team-chat-from-ai2] Response from AI2", messages)

class TestAIShell(unittest.TestCase):
    """Test the AI shell"""
    
    def setUp(self):
        self.shell = AIShell(debug=False)
    
    def test_parse_pipeline(self):
        """Test shell can parse pipeline"""
        pipeline = self.shell.parser.parse('echo "test" | apollo')
        self.assertEqual(pipeline['type'], 'pipeline')
    
    @patch.object(SocketRegistry, 'write')
    @patch.object(SocketRegistry, 'read')
    def test_execute_pipeline(self, mock_read, mock_write):
        """Test executing a pipeline"""
        # Setup mocks
        mock_write.return_value = True
        mock_read.return_value = ['Mock response from apollo']
        
        # Execute pipeline
        result = self.shell.execute_command('echo "Hello" | apollo')
        
        # Verify
        mock_write.assert_called_once()
        mock_read.assert_called_once()

if __name__ == '__main__':
    unittest.main()