# ZQTaskmaster Bootstrap Script

## Overview

The `bootstrap-zqtaskmaster.sh` script automates the bootstrap process for CI governance using ZQTaskmaster. It streamlines the setup of continuous integration governance for your repository.

## Features

- **Automated Repository Setup**: Clones repository or works with existing one
- **Branch Management**: Creates timestamped branches with the pattern `zqtaskmaster/bootstrap-YYYYMMDD-HHMMSS`
- **CI/CD Configuration**: Sets up GitHub Actions workflow for CI governance
- **Governance Configuration**: Creates ZQTaskmaster configuration files
- **Error Handling**: Robust error handling and informative logging

## Prerequisites

- Git installed and configured
- Access to the repository (read/write permissions)
- Bash shell environment

## Usage

### Basic Usage (Current Directory)

Run the script from within an existing git repository:

```bash
./bootstrap-zqtaskmaster.sh
```

### Clone and Bootstrap

Provide a repository URL and target directory:

```bash
./bootstrap-zqtaskmaster.sh <REPO_URL> <TARGET_DIR>
```

**Examples:**

```bash
# Clone and bootstrap
./bootstrap-zqtaskmaster.sh https://github.com/user/repo.git ./my-repo

# Bootstrap current directory
cd /path/to/repo
./bootstrap-zqtaskmaster.sh
```

## What It Does

1. **Checks Prerequisites**: Verifies Git is installed
2. **Prepares Repository**: Clones or updates the repository
3. **Creates Branch**: Creates a new branch named `zqtaskmaster/bootstrap-<timestamp>`
4. **Sets Up CI Governance**:
   - Creates `.github/workflows/zqtaskmaster-ci.yml` - GitHub Actions workflow
   - Creates `.zqtaskmaster.yml` - ZQTaskmaster configuration
   - Updates `.gitignore` to exclude report directories
5. **Commits Changes**: Commits all configuration files
6. **Pushes Branch**: Pushes the new branch to remote origin
7. **Displays Summary**: Shows what was done and next steps

## Created Files

### `.github/workflows/zqtaskmaster-ci.yml`

GitHub Actions workflow that runs CI governance checks on:
- Push to main/master/develop branches
- Pull requests to main/master/develop branches
- Manual workflow dispatch

### `.zqtaskmaster.yml`

Configuration file containing:
- Governance settings (enabled/strict mode)
- Branch protection rules
- CI/CD policies (code quality, security scan, compliance check)
- Notification settings
- Reporting configuration

### `.zqtaskmaster-reports/`

Directory for storing governance reports (added to .gitignore)

## Configuration

The script creates a default configuration in `.zqtaskmaster.yml` that includes:

- **Branch Protection**: Rules for main/master branches
- **CI Policies**: Code quality, security scanning, compliance checks
- **Notifications**: GitHub-based notifications
- **Reporting**: JSON format reports

You can customize these settings after the bootstrap process completes.

## Output

The script provides colored, informative output:
- **Green [INFO]**: Informational messages
- **Yellow [WARNING]**: Warning messages
- **Red [ERROR]**: Error messages

## Exit Codes

- `0`: Success
- `1`: Error (Git not installed, not in git repository, etc.)

## Next Steps After Bootstrap

1. **Review Created Files**: Check the generated configuration files
2. **Customize Configuration**: Modify `.zqtaskmaster.yml` as needed
3. **Create Pull Request**: Open a PR for the bootstrap branch
4. **Merge**: Merge the PR to enable CI governance
5. **Monitor**: Use GitHub Actions to monitor CI governance

## Troubleshooting

### "Git is not installed"
Install Git on your system before running the script.

### "Not in a git repository"
Either run the script from within a git repository or provide a repository URL as an argument.

### "Could not pull latest changes"
This warning can appear if the branch doesn't exist remotely yet. It's safe to ignore during initial setup.

## Security Considerations

- The script requires write access to the repository
- Credentials are managed through Git's credential system
- No sensitive data is stored in the configuration files
- The `.zqtaskmaster-reports/` directory is automatically ignored by Git

## Contributing

To improve the bootstrap script:
1. Create a new branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## License

This script is part of the ZQ-DDC-T1 project and follows the same license terms.

## Support

For issues or questions:
- Open an issue in the repository
- Check existing documentation
- Review GitHub Actions logs for CI governance runs
