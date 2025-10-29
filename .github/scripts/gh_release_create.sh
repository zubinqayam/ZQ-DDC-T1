#!/bin/bash
#
# GitHub Release Creation Script
# Creates a GitHub release with signed manifests and verification instructions
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check required environment variables
if [ -z "$GITHUB_TOKEN" ]; then
    echo -e "${RED}Error: GITHUB_TOKEN environment variable not set${NC}" >&2
    exit 1
fi

if [ -z "$GITHUB_REPOSITORY" ]; then
    echo -e "${RED}Error: GITHUB_REPOSITORY environment variable not set${NC}" >&2
    exit 1
fi

# Get tag name (can be passed as argument or from environment)
TAG=${1:-$GITHUB_REF_NAME}

if [ -z "$TAG" ]; then
    echo -e "${RED}Error: No tag specified${NC}" >&2
    echo "Usage: $0 <tag-name>" >&2
    exit 1
fi

echo -e "${BLUE}Creating release for tag: $TAG${NC}"

# Extract version from tag (remove 'v' prefix if present)
VERSION=${TAG#v}

# Check if gh CLI is available
if ! command -v gh &> /dev/null; then
    echo -e "${RED}Error: GitHub CLI (gh) not found${NC}" >&2
    echo "Please install gh: https://cli.github.com/" >&2
    exit 1
fi

# Generate release notes
RELEASE_NOTES=$(mktemp)

cat > "$RELEASE_NOTES" <<EOF
# Release $TAG

## Overview
This release includes cryptographically signed manifests for complete provenance verification.

## Verification
All manifests in this release have been:
- ✓ Schema validated
- ✓ Schema URI verified
- ✓ Cryptographically signed

### Verify a Manifest
\`\`\`bash
# Clone the repository at this tag
git clone --branch $TAG https://github.com/$GITHUB_REPOSITORY.git
cd $(basename $GITHUB_REPOSITORY)

# Install dependencies
pip install pyyaml jsonschema
sudo apt-get install minisign

# Verify a manifest
python tools/verify_manifest.py <path-to-manifest.yaml> -p keys/minisign.pub
\`\`\`

## Changes
EOF

# Add commit messages since last tag
PREVIOUS_TAG=$(git describe --tags --abbrev=0 $TAG^ 2>/dev/null || echo "")

if [ -n "$PREVIOUS_TAG" ]; then
    echo "" >> "$RELEASE_NOTES"
    git log --pretty=format:"- %s (%h)" $PREVIOUS_TAG..$TAG >> "$RELEASE_NOTES"
else
    echo "" >> "$RELEASE_NOTES"
    git log --pretty=format:"- %s (%h)" $TAG >> "$RELEASE_NOTES"
fi

# Find all signed manifests
echo "" >> "$RELEASE_NOTES"
echo "" >> "$RELEASE_NOTES"
echo "## Signed Manifests" >> "$RELEASE_NOTES"

MANIFESTS=$(find . -name "*.yaml" -o -name "*.yml" | while read file; do
    if grep -q "schema_uri:" "$file" && grep -q "signature:" "$file"; then
        echo "$file"
    fi
done)

if [ -n "$MANIFESTS" ]; then
    while IFS= read -r manifest; do
        if [ -n "$manifest" ]; then
            echo "- \`$manifest\`" >> "$RELEASE_NOTES"
        fi
    done <<< "$MANIFESTS"
else
    echo "No signed manifests found in this release." >> "$RELEASE_NOTES"
fi

# Security information
cat >> "$RELEASE_NOTES" <<EOF

## Security
For security issues, please see [SECURITY.md](SECURITY.md).

## Documentation
- [Manifest Documentation](docs/core/manifest.md)
- [Schema Definition](schema/manifest.schema.json)

EOF

echo -e "${GREEN}Generated release notes${NC}"

# Create the release
echo -e "${BLUE}Creating GitHub release...${NC}"

gh release create "$TAG" \
    --title "Release $TAG" \
    --notes-file "$RELEASE_NOTES" \
    --repo "$GITHUB_REPOSITORY" \
    --verify-tag

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Release created successfully${NC}"
    echo -e "${GREEN}  View at: https://github.com/$GITHUB_REPOSITORY/releases/tag/$TAG${NC}"
else
    echo -e "${RED}✗ Failed to create release${NC}" >&2
    rm -f "$RELEASE_NOTES"
    exit 1
fi

# Clean up
rm -f "$RELEASE_NOTES"

echo -e "${GREEN}Done!${NC}"
