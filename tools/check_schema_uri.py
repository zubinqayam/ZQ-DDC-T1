#!/usr/bin/env python3
"""
Schema URI checker for ZQ DDC Core V1 manifests.
Ensures manifest references the correct schema URI.
"""
import argparse
import sys
import yaml


def check_schema_uri(manifest_path, expected_uri="schema/manifest.schema.json"):
    """
    Check that manifest has a schema_uri field referencing the expected schema.
    
    Args:
        manifest_path: Path to YAML manifest
        expected_uri: Expected schema URI value
        
    Returns:
        (bool, str): (success, message)
    """
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception as e:
        return False, f"Failed to load manifest: {e}"
    
    # Check for schema_uri in top level or doc_index
    schema_uri = data.get("schema_uri") or data.get("doc_index", {}).get("schema_uri")
    
    if not schema_uri:
        return False, f"No schema_uri field found (expected: {expected_uri})"
    
    if schema_uri != expected_uri:
        return False, f"Schema URI mismatch: found '{schema_uri}', expected '{expected_uri}'"
    
    return True, f"Schema URI correct: {schema_uri}"


def main():
    parser = argparse.ArgumentParser(
        description="Check manifest schema_uri field"
    )
    parser.add_argument("manifest", help="Path to YAML manifest")
    parser.add_argument(
        "--expected",
        default="schema/manifest.schema.json",
        help="Expected schema URI (default: schema/manifest.schema.json)"
    )
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress output")
    parser.add_argument(
        "--add-if-missing",
        action="store_true",
        help="Add schema_uri field if missing"
    )
    args = parser.parse_args()
    
    success, message = check_schema_uri(args.manifest, args.expected)
    
    # If missing and --add-if-missing is set, add it
    if not success and args.add_if_missing and "No schema_uri field found" in message:
        try:
            with open(args.manifest, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            
            # Add to doc_index
            if "doc_index" not in data:
                data["doc_index"] = {}
            data["doc_index"]["schema_uri"] = args.expected
            
            with open(args.manifest, "w", encoding="utf-8") as f:
                yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)
            
            success = True
            message = f"Added schema_uri: {args.expected}"
        except Exception as e:
            success = False
            message = f"Failed to add schema_uri: {e}"
    
    if not args.quiet:
        if success:
            print(f"✓ {message}")
        else:
            print(f"✗ {message}", file=sys.stderr)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
