# Testing Strategy - Tekton-aish Improvement Sprint

## Overview

This document outlines the comprehensive testing strategy for the Tekton-aish Improvement Sprint, covering unit tests, integration tests, performance tests, and end-to-end testing.

## Testing Principles

1. **Test First**: Write tests before implementation when possible
2. **Isolation**: Each test should be independent
3. **Coverage**: Aim for 80%+ code coverage
4. **Performance**: All features must meet performance targets
5. **Regression**: Ensure backward compatibility

## Test Categories

### 1. Unit Tests

Test individual components in isolation.

#### Tekton Unit Tests

```python
# tests/test_streaming.py
import pytest
from unittest.mock import Mock, AsyncMock
from rhetor.api.streaming import stream_specialist_response

@pytest.mark.asyncio
async def test_sse_streaming():
    """Test SSE streaming sends chunks correctly"""
    mock_specialist = Mock()
    mock_specialist.generate_stream = AsyncMock()
    mock_specialist.generate_stream.return_value = async_generator([
        "Hello", " world", "!"
    ])
    
    # Test streaming response
    chunks = []
    async for chunk in stream_specialist_response(mock_specialist, "test"):
        chunks.append(chunk)
    
    assert len(chunks) == 3
    assert "".join(chunks) == "Hello world!"

# tests/test_sessions.py
import pytest
from rhetor.sessions import SessionManager

def test_session_creation():
    """Test session creation with default values"""
    manager = SessionManager(Mock())
    session = manager.create_session("apollo-ai")
    
    assert session['specialist_id'] == "apollo-ai"
    assert session['context_window'] == 10
    assert len(session['messages']) == 0

def test_session_context_pruning():
    """Test that old messages are pruned"""
    manager = SessionManager(Mock())
    session = manager.create_session("apollo-ai", context_window=2)
    
    # Add 5 messages
    for i in range(5):
        manager.add_message(session['id'], 'user', f"Message {i}")
    
    # Should only keep last 4 (2x context window)
    assert len(session['messages']) == 4
    assert session['messages'][0]['content'] == "Message 1"
```

#### aish Unit Tests

```python
# tests/test_socket_registry_streaming.py
import pytest
from socket_registry import SocketRegistry

@pytest.mark.asyncio
async def test_streaming_detection():
    """Test AI capability detection for streaming"""
    registry = SocketRegistry(debug=True)
    
    # Mock AI with streaming capability
    registry._ai_cache = {
        'apollo-ai': {
            'id': 'apollo-ai',
            'capabilities': {'streaming': True}
        }
    }
    
    ai_info = registry._get_ai_info('apollo')
    assert ai_info['capabilities']['streaming'] == True

def test_bulk_operation_parsing():
    """Test bulk operation request formatting"""
    registry = SocketRegistry()
    
    operations = [
        {"id": "op1", "ai": "apollo", "message": "test1"},
        {"id": "op2", "ai": "athena", "message": "test2", "depends_on": ["op1"]}
    ]
    
    request = registry._format_bulk_request(operations)
    assert request['execution'] == 'parallel'
    assert len(request['operations']) == 2
    assert request['operations'][1]['depends_on'] == ["op1"]
```

### 2. Integration Tests

Test component interactions.

#### Streaming Integration

```python
# tests/integration/test_streaming_integration.py
import asyncio
import aiohttp
import pytest

@pytest.mark.integration
async def test_end_to_end_streaming():
    """Test streaming from Tekton to aish"""
    # Start test Rhetor instance
    rhetor = await start_test_rhetor()
    
    # Create aish registry
    registry = SocketRegistry(f"http://localhost:{rhetor.port}")
    
    # Test streaming
    chunks = []
    await registry.write_stream(
        "apollo", 
        "Generate a long response",
        lambda chunk: chunks.append(chunk)
    )
    
    assert len(chunks) > 5  # Should receive multiple chunks
    assert "".join(chunks)  # Should form complete response
```

#### Session Integration

```python
# tests/integration/test_session_integration.py
def test_session_persistence_across_pipelines():
    """Test session context maintained in pipeline"""
    # Create session
    result = subprocess.run([
        './aish', '-c', 
        'echo "My name is Casey" | apollo --session'
    ], capture_output=True, text=True)
    
    session_id = extract_session_id(result.stdout)
    
    # Continue conversation
    result2 = subprocess.run([
        './aish', '-c', 
        f'echo "What is my name?" | apollo --session {session_id}'
    ], capture_output=True, text=True)
    
    assert "Casey" in result2.stdout
```

### 3. Performance Tests

Ensure features meet performance targets.

#### Streaming Performance

```python
# tests/performance/test_streaming_performance.py
import time

def test_streaming_first_token_latency():
    """Test time to first token < 100ms"""
    start = time.time()
    
    process = subprocess.Popen([
        './aish', '-c', 'echo "Hello" | apollo --stream'
    ], stdout=subprocess.PIPE, text=True)
    
    # Read first character
    first_char = process.stdout.read(1)
    first_token_time = time.time() - start
    
    assert first_token_time < 0.1  # 100ms
    assert first_char  # Got output

def test_streaming_throughput():
    """Test sustained streaming rate > 50 tokens/sec"""
    tokens = []
    start = time.time()
    
    # Stream a long response
    result = subprocess.run([
        './aish', '-c', 
        'echo "Write a 500 word essay" | apollo --stream'
    ], capture_output=True, text=True)
    
    duration = time.time() - start
    token_count = len(result.stdout.split())
    tokens_per_second = token_count / duration
    
    assert tokens_per_second > 50
```

#### Bulk Operation Performance

```python
# tests/performance/test_bulk_performance.py
def test_bulk_vs_sequential():
    """Test bulk operations are 50% faster"""
    # Sequential execution
    seq_start = time.time()
    for ai in ['apollo', 'athena', 'prometheus']:
        subprocess.run([
            './aish', '-c', f'echo "Analyze this" | {ai}'
        ])
    seq_time = time.time() - seq_start
    
    # Bulk execution
    bulk_start = time.time()
    subprocess.run([
        './aish', '-c', 
        'apollo,athena,prometheus << "Analyze this"'
    ])
    bulk_time = time.time() - bulk_start
    
    # Bulk should be at least 50% faster
    assert bulk_time < seq_time * 0.5
```

### 4. End-to-End Tests

Test complete user workflows.

```python
# tests/e2e/test_user_workflows.py
def test_code_review_workflow():
    """Test realistic code review pipeline"""
    # Create test file
    with open('test_code.py', 'w') as f:
        f.write('''
def process_data(data):
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
    return result
''')
    
    # Run code review pipeline
    result = subprocess.run([
        './aish', '-c',
        'cat test_code.py | apollo --capability code-analysis | '
        'athena --capability review | '
        'prometheus --capability planning > review_results.md'
    ], capture_output=True)
    
    assert result.returncode == 0
    assert os.path.exists('review_results.md')
    
    with open('review_results.md') as f:
        content = f.read()
        assert 'performance' in content.lower()
        assert 'suggestion' in content.lower()
```

### 5. WebSocket Tests

Test real-time communication.

```python
# tests/test_websocket.py
import websockets
import json

@pytest.mark.asyncio
async def test_websocket_connection():
    """Test WebSocket connection and messaging"""
    uri = "ws://localhost:8003/ws/ai/apollo-ai"
    
    async with websockets.connect(uri) as websocket:
        # Send message
        await websocket.send(json.dumps({
            "jsonrpc": "2.0",
            "method": "chat",
            "params": {"message": "Hello"},
            "id": 1
        }))
        
        # Receive response
        response = await websocket.recv()
        data = json.loads(response)
        
        assert data['jsonrpc'] == "2.0"
        assert 'result' in data
        assert data['id'] == 1

@pytest.mark.asyncio
async def test_websocket_streaming():
    """Test WebSocket streaming"""
    chunks = []
    
    async with websockets.connect("ws://localhost:8003/ws/ai/apollo-ai") as ws:
        # Request streaming
        await ws.send(json.dumps({
            "jsonrpc": "2.0",
            "method": "stream",
            "params": {"message": "Tell me a story"},
            "id": 2
        }))
        
        # Collect chunks
        while True:
            response = await ws.recv()
            data = json.loads(response)
            
            if data.get('method') == 'stream.chunk':
                chunks.append(data['params']['content'])
            elif data.get('method') == 'stream.complete':
                break
    
    assert len(chunks) > 5
    assert "".join(chunks)  # Complete message
```

### 6. Error Handling Tests

Test error scenarios and recovery.

```python
# tests/test_error_handling.py
def test_streaming_error_recovery():
    """Test recovery from streaming errors"""
    # Simulate network interruption
    # Should fallback to non-streaming
    pass

def test_session_expiry_handling():
    """Test graceful handling of expired sessions"""
    # Create session
    # Wait for expiry
    # Attempt to use
    # Should create new session
    pass

def test_bulk_partial_failure():
    """Test bulk operations with some failures"""
    result = subprocess.run([
        './aish', '-c',
        'apollo,invalid-ai,athena << "Test"'
    ], capture_output=True, text=True)
    
    # Should complete successfully for valid AIs
    assert "apollo" in result.stdout
    assert "athena" in result.stdout
    assert "error" in result.stderr.lower()
```

## Test Environment

### Local Testing

```bash
# Run all tests
make test

# Run specific category
make test-unit
make test-integration
make test-performance
make test-e2e

# Run with coverage
make test-coverage
```

### CI/CD Pipeline

```yaml
# .github/workflows/test.yml
name: Test Suite
on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run unit tests
        run: make test-unit
        
  integration-tests:
    runs-on: ubuntu-latest
    services:
      rhetor:
        image: tekton/rhetor:latest
        ports:
          - 8003:8003
    steps:
      - uses: actions/checkout@v2
      - name: Run integration tests
        run: make test-integration
        
  performance-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run performance tests
        run: make test-performance
      - name: Upload results
        uses: actions/upload-artifact@v2
        with:
          name: performance-results
          path: test-results/
```

## Test Data

### Mock Responses

```python
# tests/fixtures/mock_responses.py
MOCK_STREAMING_RESPONSE = [
    "I'll", " analyze", " your", " code", " for", " performance", "."
]

MOCK_SESSION_CONTEXT = [
    {"role": "user", "content": "My name is Casey"},
    {"role": "assistant", "content": "Nice to meet you, Casey!"},
    {"role": "user", "content": "What's my name?"}
]

MOCK_BULK_OPERATIONS = {
    "operations": [
        {"id": "op1", "ai": "apollo", "message": "Analyze"},
        {"id": "op2", "ai": "athena", "message": "Review"}
    ]
}
```

## Monitoring & Metrics

### Test Metrics to Track

1. **Coverage Metrics**
   - Line coverage > 80%
   - Branch coverage > 70%
   - Function coverage > 90%

2. **Performance Metrics**
   - Average test suite runtime
   - Slowest tests
   - Flaky test frequency

3. **Quality Metrics**
   - Test failures per commit
   - Time to fix test failures
   - Test maintenance burden

### Test Reports

Generate comprehensive test reports:

```bash
# Coverage report
coverage run -m pytest
coverage html

# Performance report
pytest --benchmark-only
pytest --profile

# Generate JUnit XML for CI
pytest --junitxml=test-results/junit.xml
```

## Test Maintenance

### Best Practices

1. **Keep Tests Fast**: Mock external dependencies
2. **Avoid Flaky Tests**: Use proper waits and retries
3. **Test One Thing**: Each test should verify one behavior
4. **Clear Names**: Test names should describe what they test
5. **Maintainable**: Update tests when implementation changes

### Regular Tasks

- Weekly: Review and fix flaky tests
- Monthly: Update test data and fixtures
- Quarterly: Performance test baseline updates
- Per Release: Full regression test suite