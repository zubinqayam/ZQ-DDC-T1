# ZQ DDC Core V1 - Validation Guide

## Overview

This document describes the validation framework for ZQ DDC Core V1, ensuring data integrity and completeness across the entire system.

## Validation Philosophy

**"MAKE SURE NO DATA MISSED"** - The core principle is comprehensive data tracking and verification:

1. All files in the integrity scope must be tracked
2. All manifests must be schema-compliant
3. All signatures must be verifiable
4. Hash consistency must be maintained
5. No files should be accidentally excluded

## Validation Tools

### 1. verify_manifest.py

**Purpose**: Deterministic signature verification

**What it does**:
- Loads manifest YAML
- Extracts doc_index and removes signature.value
- Generates canonical JSON (sorted keys, compact format)
- Verifies signature matches the canonical payload
- Optionally cryptographically verifies with public key

**Usage**:
```bash
# Check signature presence
python3 tools/verify_manifest.py manifest/core-v1.manifest.yaml

# Verify with public key
python3 tools/verify_manifest.py manifest/core-v1.manifest.yaml --pubkey ~/.minisign/key.pub
```

**Exit codes**:
- 0: Signature valid
- 1: Signature invalid or missing

### 2. validate_schema.py

**Purpose**: Schema compliance validation

**What it does**:
- Validates manifest structure against JSON schema
- Checks all required fields are present
- Validates field types (string, integer, object, array)
- Validates formats (date-time, hex patterns)
- Reports specific validation errors with paths

**Usage**:
```bash
python3 tools/validate_schema.py manifest/core-v1.manifest.yaml
```

**Common validation errors**:
- Missing required fields
- Invalid merkle_root format (must be 64-char hex)
- Invalid version format (must be semver: X.Y.Z)
- Invalid date-time format

### 3. check_schema_uri.py

**Purpose**: Schema URI validation and management

**What it does**:
- Checks manifest has schema_uri field
- Validates URI matches expected value
- Can add schema_uri if missing

**Usage**:
```bash
# Check schema URI
python3 tools/check_schema_uri.py manifest/core-v1.manifest.yaml

# Add if missing
python3 tools/check_schema_uri.py manifest/core-v1.manifest.yaml --add-if-missing

# Check against custom schema
python3 tools/check_schema_uri.py manifest/core-v1.manifest.yaml --expected custom/schema.json
```

### 4. tag_protect_unsigned.py

**Purpose**: Tag/release protection

**What it does**:
- Scans manifest directory for all YAML files
- Verifies each manifest has valid signature
- Requires public key for verification
- Fails if any manifest is unsigned or invalid

**Usage**:
```bash
python3 tools/tag_protect_unsigned.py --pubkey ~/.minisign/key.pub

# Custom manifest directory
python3 tools/tag_protect_unsigned.py --pubkey ~/.minisign/key.pub --manifest-dir custom/path
```

**Use case**: In CI/CD before creating release tags

### 5. validate_all.py

**Purpose**: Comprehensive validation suite

**What it does**:
1. **File Tracking Check**: Verifies all expected files are in inventory
2. **Hash Consistency Check**: Compares manifest merkle_root with computed value
3. **Schema Validation**: Validates manifest against schema
4. **Schema URI Check**: Validates schema_uri field
5. **Signature Check**: Verifies manifest signature

**Usage**:
```bash
# Run all checks
python3 tools/validate_all.py

# With public key verification
python3 tools/validate_all.py --pubkey ~/.minisign/key.pub

# Custom manifest
python3 tools/validate_all.py --manifest custom/manifest.yaml
```

**Output**: Color-coded report showing PASS/FAIL for each check

## Makefile Targets

Validation is integrated into the Makefile:

```bash
# Run comprehensive validation
make validate

# Schema validation only
make validate-schema

# Signature verification only
make validate-signature

# Full release with validation
make release
```

## Integrity Scope

Files tracked in the integrity scope (defined in manifest):

```yaml
integrity_scope:
  include:
    - core/**
    - tools/**
    - README.md
    - LICENSE
    - Makefile
```

**Currently tracked** (as of latest validation):
- LICENSE
- Makefile
- README.md
- core/__init__.py
- core/main.py
- tools/check_env.py
- tools/check_schema_uri.py
- tools/hash_inventory.py
- tools/sign_manifest.py
- tools/tag_protect_unsigned.py
- tools/validate_all.py
- tools/validate_schema.py
- tools/verify_manifest.py

**Excluded**:
- `__pycache__/` directories
- `*.pyc` files
- `.venv/` virtual environment
- `.git/` version control
- `docs/` documentation
- `manifest/` (except as specified)
- `schema/` (metadata, not code)

## Schema Definition

The manifest schema (`schema/manifest.schema.json`) enforces:

### Required Top-Level Fields
- `version`: Must be integer 1
- `kind`: Must be "zqddc.core"
- `doc_index`: Object with required subfields

### Required doc_index Fields
- `version`: Semver string (X.Y.Z)
- `release`: Release name
- `created_at`: ISO 8601 timestamp
- `commit`: Git SHA
- `integrity_scope`: With include array
- `integrity`: With algo="sha256" and merkle_root
- `signing`: With scheme, key_id, signature

### Signature Structure
```yaml
signing:
  scheme: minisign
  key_id: "identifier"
  signature:
    value: "minisign signature"
    created_at: "ISO 8601 timestamp"
```

## Validation Workflow

### Development Workflow

1. Make code changes to files in integrity scope
2. Generate hash inventory:
   ```bash
   make hashes
   ```
3. Update manifest with new merkle_root
4. Run validation:
   ```bash
   make validate
   ```
5. Fix any issues reported
6. Commit changes

### Release Workflow

1. Ensure all code changes committed
2. Run full release process:
   ```bash
   make release
   ```
3. This automatically:
   - Generates hash inventory
   - Signs manifest (requires minisign key)
   - Runs validation
   - Prepares release artifacts
4. All validation checks must pass
5. Tag release in git
6. CI uploads release assets

## Troubleshooting

### "Merkle root mismatch"

**Cause**: Files in integrity scope changed since last hash generation

**Fix**:
```bash
make hashes
# Update manifest with new merkle_root shown in output
```

### "Signature is placeholder or empty"

**Cause**: Manifest not signed yet

**Fix**:
```bash
make sign
```

### "Manifest validation failed"

**Cause**: Manifest doesn't conform to schema

**Fix**: Check error message for specific field/format issue. Common issues:
- merkle_root not 64-char hex
- version not in X.Y.Z format
- Missing required fields

### "Schema URI mismatch"

**Cause**: schema_uri field missing or incorrect

**Fix**:
```bash
python3 tools/check_schema_uri.py manifest/core-v1.manifest.yaml --add-if-missing
```

### "Some manifests have invalid signatures"

**Cause**: One or more manifests unsigned or signature invalid

**Fix**: Sign all manifests:
```bash
python3 tools/sign_manifest.py manifest/manifest-name.yaml --key ~/.minisign/key.secret --update
```

## Best Practices

1. **Always validate before commit**: Run `make validate`
2. **Keep scope minimal**: Only track essential files
3. **Automate in CI**: Run validation in continuous integration
4. **Use tag protection**: Require valid signatures for releases
5. **Document changes**: Update CHANGELOG.md for schema changes
6. **Version schemas**: Increment schema version for breaking changes

## Security Considerations

1. **Signature verification requires public key**: Without it, only presence is checked
2. **Canonical JSON ensures consistency**: Same payload always produces same signature
3. **Merkle tree detects tampering**: Any file change invalidates the root
4. **Schema prevents malformed data**: Invalid manifests are rejected
5. **Tag protection prevents unsigned releases**: CI enforces signature requirement

## Dependencies

Validation tools require:
- Python 3.11+
- PyYAML (`pip install pyyaml`)
- jsonschema (`pip install jsonschema`)
- minisign (for signature generation/verification)

Install all dependencies:
```bash
pip install -r requirements.txt
```

## Integration with CI/CD

Example GitHub Actions workflow:

```yaml
- name: Validate integrity
  run: |
    python3 tools/validate_all.py --pubkey .github/minisign.pub

- name: Check tag protection
  if: startsWith(github.ref, 'refs/tags/')
  run: |
    python3 tools/tag_protect_unsigned.py --pubkey .github/minisign.pub
```

This ensures:
- All PRs are validated
- Releases must have valid signatures
- No unsigned code reaches production

## Future Enhancements

Potential improvements for Core V2:

1. Multi-signature support
2. Timestamp verification
3. Dependency vulnerability scanning
4. Automated signature rotation
5. Hardware security module integration
6. Blockchain anchoring for immutability

## Support

For issues or questions about validation:
1. Check this document first
2. Review error messages carefully
3. Run `python3 tools/validate_all.py` for full diagnostics
4. Check INTEGRITY.md for system overview
5. Open an issue with validation output
