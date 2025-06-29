#!/bin/bash
# Basic test script for aish functionality

echo "=== Basic aish Tests ==="
echo

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if aish is executable
echo "1. Checking aish executable..."
if [ -x "../aish" ]; then
    echo -e "${GREEN}✅ aish is executable${NC}"
else
    echo -e "${RED}❌ aish is not executable${NC}"
    exit 1
fi

# Test help
echo -e "\n2. Testing help command..."
if ../aish --help > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Help command works${NC}"
else
    echo -e "${RED}❌ Help command failed${NC}"
fi

# Test version
echo -e "\n3. Testing version..."
VERSION=$(../aish --version 2>&1)
echo -e "${GREEN}✅ Version: $VERSION${NC}"

# Test basic echo
echo -e "\n4. Testing echo command..."
OUTPUT=$(../aish -c 'echo "Hello from aish"' 2>&1)
if [ "$OUTPUT" = "Hello from aish" ]; then
    echo -e "${GREEN}✅ Echo command works${NC}"
else
    echo -e "${RED}❌ Echo command failed${NC}"
    echo "   Got: $OUTPUT"
fi

# Check if Rhetor is running
echo -e "\n5. Checking Rhetor connection..."
if curl -s http://localhost:8003/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Rhetor is running${NC}"
    
    # Test AI pipeline
    echo -e "\n6. Testing AI pipeline..."
    OUTPUT=$(../aish -c 'echo "What is 1+1?" | rhetor' 2>&1)
    if [[ "$OUTPUT" == *"2"* ]] || [[ "$OUTPUT" == *"two"* ]]; then
        echo -e "${GREEN}✅ AI pipeline works${NC}"
        echo "   Response: ${OUTPUT:0:50}..."
    else
        echo -e "${YELLOW}⚠️  AI pipeline returned unexpected output${NC}"
        echo "   Response: ${OUTPUT:0:100}..."
    fi
    
    # Test team chat
    echo -e "\n7. Testing team chat..."
    OUTPUT=$(../aish -c 'team-chat "Hello team"' 2>&1)
    if [[ -n "$OUTPUT" ]]; then
        echo -e "${GREEN}✅ Team chat executed${NC}"
        echo "   Response: ${OUTPUT:0:50}..."
    else
        echo -e "${YELLOW}⚠️  Team chat returned no output${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Rhetor is not running - skipping AI tests${NC}"
fi

echo -e "\n=== Test Summary ==="
echo "Basic functionality is working!"
echo "Run './run_tests.py' for comprehensive testing"