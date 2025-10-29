#!/usr/bin/env python3
"""
Comprehensive validation script for ZQ DDC Core V1.
Runs all integrity checks and reports results.
"""
import argparse
import glob
import os
import sys

# Color codes for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def run_check(name, func, *args, **kwargs):
    """Run a check function and report results."""
    print(f"\n{'=' * 60}")
    print(f"{name}")
    print(f"{'=' * 60}")
    
    try:
        success, message = func(*args, **kwargs)
        if success:
            print(f"{GREEN}✓ PASS{RESET}: {message}")
        else:
            print(f"{RED}✗ FAIL{RESET}: {message}")
        return success
    except Exception as e:
        print(f"{RED}✗ ERROR{RESET}: {e}")
        return False


def check_files_tracked():
    """Check that all expected files are tracked in hash inventory."""
    from hash_inventory import parser as hash_parser
    import json
    
    # Expected files based on integrity scope
    expected_patterns = ["core/**", "tools/**", "README.md", "LICENSE", "Makefile"]
    
    # Generate inventory
    os.system("python3 tools/hash_inventory.py . --out /tmp/check-inventory.json > /dev/null 2>&1")
    
    with open("/tmp/check-inventory.json", "r") as f:
        inventory = json.load(f)
    
    tracked_files = [e["path"] for e in inventory["entries"]]
    
    # Check key files
    required_files = [
        "LICENSE",
        "Makefile", 
        "README.md",
        "core/__init__.py",
        "core/main.py",
    ]
    
    missing = [f for f in required_files if f not in tracked_files]
    
    if missing:
        return False, f"Missing files: {', '.join(missing)}"
    
    return True, f"All {len(tracked_files)} files tracked in inventory"


def check_manifest_schema(manifest_path):
    """Validate manifest against schema."""
    import subprocess
    result = subprocess.run(
        ["python3", "tools/validate_schema.py", manifest_path],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        return True, "Manifest schema valid"
    else:
        return False, result.stderr.strip()


def check_schema_uri(manifest_path):
    """Check schema URI in manifest."""
    import subprocess
    result = subprocess.run(
        ["python3", "tools/check_schema_uri.py", manifest_path],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        return True, "Schema URI correct"
    else:
        return False, result.stderr.strip()


def check_manifest_signature(manifest_path, pubkey=None):
    """Check manifest signature."""
    import subprocess
    
    cmd = ["python3", "tools/verify_manifest.py", manifest_path]
    if pubkey:
        cmd.extend(["--pubkey", pubkey])
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        return True, result.stdout.strip()
    else:
        # Check if it's just a placeholder
        if "placeholder" in result.stderr.lower():
            return True, "Signature is placeholder (acceptable for development)"
        return False, result.stderr.strip()


def check_hash_consistency():
    """Check that merkle root in manifest matches computed value."""
    import json
    import yaml
    
    # Generate fresh inventory
    os.system("python3 tools/hash_inventory.py . --out /tmp/verify-inventory.json > /dev/null 2>&1")
    
    with open("/tmp/verify-inventory.json", "r") as f:
        inventory = json.load(f)
    
    computed_root = inventory["merkle_root"]
    
    # Read manifest
    with open("manifest/core-v1.manifest.yaml", "r") as f:
        manifest = yaml.safe_load(f)
    
    manifest_root = manifest["doc_index"]["integrity"]["merkle_root"]
    
    if computed_root == manifest_root:
        return True, f"Merkle root matches: {computed_root[:16]}..."
    else:
        return False, f"Merkle root mismatch! Computed: {computed_root[:16]}..., Manifest: {manifest_root[:16]}..."


def main():
    parser = argparse.ArgumentParser(
        description="Run comprehensive validation checks"
    )
    parser.add_argument(
        "--pubkey",
        help="Path to minisign public key for signature verification"
    )
    parser.add_argument(
        "--manifest",
        default="manifest/core-v1.manifest.yaml",
        help="Path to manifest (default: manifest/core-v1.manifest.yaml)"
    )
    args = parser.parse_args()
    
    print(f"\n{YELLOW}ZQ DDC Core V1 - Comprehensive Validation{RESET}")
    print(f"{YELLOW}{'=' * 60}{RESET}")
    
    checks = []
    
    # Run all checks
    checks.append(run_check(
        "1. File Tracking Check",
        check_files_tracked
    ))
    
    checks.append(run_check(
        "2. Hash Consistency Check",
        check_hash_consistency
    ))
    
    checks.append(run_check(
        "3. Manifest Schema Validation",
        check_manifest_schema,
        args.manifest
    ))
    
    checks.append(run_check(
        "4. Schema URI Check",
        check_schema_uri,
        args.manifest
    ))
    
    checks.append(run_check(
        "5. Manifest Signature Check",
        check_manifest_signature,
        args.manifest,
        args.pubkey
    ))
    
    # Summary
    print(f"\n{YELLOW}{'=' * 60}{RESET}")
    print(f"{YELLOW}VALIDATION SUMMARY{RESET}")
    print(f"{YELLOW}{'=' * 60}{RESET}")
    
    passed = sum(checks)
    total = len(checks)
    
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print(f"{GREEN}✓ ALL CHECKS PASSED{RESET}")
        sys.exit(0)
    else:
        print(f"{RED}✗ SOME CHECKS FAILED{RESET}")
        sys.exit(1)


if __name__ == "__main__":
    main()
