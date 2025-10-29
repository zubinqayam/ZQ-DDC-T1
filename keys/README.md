# Key Management for ZQ DDC Core V1

This directory is designated for storing cryptographic keys used in the provenance system.

## ⚠️ CRITICAL SECURITY NOTICE

**NEVER commit private keys to version control!**

The `.gitignore` file is configured to exclude private keys, but you must ensure:
- Private keys (`.key` files) are never added to git
- Secret keys are stored securely (vault, secrets manager)
- Keys are protected with strong passwords
- Keys are rotated regularly (at least annually)

## Key Files

### Private Key (Secret Key)
- **Filename**: `minisign.key` (or custom name)
- **Description**: Used for signing manifests
- **Storage**: 
  - Development: Local machine, encrypted
  - Production: Secure vault, GitHub Secrets
- **Permissions**: Should be readable only by owner (chmod 600)
- **⚠️ NEVER COMMIT TO GIT**

### Public Key
- **Filename**: `minisign.pub` (or custom name)
- **Description**: Used for verifying signatures
- **Storage**: Can be committed to repository
- **Permissions**: World-readable (chmod 644)
- **✅ SAFE TO COMMIT**

## Generating Keys

### Using minisign CLI

```bash
# Interactive generation (recommended for production)
minisign -G -p keys/minisign.pub -s keys/minisign.key

# Non-interactive (for CI/CD or automated setups)
echo -e "your-password\nyour-password" | minisign -G -p keys/minisign.pub -s keys/minisign.key -W
```

### Key Format

Minisign keys are Ed25519 key pairs:
- **Algorithm**: Ed25519
- **Key Size**: 256 bits
- **Format**: Base64-encoded with metadata

Example public key format:
```
untrusted comment: minisign public key ABCD1234
RWT...base64encodedkey...
```

Example secret key format (encrypted):
```
untrusted comment: minisign encrypted secret key
RWT...base64encryptedkey...
```

## Key Storage

### Development

For development and testing:

1. Generate test keys locally:
   ```bash
   mkdir -p keys
   minisign -G -p keys/minisign.pub -s keys/minisign.key
   ```

2. Use a simple password (e.g., "test-password")

3. Add to `.gitignore` (already configured):
   ```
   keys/*.key
   keys/minisign.key
   ```

### Production

For production use:

1. Generate keys on a secure machine

2. Store private key in:
   - Hardware Security Module (HSM)
   - Secure key vault (HashiCorp Vault, AWS Secrets Manager, etc.)
   - GitHub Secrets (for CI/CD)

3. Use a strong, randomly generated password

4. Commit only the public key to the repository

## GitHub Secrets Configuration

For CI/CD workflows, store keys as GitHub Secrets:

### Setting Up Secrets

1. **Encode keys to base64**:
   ```bash
   # Encode secret key
   cat keys/minisign.key | base64 > minisign.key.b64
   
   # Encode public key
   cat keys/minisign.pub | base64 > minisign.pub.b64
   ```

2. **Add to GitHub Secrets** (Settings > Secrets and variables > Actions):
   - `MINISIGN_SECRET_KEY`: Contents of `minisign.key.b64`
   - `MINISIGN_PUBLIC_KEY`: Contents of `minisign.pub.b64`
   - `MINISIGN_PASSWORD`: Your key password

3. **Use in workflows**:
   ```yaml
   - name: Setup signing key
     run: |
       mkdir -p keys
       echo "${{ secrets.MINISIGN_SECRET_KEY }}" | base64 -d > keys/minisign.key
       echo "${{ secrets.MINISIGN_PUBLIC_KEY }}" | base64 -d > keys/minisign.pub
   ```

### Cleanup

Always clean up keys in CI/CD:
```yaml
- name: Clean up keys
  if: always()
  run: |
    rm -rf keys/minisign.key keys/minisign.pub
```

## Key Rotation

### When to Rotate

Rotate keys in these situations:
- **Regular rotation**: At least annually
- **Suspected compromise**: Immediately
- **Team member departure**: Immediately
- **Compliance requirements**: As required

### Rotation Process

1. **Generate new key pair**:
   ```bash
   minisign -G -p keys/minisign-v2.pub -s keys/minisign-v2.key
   ```

2. **Update GitHub Secrets** with new keys

3. **Re-sign all manifests** with new key:
   ```bash
   make manifest:batch-sign SECRET_KEY=keys/minisign-v2.key
   ```

4. **Update documentation** with new public key

5. **Announce rotation** to users/consumers

6. **Securely destroy old key**:
   ```bash
   shred -u keys/minisign.key  # Linux
   rm -P keys/minisign.key     # macOS
   ```

## Key Distribution

### Public Key Distribution

Distribute the public key through multiple channels:

1. **Repository**: Commit to `keys/minisign.pub`
2. **Documentation**: Include in README.md
3. **Website**: Publish on project website
4. **Keyserver**: Upload to keyserver (if applicable)
5. **Release notes**: Include in every release

### Verifying Public Key

Users should verify the public key through multiple channels:

```bash
# Check key fingerprint
cat keys/minisign.pub

# Compare with documented fingerprint
# Expected: RWT...
```

## Backup and Recovery

### Backup

1. **Encrypt backup**:
   ```bash
   gpg -c keys/minisign.key
   ```

2. **Store in multiple locations**:
   - Encrypted USB drive (offline)
   - Secure cloud storage (encrypted)
   - Hardware security module
   - Paper backup (for recovery codes)

3. **Test recovery** periodically

### Recovery

If private key is lost:
1. Cannot recover - Ed25519 keys cannot be recovered without backup
2. Must generate new key pair
3. Re-sign all manifests
4. Announce key rotation
5. Update all distribution channels

## Security Best Practices

### DO:
- ✅ Use strong passwords (20+ characters, random)
- ✅ Store keys encrypted at rest
- ✅ Limit key access (need-to-know basis)
- ✅ Rotate keys regularly
- ✅ Monitor key usage
- ✅ Use separate keys for dev/staging/prod
- ✅ Back up keys securely
- ✅ Audit key access logs

### DON'T:
- ❌ Commit private keys to version control
- ❌ Share keys via email or chat
- ❌ Use weak passwords
- ❌ Store keys unencrypted
- ❌ Reuse keys across projects
- ❌ Leave keys on shared systems
- ❌ Store passwords in code or configs
- ❌ Skip key rotation

## Troubleshooting

### "Permission denied" when using key

```bash
chmod 600 keys/minisign.key
```

### "Wrong password"

Verify password is correct. If forgotten, generate new keys.

### "Key not found"

Check file path and ensure key file exists:
```bash
ls -la keys/
```

### "Invalid key format"

Key file may be corrupted. Restore from backup or generate new keys.

## File Structure

```
keys/
├── README.md              # This file (safe to commit)
├── minisign.pub          # Public key (safe to commit)
├── minisign.key          # Private key (NEVER commit!)
├── .gitignore            # Protects private keys
└── archive/              # Old keys (if rotating)
    ├── minisign-v1.pub
    └── minisign-v1.key   # Keep secure, never commit
```

## References

- [Minisign Documentation](https://jedisct1.github.io/minisign/)
- [Ed25519 Signature Scheme](https://ed25519.cr.yp.to/)
- [Key Management Best Practices](https://csrc.nist.gov/publications/detail/sp/800-57-part-1/rev-5/final)
- [GitHub Secrets Documentation](https://docs.github.com/en/actions/security-guides/encrypted-secrets)

## Support

For key management questions or issues:
- See [SECURITY.md](../SECURITY.md)
- Contact security team (see CODEOWNERS)
- Report suspected key compromise immediately

---

**Remember**: The security of the entire provenance system depends on proper key management. Always follow best practices and treat private keys as highly sensitive credentials.
