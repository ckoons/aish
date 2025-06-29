# Testing Improvements for Tekton-aish Sprint

## Overview

This document identifies all testing improvements and changes needed as part of the Tekton-aish Improvement Sprint. These improvements will ensure comprehensive test coverage for both existing and new features.

## Current Testing Gaps

### 1. Mock Testing Infrastructure
- **Issue**: Current tests hit real APIs even when mocking is attempted
- **Need**: Proper mock infrastructure for isolated unit testing
- **Solution**: Create mock adapters for both HTTP and socket protocols

### 2. Streaming Test Infrastructure
- **Issue**: No infrastructure for testing SSE/WebSocket streams
- **Need**: Async test harness for streaming responses
- **Solution**: Mock streaming servers and async test utilities

### 3. Session State Testing
- **Issue**: No way to test stateful conversations
- **Need**: Session persistence and state verification
- **Solution**: In-memory session store for testing

### 4. Performance Testing Framework
- **Issue**: No automated performance benchmarks
- **Need**: Measure latency, throughput, resource usage
- **Solution**: Performance test suite with baseline tracking

### 5. End-to-End Test Scenarios
- **Issue**: Limited real-world workflow testing
- **Need**: Complex multi-stage pipeline tests
- **Solution**: Scenario-based test suite

## Test Implementation Plan

### Phase 1: Test Infrastructure (Days 1-2)

#### 1.1 Mock Framework
```python
# tests/mocks/mock_rhetor.py
class MockRhetor:
    """Mock Rhetor server for testing"""
    def __init__(self):
        self.specialists = {}
        self.sessions = {}
        self.responses = {}
    
    def add_specialist(self, id, capabilities):
        """Add a mock specialist"""
        pass
    
    def set_response(self, specialist_id, response):
        """Set canned response for specialist"""
        pass

# tests/mocks/mock_socket.py
class MockSocketServer:
    """Mock socket server for Greek Chorus AIs"""
    def __init__(self, port):
        self.port = port
        self.responses = []
    
    async def handle_connection(self, reader, writer):
        """Handle mock socket connections"""
        pass
```

#### 1.2 Test Fixtures
```python
# tests/fixtures/ai_fixtures.py
MOCK_SPECIALISTS = {
    'apollo-ai': {
        'id': 'apollo-ai',
        'capabilities': {
            'code-analysis': 0.95,
            'debugging': 0.90
        },
        'streaming': True,
        'sessions': True
    }
}

# tests/fixtures/response_fixtures.py
MOCK_RESPONSES = {
    'simple': "This is a simple response",
    'streaming': ["This ", "is ", "a ", "streaming ", "response"],
    'error': {"error": "AI unavailable", "code": -32001}
}
```

### Phase 2: Feature-Specific Tests (Days 3-8)

#### 2.1 Streaming Tests
```python
# tests/test_streaming.py
import asyncio
import pytest
from tests.mocks import MockRhetor, MockStreamingResponse

class TestStreaming:
    @pytest.mark.asyncio
    async def test_sse_streaming(self):
        """Test Server-Sent Events streaming"""
        mock_rhetor = MockRhetor()
        mock_rhetor.set_streaming_response('apollo-ai', [
            "Hello", " world", "!"
        ])
        
        chunks = []
        async for chunk in stream_response('apollo-ai', "test"):
            chunks.append(chunk)
        
        assert chunks == ["Hello", " world", "!"]
    
    @pytest.mark.asyncio
    async def test_streaming_error_recovery(self):
        """Test streaming continues after recoverable error"""
        # Test implementation
        pass
    
    def test_streaming_timeout(self):
        """Test streaming timeout handling"""
        # Test implementation
        pass
```

#### 2.2 Session Tests
```python
# tests/test_sessions.py
class TestSessions:
    def test_session_creation(self):
        """Test creating a new session"""
        registry = SocketRegistry(mock=True)
        session_id = registry.create_session('apollo-ai')
        
        assert session_id
        assert registry.get_session(session_id)
    
    def test_session_context_persistence(self):
        """Test context persists across messages"""
        # Implementation
        pass
    
    def test_session_expiry(self):
        """Test session expires after timeout"""
        # Implementation
        pass
    
    def test_cross_ai_session(self):
        """Test sharing session between AIs"""
        # Implementation
        pass
```

#### 2.3 Bulk Operations Tests
```python
# tests/test_bulk_operations.py
class TestBulkOperations:
    def test_parallel_execution(self):
        """Test parallel bulk operations"""
        operations = [
            {"id": "op1", "ai": "apollo", "message": "test1"},
            {"id": "op2", "ai": "athena", "message": "test2"}
        ]
        
        results = execute_bulk(operations, mode='parallel')
        assert len(results) == 2
        assert all(r['status'] == 'success' for r in results.values())
    
    def test_dependency_resolution(self):
        """Test operations with dependencies"""
        # Implementation
        pass
    
    def test_partial_failure_handling(self):
        """Test bulk with some operations failing"""
        # Implementation
        pass
```

#### 2.4 WebSocket Tests
```python
# tests/test_websocket.py
import websockets
import pytest

class TestWebSocket:
    @pytest.mark.asyncio
    async def test_websocket_connection(self):
        """Test establishing WebSocket connection"""
        async with MockWebSocketServer() as server:
            async with websockets.connect(server.url) as ws:
                await ws.send(json.dumps({
                    "jsonrpc": "2.0",
                    "method": "chat",
                    "params": {"message": "Hello"},
                    "id": 1
                }))
                
                response = await ws.recv()
                data = json.loads(response)
                assert data['id'] == 1
    
    @pytest.mark.asyncio
    async def test_websocket_streaming(self):
        """Test streaming over WebSocket"""
        # Implementation
        pass
```

### Phase 3: Integration Tests (Days 9-10)

#### 3.1 Pipeline Integration Tests
```python
# tests/integration/test_pipeline_integration.py
class TestPipelineIntegration:
    def test_streaming_pipeline(self):
        """Test streaming through multi-stage pipeline"""
        result = run_pipeline(
            'echo "Long story" | apollo --stream | athena --stream'
        )
        assert result.streamed
        assert len(result.chunks) > 10
    
    def test_session_pipeline(self):
        """Test session context in pipeline"""
        session_id = create_session()
        
        run_pipeline(f'echo "My name is Test" | apollo --session {session_id}')
        result = run_pipeline(f'echo "What is my name?" | apollo --session {session_id}')
        
        assert "Test" in result.output
    
    def test_bulk_pipeline(self):
        """Test bulk operations in pipeline"""
        result = run_pipeline('apollo,athena,prometheus << "Analyze this"')
        assert len(result.responses) == 3
```

#### 3.2 Error Scenario Tests
```python
# tests/integration/test_error_scenarios.py
class TestErrorScenarios:
    def test_network_interruption_recovery(self):
        """Test recovery from network issues"""
        with NetworkInterruptor() as interruptor:
            interruptor.interrupt_after(5)
            result = run_pipeline('echo "Test" | apollo --stream')
            assert result.recovered
            assert result.complete
    
    def test_ai_unavailable_fallback(self):
        """Test fallback when AI is unavailable"""
        with MockRhetor() as rhetor:
            rhetor.make_unavailable('apollo-ai')
            result = run_pipeline('echo "Test" | apollo')
            assert result.used_fallback
    
    def test_cascade_failure_handling(self):
        """Test pipeline handles cascade failures"""
        # Implementation
        pass
```

### Phase 4: Performance Tests (Days 11-12)

#### 4.1 Benchmark Suite
```python
# tests/performance/test_benchmarks.py
import pytest
from pytest_benchmark.plugin import benchmark

class TestPerformance:
    def test_streaming_latency(self, benchmark):
        """Benchmark time to first token"""
        def stream_first_token():
            return get_first_streaming_token("apollo", "Hello")
        
        result = benchmark(stream_first_token)
        assert result < 0.1  # 100ms target
    
    def test_bulk_throughput(self, benchmark):
        """Benchmark bulk operation throughput"""
        def bulk_operation():
            return execute_bulk([
                {"ai": f"ai{i}", "message": "test"} 
                for i in range(10)
            ])
        
        result = benchmark(bulk_operation)
        assert result < 5.0  # 5 second target for 10 ops
    
    def test_session_memory_usage(self):
        """Test session memory consumption"""
        import tracemalloc
        tracemalloc.start()
        
        # Create 100 sessions with full context
        sessions = []
        for i in range(100):
            session = create_session(context_window=20)
            for j in range(20):
                add_message(session, f"Message {j}")
            sessions.append(session)
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # Should use less than 100MB for 100 sessions
        assert peak < 100 * 1024 * 1024
```

#### 4.2 Load Tests
```python
# tests/performance/test_load.py
class TestLoad:
    def test_concurrent_connections(self):
        """Test handling concurrent connections"""
        import concurrent.futures
        
        def make_request(i):
            return run_pipeline(f'echo "Request {i}" | apollo')
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(make_request, i) for i in range(100)]
            results = [f.result() for f in futures]
        
        assert all(r.success for r in results)
        assert len(results) == 100
    
    def test_sustained_load(self):
        """Test sustained load over time"""
        # Implementation
        pass
```

### Phase 5: Test Utilities (Days 13-14)

#### 5.1 Test Helpers
```python
# tests/utils/helpers.py
class AishTestCase:
    """Base class for aish tests"""
    def setup_method(self):
        self.mock_rhetor = MockRhetor()
        self.temp_dir = tempfile.mkdtemp()
        self.registry = SocketRegistry(mock=True)
    
    def teardown_method(self):
        self.mock_rhetor.cleanup()
        shutil.rmtree(self.temp_dir)
    
    def create_mock_ai(self, name, **kwargs):
        """Helper to create mock AI"""
        return self.mock_rhetor.add_specialist(name, **kwargs)
    
    def run_pipeline(self, command, **kwargs):
        """Helper to run pipeline with mocks"""
        return PipelineRunner(self.mock_rhetor).run(command, **kwargs)

# tests/utils/async_helpers.py
class AsyncAishTestCase:
    """Base class for async aish tests"""
    async def asetup(self):
        self.mock_server = await MockStreamingServer.start()
    
    async def ateardown(self):
        await self.mock_server.stop()
```

#### 5.2 Test Runners
```python
# tests/utils/runners.py
class TestRunner:
    """Enhanced test runner with reporting"""
    def run_all_tests(self):
        suites = [
            'unit',
            'integration',
            'performance',
            'e2e'
        ]
        
        results = {}
        for suite in suites:
            results[suite] = self.run_suite(suite)
        
        self.generate_report(results)
    
    def generate_report(self, results):
        """Generate comprehensive test report"""
        # Implementation
        pass
```

## Testing Best Practices

### 1. Test Organization
```
tests/
├── unit/                 # Fast, isolated tests
├── integration/          # Component interaction tests
├── e2e/                  # Full workflow tests
├── performance/          # Benchmark and load tests
├── mocks/               # Mock implementations
├── fixtures/            # Test data and fixtures
├── utils/               # Test utilities and helpers
└── reports/             # Test reports and metrics
```

### 2. Test Naming Convention
- `test_<feature>_<scenario>_<expected_outcome>`
- Example: `test_streaming_network_error_recovers_gracefully`

### 3. Test Documentation
Each test should include:
- Purpose of the test
- Setup requirements
- Expected behavior
- Cleanup needs

### 4. Continuous Integration
- Unit tests run on every commit
- Integration tests run on PR
- Performance tests run nightly
- E2E tests run before release

## Metrics and Reporting

### Test Coverage Goals
- Unit test coverage: > 90%
- Integration test coverage: > 80%
- E2E scenario coverage: > 70%

### Performance Baselines
- Streaming first token: < 100ms
- Session creation: < 10ms
- Bulk operation overhead: < 5%
- Memory per session: < 1MB

### Test Report Format
```json
{
  "suite": "unit",
  "timestamp": "2024-01-01T12:00:00Z",
  "duration": 45.3,
  "tests": {
    "total": 150,
    "passed": 148,
    "failed": 2,
    "skipped": 0
  },
  "coverage": {
    "lines": 92.5,
    "branches": 87.3,
    "functions": 95.0
  }
}
```

## Implementation Priority

1. **Critical** (Must have for sprint):
   - Mock infrastructure
   - Streaming tests
   - Session tests
   - Basic performance tests

2. **Important** (Should have):
   - Bulk operation tests
   - WebSocket tests
   - Integration test suite
   - Error scenario tests

3. **Nice to have** (If time permits):
   - Load tests
   - Advanced performance profiling
   - Test report generation
   - CI/CD integration

## Next Steps

1. Create mock infrastructure first
2. Implement feature tests in parallel with feature development
3. Run performance baseline before optimization
4. Integrate with CI/CD pipeline
5. Generate test reports for tracking