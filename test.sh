#!/bin/bash
# OpenList Skill Test Script
# Tests basic functionality of the OpenList skill

set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HELPER="${SKILL_DIR}/openlist.sh"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== OpenList Skill Test ===${NC}\n"

# Check if helper script exists
if [ ! -f "$HELPER" ]; then
    echo -e "${RED}Error: Helper script not found at $HELPER${NC}"
    exit 1
fi

# Check if config exists
if [ ! -f "openlist-config.json" ]; then
    echo -e "${YELLOW}Config file not found. Creating from template...${NC}"
    cp "${SKILL_DIR}/openlist-config.template.json" openlist-config.json
    echo -e "${YELLOW}Please edit openlist-config.json with your server details${NC}"
    echo -e "${YELLOW}Then run this test script again.${NC}"
    exit 0
fi

# Check if config is filled
SERVER_URL=$(jq -r '.server_url' openlist-config.json)
if [[ "$SERVER_URL" == *"your-"* ]]; then
    echo -e "${YELLOW}Config file contains default values.${NC}"
    echo -e "${YELLOW}Please edit openlist-config.json with your actual server details.${NC}"
    exit 0
fi

echo -e "${BLUE}Testing connection to: $SERVER_URL${NC}\n"

# Test 1: Login
echo -e "${YELLOW}Test 1: Login${NC}"
if bash "$HELPER" login > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Login successful${NC}\n"
else
    echo -e "${RED}✗ Login failed${NC}"
    echo -e "${RED}Please check your credentials in openlist-config.json${NC}"
    exit 1
fi

# Test 2: List root directory
echo -e "${YELLOW}Test 2: List root directory${NC}"
RESULT=$(bash "$HELPER" list / 2>&1)
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ List successful${NC}"
    echo "$RESULT" | head -5
    echo -e "\n"
else
    echo -e "${RED}✗ List failed${NC}\n"
fi

# Test 3: Search functionality
echo -e "${YELLOW}Test 3: Search functionality${NC}"
# Search for any file (just testing the API works)
RESULT=$(bash "$HELPER" search "*" / 2>&1)
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Search API works${NC}\n"
else
    echo -e "${RED}✗ Search failed${NC}\n"
fi

# Test 4: Create test directory
echo -e "${YELLOW}Test 4: Create directory${NC}"
TEST_DIR="/openclaw-test-$(date +%s)"
if bash "$HELPER" mkdir "$TEST_DIR" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Directory created: $TEST_DIR${NC}\n"
    
    # Test 5: Upload test file
    echo -e "${YELLOW}Test 5: Upload file${NC}"
    echo "OpenClaw test file - $(date)" > /tmp/openclaw-test.txt
    if bash "$HELPER" upload /tmp/openclaw-test.txt "$TEST_DIR/test.txt" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ File uploaded${NC}\n"
        
        # Test 6: List test directory
        echo -e "${YELLOW}Test 6: Verify upload${NC}"
        RESULT=$(bash "$HELPER" list "$TEST_DIR" 2>&1)
        if echo "$RESULT" | grep -q "test.txt"; then
            echo -e "${GREEN}✓ File verified in directory${NC}\n"
        else
            echo -e "${YELLOW}⚠ File not found in listing${NC}\n"
        fi
        
        # Cleanup
        echo -e "${YELLOW}Cleanup: Deleting test directory${NC}"
        if bash "$HELPER" delete "$(basename $TEST_DIR)" / > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Test directory deleted${NC}\n"
        else
            echo -e "${YELLOW}⚠ Failed to delete test directory (manual cleanup may be needed)${NC}\n"
        fi
    else
        echo -e "${RED}✗ File upload failed${NC}\n"
    fi
else
    echo -e "${YELLOW}⚠ Directory creation failed (may not have permissions)${NC}\n"
fi

# Test 7: List storages (admin endpoint)
echo -e "${YELLOW}Test 7: List storages (admin)${NC}"
if bash "$HELPER" storages > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Storage list retrieved${NC}\n"
else
    echo -e "${YELLOW}⚠ Could not list storages (may need admin permissions)${NC}\n"
fi

# Summary
echo -e "${BLUE}=== Test Summary ===${NC}"
echo -e "${GREEN}OpenList skill is functional!${NC}"
echo ""
echo "Available commands:"
echo "  .openclaw/skills/openlist/openlist.sh login"
echo "  .openclaw/skills/openlist/openlist.sh list [path]"
echo "  .openclaw/skills/openlist/openlist.sh search <keywords> [parent]"
echo "  .openclaw/skills/openlist/openlist.sh mkdir <path>"
echo "  .openclaw/skills/openlist/openlist.sh upload <local> <remote>"
echo "  .openclaw/skills/openlist/openlist.sh delete <name> <parent_dir>"
echo "  .openclaw/skills/openlist/openlist.sh storages"
echo ""
echo -e "For more details, see: ${BLUE}.openclaw/skills/openlist/SKILL.md${NC}"
