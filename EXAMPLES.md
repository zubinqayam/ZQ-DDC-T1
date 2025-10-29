# ZQTaskmaster Bootstrap - Usage Examples

This document provides practical examples of using the `bootstrap-zqtaskmaster.sh` script.

## Example 1: Bootstrap Current Repository

If you're already in a git repository and want to set up CI governance:

```bash
cd /path/to/your/repo
./bootstrap-zqtaskmaster.sh
```

**Expected Output:**
```
[INFO] Starting ZQTaskmaster CI Governance Bootstrap...
[INFO] Git is installed: git version 2.x.x
[INFO] No repository URL provided, working in current directory: /path/to/your/repo
[INFO] Creating new branch: zqtaskmaster/bootstrap-20251029-123456
[INFO] Default branch is: main
[INFO] Successfully created and checked out branch: zqtaskmaster/bootstrap-20251029-123456
[INFO] Setting up CI governance configuration...
[INFO] Created GitHub Actions workflow: .github/workflows/zqtaskmaster-ci.yml
[INFO] Created ZQTaskmaster configuration: .zqtaskmaster.yml
[INFO] CI governance configuration setup completed
[INFO] Committing changes...
[INFO] Changes committed successfully
[INFO] Pushing branch to remote: zqtaskmaster/bootstrap-20251029-123456
[INFO] Branch pushed successfully

========================================
[INFO] ZQTaskmaster Bootstrap Completed!
========================================

Branch created: zqtaskmaster/bootstrap-20251029-123456
Files created:
  - .github/workflows/zqtaskmaster-ci.yml
  - .zqtaskmaster.yml

Next steps:
  1. Review the created files
  2. Create a Pull Request for the branch
  3. Merge to enable CI governance

[INFO] Repository is now ready for ZQTaskmaster CI governance!
[INFO] Bootstrap process completed successfully!
```

## Example 2: Clone and Bootstrap Remote Repository

To clone a repository and bootstrap it in one command:

```bash
./bootstrap-zqtaskmaster.sh https://github.com/user/repo.git ./target-directory
```

This will:
1. Clone the repository to `./target-directory`
2. Create a bootstrap branch
3. Set up CI governance
4. Commit and push changes

## Example 3: Bootstrap Multiple Repositories

Create a wrapper script to bootstrap multiple repositories:

```bash
#!/bin/bash
# bootstrap-all.sh

REPOS=(
    "https://github.com/org/repo1.git"
    "https://github.com/org/repo2.git"
    "https://github.com/org/repo3.git"
)

for REPO in "${REPOS[@]}"; do
    REPO_NAME=$(basename "$REPO" .git)
    echo "Bootstrapping $REPO_NAME..."
    ./bootstrap-zqtaskmaster.sh "$REPO" "./$REPO_NAME"
    echo "---"
done
```

## Example 4: Verify Bootstrap Success

After running the bootstrap script, verify the setup:

```bash
# Check the created branch
git branch -a | grep zqtaskmaster/bootstrap

# View the workflow file
cat .github/workflows/zqtaskmaster-ci.yml

# View the configuration
cat .zqtaskmaster.yml

# Check git history
git log --oneline -1
```

## Example 5: Create Pull Request After Bootstrap

Using GitHub CLI to create a PR:

```bash
# After bootstrap completes
gh pr create \
  --title "feat: Enable ZQTaskmaster CI governance" \
  --body "This PR enables automated CI governance using ZQTaskmaster.

Created files:
- GitHub Actions workflow for CI checks
- ZQTaskmaster configuration with governance policies
- Reports directory structure

Please review and merge to activate CI governance." \
  --base main
```

## Example 6: Customize Configuration Before Committing

If you want to review/modify configurations before committing:

```bash
# Run bootstrap script (it will create files and commit)
./bootstrap-zqtaskmaster.sh

# If you need to make changes, you can amend the commit:
git checkout zqtaskmaster/bootstrap-YYYYMMDD-HHMMSS
vim .zqtaskmaster.yml  # Make your changes
git add .zqtaskmaster.yml
git commit --amend --no-edit
git push -f origin zqtaskmaster/bootstrap-YYYYMMDD-HHMMSS
```

## Example 7: Troubleshooting - Cleanup Failed Bootstrap

If a bootstrap fails and you need to cleanup:

```bash
# Delete the bootstrap branch
git branch -D zqtaskmaster/bootstrap-YYYYMMDD-HHMMSS

# Remove created files (if any)
rm -rf .github/workflows/zqtaskmaster-ci.yml
rm -rf .zqtaskmaster.yml
rm -rf .zqtaskmaster-reports/

# Return to main branch
git checkout main

# Try bootstrap again
./bootstrap-zqtaskmaster.sh
```

## Example 8: Running Tests

Before using the script, run the test suite:

```bash
# Make test script executable
chmod +x test-bootstrap.sh

# Run tests
./test-bootstrap.sh
```

Expected output will show all tests passing:
```
Testing ZQTaskmaster Bootstrap Script
========================================
Test 1: Check script exists and is executable
✓ Script exists and is executable
...
All tests passed successfully!
```

## Example 9: Integration with CI/CD Pipeline

Add bootstrap automation to your CI/CD pipeline:

```yaml
# .github/workflows/governance-setup.yml
name: Setup Governance

on:
  repository_dispatch:
    types: [setup-governance]

jobs:
  bootstrap:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run ZQTaskmaster Bootstrap
        run: |
          chmod +x bootstrap-zqtaskmaster.sh
          ./bootstrap-zqtaskmaster.sh
          
      - name: Create Pull Request
        uses: peter-evans/create-pull-request@v5
        with:
          title: "chore: Enable ZQTaskmaster CI governance"
          branch: zqtaskmaster/bootstrap-automated
          commit-message: "feat: Bootstrap CI governance"
```

## Notes

- The script automatically generates unique branch names using timestamps
- All operations are logged with color-coded messages
- The script exits on any error (set -e)
- Git credentials are handled by your system's git credential manager
- The script is idempotent for most operations (safe to run multiple times)

## Getting Help

For more information:
- See [BOOTSTRAP.md](BOOTSTRAP.md) for detailed documentation
- Check [README.md](README.md) for quick start guide
- Review the script itself for inline documentation
