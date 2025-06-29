# Implementation Plan - Tekton-aish Improvement Sprint

## Overview

This document provides detailed implementation guidance for each component of the Tekton-aish improvements.

## Component 1: Streaming Implementation

### Tekton Side - SSE Streaming

```python
# rhetor/api/streaming.py
import asyncio
from aiohttp import web
from aiohttp_sse import sse_response

async def stream_specialist_response(request):
    specialist_id = request.match_info['specialist_id']
    message = await request.json()
    
    async with sse_response(request) as resp:
        async for chunk in specialist.generate_stream(message['content']):
            await resp.send(json.dumps({
                'type': 'content',
                'data': chunk,
                'specialist_id': specialist_id
            }))
        
        # Send completion event
        await resp.send(json.dumps({
            'type': 'done',
            'specialist_id': specialist_id
        }))
    
    return resp

# rhetor/models/specialist.py
class Specialist:
    async def generate_stream(self, prompt):
        """Generate response in chunks"""
        async for chunk in self.model.stream(prompt):
            yield chunk
```

### aish Side - Stream Processing

```python
# socket_registry.py additions
import aiohttp
import asyncio

class SocketRegistry:
    async def write_stream(self, socket_id: str, message: str, callback):
        """Write message and stream response"""
        socket_info = self.sockets.get(socket_id)
        if not socket_info:
            return False
        
        ai_name = socket_info['ai_name']
        ai_info = self._get_ai_info(ai_name)
        
        # Check if streaming supported
        if ai_info.get('capabilities', {}).get('streaming'):
            url = f"{self.rhetor_endpoint}/api/v2/ai/{ai_name}/stream"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json={'content': message}) as resp:
                    async for line in resp.content:
                        if line:
                            data = json.loads(line.decode('utf-8').strip('data: '))
                            if data['type'] == 'content':
                                callback(data['data'])
                            elif data['type'] == 'done':
                                break
            return True
        else:
            # Fallback to non-streaming
            return self.write(socket_id, message)
```

### Shell Integration

```python
# shell.py modifications
class AIShell:
    def _execute_pipe_stages_streaming(self, stages):
        """Execute pipeline with streaming support"""
        async def stream_pipeline():
            current_data = None
            
            for i, stage in enumerate(stages):
                if stage['type'] == 'echo':
                    current_data = stage['content']
                elif stage['type'] == 'ai':
                    ai_name = stage['name']
                    socket_id = self._get_or_create_socket(ai_name)
                    
                    # Stream response with live output
                    chunks = []
                    def print_chunk(chunk):
                        print(chunk, end='', flush=True)
                        chunks.append(chunk)
                    
                    await self.registry.write_stream(socket_id, current_data, print_chunk)
                    current_data = ''.join(chunks)
                    print()  # New line after streaming
        
        # Run async pipeline
        asyncio.run(stream_pipeline())
```

## Component 2: Session Management

### Tekton Side - Session API

```python
# rhetor/api/sessions.py
from datetime import datetime, timedelta
import uuid

class SessionManager:
    def __init__(self, store):
        self.store = store  # Redis or SQLite backend
    
    async def create_session(self, specialist_id, context_window=10):
        session = {
            'id': str(uuid.uuid4()),
            'specialist_id': specialist_id,
            'created_at': datetime.utcnow(),
            'context_window': context_window,
            'messages': [],
            'metadata': {}
        }
        await self.store.set(session['id'], session, ttl=3600)
        return session
    
    async def add_message(self, session_id, role, content):
        session = await self.store.get(session_id)
        if not session:
            raise SessionNotFoundError(session_id)
        
        session['messages'].append({
            'role': role,
            'content': content,
            'timestamp': datetime.utcnow()
        })
        
        # Prune old messages
        if len(session['messages']) > session['context_window'] * 2:
            session['messages'] = session['messages'][-session['context_window']:]
        
        await self.store.set(session_id, session, ttl=3600)
        return session

# rhetor/api/endpoints.py
async def create_session(request):
    data = await request.json()
    session = await session_manager.create_session(
        specialist_id=data['specialist_id'],
        context_window=data.get('context_window', 10)
    )
    return web.json_response(session)

async def session_message(request):
    session_id = request.match_info['session_id']
    data = await request.json()
    
    # Add user message
    await session_manager.add_message(session_id, 'user', data['message'])
    
    # Get specialist response with context
    session = await session_manager.get(session_id)
    context = [msg for msg in session['messages'][-session['context_window']:]]
    
    response = await specialist.generate(context)
    
    # Add AI response
    await session_manager.add_message(session_id, 'assistant', response)
    
    return web.json_response({'response': response, 'session_id': session_id})
```

### aish Side - Session Tracking

```python
# socket_registry.py additions
class SocketRegistry:
    def __init__(self, rhetor_endpoint=None, debug=False):
        # ... existing init ...
        self.sessions = {}  # Track sessions by socket_id
    
    async def create_session(self, ai_name: str, context_window: int = 10):
        """Create a new session for an AI"""
        payload = {
            'specialist_id': self._resolve_ai_name(ai_name),
            'context_window': context_window
        }
        
        response = requests.post(
            f"{self.rhetor_endpoint}/api/v2/sessions",
            json=payload
        )
        
        if response.status_code == 200:
            session = response.json()
            return session['id']
        return None
    
    def create_with_session(self, ai_name: str, context_window: int = 10):
        """Create socket with associated session"""
        socket_id = self.create(ai_name)
        session_id = asyncio.run(self.create_session(ai_name, context_window))
        
        if session_id:
            self.sessions[socket_id] = session_id
            self.sockets[socket_id]['session_id'] = session_id
        
        return socket_id

# shell.py additions
class AIShell:
    def execute_command(self, command):
        # Check for session syntax
        if '--session' in command or '-s' in command:
            # Extract session parameters
            # echo "Hello" | apollo --session 10
            self.use_sessions = True
```

## Component 3: Bulk Operations

### Tekton Side - Bulk Endpoint

```python
# rhetor/api/bulk.py
import asyncio
from concurrent.futures import ThreadPoolExecutor

class BulkOperationHandler:
    def __init__(self, max_parallel=20):
        self.executor = ThreadPoolExecutor(max_workers=max_parallel)
    
    async def execute_bulk(self, operations, execution_mode='parallel'):
        results = {}
        
        if execution_mode == 'parallel':
            # Execute all independent operations in parallel
            tasks = []
            for op in operations:
                if not op.get('depends_on'):
                    task = self._execute_operation(op, results)
                    tasks.append(task)
            
            await asyncio.gather(*tasks)
            
            # Execute dependent operations
            await self._execute_dependencies(operations, results)
        else:
            # Sequential execution
            for op in operations:
                await self._execute_operation(op, results)
        
        return results
    
    async def _execute_operation(self, operation, results):
        op_id = operation['id']
        
        # Wait for dependencies
        if operation.get('depends_on'):
            for dep in operation['depends_on']:
                while dep not in results:
                    await asyncio.sleep(0.1)
        
        # Execute operation
        specialist = self.get_specialist(operation['ai'])
        
        # Prepare message with dependency results
        message = operation['message']
        if operation.get('depends_on'):
            context = {dep: results[dep]['response'] for dep in operation['depends_on']}
            message = self._inject_context(message, context)
        
        response = await specialist.generate(message)
        
        results[op_id] = {
            'status': 'success',
            'response': response,
            'ai': operation['ai'],
            'execution_time': time.time() - start_time
        }
```

### aish Side - Bulk Pipeline Optimization

```python
# parser/pipeline.py additions
class PipelineParser:
    def parse_bulk(self, command):
        """Parse bulk pipeline syntax"""
        # Syntax: apollo,athena,prometheus << "message"
        # Or: {apollo|athena} | prometheus
        
        if '<<' in command:
            # Broadcast to multiple AIs
            ais, message = command.split('<<')
            ai_list = [ai.strip() for ai in ais.split(',')]
            return {
                'type': 'bulk-broadcast',
                'ais': ai_list,
                'message': message.strip().strip('"')
            }
        elif '{' in command and '}' in command:
            # Parallel execution block
            return self._parse_parallel_block(command)

# socket_registry.py additions
class SocketRegistry:
    async def write_bulk(self, operations):
        """Execute bulk operations efficiently"""
        payload = {
            'operations': operations,
            'execution': 'parallel'
        }
        
        response = requests.post(
            f"{self.rhetor_endpoint}/api/v2/bulk",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()
        return None
```

## Component 4: Enhanced Discovery

### Tekton Side - Capability Registry

```python
# shared/ai/capability_registry.py
class CapabilityRegistry:
    def __init__(self):
        self.capabilities = {
            'apollo-ai': {
                'primary': ['code-analysis', 'debugging', 'optimization'],
                'scores': {
                    'code-analysis': 0.95,
                    'debugging': 0.90,
                    'planning': 0.70,
                    'creative-writing': 0.30,
                    'data-analysis': 0.75
                },
                'context_window': 100000,
                'max_tokens': 4000,
                'avg_response_time': 1.2,
                'success_rate': 0.98,
                'cost_per_1k_tokens': 0.002
            },
            # ... other AIs ...
        }
    
    def match_capability(self, required_capability, threshold=0.7):
        """Find AIs that match a capability above threshold"""
        matches = []
        
        for ai_id, caps in self.capabilities.items():
            score = caps['scores'].get(required_capability, 0)
            if score >= threshold:
                matches.append({
                    'ai_id': ai_id,
                    'score': score,
                    'primary': required_capability in caps['primary']
                })
        
        # Sort by score, preferring primary capabilities
        matches.sort(key=lambda x: (x['primary'], x['score']), reverse=True)
        return matches

# Integration with discovery
class AIDiscoveryService:
    def get_ai_info(self, ai_id):
        info = super().get_ai_info(ai_id)
        
        # Add capability information
        if ai_id in self.capability_registry.capabilities:
            info['capabilities'] = self.capability_registry.capabilities[ai_id]
        
        return info
```

### aish Side - Intelligent Routing

```python
# socket_registry.py additions
class SocketRegistry:
    def find_best_ai(self, task_type):
        """Find the best AI for a given task"""
        ais = self.discover_ais()
        
        best_match = None
        best_score = 0
        
        for ai_id, ai_info in ais.items():
            if 'capabilities' in ai_info and 'scores' in ai_info['capabilities']:
                score = ai_info['capabilities']['scores'].get(task_type, 0)
                if score > best_score:
                    best_score = score
                    best_match = ai_id
        
        return best_match if best_score > 0.5 else None

# shell.py additions
class AIShell:
    def _execute_capability_routing(self, command):
        """Route to best AI based on capability"""
        # Syntax: @code-analysis << "review this function"
        match = re.match(r'@(\w+)\s*<<\s*"([^"]+)"', command)
        if match:
            capability = match.group(1)
            message = match.group(2)
            
            # Find best AI
            ai_name = self.registry.find_best_ai(capability)
            if ai_name:
                print(f"Routing to {ai_name} (best match for {capability})")
                return self.execute_command(f'echo "{message}" | {ai_name}')
            else:
                print(f"No AI found for capability: {capability}")
```

## Component 5: WebSocket Implementation

### Tekton Side - WebSocket Server

```python
# rhetor/websocket/server.py
from aiohttp import web
import aiohttp
import weakref
import json

class WebSocketManager:
    def __init__(self):
        self._connections = weakref.WeakObjectKeySet()
    
    async def handle_websocket(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        self._connections.add(ws)
        specialist_id = request.match_info.get('specialist_id')
        
        try:
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    
                    if data.get('method') == 'chat':
                        # Handle chat message
                        response = await self._handle_chat(
                            specialist_id, 
                            data.get('params', {})
                        )
                        await ws.send_json(response)
                    
                    elif data.get('method') == 'stream':
                        # Handle streaming request
                        await self._handle_stream(
                            ws,
                            specialist_id,
                            data.get('params', {})
                        )
                
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    print(f'WebSocket error: {ws.exception()}')
        
        finally:
            self._connections.discard(ws)
        
        return ws
    
    async def _handle_stream(self, ws, specialist_id, params):
        """Stream response over WebSocket"""
        specialist = self.get_specialist(specialist_id)
        
        async for chunk in specialist.generate_stream(params.get('message')):
            await ws.send_json({
                'jsonrpc': '2.0',
                'method': 'stream.chunk',
                'params': {
                    'content': chunk,
                    'specialist_id': specialist_id
                }
            })
        
        # Send completion
        await ws.send_json({
            'jsonrpc': '2.0',
            'method': 'stream.complete',
            'params': {'specialist_id': specialist_id}
        })
```

### aish Side - WebSocket Client

```python
# socket_registry.py additions
import websockets
import asyncio

class SocketRegistry:
    async def connect_websocket(self, ai_name):
        """Establish WebSocket connection to AI"""
        ai_info = self._get_ai_info(ai_name)
        
        if ai_info and ai_info.get('websocket_supported'):
            uri = f"ws://{ai_info['host']}:{ai_info['port']}/ws/ai/{ai_info['id']}"
            
            try:
                websocket = await websockets.connect(uri)
                return WebSocketConnection(websocket, ai_name)
            except Exception as e:
                if self.debug:
                    print(f"WebSocket connection failed: {e}")
        
        return None

class WebSocketConnection:
    def __init__(self, websocket, ai_name):
        self.websocket = websocket
        self.ai_name = ai_name
        self.request_id = 0
    
    async def send_message(self, message):
        """Send message and get response"""
        self.request_id += 1
        
        await self.websocket.send(json.dumps({
            'jsonrpc': '2.0',
            'method': 'chat',
            'params': {'message': message},
            'id': self.request_id
        }))
        
        response = await self.websocket.recv()
        return json.loads(response)
    
    async def stream_message(self, message, callback):
        """Send message and stream response"""
        self.request_id += 1
        
        await self.websocket.send(json.dumps({
            'jsonrpc': '2.0',
            'method': 'stream',
            'params': {'message': message},
            'id': self.request_id
        }))
        
        while True:
            response = await self.websocket.recv()
            data = json.loads(response)
            
            if data.get('method') == 'stream.chunk':
                callback(data['params']['content'])
            elif data.get('method') == 'stream.complete':
                break
    
    async def close(self):
        await self.websocket.close()

# shell.py interactive mode enhancement
class AIShell:
    async def interactive_session(self, ai_name):
        """Start interactive WebSocket session with AI"""
        connection = await self.registry.connect_websocket(ai_name)
        
        if not connection:
            print(f"Could not establish WebSocket connection to {ai_name}")
            return
        
        print(f"Connected to {ai_name}. Type 'exit' to end session.")
        
        try:
            while True:
                message = input(f"{ai_name}> ")
                if message.lower() == 'exit':
                    break
                
                # Stream response
                await connection.stream_message(
                    message,
                    lambda chunk: print(chunk, end='', flush=True)
                )
                print()  # New line after response
        
        finally:
            await connection.close()
```

## Testing Strategy

### Unit Tests
```python
# tests/test_streaming.py
async def test_sse_streaming():
    """Test SSE streaming functionality"""
    async with aiohttp.ClientSession() as session:
        url = "http://localhost:8003/api/v2/ai/apollo-ai/stream"
        chunks = []
        
        async with session.post(url, json={'content': 'Hello'}) as resp:
            async for line in resp.content:
                if line:
                    chunks.append(line)
        
        assert len(chunks) > 0
        assert any(b'done' in chunk for chunk in chunks)

# tests/test_sessions.py
def test_session_management():
    """Test session creation and message handling"""
    # Create session
    response = requests.post(
        "http://localhost:8003/api/v2/sessions",
        json={'specialist_id': 'apollo-ai'}
    )
    session = response.json()
    
    # Send message with session
    response = requests.post(
        f"http://localhost:8003/api/v2/sessions/{session['id']}/message",
        json={'message': 'Hello'}
    )
    
    assert response.status_code == 200
    assert 'response' in response.json()
```

### Integration Tests
```python
# tests/test_integration_streaming.py
def test_aish_streaming_pipeline():
    """Test streaming through aish pipeline"""
    # This will require actual implementation
    # but should verify end-to-end streaming works
    pass
```

### Performance Tests
```python
# tests/test_performance.py
def test_bulk_performance():
    """Ensure bulk operations are faster than sequential"""
    # Time sequential execution
    start = time.time()
    for ai in ['apollo', 'athena', 'prometheus']:
        subprocess.run(['./aish', '-c', f'echo "test" | {ai}'])
    sequential_time = time.time() - start
    
    # Time bulk execution
    start = time.time()
    subprocess.run(['./aish', '-c', 'apollo,athena,prometheus << "test"'])
    bulk_time = time.time() - start
    
    assert bulk_time < sequential_time * 0.6  # At least 40% faster
```

## Migration Guide

### For Existing aish Users
1. Streaming is automatic when available
2. Use `--session` flag for stateful conversations
3. New bulk syntax: `ai1,ai2,ai3 << "message"`
4. Capability routing: `@code-analysis << "message"`

### For API Clients
1. Check `/api/capabilities` for feature availability
2. SSE endpoints at `/api/v2/ai/{id}/stream`
3. Session endpoints at `/api/v2/sessions`
4. Bulk endpoint at `/api/v2/bulk`

### Backward Compatibility
- All v1 endpoints remain functional
- Non-streaming fallback automatic
- Session-less operation still default