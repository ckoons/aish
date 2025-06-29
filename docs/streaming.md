# Streaming Guide

Learn how to use aish's streaming capabilities for real-time AI responses.

## What is Streaming?

Streaming allows you to see AI responses as they're generated, character by character, instead of waiting for the complete response. This creates a more interactive, responsive experience.

### Traditional vs Streaming

**Traditional (Buffered)**:
```bash
$ echo "Write a long story" | apollo
[Wait 10-15 seconds...]
[Entire story appears at once]
```

**Streaming**:
```bash
$ echo "Write a long story" | apollo --stream
Once upon a time... [text appears as it's generated]
```

## Basic Streaming Usage

### Enable Streaming

Add the `--stream` flag to any AI command:

```bash
# Stream a single AI response
echo "Explain quantum computing in detail" | athena --stream

# Stream through a pipeline
echo "Design a web app" | prometheus --stream | apollo --stream

# Stream to file (appears in real-time)
echo "Generate documentation" | hermes --stream > docs.md
```

### Interactive Streaming

In interactive mode:

```bash
aish
aish> apollo --stream
apollo (streaming)> Tell me about machine learning
Machine learning is... [response streams in real-time]
```

## Streaming Options

### Control Streaming Behavior

```bash
# Fast streaming (minimal buffering)
echo "Quick response" | apollo --stream --buffer-size 1

# Smooth streaming (small buffer)
echo "Normal response" | apollo --stream --buffer-size 50

# Line-buffered streaming
echo "List items" | apollo --stream --line-buffered
```

### Stream Formatting

```bash
# Show streaming progress
echo "Long task" | apollo --stream --show-progress

# Add timestamps
echo "Real-time data" | hermes --stream --timestamps

# Colorized streaming (if terminal supports)
echo "Highlight important" | apollo --stream --color
```

## Streaming in Pipelines

### Multi-Stage Streaming

Stream through multiple AIs:

```bash
# Each stage streams its output
echo "Complex question" | \
    apollo --stream | \
    athena --stream | \
    hermes --stream > result.md

# Watch the file grow in real-time
tail -f result.md
```

### Parallel Streaming

Stream from multiple AIs simultaneously:

```bash
# In separate terminals
echo "Question" | apollo --stream > apollo_response.txt &
echo "Question" | athena --stream > athena_response.txt &
echo "Question" | hermes --stream > hermes_response.txt &

# Monitor all streams
tail -f *_response.txt
```

## Advanced Streaming Features

### Stream Processing

Process streams as they arrive:

```bash
#!/bin/bash
# Process streaming output in real-time

echo "Generate CSV data" | apollo --stream | while IFS= read -r line; do
    # Process each line as it arrives
    echo "$line" | awk -F',' '{print $1}'
done
```

### Stream Filtering

Filter streaming content:

```bash
# Only show lines containing keywords
echo "Technical analysis" | apollo --stream | grep -i "important" --line-buffered

# Transform stream in real-time
echo "Generate code" | apollo --stream | sed 's/var/let/g' --unbuffered
```

### Stream Recording

Record streaming sessions:

```bash
# Record with timing information
script -t streaming_session.time streaming_session.log aish -c 'echo "Demo" | apollo --stream'

# Playback at original speed
scriptreplay streaming_session.time streaming_session.log
```

## Streaming Performance

### Optimize Streaming

```bash
# Reduce latency
export AISH_STREAM_BUFFER=1

# Increase throughput
export AISH_STREAM_BUFFER=1024

# Auto-adjust buffer size
echo "Content" | apollo --stream --adaptive-buffer
```

### Monitor Streaming

```bash
# Show streaming statistics
echo "Long content" | apollo --stream --stats

Streaming Statistics:
- First token: 89ms
- Tokens/second: 67.3
- Total tokens: 1,234
- Stream duration: 18.3s
```

## Error Handling in Streams

### Stream Interruption

Handle interrupted streams:

```bash
#!/bin/bash
# Resumable streaming

stream_with_resume() {
    local prompt=$1
    local output=$2
    local resume_from=0
    
    if [ -f "$output" ]; then
        resume_from=$(wc -c < "$output")
    fi
    
    echo "$prompt" | apollo --stream --resume-from $resume_from >> "$output"
}

stream_with_resume "Long generation task" "output.txt"
```

### Stream Validation

Ensure stream integrity:

```bash
# Validate streaming output
echo "Generate JSON" | apollo --stream | jq . --unbuffered

# Check for stream errors
echo "Task" | apollo --stream 2>&1 | tee output.log | grep -E "ERROR|WARNING"
```

## Streaming with Sessions

Combine streaming with session management:

```bash
# Start streaming session
SESSION=$(echo "Hello" | apollo --stream --session --get-id)

# Continue streaming in same session
echo "Continue the story" | apollo --stream --session $SESSION

# Interactive streaming session
aish --session apollo --stream
apollo (session: sess_123, streaming)> Tell me more
[Response streams with context awareness...]
```

## WebSocket Streaming

For ultimate real-time experience:

```bash
# WebSocket streaming mode
aish --websocket apollo

Connected to apollo-ai (WebSocket)
Streaming enabled, type your message:

> Generate a detailed report
[Response streams character by character with minimal latency]

> Continue with more details
[Immediate streaming response...]
```

## Streaming Use Cases

### 1. Live Documentation

```bash
# Stream documentation as you code
watch -n 1 'cat current_function.py | hermes --stream --prompt "Document this:"'
```

### 2. Real-time Translation

```bash
# Stream translations
echo "Long English text" | hermes --stream --capability translation-french
```

### 3. Progressive Analysis

```bash
# Stream code analysis
cat large_codebase.py | apollo --stream --verbose | \
    tee >(grep "ERROR" > errors.log) \
        >(grep "WARNING" > warnings.log)
```

### 4. Interactive Tutoring

```bash
# Streaming tutorial
aish --session athena --stream --session-id "learn-python"

athena> Let's learn Python step by step...
[Content streams naturally as in conversation]
```

## Streaming Configuration

### Environment Variables

```bash
# Default streaming behavior
export AISH_STREAM_DEFAULT=true

# Stream buffer size (bytes)
export AISH_STREAM_BUFFER=256

# Stream timeout (seconds)
export AISH_STREAM_TIMEOUT=300

# Show streaming indicator
export AISH_STREAM_INDICATOR="▊"
```

### Configuration File

Add to `~/.aish/config.yaml`:

```yaml
streaming:
  enabled: true
  default_buffer: 256
  show_progress: true
  indicators:
    active: "▊"
    done: "✓"
  performance:
    adaptive_buffer: true
    min_buffer: 1
    max_buffer: 4096
```

## Streaming Best Practices

### 1. Choose Right Buffer Size

- **Small (1-50)**: Interactive feel, may flicker
- **Medium (256)**: Balanced performance
- **Large (1024+)**: Smooth but less responsive

### 2. Handle Long Streams

```bash
# Add timeout for very long streams
echo "Generate book" | apollo --stream --timeout 600

# Save long streams
echo "Long content" | apollo --stream | tee full_output.txt | head -n 50
```

### 3. Network Considerations

```bash
# For slow connections
echo "Task" | apollo --stream --retry-on-disconnect --max-retries 3

# For unstable connections
echo "Task" | apollo --stream --checkpoint-every 1000
```

## Troubleshooting

### No Streaming Output

```bash
# Check if AI supports streaming
aish -l --capabilities | grep streaming

# Force streaming fallback
echo "Test" | apollo --stream --force

# Debug streaming
AISH_DEBUG=2 echo "Test" | apollo --stream
```

### Garbled Output

```bash
# Fix terminal encoding
export LANG=en_US.UTF-8

# Use ASCII-only streaming
echo "Test" | apollo --stream --ascii-only

# Reset terminal
reset
```

### Performance Issues

```bash
# Disable progress indicators
echo "Test" | apollo --stream --no-progress

# Use line-buffered mode
echo "Test" | apollo --stream --line-buffered

# Increase buffer for stability
echo "Test" | apollo --stream --buffer-size 1024
```

## Future Streaming Features

Planned enhancements:

- Binary streaming for audio/video
- Compressed streaming for large responses
- Multi-stream synchronization
- Stream branching and merging
- Visual streaming indicators

Start streaming today for a more responsive, interactive AI experience!