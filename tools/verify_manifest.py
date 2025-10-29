#!/usr/bin/env python3
"""
Deterministic manifest signature verifier.
Verifies that the signature in a manifest matches the canonical payload.
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
import yaml


def canonical(obj):
    """Generate canonical JSON representation."""
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def verify_manifest(manifest_path, pubkey_path=None):
    """
    Verify manifest signature against canonical payload.
    
    Args:
        manifest_path: Path to YAML manifest
        pubkey_path: Optional path to minisign public key
        
    Returns:
        (bool, str): (success, message)
    """
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception as e:
        return False, f"Failed to load manifest: {e}"
    
    # Extract doc_index for verification
    doc_index = data.get("doc_index", {})
    signing = doc_index.get("signing", {})
    signature_obj = signing.get("signature", {})
    signature_value = signature_obj.get("value", "")
    
    if not signature_value:
        return False, "No signature found in manifest"
    
    # Create canonical payload WITHOUT signature.value
    # We need to create a copy of doc_index with signature.value removed
    payload_data = json.loads(json.dumps(doc_index))  # Deep copy
    if "signing" in payload_data and "signature" in payload_data["signing"]:
        if "value" in payload_data["signing"]["signature"]:
            del payload_data["signing"]["signature"]["value"]
    
    canonical_payload = canonical(payload_data)
    
    # If pubkey provided, verify with minisign
    if pubkey_path:
        if not os.path.exists(pubkey_path):
            return False, f"Public key not found: {pubkey_path}"
        
        try:
            with tempfile.TemporaryDirectory() as td:
                # Write payload
                payload_file = os.path.join(td, "payload.json")
                with open(payload_file, "w", encoding="utf-8") as pf:
                    pf.write(canonical_payload)
                
                # Write signature
                sig_file = payload_file + ".minisig"
                with open(sig_file, "w", encoding="utf-8") as sf:
                    sf.write(signature_value)
                
                # Verify with minisign
                result = subprocess.run(
                    ["minisign", "-Vm", payload_file, "-p", pubkey_path, "-x", sig_file],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    return False, f"Signature verification failed: {result.stderr}"
                
                return True, "Signature verified successfully"
        except FileNotFoundError:
            return False, "minisign not found. Install minisign to verify signatures."
        except Exception as e:
            return False, f"Verification error: {e}"
    else:
        # Without pubkey, just check signature is present and non-empty
        if signature_value and signature_value != "${MINISIGN_SIG}":
            return True, "Signature present (not verified without public key)"
        else:
            return False, "Signature is placeholder or empty"


def main():
    parser = argparse.ArgumentParser(
        description="Verify manifest signature against canonical payload"
    )
    parser.add_argument("manifest", help="Path to YAML manifest")
    parser.add_argument("--pubkey", help="Path to minisign public key (optional)")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress output")
    args = parser.parse_args()
    
    success, message = verify_manifest(args.manifest, args.pubkey)
    
    if not args.quiet:
        if success:
            print(f"✓ {message}")
        else:
            print(f"✗ {message}", file=sys.stderr)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
