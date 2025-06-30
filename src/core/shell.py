"""
AIShell - Main shell implementation
"""

import os
import sys
import subprocess
import readline
import atexit
from pathlib import Path

from parser.pipeline import PipelineParser
from registry.socket_registry import SocketRegistry
from core.history import AIHistory

class AIShell:
    """The AI Shell - orchestrates AI pipelines"""
    
    def __init__(self, rhetor_endpoint=None, debug=False):
        if rhetor_endpoint:
            self.rhetor_endpoint = rhetor_endpoint
        else:
            # Check environment variable, then use default
            port = os.environ.get('TEKTON_RHETOR_PORT', '8003')
            self.rhetor_endpoint = f"http://localhost:{port}"
        
        self.debug = debug
        self.parser = PipelineParser()
        self.registry = SocketRegistry(self.rhetor_endpoint, debug=debug)
        self.history_file = Path.home() / '.aish_history'
        self.active_sockets = {}  # Track active socket IDs by AI name
        self.ai_history = AIHistory()  # Conversation history tracker
        
        # Setup readline for interactive mode
        self._setup_readline()
    
    def _setup_readline(self):
        """Configure readline for better interactive experience"""
        # Load history
        if self.history_file.exists():
            readline.read_history_file(self.history_file)
        
        # Save history on exit
        def save_history():
            try:
                if self.history_file.exists():
                    readline.write_history_file(self.history_file)
            except:
                pass  # Ignore errors on exit
        atexit.register(save_history)
        
        # Tab completion would go here
        # readline.set_completer(self._completer)
        # readline.parse_and_bind("tab: complete")
    
    def execute_command(self, command):
        """Execute a single AI pipeline command"""
        try:
            # Parse the command
            pipeline = self.parser.parse(command)
            
            if self.debug:
                print(f"[DEBUG] Parsed pipeline: {pipeline}")
            
            # Execute the pipeline and track responses
            result, responses = self._execute_pipeline_with_tracking(pipeline)
            
            # Add to history if we got responses
            if responses:
                self.ai_history.add_command(command, responses)
            
            # Output result
            if result:
                print(result)
                
        except Exception as e:
            print(f"aish: {e}", file=sys.stderr)
            return 1
        
        return 0
    
    def execute_script(self, script_path):
        """Execute an AI script file"""
        try:
            with open(script_path, 'r') as f:
                # Skip shebang if present
                lines = f.readlines()
                if lines and lines[0].startswith('#!'):
                    lines = lines[1:]
                
                # Execute each line
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        self.execute_command(line)
                        
        except FileNotFoundError:
            print(f"aish: {script_path}: No such file", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"aish: {script_path}: {e}", file=sys.stderr)
            return 1
        
        return 0
    
    def interactive(self):
        """Run interactive AI shell"""
        print("aish - The AI Shell v0.1.0")
        print(f"Connected to Rhetor at: {self.rhetor_endpoint}")
        print("Type 'help' for help, 'exit' to quit")
        print()
        
        while True:
            try:
                # Get command
                command = input("aish> ").strip()
                
                # Handle special commands
                if command == 'exit':
                    break
                elif command == 'help':
                    self._show_help()
                elif command == 'list-ais' or command == 'ais':
                    self._list_ais()
                elif command == 'history':
                    self._show_history()
                elif command.startswith('!'):
                    # Handle history expansion (!number)
                    if command[1:].isdigit():
                        cmd_num = int(command[1:])
                        replay_cmd = self.ai_history.replay(cmd_num)
                        if replay_cmd:
                            print(f"Replaying: {replay_cmd}")
                            self.execute_command(replay_cmd)
                        else:
                            print(f"!{cmd_num}: event not found")
                    else:
                        # Regular shell escape
                        subprocess.run(command[1:], shell=True)
                elif command:
                    self.execute_command(command)
                    
            except KeyboardInterrupt:
                print()  # New line after ^C
                continue
            except EOFError:
                print()  # New line after ^D
                break
    
    def _execute_pipeline(self, pipeline):
        """Execute a parsed pipeline"""
        pipeline_type = pipeline.get('type')
        
        if pipeline_type == 'team-chat':
            return self._execute_team_chat(pipeline['message'])
        elif pipeline_type == 'pipeline':
            return self._execute_pipe_stages(pipeline['stages'])
        elif pipeline_type == 'simple':
            return self._execute_simple_command(pipeline['command'])
        else:
            return f"Unsupported pipeline type: {pipeline_type}"
    
    def _execute_pipeline_with_tracking(self, pipeline):
        """Execute a pipeline and track responses for history.
        
        Returns:
            Tuple of (result_string, responses_dict)
        """
        pipeline_type = pipeline.get('type')
        responses = {}
        
        if pipeline_type == 'team-chat':
            result = self._execute_team_chat(pipeline['message'])
            # Parse team chat responses
            for line in result.split('\n'):
                if line.startswith('[team-chat-from-') and ']' in line:
                    ai_name = line[len('[team-chat-from-'):line.index(']')]
                    message = line[line.index(']')+1:].strip()
                    responses[ai_name] = message
            return result, responses
            
        elif pipeline_type == 'pipeline':
            result, responses = self._execute_pipe_stages_with_tracking(pipeline['stages'])
            return result, responses
            
        elif pipeline_type == 'simple':
            result = self._execute_simple_command(pipeline['command'])
            return result, {}
            
        else:
            return f"Unsupported pipeline type: {pipeline_type}", {}
    
    def _execute_team_chat(self, message):
        """Execute team-chat broadcast"""
        # Send to all active AIs
        self.registry.write("team-chat-all", message)
        
        # Read responses
        responses = self.registry.read("team-chat-all")
        return '\n'.join(responses) if responses else "No responses yet"
    
    def _execute_pipe_stages(self, stages):
        """Execute pipeline stages"""
        current_data = None
        
        for i, stage in enumerate(stages):
            if stage['type'] == 'echo':
                # Start of pipeline with echo
                current_data = stage['content']
            elif stage['type'] == 'ai':
                # Process through AI
                ai_name = stage['name']
                
                # Get or create socket for this AI
                socket_id = self._get_or_create_socket(ai_name)
                
                if current_data is not None:
                    # Write input to AI
                    success = self.registry.write(socket_id, current_data)
                    if not success:
                        return f"Failed to write to {ai_name}"
                    
                    # Read response
                    responses = self.registry.read(socket_id)
                    if responses:
                        # Extract message content (remove header)
                        current_data = responses[0]
                        # Remove header if present
                        if current_data.startswith(f"[team-chat-from-{ai_name}]"):
                            current_data = current_data[len(f"[team-chat-from-{ai_name}]"):].strip()
                    else:
                        current_data = f"No response from {ai_name}"
                else:
                    return f"No input data for {ai_name}"
            else:
                # Other command types
                current_data = f"Unsupported stage type: {stage['type']}"
        
        return current_data if current_data else "Pipeline completed"
    
    def _execute_pipe_stages_with_tracking(self, stages):
        """Execute pipeline stages and track AI responses."""
        current_data = None
        responses = {}
        
        for i, stage in enumerate(stages):
            if stage['type'] == 'echo':
                # Start of pipeline with echo
                current_data = stage['content']
            elif stage['type'] == 'ai':
                # Process through AI
                ai_name = stage['name']
                
                # Get or create socket for this AI
                socket_id = self._get_or_create_socket(ai_name)
                
                if current_data is not None:
                    # Write input to AI
                    success = self.registry.write(socket_id, current_data)
                    if not success:
                        return f"Failed to write to {ai_name}", responses
                    
                    # Read response
                    ai_responses = self.registry.read(socket_id)
                    if ai_responses:
                        # Extract message content (remove header)
                        current_data = ai_responses[0]
                        # Remove header if present
                        if current_data.startswith(f"[team-chat-from-{ai_name}"):
                            current_data = current_data[len(f"[team-chat-from-{ai_name}"):].strip()
                            # Find the closing bracket
                            if current_data.startswith(']'):
                                current_data = current_data[1:].strip()
                        
                        # Track response
                        responses[ai_name] = current_data
                    else:
                        current_data = f"No response from {ai_name}"
                else:
                    return f"No input data for {ai_name}", responses
            else:
                # Other command types
                current_data = f"Unsupported stage type: {stage['type']}"
        
        result = current_data if current_data else "Pipeline completed"
        return result, responses
    
    def _execute_simple_command(self, command):
        """Execute a simple command"""
        return f"Simple command: {command}"
    
    def _get_or_create_socket(self, ai_name):
        """Get existing socket or create new one for AI"""
        if ai_name not in self.active_sockets:
            socket_id = self.registry.create(ai_name)
            self.active_sockets[ai_name] = socket_id
            if self.debug:
                print(f"[DEBUG] Created socket {socket_id} for {ai_name}")
        return self.active_sockets[ai_name]
    
    def _show_help(self):
        """Display help information"""
        print("""
AI Shell Commands:
  echo "text" | ai_name    - Send text to an AI
  ai1 | ai2 | ai3         - Pipeline AIs together  
  team-chat "message"     - Broadcast to all AIs
  list-ais, ais           - List available AI specialists
  history                 - Show recent conversation history
  !number                 - Replay command from history (e.g., !1716)
  !command                - Execute shell command
  help                    - Show this help
  exit                    - Exit aish

Examples:
  echo "analyze this" | apollo
  apollo | athena > output.txt
  team-chat "what should we optimize?"
  !1716                   - Replay command number 1716
  history                 - View recent AI conversations
  
History Management:
  aish-history            - View history (outside of shell)
  aish-history --json     - Export as JSON for processing
  aish-history --search   - Search history
        """)
    
    def _list_ais(self):
        """List available AI specialists"""
        print("Discovering available AI specialists...")
        ais = self.registry.discover_ais(force_refresh=True)
        
        if not ais:
            print("No AI specialists found. Is Rhetor running?")
            return
        
        # Deduplicate first
        unique_ais = {}
        for ai_info in ais.values():
            if ai_info['id'] not in unique_ais:
                unique_ais[ai_info['id']] = ai_info
        
        print(f"\nAvailable AI Specialists ({len(unique_ais)}):")
        print("-" * 60)
        
        # Group by status
        active = []
        inactive = []
        
        for ai_info in unique_ais.values():
            if ai_info.get('status') in ['active', 'healthy']:
                active.append(ai_info)
            else:
                inactive.append(ai_info)
        
        # Show active first (deduplicated)
        if active:
            print("\nActive:")
            seen = set()
            for ai in sorted(active, key=lambda x: x['id']):
                if ai['id'] not in seen:
                    seen.add(ai['id'])
                    caps = ', '.join(ai.get('capabilities', [])[:3])
                    if caps:
                        print(f"  {ai['id']:<20} - {caps}")
                    else:
                        print(f"  {ai['id']}")
        
        # Show inactive
        if inactive:
            print("\nInactive:")
            for ai in sorted(inactive, key=lambda x: x['id']):
                print(f"  {ai['id']:<20} - {ai.get('status', 'unknown')}")
        
        print("\nUse any AI name in a pipeline: echo \"hello\" | apollo")
    
    def _show_history(self):
        """Show recent conversation history."""
        entries = self.ai_history.get_history(20)  # Last 20 entries
        if entries:
            print("Recent conversation history:")
            print("-" * 60)
            for line in entries:
                print(line.rstrip())
            print("-" * 60)
            print("Use !<number> to replay a command (e.g., !1716)")
        else:
            print("No conversation history yet. Start chatting with AIs!")


if __name__ == '__main__':
    # Test shell
    shell = AIShell(debug=True)
    shell.interactive()