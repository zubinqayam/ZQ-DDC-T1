#!/bin/bash

###############################################################################
# ZQTaskmaster CI Governance Bootstrap Script
#
# This script automates the bootstrap process for CI governance using 
# ZQTaskmaster. It performs the following operations:
# 1. Clones the repository (if needed)
# 2. Creates a new branch named 'zqtaskmaster/bootstrap-<timestamp>'
# 3. Sets up CI governance configuration
# 4. Commits and pushes changes
#
# Usage:
#   ./bootstrap-zqtaskmaster.sh [REPO_URL] [TARGET_DIR]
#
# Arguments:
#   REPO_URL    - Git repository URL (optional, defaults to current repo)
#   TARGET_DIR  - Target directory for clone (optional, defaults to current dir)
#
###############################################################################

set -e  # Exit on error
set -u  # Exit on undefined variable

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Function to check if git is installed
check_git() {
    if ! command -v git &> /dev/null; then
        log_error "Git is not installed. Please install git and try again."
        exit 1
    fi
    log_info "Git is installed: $(git --version)"
}

# Function to clone repository
clone_repository() {
    local repo_url="$1"
    local target_dir="$2"
    
    log_info "Cloning repository: $repo_url"
    
    if [ -d "$target_dir/.git" ]; then
        log_warning "Repository already exists at $target_dir. Skipping clone."
        cd "$target_dir"
        git fetch origin
    else
        git clone "$repo_url" "$target_dir"
        cd "$target_dir"
    fi
    
    log_info "Repository ready at: $(pwd)"
}

# Function to create bootstrap branch
create_bootstrap_branch() {
    local timestamp=$(date +"%Y%m%d-%H%M%S")
    local branch_name="zqtaskmaster/bootstrap-${timestamp}"
    
    log_info "Creating new branch: $branch_name"
    
    # Ensure we're on the default branch
    default_branch=$(git symbolic-ref refs/remotes/origin/HEAD | sed 's@^refs/remotes/origin/@@')
    log_info "Default branch is: $default_branch"
    
    # Check out default branch
    git checkout "$default_branch" 2>/dev/null || git checkout -b "$default_branch"
    
    # Pull latest changes
    git pull origin "$default_branch" 2>/dev/null || log_warning "Could not pull latest changes"
    
    # Create and checkout new branch
    git checkout -b "$branch_name"
    
    log_info "Successfully created and checked out branch: $branch_name"
    echo "$branch_name"
}

# Function to setup CI governance configuration
setup_ci_governance() {
    log_info "Setting up CI governance configuration..."
    
    # Create .github directory if it doesn't exist
    mkdir -p .github/workflows
    
    # Create ZQTaskmaster CI configuration
    cat > .github/workflows/zqtaskmaster-ci.yml <<'EOF'
name: ZQTaskmaster CI Governance

on:
  push:
    branches: [ main, master, develop ]
  pull_request:
    branches: [ main, master, develop ]
  workflow_dispatch:

jobs:
  governance-check:
    name: CI Governance Check
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: ZQTaskmaster Governance Validation
        run: |
          echo "Running ZQTaskmaster CI governance checks..."
          echo "Repository: ${{ github.repository }}"
          echo "Branch: ${{ github.ref_name }}"
          echo "Commit: ${{ github.sha }}"
          
          # Add your governance checks here
          # Examples:
          # - Code quality checks
          # - Security scans
          # - Compliance validations
          # - Policy enforcement
          
          echo "Governance checks completed successfully!"
      
      - name: Report Status
        if: always()
        run: |
          echo "ZQTaskmaster CI Governance Report"
          echo "=================================="
          echo "Status: ${{ job.status }}"
          echo "Timestamp: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
EOF
    
    log_info "Created GitHub Actions workflow: .github/workflows/zqtaskmaster-ci.yml"
    
    # Create ZQTaskmaster configuration file
    cat > .zqtaskmaster.yml <<'EOF'
# ZQTaskmaster CI Governance Configuration
version: 1.0

# Governance settings
governance:
  enabled: true
  strict_mode: false
  
  # Branch protection rules
  branch_protection:
    - branch: main
      required_reviews: 1
      require_ci_pass: true
    - branch: master
      required_reviews: 1
      require_ci_pass: true
  
  # CI/CD policies
  ci_policies:
    - name: code_quality
      enabled: true
      fail_on_warning: false
    
    - name: security_scan
      enabled: true
      fail_on_warning: true
    
    - name: compliance_check
      enabled: true
      fail_on_warning: false

# Notification settings
notifications:
  enabled: true
  channels:
    - type: github
      on_failure: true
      on_success: false

# Reporting
reporting:
  enabled: true
  format: json
  output_path: .zqtaskmaster-reports/
EOF
    
    log_info "Created ZQTaskmaster configuration: .zqtaskmaster.yml"
    
    # Create reports directory
    mkdir -p .zqtaskmaster-reports
    
    # Create .gitignore for reports if not exists
    if [ ! -f .gitignore ]; then
        echo ".zqtaskmaster-reports/" > .gitignore
    elif ! grep -q ".zqtaskmaster-reports/" .gitignore; then
        echo ".zqtaskmaster-reports/" >> .gitignore
    fi
    
    log_info "CI governance configuration setup completed"
}

# Function to commit and push changes
commit_and_push() {
    local branch_name="$1"
    
    log_info "Committing changes..."
    
    # Add all changes
    git add .github/workflows/zqtaskmaster-ci.yml
    git add .zqtaskmaster.yml
    git add .gitignore
    
    # Commit changes
    git commit -m "feat: Bootstrap ZQTaskmaster CI governance

- Add GitHub Actions workflow for CI governance
- Add ZQTaskmaster configuration file
- Configure branch protection and CI policies
- Set up reporting infrastructure

Automated by: bootstrap-zqtaskmaster.sh"
    
    log_info "Changes committed successfully"
    
    # Push to remote
    log_info "Pushing branch to remote: $branch_name"
    git push -u origin "$branch_name"
    
    log_info "Branch pushed successfully"
}

# Function to display summary
display_summary() {
    local branch_name="$1"
    
    echo ""
    echo "========================================"
    log_info "ZQTaskmaster Bootstrap Completed!"
    echo "========================================"
    echo ""
    echo "Branch created: $branch_name"
    echo "Files created:"
    echo "  - .github/workflows/zqtaskmaster-ci.yml"
    echo "  - .zqtaskmaster.yml"
    echo ""
    echo "Next steps:"
    echo "  1. Review the created files"
    echo "  2. Create a Pull Request for the branch"
    echo "  3. Merge to enable CI governance"
    echo ""
    log_info "Repository is now ready for ZQTaskmaster CI governance!"
}

# Main execution
main() {
    log_info "Starting ZQTaskmaster CI Governance Bootstrap..."
    
    # Check prerequisites
    check_git
    
    # Parse arguments
    local repo_url="${1:-}"
    local target_dir="${2:-$(pwd)}"
    
    # If repo_url is provided, clone the repository
    if [ -n "$repo_url" ]; then
        clone_repository "$repo_url" "$target_dir"
    else
        log_info "No repository URL provided, working in current directory: $(pwd)"
        
        # Check if we're in a git repository
        if [ ! -d .git ]; then
            log_error "Not in a git repository. Please provide a repository URL or run from within a git repository."
            exit 1
        fi
    fi
    
    # Create bootstrap branch
    branch_name=$(create_bootstrap_branch)
    
    # Setup CI governance
    setup_ci_governance
    
    # Commit and push changes
    commit_and_push "$branch_name"
    
    # Display summary
    display_summary "$branch_name"
    
    log_info "Bootstrap process completed successfully!"
}

# Run main function
main "$@"
