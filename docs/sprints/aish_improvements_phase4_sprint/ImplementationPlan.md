# aish Phase 4 Implementation Plan

## 1. SSE Client Implementation

### Basic SSE Client
```python
# src/utils/streaming.py
import asyncio
import aiohttp
from typing import AsyncIterator, Optional

class SSEClient:
    """Server-Sent Events client for streaming AI responses."""
    
    def __init__(self, url: str, headers: Optional[dict] = None):
        self.url = url
        self.headers = headers or {}
        self.headers['Accept'] = 'text/event-stream'
        
    async def stream(self, data: dict) -> AsyncIterator[dict]:
        """Stream responses from SSE endpoint."""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.url,
                json=data,
                headers=self.headers
            ) as response:
                async for line in response.content:
                    if line:
                        decoded = line.decode('utf-8').strip()
                        if decoded.startswith('data: '):
                            try:
                                event_data = json.loads(decoded[6:])
                                yield event_data
                            except json.JSONDecodeError:
                                continue
                        elif decoded == 'event: done':
                            break
```

### Integration with Shell
```python
# src/core/shell.py
async def _execute_streaming_command(self, command: str):
    """Execute command with streaming output."""
    pipeline = self.parser.parse(command)
    
    if pipeline['type'] == 'pipeline' and self._supports_streaming(pipeline):
        await self._stream_pipeline(pipeline)
    else:
        # Fallback to regular execution
        result, responses = self._execute_pipeline_with_tracking(pipeline)
        print(result)

async def _stream_pipeline(self, pipeline):
    """Stream pipeline execution."""
    print("[Streaming...] ", end='', flush=True)
    
    start_time = time.time()
    token_count = 0
    
    async for token in self._execute_pipeline_stream(pipeline):
        print(token, end='', flush=True)
        token_count += 1
    
    elapsed = time.time() - start_time
    print(f"\n[Complete - {elapsed:.1f}s, {token_count} tokens]")
```

## 2. Stream Wrapper Design

### Abstract Stream Interface
```python
# src/utils/stream_wrapper.py
from abc import ABC, abstractmethod
from typing import AsyncIterator, Optional

class StreamWrapper(ABC):
    """Abstract base for all stream types."""
    
    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection."""
        pass
    
    @abstractmethod
    async def send(self, message: str) -> bool:
        """Send message to stream."""
        pass
    
    @abstractmethod
    async def receive(self) -> AsyncIterator[str]:
        """Receive streaming data."""
        pass
    
    @abstractmethod
    async def close(self):
        """Close stream."""
        pass
    
    async def heartbeat_loop(self, interval: float = 25.0):
        """Maintain connection with heartbeats."""
        while self.connected:
            await self.send_heartbeat()
            await asyncio.sleep(interval)

class SSEStreamWrapper(StreamWrapper):
    """SSE implementation of stream wrapper."""
    
    def __init__(self, url: str):
        self.client = SSEClient(url)
        self.connected = False
    
    async def receive(self) -> AsyncIterator[str]:
        async for event in self.client.stream():
            if event.get('event') == 'token':
                yield event.get('data', {}).get('token', '')
```

## 3. Pipeline Context Implementation

### Context-Aware Pipeline Parser
```python
# src/parser/pipeline.py
def parse_with_context(self, command: str, context: dict = None) -> dict:
    """Parse command with context support."""
    base_pipeline = self.parse(command)
    
    if context and base_pipeline.get('type') == 'pipeline':
        # Inject context into pipeline
        base_pipeline['context'] = context
        
        # Add context to each stage
        for stage in base_pipeline.get('stages', []):
            stage['context'] = self._build_stage_context(stage, context)
    
    return base_pipeline
```

### Pipeline Execution with Context
```python
# src/core/shell.py
def _execute_pipe_stages_with_context(self, stages, initial_context=None):
    """Execute pipeline with context passing."""
    current_data = None
    current_context = initial_context or {}
    responses = {}
    
    for i, stage in enumerate(stages):
        if stage['type'] == 'ai':
            ai_name = stage['name']
            
            # Build context for this stage
            stage_context = {
                'pipeline_position': i,
                'previous_ai': list(responses.keys())[-1] if responses else None,
                'previous_response': current_data,
                'memory_hints': stage.get('context', {}).get('memory_hints', [])
            }
            
            # Merge with pipeline context
            stage_context.update(current_context)
            
            # Send with context
            socket_id = self._get_or_create_socket(ai_name)
            message_with_context = {
                'content': current_data,
                'context': stage_context
            }
            
            success = self.registry.write_with_context(socket_id, message_with_context)
            # ... rest of execution
```

## 4. History Streaming Support

### Streaming-Aware History
```python
# src/core/history.py
def add_streaming_command(self, command: str, 
                         responses: Dict[str, str],
                         metadata: Dict[str, Any]) -> int:
    """Add streaming command with metadata."""
    cmd_num = self.command_number
    self.command_number += 1
    
    # Enhanced format for streaming
    text_entry = f"{cmd_num}: {command}\n"
    
    # Add streaming indicator
    if metadata.get('streamed'):
        text_entry += f"      # [Streamed in {metadata['duration']:.1f}s]\n"
    
    # Add responses as usual
    for ai_name, response in responses.items():
        truncated = response[:100] + "..." if len(response) > 100 else response
        text_entry += f"      # {ai_name}: {truncated}\n"
    
    # JSON includes full metadata
    json_entry = {
        "number": cmd_num,
        "timestamp": time.time(),
        "command": command,
        "responses": responses,
        "metadata": metadata  # Includes streaming info
    }
```

## 5. Testing Strategy

### Streaming Test
```python
# tests/test_streaming.py
async def test_sse_streaming():
    """Test SSE streaming functionality."""
    shell = AIShell()
    
    # Mock SSE endpoint
    with aioresponses() as mocked:
        mocked.post(
            'http://localhost:8003/api/chat/athena-ai/stream',
            status=200,
            body='''data: {"event": "token", "data": {"token": "Hello"}}
data: {"event": "token", "data": {"token": " from"}}
data: {"event": "token", "data": {"token": " streaming!"}}
event: done
'''
        )
        
        # Execute streaming command
        tokens = []
        async for token in shell._stream_to_ai('athena', 'Test message'):
            tokens.append(token)
        
        assert tokens == ['Hello', ' from', ' streaming!']
```

### Pipeline Context Test
```python
def test_pipeline_context():
    """Test context passing in pipelines."""
    shell = AIShell()
    
    # Execute with context
    context = {'session_id': 'test-123', 'memory_hints': ['previous discussion']}
    result = shell.execute_command_with_context(
        'echo "Continue the thought" | apollo | athena',
        context
    )
    
    # Verify context was passed
    # Check that apollo received context
    # Check that athena received apollo's response as context
```

## 6. Performance Considerations

1. **Token Buffering**: Buffer tokens for smoother display
2. **Async Display**: Don't block on terminal output
3. **Memory Management**: Stream large responses without storing all
4. **Reconnection**: Automatic retry with exponential backoff

## 7. Fallback Strategy

If streaming is not available:
1. Check endpoint availability
2. Fall back to regular request/response
3. Notify user of degraded mode
4. Still record in history properly