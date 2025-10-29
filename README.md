# ZQ-DDC-T1: Deep Data Construction with Provenance

[![Manifest Provenance](https://github.com/ZQ-DDC-T1/ZQ-DDC-T1/actions/workflows/manifest-provenance.yml/badge.svg)](https://github.com/ZQ-DDC-T1/ZQ-DDC-T1/actions/workflows/manifest-provenance.yml)
[![Test Provenance](https://github.com/ZQ-DDC-T1/ZQ-DDC-T1/actions/workflows/test-provenance.yml/badge.svg)](https://github.com/ZQ-DDC-T1/ZQ-DDC-T1/actions/workflows/test-provenance.yml)
[![Schema Validation](https://github.com/ZQ-DDC-T1/ZQ-DDC-T1/actions/workflows/schema-validate.yml/badge.svg)](https://github.com/ZQ-DDC-T1/ZQ-DDC-T1/actions/workflows/schema-validate.yml)

**ZQ DDC Core V1** - A comprehensive cryptographic provenance system for software artifacts with deterministic signing, schema validation, and automated verification.

## Overview

ZQ-DDC-T1 implements a complete provenance system that ensures:

- ✅ **Integrity** - Cryptographic verification that manifests haven't been tampered with
- ✅ **Authenticity** - Proof of who created and signed the manifest  
- ✅ **Provenance** - Complete build and source information
- ✅ **Traceability** - Dependency tracking and artifact checksums
- ✅ **Compliance** - Schema-validated structure for consistency

## Features

### 🔐 Cryptographic Signing
- **Deterministic signing** using minisign (Ed25519)
- Reproducible signatures for the same payload
- Support for batch signing and verification

### 📋 Schema Validation
- JSON Schema-based manifest validation
- Enforced required fields and type checking
- Comprehensive provenance metadata

### 🛡️ Tag Protection
- Automated blocking of unsigned manifests on tags
- Pre-release signature verification
- Prevents deployment of unverified artifacts

### 🔄 CI/CD Integration
- Automated manifest verification on PRs
- Automatic signing on tag creation
- Release automation with signed artifacts

### 🧪 Testing
- Comprehensive test suite with pytest
- Round-trip signing and verification tests
- Tamper detection validation

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/ZQ-DDC-T1/ZQ-DDC-T1.git
cd ZQ-DDC-T1

# Install Python dependencies
pip install pyyaml jsonschema pytest

# Install minisign (for signing/verification)
# Ubuntu/Debian:
sudo apt-get install minisign

# macOS:
brew install minisign

# Windows:
# Download from https://jedisct1.github.io/minisign/
```

### Generate Keys

```bash
# Generate a key pair
mkdir -p keys
minisign -G -p keys/minisign.pub -s keys/minisign.key

# IMPORTANT: Never commit keys/minisign.key to version control!
```

### Sign a Manifest

```bash
# Sign a single manifest
python tools/sign_manifest.py tests/provenance/sample-manifest.yaml \
  -s keys/minisign.key

# Or use make
make manifest:sign MANIFEST=tests/provenance/sample-manifest.yaml
```

### Verify a Manifest

```bash
# Verify a single manifest
python tools/verify_manifest.py tests/provenance/sample-manifest.yaml \
  -p keys/minisign.pub

# Or use make
make manifest:verify MANIFEST=tests/provenance/sample-manifest.yaml
```

### Validate Schema

```bash
# Validate manifest against schema
python tools/validate_schema.py tests/provenance/sample-manifest.yaml \
  -s schema/manifest.schema.json

# Or use make
make manifest:validate
```

## Project Structure

```
ZQ-DDC-T1/
├── .github/
│   ├── workflows/          # CI/CD workflows
│   │   ├── manifest-provenance.yml
│   │   ├── sign-manifest.yml
│   │   ├── release.yml
│   │   ├── test-provenance.yml
│   │   ├── schema-validate.yml
│   │   ├── docs-check.yml
│   │   └── tag-protect.yml
│   └── scripts/
│       └── gh_release_create.sh
├── tools/                  # Provenance tools
│   ├── sign_manifest.py
│   ├── verify_manifest.py
│   ├── validate_schema.py
│   ├── check_schema_uri.py
│   ├── tag_protect_unsigned.py
│   └── hooks/
│       └── ddc-verify.sh
├── schema/                 # JSON schemas
│   └── manifest.schema.json
├── docs/                   # Documentation
│   └── core/
│       └── manifest.md
├── tests/                  # Test suite
│   └── provenance/
│       ├── sample-manifest.yaml
│       └── test_roundtrip.py
├── keys/                   # Key storage (gitignored)
│   └── README.md
├── .vscode/               # VS Code integration
│   ├── tasks.json
│   └── README.md
├── Makefile               # Build automation
├── .pre-commit-config.yaml
├── CODEOWNERS
├── SECURITY.md
└── README.md
```

## Makefile Targets

```bash
make help                    # Show all available targets

# Manifest operations
make manifest:all            # Run all manifest checks
make manifest:validate       # Validate all manifests
make manifest:docs-check     # Check schema URIs
make manifest:tag-protect    # Verify all are signed
make manifest:sign          # Sign specific manifest
make manifest:verify        # Verify specific manifest
make manifest:batch-sign    # Sign all manifests
make manifest:batch-verify  # Verify all manifests

# Testing
make test                   # Run all tests
make clean                  # Clean up generated files
```

## CI/CD Workflows

### Manifest Provenance
Runs on every PR and push to main:
- Finds all manifest files
- Validates schema compliance
- Checks schema URI references

### Schema Validation
Validates manifests against JSON schema on changes.

### Documentation Check
Ensures documentation references match schema URIs.

### Test Provenance
Runs comprehensive test suite including:
- Round-trip signing tests
- Verification tests
- Tamper detection tests

### Sign Manifest
Automatically signs manifests when tags are created (requires secrets).

### Tag Protection
Blocks tags/releases with unsigned or invalid manifests.

### Release
Creates GitHub releases with:
- Signed manifests
- Release notes
- Verification instructions

## Manifest Format

Example manifest:

```yaml
schema_uri: schema/manifest.schema.json
version: 1.0.0
metadata:
  name: my-application
  type: application
  version: 2.1.0
  description: Example application
  license: MIT

provenance:
  build:
    builder: GitHub Actions
    timestamp: "2024-01-15T10:30:00Z"
  source:
    repository: https://github.com/org/repo
    commit: abc123
    ref: refs/tags/v2.1.0

artifacts:
  - path: dist/app.tar.gz
    hash: sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
    size: 1024000

signing:
  algorithm: minisign
  signature:
    value: |
      untrusted comment: signature from minisign
      RWT...base64...
```

See [docs/core/manifest.md](docs/core/manifest.md) for complete documentation.

## Security

### Key Management

**CRITICAL**: Private keys must NEVER be committed to version control!

- Store private keys securely (vault, secrets manager)
- Use GitHub Secrets for CI/CD workflows
- Rotate keys regularly (at least annually)
- See [SECURITY.md](SECURITY.md) for details

### Pre-commit Hooks

Install pre-commit hooks to automatically verify manifests:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

### Reporting Vulnerabilities

See [SECURITY.md](SECURITY.md) for vulnerability reporting procedures.

## Development

### Running Tests

```bash
# Run all tests
make test

# Or use pytest directly
pytest tests/ -v
```

### Adding a New Manifest

1. Create YAML file with required fields
2. Validate schema: `make manifest:validate`
3. Sign manifest: `make manifest:sign MANIFEST=path/to/manifest.yaml`
4. Verify: `make manifest:verify MANIFEST=path/to/manifest.yaml`
5. Commit the signed manifest

### Batch Operations

```bash
# Sign all unsigned manifests
make manifest:batch-sign SECRET_KEY=keys/minisign.key

# Verify all manifests
make manifest:batch-verify PUBLIC_KEY=keys/minisign.pub

# Run all checks
make manifest:all
```

## VS Code Integration

Tasks are provided for common operations:

- **Sign Manifest** - Sign the current manifest file
- **Verify Manifest** - Verify the current manifest
- **Validate Schema** - Validate against JSON schema
- **Check Schema URI** - Verify schema URI reference

See [.vscode/README.md](.vscode/README.md) for details.

## Documentation

- [Manifest Documentation](docs/core/manifest.md) - Complete manifest format guide
- [Schema Definition](schema/manifest.schema.json) - JSON Schema specification
- [Security Policy](SECURITY.md) - Security practices and reporting
- [Code Owners](CODEOWNERS) - Review requirements

## Tools

### Core Tools

- **sign_manifest.py** - Deterministic manifest signer
- **verify_manifest.py** - Signature verifier
- **validate_schema.py** - Schema validator
- **check_schema_uri.py** - Schema URI checker
- **tag_protect_unsigned.py** - Tag protection enforcement

### Hooks

- **ddc-verify.sh** - Pre-commit verification hook

### Scripts

- **gh_release_create.sh** - GitHub release automation

## Requirements

- Python 3.11+
- PyYAML 6.0+
- jsonschema 4.20+
- minisign (latest)
- pytest 7.0+ (for testing)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add/update tests
5. Run `make test` and `make manifest:all`
6. Submit a pull request

All contributions must:
- Pass all CI checks
- Include tests for new features
- Follow code ownership rules (see CODEOWNERS)
- Sign manifests if adding/modifying them

## License

See [LICENSE](LICENSE) file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/ZQ-DDC-T1/ZQ-DDC-T1/issues)
- **Security**: See [SECURITY.md](SECURITY.md)
- **Documentation**: [docs/core/manifest.md](docs/core/manifest.md)

## Acknowledgments

Built with:
- [minisign](https://jedisct1.github.io/minisign/) - Cryptographic signing
- [JSON Schema](https://json-schema.org/) - Schema validation
- [PyYAML](https://pyyaml.org/) - YAML processing

---

**ZQ DDC Core V1** - Ensuring integrity, authenticity, and provenance for software artifacts.
