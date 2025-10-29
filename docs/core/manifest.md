# ZQ DDC Core V1 Manifest Documentation

## Overview

The ZQ DDC Core V1 manifest is a cryptographically signed YAML file that provides comprehensive provenance information for software artifacts. It ensures integrity, authenticity, and traceability throughout the software supply chain.

## Purpose

The manifest system provides:

1. **Integrity** - Cryptographic verification that manifests haven't been tampered with
2. **Authenticity** - Proof of who created and signed the manifest
3. **Provenance** - Complete build and source information
4. **Traceability** - Dependency tracking and artifact checksums
5. **Compliance** - Schema-validated structure for consistency

## Manifest Structure

### Required Fields

#### `schema_uri`
- **Type**: `string`
- **Value**: `schema/manifest.schema.json`
- **Description**: Reference to the schema definition

#### `version`
- **Type**: `string`
- **Format**: Semantic version (e.g., `1.0.0`)
- **Description**: Version of the manifest format

#### `metadata`
- **Type**: `object`
- **Required Fields**:
  - `name`: Name of the artifact or component
  - `type`: Type of artifact (application, library, service, container, document, data, other)
- **Optional Fields**:
  - `version`: Artifact version
  - `description`: Human-readable description
  - `authors`: List of authors or maintainers
  - `license`: SPDX license identifier
  - `repository`: Source repository URL
  - `created`: Creation timestamp (ISO 8601)
  - `tags`: Classification tags

### Optional Sections

#### `provenance`
Detailed provenance information including:

**Build Information**:
```yaml
provenance:
  build:
    builder: "GitHub Actions"
    timestamp: "2024-01-15T10:30:00Z"
    environment:
      os: "ubuntu-22.04"
      arch: "x86_64"
    inputs:
      - name: "source-code"
        version: "1.2.3"
        hash: "sha256:abc123..."
```

**Source Information**:
```yaml
provenance:
  source:
    repository: "https://github.com/org/repo"
    commit: "a1b2c3d4..."
    ref: "refs/tags/v1.0.0"
```

**Dependencies**:
```yaml
provenance:
  dependencies:
    - name: "library-name"
      version: "2.3.4"
      type: "runtime"
```

#### `artifacts`
List of artifacts with checksums:
```yaml
artifacts:
  - path: "dist/app.jar"
    hash: "sha256:def456..."
    size: 1024000
    type: "application/java-archive"
```

#### `signing`
Cryptographic signature information:
```yaml
signing:
  algorithm: "minisign"
  signer:
    name: "Build System"
    email: "build@example.com"
    key_id: "ABCD1234"
  signature:
    value: "untrusted comment: signature...\n..."
    timestamp: "2024-01-15T10:35:00Z"
```

#### `attestations`
Third-party attestations or verifications:
```yaml
attestations:
  - type: "security-scan"
    provider: "Snyk"
    timestamp: "2024-01-15T10:40:00Z"
    data:
      vulnerabilities: 0
      score: "A+"
```

## Signing Process

### Deterministic Signing

The signing process is deterministic to ensure reproducible signatures:

1. **Load Manifest**: Parse YAML file maintaining key order
2. **Remove Signature**: Strip any existing `signing.signature.value` field
3. **Canonicalize**: Serialize to consistent YAML format (no sorting)
4. **Sign**: Use minisign to create Ed25519 signature
5. **Insert**: Add signature back to manifest

### Signing Command

```bash
python tools/sign_manifest.py manifest.yaml -s keys/minisign.key
```

### Verification Command

```bash
python tools/verify_manifest.py manifest.yaml -p keys/minisign.pub
```

## Validation

### Schema Validation

Validates manifest structure against JSON schema:

```bash
python tools/validate_schema.py manifest.yaml -s schema/manifest.schema.json
```

### Schema URI Check

Ensures manifest references correct schema:

```bash
python tools/check_schema_uri.py manifest.yaml
```

### Tag Protection

Blocks tags/releases with unsigned manifests:

```bash
python tools/tag_protect_unsigned.py -d . -p keys/minisign.pub
```

## Best Practices

### 1. Always Sign Before Committing
Manifests should be signed before being committed to the repository.

### 2. Use Pre-commit Hooks
Install the pre-commit hook to automatically validate manifests:
```bash
ln -s ../../tools/hooks/ddc-verify.sh .git/hooks/pre-commit
```

### 3. Protect Keys
- Never commit private keys to the repository
- Store keys securely (e.g., GitHub Secrets, vault)
- Rotate keys periodically

### 4. Verify on CI/CD
Always verify signatures in CI/CD pipelines before deployment.

### 5. Include Comprehensive Provenance
Populate all relevant provenance fields for maximum traceability.

### 6. Version Control
- Use semantic versioning for manifest format (`version` field)
- Track artifact versions in `metadata.version`

## Example Manifest

```yaml
schema_uri: schema/manifest.schema.json
version: 1.0.0
metadata:
  name: my-application
  type: application
  version: 2.1.0
  description: Example application manifest
  authors:
    - "Jane Developer"
  license: MIT
  repository: https://github.com/org/repo
  created: "2024-01-15T10:00:00Z"
  tags:
    - production
    - verified

provenance:
  build:
    builder: GitHub Actions
    timestamp: "2024-01-15T10:30:00Z"
    environment:
      os: ubuntu-22.04
      arch: x86_64
  source:
    repository: https://github.com/org/repo
    commit: a1b2c3d4e5f6
    ref: refs/tags/v2.1.0
  dependencies:
    - name: express
      version: 4.18.2
      type: runtime

artifacts:
  - path: dist/app.js
    hash: "sha256:abc123def456..."
    size: 102400
    type: application/javascript

signing:
  algorithm: minisign
  signer:
    name: CI/CD Pipeline
    key_id: RWS1234ABCD
  signature:
    value: |
      untrusted comment: signature from minisign secret key
      RWT...base64signature...
    timestamp: "2024-01-15T10:35:00Z"
```

## Troubleshooting

### Signature Verification Fails
- Ensure the manifest hasn't been modified after signing
- Check that you're using the correct public key
- Verify minisign is properly installed

### Schema Validation Fails
- Check that all required fields are present
- Verify field types match the schema
- Ensure enums use valid values

### Schema URI Mismatch
- Update `schema_uri` to match expected value: `schema/manifest.schema.json`
- Don't use absolute paths or URLs

## Security Considerations

1. **Key Management**: Private keys must be protected and never committed to version control
2. **Signature Verification**: Always verify signatures before trusting manifest data
3. **Hash Validation**: Verify artifact hashes match manifest values
4. **Schema Compliance**: Reject manifests that don't validate against schema
5. **Timestamp Verification**: Check signing timestamps for suspicious activity

## Related Tools

- `sign_manifest.py` - Sign manifests with minisign
- `verify_manifest.py` - Verify manifest signatures
- `validate_schema.py` - Validate against JSON schema
- `check_schema_uri.py` - Check schema URI field
- `tag_protect_unsigned.py` - Block unsigned manifests on tags
- `hooks/ddc-verify.sh` - Pre-commit verification hook

## References

- [Minisign](https://jedisct1.github.io/minisign/)
- [JSON Schema](https://json-schema.org/)
- [YAML Specification](https://yaml.org/spec/)
- [Semantic Versioning](https://semver.org/)
- [SPDX License List](https://spdx.org/licenses/)
