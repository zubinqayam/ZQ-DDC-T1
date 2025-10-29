.PHONY: help manifest-all manifest-validate manifest-docs-check manifest-tag-protect manifest-sign manifest-verify manifest-batch-sign manifest-batch-verify test clean

# Default target
help:
	@echo "ZQ DDC Core V1 Provenance System - Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  manifest-all          - Run all manifest checks (validate, docs-check)"
	@echo "  manifest-validate     - Validate all manifests against schema"
	@echo "  manifest-docs-check   - Check schema URI in all manifests"
	@echo "  manifest-tag-protect  - Verify all manifests are signed (requires PUBLIC_KEY)"
	@echo "  manifest-sign         - Sign a specific manifest (requires MANIFEST, SECRET_KEY)"
	@echo "  manifest-verify       - Verify a specific manifest (requires MANIFEST, PUBLIC_KEY)"
	@echo "  manifest-batch-sign   - Sign all unsigned manifests (requires SECRET_KEY)"
	@echo "  manifest-batch-verify - Verify all signed manifests (requires PUBLIC_KEY)"
	@echo "  test                  - Run all tests"
	@echo "  clean                 - Clean up generated files"
	@echo ""
	@echo "Environment variables:"
	@echo "  MANIFEST              - Path to manifest file"
	@echo "  SECRET_KEY            - Path to minisign secret key (default: keys/minisign.key)"
	@echo "  PUBLIC_KEY            - Path to minisign public key (default: keys/minisign.pub)"
	@echo "  MINISIGN_PASSWORD     - Password for secret key (for automated signing)"
	@echo ""
	@echo "Examples:"
	@echo "  make manifest-sign MANIFEST=tests/provenance/sample-manifest.yaml"
	@echo "  make manifest-verify MANIFEST=tests/provenance/sample-manifest.yaml"
	@echo "  make manifest-batch-sign"
	@echo "  make manifest-all"

# Configuration
PYTHON := python3
SECRET_KEY ?= keys/minisign.key
PUBLIC_KEY ?= keys/minisign.pub
SCHEMA := schema/manifest.schema.json

# Find all manifests
MANIFESTS := $(shell find . -name "*.yaml" -o -name "*.yml" | while read f; do \
	if grep -q "^schema_uri:" "$$f" 2>/dev/null; then echo "$$f"; fi; \
done)

# All checks
manifest-all: manifest-validate manifest-docs-check
	@echo ""
	@echo "✓ All manifest checks passed"

# Validate manifests against schema
manifest-validate:
	@echo "Validating manifests against schema..."
	@if [ -z "$(MANIFESTS)" ]; then \
		echo "No manifests found"; \
		exit 0; \
	fi; \
	FAILED=0; \
	for manifest in $(MANIFESTS); do \
		echo "Validating: $$manifest"; \
		$(PYTHON) tools/validate_schema.py "$$manifest" -s $(SCHEMA) || FAILED=1; \
	done; \
	if [ $$FAILED -ne 0 ]; then \
		echo ""; \
		echo "✗ Schema validation failed"; \
		exit 1; \
	fi; \
	echo ""; \
	echo "✓ All manifests validated successfully"

# Check schema URI in manifests
manifest-docs-check:
	@echo "Checking schema URI in manifests..."
	@if [ -z "$(MANIFESTS)" ]; then \
		echo "No manifests found"; \
		exit 0; \
	fi; \
	FAILED=0; \
	for manifest in $(MANIFESTS); do \
		echo "Checking: $$manifest"; \
		$(PYTHON) tools/check_schema_uri.py "$$manifest" || FAILED=1; \
	done; \
	if [ $$FAILED -ne 0 ]; then \
		echo ""; \
		echo "✗ Schema URI check failed"; \
		exit 1; \
	fi; \
	echo ""; \
	echo "✓ All schema URIs correct"

# Tag protection (verify all manifests are signed)
manifest-tag-protect:
	@if [ ! -f "$(PUBLIC_KEY)" ]; then \
		echo "Error: Public key not found: $(PUBLIC_KEY)"; \
		exit 1; \
	fi
	@echo "Running tag protection check..."
	@$(PYTHON) tools/tag_protect_unsigned.py -d . -p $(PUBLIC_KEY)

# Sign a specific manifest
manifest-sign:
	@if [ -z "$(MANIFEST)" ]; then \
		echo "Error: MANIFEST variable not set"; \
		echo "Usage: make manifest:sign MANIFEST=path/to/manifest.yaml"; \
		exit 1; \
	fi
	@if [ ! -f "$(SECRET_KEY)" ]; then \
		echo "Error: Secret key not found: $(SECRET_KEY)"; \
		exit 1; \
	fi
	@echo "Signing manifest: $(MANIFEST)"
	@if [ -n "$(MINISIGN_PASSWORD)" ]; then \
		$(PYTHON) tools/sign_manifest.py "$(MANIFEST)" -s $(SECRET_KEY) -p "$(MINISIGN_PASSWORD)"; \
	else \
		$(PYTHON) tools/sign_manifest.py "$(MANIFEST)" -s $(SECRET_KEY); \
	fi
	@echo "✓ Manifest signed successfully"

# Verify a specific manifest
manifest-verify:
	@if [ -z "$(MANIFEST)" ]; then \
		echo "Error: MANIFEST variable not set"; \
		echo "Usage: make manifest:verify MANIFEST=path/to/manifest.yaml"; \
		exit 1; \
	fi
	@if [ ! -f "$(PUBLIC_KEY)" ]; then \
		echo "Error: Public key not found: $(PUBLIC_KEY)"; \
		exit 1; \
	fi
	@echo "Verifying manifest: $(MANIFEST)"
	@$(PYTHON) tools/verify_manifest.py "$(MANIFEST)" -p $(PUBLIC_KEY)

# Batch sign all unsigned manifests
manifest-batch-sign:
	@if [ ! -f "$(SECRET_KEY)" ]; then \
		echo "Error: Secret key not found: $(SECRET_KEY)"; \
		exit 1; \
	fi
	@echo "Batch signing all manifests..."
	@if [ -z "$(MANIFESTS)" ]; then \
		echo "No manifests found"; \
		exit 0; \
	fi; \
	COUNT=0; \
	for manifest in $(MANIFESTS); do \
		echo "Signing: $$manifest"; \
		if [ -n "$(MINISIGN_PASSWORD)" ]; then \
			$(PYTHON) tools/sign_manifest.py "$$manifest" -s $(SECRET_KEY) -p "$(MINISIGN_PASSWORD)" && COUNT=$$((COUNT+1)); \
		else \
			$(PYTHON) tools/sign_manifest.py "$$manifest" -s $(SECRET_KEY) && COUNT=$$((COUNT+1)); \
		fi; \
	done; \
	echo ""; \
	echo "✓ Signed $$COUNT manifest(s)"

# Batch verify all signed manifests
manifest-batch-verify:
	@if [ ! -f "$(PUBLIC_KEY)" ]; then \
		echo "Error: Public key not found: $(PUBLIC_KEY)"; \
		exit 1; \
	fi
	@echo "Batch verifying all manifests..."
	@if [ -z "$(MANIFESTS)" ]; then \
		echo "No manifests found"; \
		exit 0; \
	fi; \
	FAILED=0; \
	COUNT=0; \
	for manifest in $(MANIFESTS); do \
		echo "Verifying: $$manifest"; \
		if $(PYTHON) tools/verify_manifest.py "$$manifest" -p $(PUBLIC_KEY); then \
			COUNT=$$((COUNT+1)); \
		else \
			FAILED=1; \
		fi; \
	done; \
	if [ $$FAILED -ne 0 ]; then \
		echo ""; \
		echo "✗ Some manifests failed verification"; \
		exit 1; \
	fi; \
	echo ""; \
	echo "✓ Verified $$COUNT manifest(s) successfully"

# Run tests
test:
	@echo "Running tests..."
	@if command -v pytest > /dev/null 2>&1; then \
		pytest tests/ -v; \
	else \
		echo "pytest not found, installing..."; \
		$(PYTHON) -m pip install pytest pyyaml jsonschema; \
		pytest tests/ -v; \
	fi

# Clean up
clean:
	@echo "Cleaning up..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✓ Clean complete"
