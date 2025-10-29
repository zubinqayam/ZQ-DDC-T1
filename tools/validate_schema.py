#!/usr/bin/env python3
"""
Schema validator for ZQ DDC Core V1 manifests.
Validates manifest structure against JSON schema.
"""
import argparse
import json
import sys
import yaml

try:
    import jsonschema
    from jsonschema import validate, ValidationError
except ImportError:
    print("Error: jsonschema package not installed", file=sys.stderr)
    print("Install with: pip install jsonschema", file=sys.stderr)
    sys.exit(1)


def validate_manifest(manifest_path, schema_path):
    """
    Validate manifest against JSON schema.
    
    Args:
        manifest_path: Path to YAML manifest
        schema_path: Path to JSON schema
        
    Returns:
        (bool, list): (success, list of error messages)
    """
    errors = []
    
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest_data = yaml.safe_load(f)
    except Exception as e:
        return False, [f"Failed to load manifest: {e}"]
    
    try:
        with open(schema_path, "r", encoding="utf-8") as f:
            schema_data = json.load(f)
    except Exception as e:
        return False, [f"Failed to load schema: {e}"]
    
    try:
        validate(instance=manifest_data, schema=schema_data)
        return True, []
    except ValidationError as e:
        # Build a readable error message
        path = " -> ".join(str(p) for p in e.path) if e.path else "root"
        errors.append(f"Validation error at {path}: {e.message}")
        
        # Add context if available
        if e.context:
            for ctx_error in e.context:
                ctx_path = " -> ".join(str(p) for p in ctx_error.path) if ctx_error.path else "root"
                errors.append(f"  Context at {ctx_path}: {ctx_error.message}")
        
        return False, errors
    except Exception as e:
        return False, [f"Validation error: {e}"]


def main():
    parser = argparse.ArgumentParser(
        description="Validate manifest against JSON schema"
    )
    parser.add_argument("manifest", help="Path to YAML manifest")
    parser.add_argument(
        "--schema",
        default="schema/manifest.schema.json",
        help="Path to JSON schema (default: schema/manifest.schema.json)"
    )
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress output")
    args = parser.parse_args()
    
    success, errors = validate_manifest(args.manifest, args.schema)
    
    if not args.quiet:
        if success:
            print("✓ Manifest is valid")
        else:
            print("✗ Manifest validation failed:", file=sys.stderr)
            for error in errors:
                print(f"  {error}", file=sys.stderr)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
