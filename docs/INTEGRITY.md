# Integrity Model

## Overview
ZQ DDC Core V1 uses a comprehensive integrity validation system to ensure no data is missed and all files are properly tracked and verified.

## Components

### Hash Inventory
- `tools/hash_inventory.py` produces `manifest/hash-inventory.json` and Merkle root.
- Tracks all files in the integrity scope: `core/**`, `tools/**`, `README.md`, `LICENSE`, `Makefile`
- Automatically excludes `__pycache__` directories and `.pyc` files
- Generates SHA-256 hash for each tracked file
- Computes Merkle tree root from file hashes

### Manifest Signing
- `tools/sign_manifest.py` signs `manifest/core-v1.manifest.yaml` (doc_index only) using minisign.
- Creates deterministic canonical JSON payload (with signature.value stripped)
- Signs using minisign cryptographic signatures
- Updates manifest with signature and timestamp

### Validation Tools

#### 1. Manifest Verifier (`tools/verify_manifest.py`)
- Verifies deterministic signature against canonical payload
- Confirms signature.value matches the hashed doc_index (minus signature.value itself)
- Optionally verifies cryptographic signature with public key

#### 2. Schema Validator (`tools/validate_schema.py`)
- Validates manifest structure against `schema/manifest.schema.json`
- Ensures all required fields are present
- Validates field types and formats (e.g., merkle_root must be 64-char hex)

#### 3. Schema URI Checker (`tools/check_schema_uri.py`)
- Ensures manifest references correct schema URI
- Can automatically add schema_uri field if missing
- Prevents schema version mismatches

#### 4. Tag Protection (`tools/tag_protect_unsigned.py`)
- Validates all manifests have valid signatures before release
- Prevents unsigned releases when used in CI/CD
- Requires public key for cryptographic verification

#### 5. Comprehensive Validator (`tools/validate_all.py`)
- Runs all validation checks in sequence
- Verifies file tracking completeness
- Checks hash consistency between inventory and manifest
- Validates schema compliance
- Verifies signatures
- Provides detailed pass/fail report

## Usage

### Generate Hash Inventory
```bash
make hashes
# or
python3 tools/hash_inventory.py . --out manifest/hash-inventory.json
```

### Sign Manifest
```bash
make sign
# or
python3 tools/sign_manifest.py manifest/core-v1.manifest.yaml --key ~/.minisign/key.secret --update
```

### Validate Everything
```bash
make validate
# or
python3 tools/validate_all.py
```

### Individual Validations
```bash
# Schema validation
python3 tools/validate_schema.py manifest/core-v1.manifest.yaml

# Signature verification
python3 tools/verify_manifest.py manifest/core-v1.manifest.yaml --pubkey ~/.minisign/key.pub

# Schema URI check
python3 tools/check_schema_uri.py manifest/core-v1.manifest.yaml

# Tag protection check
python3 tools/tag_protect_unsigned.py --pubkey ~/.minisign/key.pub
```

## Release Process

The release process includes validation:
```bash
make release
```

This runs:
1. `make hashes` - Generate hash inventory
2. `make sign` - Sign manifest with minisign
3. `make validate` - Run all validation checks
4. Prepare release artifacts

## Schema

The manifest schema (`schema/manifest.schema.json`) defines:
- Required fields and structure
- Field types and formats
- Integrity scope patterns
- Signing metadata requirements

## Security Properties

1. **Deterministic Verification**: Signature verification uses canonical JSON (sorted keys, no whitespace)
2. **Merkle Tree Integrity**: File changes are detected via Merkle root mismatch
3. **Schema Compliance**: All manifests must conform to versioned schema
4. **Cryptographic Signatures**: Minisign provides Ed25519 signature verification
5. **Complete Coverage**: All files in integrity scope are tracked

## Continuous Integration

- Release assets are uploaded by CI after validation
- Tag protection requires valid signatures
- All validation checks must pass before release
