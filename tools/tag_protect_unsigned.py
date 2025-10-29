#!/usr/bin/env python3
"""
Tag protection validator for ZQ DDC Core V1.
Verifies that manifests have valid signatures when releasing tags.
"""
import argparse
import glob
import os
import sys
import yaml

# Import verify function from verify_manifest
try:
    from verify_manifest import verify_manifest
except ImportError:
    # If not importable, define inline
    import json
    import subprocess
    import tempfile
    
    def canonical(obj):
        return json.dumps(obj, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    
    def verify_manifest(manifest_path, pubkey_path=None):
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except Exception as e:
            return False, f"Failed to load manifest: {e}"
        
        doc_index = data.get("doc_index", {})
        signing = doc_index.get("signing", {})
        signature_obj = signing.get("signature", {})
        signature_value = signature_obj.get("value", "")
        
        if not signature_value:
            return False, "No signature found in manifest"
        
        payload_data = json.loads(json.dumps(doc_index))
        if "signing" in payload_data and "signature" in payload_data["signing"]:
            if "value" in payload_data["signing"]["signature"]:
                del payload_data["signing"]["signature"]["value"]
        
        canonical_payload = canonical(payload_data)
        
        if pubkey_path:
            if not os.path.exists(pubkey_path):
                return False, f"Public key not found: {pubkey_path}"
            
            try:
                with tempfile.TemporaryDirectory() as td:
                    payload_file = os.path.join(td, "payload.json")
                    with open(payload_file, "w", encoding="utf-8") as pf:
                        pf.write(canonical_payload)
                    
                    sig_file = payload_file + ".minisig"
                    with open(sig_file, "w", encoding="utf-8") as sf:
                        sf.write(signature_value)
                    
                    result = subprocess.run(
                        ["minisign", "-Vm", payload_file, "-p", pubkey_path, "-x", sig_file],
                        capture_output=True,
                        text=True
                    )
                    
                    if result.returncode != 0:
                        return False, f"Signature verification failed: {result.stderr}"
                    
                    return True, "Signature verified successfully"
            except FileNotFoundError:
                return False, "minisign not found"
            except Exception as e:
                return False, f"Verification error: {e}"
        else:
            if signature_value and signature_value != "${MINISIGN_SIG}":
                return True, "Signature present"
            else:
                return False, "Signature is placeholder or empty"


def check_tag_protection(manifest_dir, pubkey_path):
    """
    Check all manifests in directory for valid signatures.
    
    Args:
        manifest_dir: Directory containing manifests
        pubkey_path: Path to minisign public key
        
    Returns:
        (bool, list): (all_valid, list of results)
    """
    manifests = glob.glob(os.path.join(manifest_dir, "*.yaml")) + \
                glob.glob(os.path.join(manifest_dir, "*.yml"))
    
    if not manifests:
        return False, [f"No manifests found in {manifest_dir}"]
    
    results = []
    all_valid = True
    
    for manifest_path in sorted(manifests):
        manifest_name = os.path.basename(manifest_path)
        success, message = verify_manifest(manifest_path, pubkey_path)
        
        results.append({
            "manifest": manifest_name,
            "success": success,
            "message": message
        })
        
        if not success:
            all_valid = False
    
    return all_valid, results


def main():
    parser = argparse.ArgumentParser(
        description="Verify tag protection via manifest signatures"
    )
    parser.add_argument(
        "--manifest-dir",
        default="manifest",
        help="Directory containing manifests (default: manifest)"
    )
    parser.add_argument(
        "--pubkey",
        required=True,
        help="Path to minisign public key"
    )
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress output")
    args = parser.parse_args()
    
    all_valid, results = check_tag_protection(args.manifest_dir, args.pubkey)
    
    if not args.quiet:
        print("Tag Protection Validation")
        print("=" * 50)
        for result in results:
            status = "✓" if result["success"] else "✗"
            print(f"{status} {result['manifest']}: {result['message']}")
        print("=" * 50)
        
        if all_valid:
            print("✓ All manifests have valid signatures")
        else:
            print("✗ Some manifests have invalid or missing signatures", file=sys.stderr)
    
    sys.exit(0 if all_valid else 1)


if __name__ == "__main__":
    main()
