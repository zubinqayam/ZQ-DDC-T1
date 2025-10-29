# VS Code Integration for ZQ DDC Core V1

This directory contains VS Code tasks for working with the provenance system.

## Available Tasks

Access tasks via `Terminal > Run Task...` or `Ctrl+Shift+P` > "Tasks: Run Task"

### Manifest Operations (Current File)

- **Manifest: Sign Current File** - Sign the currently open manifest file
- **Manifest: Verify Current File** - Verify the currently open manifest
- **Manifest: Validate Schema** - Validate current file against JSON schema
- **Manifest: Check Schema URI** - Verify schema URI in current file

### Manifest Operations (Batch)

- **Manifest: All Checks** - Run all validation checks on all manifests
- **Manifest: Batch Sign All** - Sign all unsigned manifests in the repository
- **Manifest: Batch Verify All** - Verify all signed manifests
- **Manifest: Tag Protection Check** - Verify all manifests are signed for tag

### Testing

- **Test: Run All Tests** (Default test task - `Ctrl+Shift+T`)
- **Test: Run Provenance Tests** - Run only provenance-related tests

### Utilities

- **Keys: Generate Test Keys** - Generate test key pair for development
- **Clean: Remove Generated Files** - Clean up temporary files

## Usage

### Signing a Manifest

1. Open a manifest YAML file
2. Run task: `Manifest: Sign Current File`
3. Enter your key password when prompted
4. The file will be updated with the signature

### Verifying a Manifest

1. Open a manifest YAML file
2. Run task: `Manifest: Verify Current File`
3. Check the output for verification status

### Running All Checks

1. Run task: `Manifest: All Checks`
2. This will:
   - Validate all manifests against schema
   - Check all schema URIs
   - Report any issues

### Development Workflow

For development and testing:

1. Generate test keys once:
   ```
   Run task: Keys: Generate Test Keys
   ```

2. Create/edit a manifest file

3. Validate the schema:
   ```
   Run task: Manifest: Validate Schema
   ```

4. Sign the manifest:
   ```
   Run task: Manifest: Sign Current File
   ```

5. Verify it works:
   ```
   Run task: Manifest: Verify Current File
   ```

6. Run tests:
   ```
   Run task: Test: Run All Tests
   ```

## Keyboard Shortcuts

You can add keyboard shortcuts to `.vscode/keybindings.json`:

```json
[
  {
    "key": "ctrl+alt+s",
    "command": "workbench.action.tasks.runTask",
    "args": "Manifest: Sign Current File"
  },
  {
    "key": "ctrl+alt+v",
    "command": "workbench.action.tasks.runTask",
    "args": "Manifest: Verify Current File"
  },
  {
    "key": "ctrl+alt+a",
    "command": "workbench.action.tasks.runTask",
    "args": "Manifest: All Checks"
  }
]
```

## Requirements

Ensure you have the following installed:

- Python 3.11+
- PyYAML: `pip install pyyaml`
- jsonschema: `pip install jsonschema`
- pytest: `pip install pytest`
- minisign: Platform-specific installation
  - Ubuntu/Debian: `sudo apt-get install minisign`
  - macOS: `brew install minisign`
  - Windows: Download from https://jedisct1.github.io/minisign/

## Configuration

### Custom Key Paths

Tasks use default key paths:
- Secret key: `${workspaceFolder}/keys/minisign.key`
- Public key: `${workspaceFolder}/keys/minisign.pub`

To use custom paths, edit `tasks.json` and update the paths in the task definitions.

### Environment Variables

You can set environment variables in your VS Code settings:

```json
{
  "terminal.integrated.env.linux": {
    "MINISIGN_PASSWORD": "your-password-here"
  }
}
```

**Note**: Storing passwords in settings is not recommended for production. Use this only for development with test keys.

## Troubleshooting

### "minisign: command not found"

Install minisign for your platform (see Requirements above).

### "keys/minisign.key: No such file or directory"

Generate keys first:
```
Run task: Keys: Generate Test Keys
```

Or generate production keys:
```bash
mkdir -p keys
minisign -G -p keys/minisign.pub -s keys/minisign.key
```

### "Permission denied" when running tasks

Ensure scripts are executable:
```bash
chmod +x tools/hooks/ddc-verify.sh
chmod +x .github/scripts/gh_release_create.sh
```

### Python module not found

Install required dependencies:
```bash
pip install pyyaml jsonschema pytest
```

## Tips

1. **Auto-save**: Enable auto-save in VS Code to avoid forgetting to save before running tasks

2. **Task Output**: Keep the task output panel open to see results immediately

3. **Batch Operations**: Use batch tasks when working with multiple manifests

4. **Pre-commit**: Install pre-commit hooks for automatic validation:
   ```bash
   pip install pre-commit
   pre-commit install
   ```

5. **Test Keys**: Always use test keys for development, never commit production keys

## Related Documentation

- [Manifest Documentation](../docs/core/manifest.md)
- [Security Policy](../SECURITY.md)
- [Main README](../README.md)

## Support

For issues with VS Code integration:
- Check task definitions in `tasks.json`
- Verify tool installations
- See main documentation in `README.md`
