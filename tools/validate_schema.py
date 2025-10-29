#!/usr/bin/env python3
"""
Schema validator for ZQ DDC Core V1 manifests.

This tool validates YAML manifests against the JSON schema definition
to ensure structural compliance and field-level correctness.
"""

import sys
import yaml
import json
from pathlib import Path
import argparse
import jsonschema
from jsonschema import validate, ValidationError


def load_yaml(path):
    """Load YAML file."""
    with open(path, 'r') as f:
        return yaml.safe_load(f)


def load_json(path):
    """Load JSON file."""
    with open(path, 'r') as f:
        return json.load(f)


def validate_manifest(manifest_path, schema_path):
    """Validate a manifest against a JSON schema."""
    manifest_path = Path(manifest_path)
    schema_path = Path(schema_path)
    
    if not manifest_path.exists():
        print(f"Error: Manifest file not found: {manifest_path}", file=sys.stderr)
        return False
    
    if not schema_path.exists():
        print(f"Error: Schema file not found: {schema_path}", file=sys.stderr)
        return False
    
    try:
        # Load manifest and schema
        manifest = load_yaml(manifest_path)
        schema = load_json(schema_path)
        
        # Validate
        validate(instance=manifest, schema=schema)
        
        print(f"✓ Schema validation passed for: {manifest_path}")
        return True
        
    except ValidationError as e:
        print(f"✗ Schema validation failed for: {manifest_path}", file=sys.stderr)
        print(f"  Error: {e.message}", file=sys.stderr)
        if e.path:
            print(f"  Path: {' -> '.join(str(p) for p in e.path)}", file=sys.stderr)
        return False
    except yaml.YAMLError as e:
        print(f"✗ YAML parsing error in: {manifest_path}", file=sys.stderr)
        print(f"  Error: {e}", file=sys.stderr)
        return False
    except json.JSONDecodeError as e:
        print(f"✗ JSON parsing error in schema: {schema_path}", file=sys.stderr)
        print(f"  Error: {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"✗ Unexpected error validating: {manifest_path}", file=sys.stderr)
        print(f"  Error: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Validate a ZQ DDC Core V1 manifest against JSON schema'
    )
    parser.add_argument(
        'manifest',
        help='Path to the manifest file to validate'
    )
    parser.add_argument(
        '-s', '--schema',
        default='schema/manifest.schema.json',
        help='Path to the JSON schema file (default: schema/manifest.schema.json)'
    )
    
    args = parser.parse_args()
    
    success = validate_manifest(args.manifest, args.schema)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
