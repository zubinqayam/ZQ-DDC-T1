#!/bin/bash
#
# Pre-commit hook for manifest verification in ZQ DDC Core V1
#
# This hook runs before each commit to verify that all modified manifest
# files are properly signed and validated.
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Find the repository root
REPO_ROOT=$(git rev-parse --show-toplevel)

# Find Python
PYTHON=${PYTHON:-python3}

# Check if tools are available
if ! command -v "$PYTHON" &> /dev/null; then
    echo -e "${RED}Error: Python 3 not found${NC}" >&2
    exit 1
fi

if ! command -v minisign &> /dev/null; then
    echo -e "${YELLOW}Warning: minisign not found, signature verification will be skipped${NC}" >&2
fi

# Get list of staged YAML files that might be manifests
STAGED_MANIFESTS=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.ya?ml$' || true)

if [ -z "$STAGED_MANIFESTS" ]; then
    # No YAML files staged
    exit 0
fi

echo -e "${GREEN}Checking staged manifests...${NC}"

FAILED=0

for manifest in $STAGED_MANIFESTS; do
    FULL_PATH="$REPO_ROOT/$manifest"
    
    # Check if file exists (might be deleted)
    if [ ! -f "$FULL_PATH" ]; then
        continue
    fi
    
    # Check if it's a manifest (has schema_uri field)
    if ! grep -q "schema_uri:" "$FULL_PATH"; then
        continue
    fi
    
    echo "Checking: $manifest"
    
    # Check schema URI
    if [ -f "$REPO_ROOT/tools/check_schema_uri.py" ]; then
        if ! "$PYTHON" "$REPO_ROOT/tools/check_schema_uri.py" "$FULL_PATH" 2>&1; then
            echo -e "${RED}✗ Schema URI check failed for: $manifest${NC}" >&2
            FAILED=1
        fi
    fi
    
    # Validate schema
    if [ -f "$REPO_ROOT/tools/validate_schema.py" ] && [ -f "$REPO_ROOT/schema/manifest.schema.json" ]; then
        if ! "$PYTHON" "$REPO_ROOT/tools/validate_schema.py" "$FULL_PATH" -s "$REPO_ROOT/schema/manifest.schema.json" 2>&1; then
            echo -e "${RED}✗ Schema validation failed for: $manifest${NC}" >&2
            FAILED=1
        fi
    fi
    
    # Verify signature if public key exists
    if [ -f "$REPO_ROOT/tools/verify_manifest.py" ] && [ -f "$REPO_ROOT/keys/minisign.pub" ]; then
        if ! "$PYTHON" "$REPO_ROOT/tools/verify_manifest.py" "$FULL_PATH" -p "$REPO_ROOT/keys/minisign.pub" 2>&1; then
            echo -e "${YELLOW}⚠ Warning: Signature verification failed for: $manifest${NC}" >&2
            echo -e "${YELLOW}  (You may need to sign the manifest before committing)${NC}" >&2
        fi
    fi
done

if [ $FAILED -ne 0 ]; then
    echo -e "${RED}✗ Pre-commit checks failed${NC}" >&2
    exit 1
fi

echo -e "${GREEN}✓ All pre-commit checks passed${NC}"
exit 0
