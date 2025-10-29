# ZQTaskmaster Configuration Template

This file provides a reference template for `.zqtaskmaster.yml` configuration.
The bootstrap script creates a default configuration, but you can customize it
based on your needs.

## Basic Configuration

```yaml
# ZQTaskmaster CI Governance Configuration
version: 1.0

# Governance settings
governance:
  enabled: true
  strict_mode: false
```

## Branch Protection Rules

```yaml
  # Branch protection rules
  branch_protection:
    - branch: main
      required_reviews: 1
      require_ci_pass: true
      dismiss_stale_reviews: true
      require_code_owner_reviews: false
      
    - branch: master
      required_reviews: 1
      require_ci_pass: true
      dismiss_stale_reviews: true
      require_code_owner_reviews: false
      
    - branch: develop
      required_reviews: 0
      require_ci_pass: true
      dismiss_stale_reviews: false
      require_code_owner_reviews: false
```

## CI/CD Policies

```yaml
  # CI/CD policies
  ci_policies:
    - name: code_quality
      enabled: true
      fail_on_warning: false
      tools:
        - eslint
        - pylint
        - rubocop
      thresholds:
        min_coverage: 80
        max_complexity: 10
    
    - name: security_scan
      enabled: true
      fail_on_warning: true
      tools:
        - snyk
        - dependabot
        - codeql
      severity_levels:
        - critical
        - high
    
    - name: compliance_check
      enabled: true
      fail_on_warning: false
      standards:
        - GDPR
        - SOC2
        - PCI-DSS
    
    - name: license_check
      enabled: true
      fail_on_warning: true
      allowed_licenses:
        - MIT
        - Apache-2.0
        - BSD-3-Clause
      blocked_licenses:
        - GPL-3.0
        - AGPL-3.0
```

## Notification Settings

```yaml
# Notification settings
notifications:
  enabled: true
  channels:
    - type: github
      on_failure: true
      on_success: false
      
    - type: slack
      enabled: false
      webhook_url: "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
      channel: "#ci-alerts"
      on_failure: true
      on_success: false
      
    - type: email
      enabled: false
      recipients:
        - team@example.com
      on_failure: true
      on_success: false
```

## Reporting Configuration

```yaml
# Reporting
reporting:
  enabled: true
  format: json
  output_path: .zqtaskmaster-reports/
  retention_days: 30
  include_details: true
  
  # Report types
  types:
    - governance_summary
    - security_findings
    - compliance_status
    - code_quality_metrics
```

## Advanced Settings

```yaml
# Advanced settings
advanced:
  # Automatic remediation
  auto_fix:
    enabled: false
    types:
      - code_style
      - dependency_updates
    require_approval: true
  
  # Custom checks
  custom_checks:
    - name: "API Documentation"
      command: "npm run check-docs"
      required: true
      
    - name: "Database Migrations"
      command: "bundle exec rake db:migrate:status"
      required: false
  
  # Performance thresholds
  performance:
    max_build_time_minutes: 30
    max_test_time_minutes: 15
    
  # Resource limits
  resources:
    max_parallel_jobs: 5
    timeout_minutes: 60
```

## Environment-Specific Configuration

```yaml
# Environment-specific settings
environments:
  production:
    governance:
      strict_mode: true
    branch_protection:
      - branch: main
        required_reviews: 2
        require_code_owner_reviews: true
        
  staging:
    governance:
      strict_mode: false
    branch_protection:
      - branch: staging
        required_reviews: 1
        require_ci_pass: true
        
  development:
    governance:
      strict_mode: false
    ci_policies:
      - name: code_quality
        fail_on_warning: false
```

## Complete Example Configuration

```yaml
# ZQTaskmaster CI Governance Configuration
version: 1.0

# Governance settings
governance:
  enabled: true
  strict_mode: false
  
  # Branch protection rules
  branch_protection:
    - branch: main
      required_reviews: 2
      require_ci_pass: true
      dismiss_stale_reviews: true
      require_code_owner_reviews: true
      
    - branch: develop
      required_reviews: 1
      require_ci_pass: true
  
  # CI/CD policies
  ci_policies:
    - name: code_quality
      enabled: true
      fail_on_warning: false
      thresholds:
        min_coverage: 85
        max_complexity: 15
    
    - name: security_scan
      enabled: true
      fail_on_warning: true
      severity_levels:
        - critical
        - high
    
    - name: compliance_check
      enabled: true
      fail_on_warning: false
      standards:
        - SOC2
        - GDPR
    
    - name: license_check
      enabled: true
      fail_on_warning: true
      allowed_licenses:
        - MIT
        - Apache-2.0
        - BSD-3-Clause

# Notification settings
notifications:
  enabled: true
  channels:
    - type: github
      on_failure: true
      on_success: false
    
    - type: slack
      enabled: true
      webhook_url: "${SLACK_WEBHOOK_URL}"
      channel: "#ci-governance"
      on_failure: true
      on_success: true

# Reporting
reporting:
  enabled: true
  format: json
  output_path: .zqtaskmaster-reports/
  retention_days: 90
  include_details: true
  types:
    - governance_summary
    - security_findings
    - compliance_status
    - code_quality_metrics

# Advanced settings
advanced:
  auto_fix:
    enabled: true
    types:
      - code_style
    require_approval: true
  
  custom_checks:
    - name: "API Documentation"
      command: "npm run validate-openapi"
      required: true
  
  performance:
    max_build_time_minutes: 45
    max_test_time_minutes: 20
  
  resources:
    max_parallel_jobs: 10
    timeout_minutes: 90
```

## Configuration Variables

You can use environment variables in your configuration:

```yaml
notifications:
  channels:
    - type: slack
      webhook_url: "${SLACK_WEBHOOK_URL}"
      
reporting:
  output_path: "${CI_REPORTS_PATH:-/.zqtaskmaster-reports/}"
```

## Validation

After modifying the configuration, validate it:

```bash
# Using yamllint (if available)
yamllint .zqtaskmaster.yml

# Check YAML syntax
python -c "import yaml; yaml.safe_load(open('.zqtaskmaster.yml'))"
```

## Best Practices

1. **Start Simple**: Begin with the default configuration and gradually add complexity
2. **Use Comments**: Document why specific settings are chosen
3. **Environment Variables**: Use environment variables for sensitive data
4. **Version Control**: Keep configuration in version control
5. **Review Regularly**: Periodically review and update governance policies
6. **Test Changes**: Test configuration changes in a development branch first
7. **Document Customizations**: Note any custom configurations in your repository docs

## Common Configuration Patterns

### Strict Production Protection
```yaml
governance:
  enabled: true
  strict_mode: true
  
branch_protection:
  - branch: main
    required_reviews: 2
    require_ci_pass: true
    require_code_owner_reviews: true
```

### Lenient Development Setup
```yaml
governance:
  enabled: true
  strict_mode: false
  
branch_protection:
  - branch: develop
    required_reviews: 0
    require_ci_pass: false
```

### Security-Focused Configuration
```yaml
ci_policies:
  - name: security_scan
    enabled: true
    fail_on_warning: true
    severity_levels:
      - critical
      - high
      - medium
  
  - name: license_check
    enabled: true
    fail_on_warning: true
```

## Troubleshooting

### Configuration Not Applied
- Ensure `.zqtaskmaster.yml` is in the repository root
- Check YAML syntax validity
- Verify the configuration version is supported

### Policies Too Strict
- Temporarily set `strict_mode: false`
- Adjust individual policy `fail_on_warning` settings
- Review and update thresholds

### Notifications Not Working
- Verify webhook URLs and credentials
- Check network connectivity
- Review notification channel configuration

## Further Reading

- See [BOOTSTRAP.md](BOOTSTRAP.md) for bootstrap process documentation
- See [EXAMPLES.md](EXAMPLES.md) for usage examples
- Check GitHub Actions documentation for workflow integration
