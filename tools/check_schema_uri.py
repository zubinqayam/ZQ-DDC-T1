#!/usr/bin/env python3
"""
Schema URI checker for ZQ DDC Core V1 manifests.

This tool ensures that every manifest's schema_uri field references
the expected schema, preventing mismatches or outdated references.
"""

import sys
import yaml
from pathlib import Path
import argparse


def check_schema_uri(manifest_path, expected_uri='schema/manifest.schema.json'):
    """Check that manifest has the expected schema_uri."""
    manifest_path = Path(manifest_path)
    
    if not manifest_path.exists():
        print(f"Error: Manifest file not found: {manifest_path}", file=sys.stderr)
        return False
    
    try:
        # Load manifest
        with open(manifest_path, 'r') as f:
            manifest = yaml.safe_load(f)
        
        # Check schema_uri field
        if 'schema_uri' not in manifest:
            print(f"✗ Missing schema_uri field in: {manifest_path}", file=sys.stderr)
            return False
        
        actual_uri = manifest['schema_uri']
        
        if actual_uri != expected_uri:
            print(f"✗ Schema URI mismatch in: {manifest_path}", file=sys.stderr)
            print(f"  Expected: {expected_uri}", file=sys.stderr)
            print(f"  Actual: {actual_uri}", file=sys.stderr)
            return False
        
        print(f"✓ Schema URI correct for: {manifest_path}")
        return True
        
    except yaml.YAMLError as e:
        print(f"✗ YAML parsing error in: {manifest_path}", file=sys.stderr)
        print(f"  Error: {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"✗ Unexpected error checking: {manifest_path}", file=sys.stderr)
        print(f"  Error: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Check schema_uri field in ZQ DDC Core V1 manifests'
    )
    parser.add_argument(
        'manifest',
        help='Path to the manifest file to check'
    )
    parser.add_argument(
        '-e', '--expected',
        default='schema/manifest.schema.json',
        help='Expected schema URI (default: schema/manifest.schema.json)'
    )
    
    args = parser.parse_args()
    
    success = check_schema_uri(args.manifest, args.expected)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
