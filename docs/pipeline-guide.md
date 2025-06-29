# AI Pipeline Guide

Learn how to build powerful AI pipelines with aish.

## Understanding AI Pipelines

In aish, AI pipelines work like Unix pipes - data flows from one AI to another, with each AI transforming the data.

```
Input → AI₁ → AI₂ → AI₃ → Output
```

## Basic Pipeline Patterns

### 1. Simple Pipeline
Transform data through a single AI:

```bash
echo "Explain quantum computing" | athena
```

### 2. Chain Pipeline
Pass output from one AI to another:

```bash
echo "Write a Python function" | apollo | athena | hermes
```

### 3. Analysis Pipeline
Analyze code or text through multiple perspectives:

```bash
cat code.py | apollo | athena | prometheus > analysis.md
```

## Advanced Pipeline Patterns

### 1. Branching Pipeline (Coming Soon)
Send output to multiple AIs:

```bash
echo "Design a system" | prometheus | tee >(apollo > code.md) >(athena > review.md)
```

### 2. Conditional Pipeline
Execute based on conditions:

```bash
echo "Is this code optimal?" | apollo && echo "Deploy" || echo "Refactor"
```

### 3. Iterative Pipeline
Process in loops:

```bash
for i in {1..3}; do
    echo "Iteration $i: Improve this design" | prometheus
done
```

## Real-World Pipeline Examples

### Code Review Pipeline

Complete code review with multiple perspectives:

```bash
#!/bin/bash
# code-review.sh - Comprehensive code review pipeline

FILE=$1
cat "$FILE" | \
    apollo --capability code-analysis | \
    athena --capability security-review | \
    hermes --capability documentation | \
    tee full_review.md | \
    prometheus --capability planning > improvement_plan.md
```

### Documentation Pipeline

Generate comprehensive documentation:

```bash
# Extract code structure
cat project.py | apollo --capability ast-analysis > structure.json

# Generate docs
echo "Document this structure: $(cat structure.json)" | \
    hermes --capability technical-writing | \
    sophia --capability formatting > documentation.md
```

### Problem-Solving Pipeline

Collaborative problem solving:

```bash
# Define problem
PROBLEM="How to scale a web service to 1M users"

# Get solutions from multiple AIs
echo "$PROBLEM" | team-chat | tee initial_ideas.txt

# Refine best ideas
cat initial_ideas.txt | \
    prometheus --capability planning | \
    apollo --capability technical-details | \
    telos --capability goal-alignment > solution.md
```

## Pipeline Best Practices

### 1. Order Matters

Place AIs in logical order:

```bash
# Good: Analysis → Synthesis → Documentation
echo "Code" | apollo | athena | hermes

# Poor: Documentation → Analysis
echo "Code" | hermes | apollo
```

### 2. Use Appropriate AIs

Match AI capabilities to tasks:

```bash
# Code tasks → Apollo
cat code.py | apollo

# Planning tasks → Prometheus
echo "Design a system" | prometheus

# Communication → Hermes
echo "Write an email" | hermes
```

### 3. Save Intermediate Results

For complex pipelines, save progress:

```bash
echo "Design request" | prometheus > design.md
cat design.md | apollo > implementation.md
cat implementation.md | athena > review.md
```

### 4. Handle Errors Gracefully

Add error handling:

```bash
#!/bin/bash
if echo "Test" | apollo > /dev/null 2>&1; then
    echo "Complex query" | apollo | athena
else
    echo "Apollo unavailable, using athena directly"
    echo "Complex query" | athena
fi
```

## Streaming Pipelines

For real-time output:

```bash
# Stream responses as they generate
echo "Tell me a long story" | apollo --stream | athena --stream

# Stream to file
echo "Generate documentation" | hermes --stream > docs.md
```

## Session-Based Pipelines

Maintain context across pipeline stages:

```bash
# Start a session
SESSION=$(echo "I'm working on a web app" | apollo --session --get-id)

# Continue in same session
echo "Add user authentication" | apollo --session $SESSION | \
    athena --session $SESSION
```

## Bulk Pipeline Operations

Process multiple inputs efficiently:

```bash
# Analyze multiple files
apollo,athena,prometheus << EOF
File 1: $(cat file1.py)
File 2: $(cat file2.py)
File 3: $(cat file3.py)
EOF
```

## Pipeline Debugging

### Enable Debug Mode

```bash
aish -d -c 'echo "test" | apollo | athena'
```

### Trace Pipeline Execution

```bash
set -x  # Enable shell tracing
echo "Debug this" | apollo | athena
set +x  # Disable tracing
```

### Test Individual Stages

```bash
# Test each stage separately
echo "Input" | apollo
echo "Apollo output" | athena
echo "Athena output" | prometheus
```

## Performance Optimization

### 1. Parallel Execution

When order doesn't matter:

```bash
# Parallel analysis
{
    echo "$CODE" | apollo > analysis1.txt &
    echo "$CODE" | athena > analysis2.txt &
    echo "$CODE" | hermes > analysis3.txt &
    wait
}
cat analysis*.txt | prometheus
```

### 2. Caching Results

For repeated operations:

```bash
# Cache AI responses
CACHE_DIR=~/.aish/cache
mkdir -p $CACHE_DIR

HASH=$(echo "$INPUT" | md5sum | cut -d' ' -f1)
CACHE_FILE="$CACHE_DIR/$HASH"

if [ -f "$CACHE_FILE" ]; then
    cat "$CACHE_FILE"
else
    echo "$INPUT" | apollo | tee "$CACHE_FILE"
fi
```

### 3. Bulk Operations

Use bulk API for multiple operations:

```bash
# Instead of:
for file in *.py; do
    cat "$file" | apollo
done

# Use:
find . -name "*.py" -exec cat {} \; | apollo --bulk
```

## Pipeline Templates

### Code Review Template

```bash
#!/bin/bash
# comprehensive-review.sh

review_code() {
    local file=$1
    cat "$file" | \
        apollo --capability syntax-check | \
        apollo --capability code-analysis | \
        athena --capability security-review | \
        hermes --capability doc-check | \
        prometheus --capability improvement-suggestions
}
```

### Documentation Generator

```bash
#!/bin/bash
# generate-docs.sh

generate_docs() {
    local project_dir=$1
    find "$project_dir" -name "*.py" | \
        xargs cat | \
        apollo --capability extract-structure | \
        hermes --capability generate-docs | \
        sophia --capability format-markdown
}
```

### Problem Solver

```bash
#!/bin/bash
# solve-problem.sh

solve_problem() {
    local problem=$1
    echo "Problem: $problem" | \
        team-chat | \
        prometheus --capability synthesize | \
        apollo --capability technical-details | \
        telos --capability validate-solution
}
```

## Monitoring Pipelines

Track pipeline performance:

```bash
# Time pipeline execution
time (echo "Complex task" | apollo | athena | prometheus)

# Count tokens used
echo "Task" | apollo --count-tokens | athena --count-tokens

# Monitor resource usage
/usr/bin/time -v aish -c 'echo "Task" | apollo | athena'
```

## Error Recovery

Build resilient pipelines:

```bash
#!/bin/bash
# resilient-pipeline.sh

with_retry() {
    local max_attempts=3
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if "$@"; then
            return 0
        fi
        echo "Attempt $attempt failed, retrying..."
        ((attempt++))
        sleep 2
    done
    
    return 1
}

# Use with pipeline
with_retry echo "Important task" | apollo | athena
```

## Next Steps

1. Experiment with different AI combinations
2. Create your own pipeline templates
3. Share useful pipelines with the community
4. Explore advanced features like streaming and sessions
5. Build automation around common tasks

Remember: The power of aish comes from composing simple operations into complex workflows!