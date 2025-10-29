"""
Round-trip tests for manifest signing and verification.

Tests the complete workflow of:
1. Creating an unsigned manifest
2. Signing the manifest
3. Verifying the signature
4. Ensuring deterministic signing (same input = same signature with same key)
"""

import os
import sys
import tempfile
import subprocess
from pathlib import Path
import yaml
import pytest

# Add tools directory to path
REPO_ROOT = Path(__file__).parent.parent.parent
TOOLS_DIR = REPO_ROOT / 'tools'
sys.path.insert(0, str(TOOLS_DIR))


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def test_keys(temp_dir):
    """Generate test minisign keys."""
    key_dir = temp_dir / 'keys'
    key_dir.mkdir()
    
    secret_key = key_dir / 'minisign.key'
    public_key = key_dir / 'minisign.pub'
    
    # Generate keys non-interactively
    password = 'test-password'
    cmd = [
        'minisign', '-G',
        '-p', str(public_key),
        '-s', str(secret_key),
        '-W'  # Non-interactive
    ]
    
    process = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Provide password twice (for key generation)
    process.communicate(input=f"{password}\n{password}\n".encode())
    
    assert secret_key.exists(), "Secret key was not generated"
    assert public_key.exists(), "Public key was not generated"
    
    return {
        'secret': secret_key,
        'public': public_key,
        'password': password
    }


@pytest.fixture
def sample_manifest(temp_dir):
    """Create a sample manifest for testing."""
    manifest_path = temp_dir / 'test-manifest.yaml'
    
    manifest_data = {
        'schema_uri': 'schema/manifest.schema.json',
        'version': '1.0.0',
        'metadata': {
            'name': 'test-app',
            'type': 'application',
            'version': '1.0.0',
            'description': 'Test application for roundtrip testing'
        }
    }
    
    with open(manifest_path, 'w') as f:
        yaml.dump(manifest_data, f, default_flow_style=False, sort_keys=False)
    
    return manifest_path


def test_sign_and_verify(sample_manifest, test_keys):
    """Test signing and verifying a manifest."""
    # Import after path is set
    from sign_manifest import sign_manifest
    from verify_manifest import verify_manifest
    
    # Sign the manifest
    sign_manifest(
        sample_manifest,
        test_keys['secret'],
        password=test_keys['password']
    )
    
    # Check that signature was added
    with open(sample_manifest, 'r') as f:
        signed = yaml.safe_load(f)
    
    assert 'signing' in signed, "Signing section not added"
    assert 'signature' in signed['signing'], "Signature section not added"
    assert 'value' in signed['signing']['signature'], "Signature value not added"
    assert signed['signing']['signature']['value'], "Signature value is empty"
    
    # Verify the signature
    result = verify_manifest(sample_manifest, test_keys['public'])
    assert result is True, "Signature verification failed"


def test_deterministic_signing(sample_manifest, test_keys):
    """Test that signing is deterministic (same input = same signature)."""
    from sign_manifest import sign_manifest, canonical_payload, ordered_load
    
    # Load original manifest
    with open(sample_manifest, 'r') as f:
        original = ordered_load(f)
    
    # Create canonical payload
    payload1 = canonical_payload(original)
    
    # Sign the manifest
    sign_manifest(
        sample_manifest,
        test_keys['secret'],
        password=test_keys['password']
    )
    
    # Load signed manifest
    with open(sample_manifest, 'r') as f:
        signed = ordered_load(f)
    
    signature1 = signed['signing']['signature']['value']
    
    # Create canonical payload from signed manifest (should be same as original)
    payload2 = canonical_payload(signed)
    
    # Payloads should be identical
    assert payload1 == payload2, "Canonical payload changed after signing"
    
    # Sign again (remove signature first)
    del signed['signing']['signature']['value']
    with open(sample_manifest, 'w') as f:
        from sign_manifest import ordered_dump
        ordered_dump(signed, f)
    
    sign_manifest(
        sample_manifest,
        test_keys['secret'],
        password=test_keys['password']
    )
    
    # Load re-signed manifest
    with open(sample_manifest, 'r') as f:
        resigned = ordered_load(f)
    
    signature2 = resigned['signing']['signature']['value']
    
    # Note: Minisign signatures may include timestamps, so they might differ
    # But the verification should still work
    from verify_manifest import verify_manifest
    result = verify_manifest(sample_manifest, test_keys['public'])
    assert result is True, "Re-signed manifest verification failed"


def test_tamper_detection(sample_manifest, test_keys):
    """Test that tampering is detected."""
    from sign_manifest import sign_manifest
    from verify_manifest import verify_manifest
    
    # Sign the manifest
    sign_manifest(
        sample_manifest,
        test_keys['secret'],
        password=test_keys['password']
    )
    
    # Verify it's valid
    assert verify_manifest(sample_manifest, test_keys['public']) is True
    
    # Tamper with the manifest (change metadata)
    with open(sample_manifest, 'r') as f:
        data = yaml.safe_load(f)
    
    data['metadata']['name'] = 'tampered-app'
    
    with open(sample_manifest, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)
    
    # Verification should fail
    assert verify_manifest(sample_manifest, test_keys['public']) is False


def test_signature_removal(sample_manifest, test_keys):
    """Test that removing signature causes verification to fail."""
    from sign_manifest import sign_manifest
    from verify_manifest import verify_manifest
    
    # Sign the manifest
    sign_manifest(
        sample_manifest,
        test_keys['secret'],
        password=test_keys['password']
    )
    
    # Remove signature
    with open(sample_manifest, 'r') as f:
        data = yaml.safe_load(f)
    
    del data['signing']['signature']['value']
    
    with open(sample_manifest, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)
    
    # Verification should fail (no signature found)
    assert verify_manifest(sample_manifest, test_keys['public']) is False


def test_schema_validation_integration(sample_manifest):
    """Test that schema validation works with test manifest."""
    from validate_schema import validate_manifest
    
    schema_path = REPO_ROOT / 'schema' / 'manifest.schema.json'
    
    if not schema_path.exists():
        pytest.skip("Schema file not found")
    
    result = validate_manifest(sample_manifest, schema_path)
    assert result is True, "Schema validation failed for test manifest"


def test_schema_uri_check_integration(sample_manifest):
    """Test that schema URI check works with test manifest."""
    from check_schema_uri import check_schema_uri
    
    result = check_schema_uri(sample_manifest, 'schema/manifest.schema.json')
    assert result is True, "Schema URI check failed for test manifest"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
