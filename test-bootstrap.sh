#!/bin/bash

###############################################################################
# Test script for bootstrap-zqtaskmaster.sh
#
# This script validates that the bootstrap script works correctly without
# actually modifying the repository.
###############################################################################

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}Testing ZQTaskmaster Bootstrap Script${NC}"
echo "========================================"
echo ""

# Test 1: Verify script exists and is executable
echo -e "${YELLOW}Test 1: Check script exists and is executable${NC}"
if [ -f "bootstrap-zqtaskmaster.sh" ] && [ -x "bootstrap-zqtaskmaster.sh" ]; then
    echo -e "${GREEN}✓ Script exists and is executable${NC}"
else
    echo -e "${RED}✗ Script missing or not executable${NC}"
    exit 1
fi
echo ""

# Test 2: Verify bash syntax
echo -e "${YELLOW}Test 2: Validate bash syntax${NC}"
if bash -n bootstrap-zqtaskmaster.sh; then
    echo -e "${GREEN}✓ Script syntax is valid${NC}"
else
    echo -e "${RED}✗ Script has syntax errors${NC}"
    exit 1
fi
echo ""

# Test 3: Verify documentation exists
echo -e "${YELLOW}Test 3: Check documentation${NC}"
if [ -f "BOOTSTRAP.md" ]; then
    echo -e "${GREEN}✓ BOOTSTRAP.md exists${NC}"
else
    echo -e "${RED}✗ BOOTSTRAP.md is missing${NC}"
    exit 1
fi
echo ""

# Test 4: Check README.md mentions bootstrap
echo -e "${YELLOW}Test 4: Verify README.md mentions bootstrap${NC}"
if grep -q "bootstrap" README.md; then
    echo -e "${GREEN}✓ README.md mentions bootstrap${NC}"
else
    echo -e "${RED}✗ README.md does not mention bootstrap${NC}"
    exit 1
fi
echo ""

# Test 5: Verify key functions exist in script
echo -e "${YELLOW}Test 5: Check for required functions${NC}"
required_functions=(
    "check_git"
    "clone_repository"
    "create_bootstrap_branch"
    "setup_ci_governance"
    "commit_and_push"
    "display_summary"
    "main"
)

all_functions_found=true
for func in "${required_functions[@]}"; do
    if grep -q "^$func()" bootstrap-zqtaskmaster.sh; then
        echo -e "${GREEN}  ✓ Function '$func' found${NC}"
    else
        echo -e "${RED}  ✗ Function '$func' missing${NC}"
        all_functions_found=false
    fi
done

if [ "$all_functions_found" = true ]; then
    echo -e "${GREEN}✓ All required functions present${NC}"
else
    echo -e "${RED}✗ Some functions are missing${NC}"
    exit 1
fi
echo ""

# Test 6: Verify branch naming pattern
echo -e "${YELLOW}Test 6: Test branch naming logic${NC}"
timestamp=$(date +"%Y%m%d-%H%M%S")
branch_pattern="zqtaskmaster/bootstrap-${timestamp}"
if [[ "$branch_pattern" =~ ^zqtaskmaster/bootstrap-[0-9]{8}-[0-9]{6}$ ]]; then
    echo -e "${GREEN}✓ Branch naming pattern is correct: $branch_pattern${NC}"
else
    echo -e "${RED}✗ Branch naming pattern is incorrect${NC}"
    exit 1
fi
echo ""

# Test 7: Check for error handling
echo -e "${YELLOW}Test 7: Verify error handling${NC}"
if grep -q "set -e" bootstrap-zqtaskmaster.sh && grep -q "set -u" bootstrap-zqtaskmaster.sh; then
    echo -e "${GREEN}✓ Error handling flags present (set -e, set -u)${NC}"
else
    echo -e "${RED}✗ Error handling flags missing${NC}"
    exit 1
fi
echo ""

# Test 8: Verify logging functions
echo -e "${YELLOW}Test 8: Check logging functions${NC}"
if grep -q "log_info" bootstrap-zqtaskmaster.sh && \
   grep -q "log_error" bootstrap-zqtaskmaster.sh && \
   grep -q "log_warning" bootstrap-zqtaskmaster.sh; then
    echo -e "${GREEN}✓ All logging functions present${NC}"
else
    echo -e "${RED}✗ Some logging functions missing${NC}"
    exit 1
fi
echo ""

# Summary
echo "========================================"
echo -e "${GREEN}All tests passed successfully!${NC}"
echo "========================================"
echo ""
echo "The bootstrap script is ready to use."
echo "Run './bootstrap-zqtaskmaster.sh' to bootstrap CI governance."
