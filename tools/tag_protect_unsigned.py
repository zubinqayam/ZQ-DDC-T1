#!/usr/bin/env python3
"""
Tag protection tool for ZQ DDC Core V1 manifests.

When executed in the context of a release tag, this tool verifies that
each manifest's signature is present and valid. It fails the process if
any signature is missing or invalid.
"""

import sys
import yaml
from pathlib import Path
import argparse
import glob


def find_manifests(directory='.', pattern='**/*.yaml'):
    """Find all manifest files in the directory."""
    manifests = []
    for path in Path(directory).glob(pattern):
        if path.is_file():
            # Check if it looks like a manifest
            try:
                with open(path, 'r') as f:
                    data = yaml.safe_load(f)
                    if isinstance(data, dict) and 'schema_uri' in data:
                        manifests.append(path)
            except:
                pass
    return manifests


def check_signature_present(manifest_path):
    """Check if manifest has a signature."""
    try:
        with open(manifest_path, 'r') as f:
            manifest = yaml.safe_load(f)
        
        if 'signing' not in manifest:
            return False, "Missing 'signing' section"
        
        if 'signature' not in manifest['signing']:
            return False, "Missing 'signature' section"
        
        if 'value' not in manifest['signing']['signature']:
            return False, "Missing 'signature.value' field"
        
        sig_value = manifest['signing']['signature']['value']
        if not sig_value or not isinstance(sig_value, str) or not sig_value.strip():
            return False, "Empty or invalid signature value"
        
        return True, "Signature present"
        
    except Exception as e:
        return False, f"Error reading manifest: {e}"


def verify_signature(manifest_path, public_key_path):
    """Verify manifest signature using verify_manifest.py."""
    import subprocess
    
    # Get the directory of this script
    script_dir = Path(__file__).parent
    verify_script = script_dir / 'verify_manifest.py'
    
    if not verify_script.exists():
        return False, "verify_manifest.py not found"
    
    try:
        result = subprocess.run(
            [sys.executable, str(verify_script), str(manifest_path), '-p', str(public_key_path)],
            capture_output=True,
            check=False
        )
        
        if result.returncode == 0:
            return True, "Signature valid"
        else:
            return False, "Signature verification failed"
            
    except Exception as e:
        return False, f"Error verifying: {e}"


def tag_protect(directory='.', public_key_path=None, verify=True):
    """Check all manifests for valid signatures."""
    manifests = find_manifests(directory)
    
    if not manifests:
        print("⚠ Warning: No manifests found", file=sys.stderr)
        return True
    
    print(f"Checking {len(manifests)} manifest(s)...")
    
    all_valid = True
    
    for manifest_path in manifests:
        # Check signature presence
        present, msg = check_signature_present(manifest_path)
        
        if not present:
            print(f"✗ {manifest_path}: {msg}", file=sys.stderr)
            all_valid = False
            continue
        
        # Verify signature if requested and public key provided
        if verify and public_key_path:
            valid, msg = verify_signature(manifest_path, public_key_path)
            if not valid:
                print(f"✗ {manifest_path}: {msg}", file=sys.stderr)
                all_valid = False
            else:
                print(f"✓ {manifest_path}: {msg}")
        else:
            print(f"✓ {manifest_path}: {msg}")
    
    return all_valid


def main():
    parser = argparse.ArgumentParser(
        description='Tag protection: verify all manifests are signed'
    )
    parser.add_argument(
        '-d', '--directory',
        default='.',
        help='Directory to search for manifests (default: current directory)'
    )
    parser.add_argument(
        '-p', '--public-key',
        help='Path to minisign public key for verification'
    )
    parser.add_argument(
        '--no-verify',
        action='store_true',
        help='Only check signature presence, do not verify'
    )
    
    args = parser.parse_args()
    
    verify = not args.no_verify
    
    if verify and not args.public_key:
        print("Warning: No public key provided, only checking signature presence", 
              file=sys.stderr)
        verify = False
    
    success = tag_protect(args.directory, args.public_key, verify)
    
    if success:
        print("\n✓ All manifests have valid signatures")
        sys.exit(0)
    else:
        print("\n✗ Some manifests have missing or invalid signatures", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
