# Security Policy

## Supported Versions

This section describes which versions of the ZQ DDC Core V1 provenance system are currently supported with security updates.

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of the ZQ DDC Core V1 provenance system seriously. If you discover a security vulnerability, please follow these guidelines:

### Where to Report

**DO NOT** open a public GitHub issue for security vulnerabilities.

Instead, please report security vulnerabilities by emailing:
- **security@example.com** (replace with actual security contact)

### What to Include

Please include the following information in your report:

1. **Type of vulnerability** - What type of security issue is it?
2. **Affected component** - Which tool, workflow, or component is affected?
3. **Impact** - What is the potential impact of the vulnerability?
4. **Reproduction steps** - Detailed steps to reproduce the vulnerability
5. **Proof of concept** - If possible, provide a minimal proof of concept
6. **Suggested fix** - If you have ideas on how to fix it, please share

### Response Timeline

We aim to respond to security reports according to the following timeline:

- **Initial Response**: Within 48 hours
- **Triage**: Within 5 business days
- **Fix Development**: Based on severity
  - Critical: Within 7 days
  - High: Within 14 days
  - Medium: Within 30 days
  - Low: Within 90 days
- **Public Disclosure**: Coordinated with reporter

## Security Best Practices

### Key Management

1. **Never commit private keys** to version control
   - Private keys should be stored in secure key management systems
   - Use GitHub Secrets for CI/CD workflows
   - Rotate keys regularly (at least annually)

2. **Protect public keys**
   - Commit public keys to the repository (in `keys/` directory)
   - Document key ownership and expiration
   - Maintain a backup of public keys

3. **Use strong passwords**
   - Secret keys should be protected with strong passwords
   - Use password managers to generate and store passwords
   - Never hardcode passwords in scripts

### Manifest Signing

1. **Sign before committing**
   - All manifests should be signed before being committed
   - Use pre-commit hooks to enforce signing
   - Verify signatures in CI/CD pipelines

2. **Verify on every pull**
   - Always verify manifest signatures when pulling code
   - Use `make manifest:verify` or `tools/verify_manifest.py`
   - Reject unsigned or invalidly signed manifests

3. **Tag protection**
   - Enable tag protection workflows
   - Block releases with unsigned manifests
   - Require signature verification before deployment

### CI/CD Security

1. **Secure secrets**
   - Store signing keys as GitHub Secrets (base64 encoded)
   - Limit secret access to necessary workflows only
   - Rotate secrets when team members change

2. **Workflow permissions**
   - Use minimal required permissions for workflows
   - Avoid `contents: write` unless necessary
   - Review workflow permissions regularly

3. **Dependency security**
   - Pin workflow action versions (no `@main` or `@master`)
   - Review dependency updates for security issues
   - Use Dependabot for automated security updates

### Code Review

1. **Security-critical changes**
   - All changes to signing/verification code require security team review
   - Changes to workflows require devops team review
   - See CODEOWNERS for specific requirements

2. **Provenance verification**
   - Review manifest changes carefully
   - Verify that signatures are updated when manifests change
   - Check for suspicious provenance data

## Vulnerability Disclosure

### Coordinated Disclosure

We follow coordinated vulnerability disclosure practices:

1. Reporter submits vulnerability privately
2. We acknowledge receipt within 48 hours
3. We work with reporter to understand and verify the issue
4. We develop and test a fix
5. We coordinate disclosure timing with reporter
6. We release fix and publish security advisory
7. Reporter receives credit in security advisory (if desired)

### Public Disclosure

After a fix is released, we will:

1. Publish a GitHub Security Advisory
2. Update this SECURITY.md file
3. Notify users through release notes
4. Credit the reporter (with permission)

## Security Features

The ZQ DDC Core V1 provenance system includes the following security features:

### Cryptographic Signing

- **Algorithm**: Ed25519 (via minisign)
- **Key Size**: 256 bits
- **Signature Format**: Minisign format with base64 encoding

### Deterministic Signing

- Signatures are reproducible with same key and payload
- Canonical YAML serialization ensures consistency
- Signature verification is independent of key order

### Schema Validation

- JSON Schema validation prevents malformed manifests
- Required fields are enforced
- Type checking prevents injection attacks

### Tag Protection

- Automated blocking of unsigned manifests on tags
- Signature verification required for releases
- Prevents deployment of unverified code

## Threat Model

### In Scope

The following are within the scope of our security model:

1. **Manifest tampering** - Modifying signed manifests without detection
2. **Signature forgery** - Creating valid signatures without the private key
3. **Key compromise** - Unauthorized access to signing keys
4. **Schema bypass** - Circumventing schema validation
5. **Replay attacks** - Reusing old signatures on new manifests
6. **Supply chain attacks** - Compromising build/signing pipeline

### Out of Scope

The following are generally out of scope:

1. **Social engineering** - Tricking authorized signers
2. **Physical access** - Physical access to signing machines
3. **GitHub platform vulnerabilities** - Issues with GitHub itself
4. **Denial of service** - Making the system unavailable

## Security Updates

Security updates will be released as soon as possible after verification. We use the following severity levels:

- **Critical** - Remote code execution, key compromise
- **High** - Signature bypass, authentication bypass
- **Medium** - Information disclosure, limited tampering
- **Low** - Minor issues with limited impact

## Contact

For security concerns, please contact:
- **Email**: security@example.com (replace with actual contact)
- **GPG Key**: [Link to GPG key] (if available)

For general questions about the provenance system:
- Open a GitHub issue (for non-security topics)
- See documentation in `docs/core/manifest.md`

## Acknowledgments

We thank the security research community for helping keep ZQ DDC Core V1 secure. Contributors who report valid security issues will be acknowledged in our security advisories (with permission).

---

*Last updated: 2024-01-15*
