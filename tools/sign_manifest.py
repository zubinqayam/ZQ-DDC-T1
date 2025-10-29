#!/usr/bin/env python3
"""
Deterministic minisign-based signer for ZQ DDC Core V1 manifests.

This tool signs YAML manifests in a reproducible way by:
1. Loading the manifest YAML
2. Removing any existing signature field
3. Serializing to canonical YAML (deterministic ordering)
4. Computing the signature using minisign
5. Inserting the signature back into the manifest
"""

import sys
import subprocess
import json
import yaml
from pathlib import Path
from collections import OrderedDict
import argparse


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
    """Create canonical payload for signing (manifest without signature)."""
    clean_manifest = remove_signature(manifest)
    return ordered_dump(clean_manifest).encode('utf-8')


def sign_with_minisign(payload, secret_key_path, password=None):
    """Sign payload using minisign."""
    cmd = ['minisign', '-S', '-m', '-', '-s', str(secret_key_path), '-x', '-']
    
    if password:
        # Use password if provided
        env = {'MINISIGN_PASSWORD': password}
    else:
        # Interactive password entry
        env = None
    
    try:
        result = subprocess.run(
            cmd,
            input=payload,
            capture_output=True,
            check=True,
            env=env
        )
        signature = result.stdout.decode('utf-8').strip()
        return signature
    except subprocess.CalledProcessError as e:
        print(f"Error signing with minisign: {e.stderr.decode('utf-8')}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("Error: minisign not found. Please install minisign.", file=sys.stderr)
        sys.exit(1)


def insert_signature(manifest, signature):
    """Insert signature into manifest."""
    if 'signing' not in manifest:
        manifest['signing'] = OrderedDict()
    if 'signature' not in manifest['signing']:
        manifest['signing']['signature'] = OrderedDict()
    
    manifest['signing']['signature']['value'] = signature
    return manifest


def sign_manifest(manifest_path, secret_key_path, output_path=None, password=None):
    """Sign a manifest file."""
    manifest_path = Path(manifest_path)
    secret_key_path = Path(secret_key_path)
    
    if not manifest_path.exists():
        print(f"Error: Manifest file not found: {manifest_path}", file=sys.stderr)
        sys.exit(1)
    
    if not secret_key_path.exists():
        print(f"Error: Secret key not found: {secret_key_path}", file=sys.stderr)
        sys.exit(1)
    
    # Load manifest
    with open(manifest_path, 'r') as f:
        manifest = ordered_load(f)
    
    # Create canonical payload
    payload = canonical_payload(manifest)
    
    # Sign payload
    signature = sign_with_minisign(payload, secret_key_path, password)
    
    # Insert signature
    signed_manifest = insert_signature(manifest, signature)
    
    # Write output
    if output_path:
        output_path = Path(output_path)
        with open(output_path, 'w') as f:
            ordered_dump(signed_manifest, f)
        print(f"Signed manifest written to: {output_path}")
    else:
        # Overwrite original
        with open(manifest_path, 'w') as f:
            ordered_dump(signed_manifest, f)
        print(f"Signed manifest written to: {manifest_path}")
    
    return signed_manifest


def main():
    parser = argparse.ArgumentParser(
        description='Sign a ZQ DDC Core V1 manifest using minisign'
    )
    parser.add_argument(
        'manifest',
        help='Path to the manifest file to sign'
    )
    parser.add_argument(
        '-s', '--secret-key',
        required=True,
        help='Path to minisign secret key file'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output path (default: overwrite input file)'
    )
    parser.add_argument(
        '-p', '--password',
        help='Secret key password (not recommended, use interactive entry)'
    )
    
    args = parser.parse_args()
    
    sign_manifest(args.manifest, args.secret_key, args.output, args.password)


if __name__ == '__main__':
    main()
