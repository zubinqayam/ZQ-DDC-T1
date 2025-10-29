#!/usr/bin/env python3
"""
Deterministic minisign-based verifier for ZQ DDC Core V1 manifests.

This tool verifies signed YAML manifests by:
1. Loading the manifest YAML
2. Extracting the signature
3. Removing the signature field to create canonical payload
4. Verifying the signature using minisign
"""

import sys
import subprocess
import yaml
from pathlib import Path
from collections import OrderedDict
import argparse
import tempfile


def ordered_load(stream):
    """Load YAML with ordered dictionaries to maintain key order."""
    class OrderedLoader(yaml.SafeLoader):
        pass
    
    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return OrderedDict(loader.construct_pairs(node))
    
    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping
    )
    
    return yaml.load(stream, OrderedLoader)


def ordered_dump(data, stream=None):
    """Dump YAML with consistent ordering."""
    class OrderedDumper(yaml.SafeDumper):
        pass
    
    def _dict_representer(dumper, data):
        return dumper.represent_mapping(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
            data.items()
        )
    
    OrderedDumper.add_representer(OrderedDict, _dict_representer)
    
    return yaml.dump(
        data,
        stream,
        Dumper=OrderedDumper,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False
    )


def extract_signature(manifest):
    """Extract signature from manifest."""
    try:
        return manifest['signing']['signature']['value']
    except KeyError:
        return None


def remove_signature(manifest):
    """Remove signature field from manifest for canonical payload."""
    manifest = manifest.copy()
    if 'signing' in manifest and 'signature' in manifest['signing']:
        if 'value' in manifest['signing']['signature']:
            del manifest['signing']['signature']['value']
        # Clean up empty structures
        if not manifest['signing']['signature']:
            del manifest['signing']['signature']
        if not manifest['signing']:
            del manifest['signing']
    return manifest


def canonical_payload(manifest):
    """Create canonical payload for verification (manifest without signature)."""
    clean_manifest = remove_signature(manifest)
    return ordered_dump(clean_manifest).encode('utf-8')


def verify_with_minisign(payload, signature, public_key_path):
    """Verify payload signature using minisign."""
    public_key_path = Path(public_key_path)
    
    if not public_key_path.exists():
        print(f"Error: Public key not found: {public_key_path}", file=sys.stderr)
        return False
    
    # Create temporary files for payload and signature
    with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.payload') as payload_file:
        payload_file.write(payload)
        payload_path = payload_file.name
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.minisig') as sig_file:
        sig_file.write(signature)
        sig_path = sig_file.name
    
    try:
        cmd = ['minisign', '-V', '-m', payload_path, '-x', sig_path, '-P', 
               public_key_path.read_text().strip()]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            check=False
        )
        
        success = result.returncode == 0
        
        if not success:
            print(f"Signature verification failed: {result.stderr.decode('utf-8')}", 
                  file=sys.stderr)
        
        return success
        
    except FileNotFoundError:
        print("Error: minisign not found. Please install minisign.", file=sys.stderr)
        return False
    finally:
        # Clean up temporary files
        Path(payload_path).unlink(missing_ok=True)
        Path(sig_path).unlink(missing_ok=True)


def verify_manifest(manifest_path, public_key_path):
    """Verify a signed manifest file."""
    manifest_path = Path(manifest_path)
    
    if not manifest_path.exists():
        print(f"Error: Manifest file not found: {manifest_path}", file=sys.stderr)
        return False
    
    # Load manifest
    with open(manifest_path, 'r') as f:
        manifest = ordered_load(f)
    
    # Extract signature
    signature = extract_signature(manifest)
    if not signature:
        print(f"Error: No signature found in manifest: {manifest_path}", file=sys.stderr)
        return False
    
    # Create canonical payload
    payload = canonical_payload(manifest)
    
    # Verify signature
    if verify_with_minisign(payload, signature, public_key_path):
        print(f"✓ Signature valid for: {manifest_path}")
        return True
    else:
        print(f"✗ Signature verification failed for: {manifest_path}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Verify a signed ZQ DDC Core V1 manifest using minisign'
    )
    parser.add_argument(
        'manifest',
        help='Path to the signed manifest file'
    )
    parser.add_argument(
        '-p', '--public-key',
        required=True,
        help='Path to minisign public key file'
    )
    
    args = parser.parse_args()
    
    success = verify_manifest(args.manifest, args.public_key)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
